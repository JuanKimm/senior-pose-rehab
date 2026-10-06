import json
import logging
from asyncio import TimeoutError, wait_for
from pathlib import Path
from time import monotonic

import cv2
import httpx
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from clients.backend_client import BackendClient
from core.config import (
    FRONTEND_ORIGINS,
    JPEG_QUALITY,
    POSE_MODEL_PATH,
    TARGET_REP_COUNT,
)
from core.exercise_catalog import get_exercise
from models.schemas import AnalysisResponse, ErrorResponse, SessionSummaryResponse
from models.session_state import SessionState
from services.pose.blazepose_estimator import BlazePoseEstimator
from services.pose.pose_renderer import draw_pose
from services.reference.reference_repository import ReferenceRepository
from services.session.session_manager import SessionAlreadyActiveError, SessionManager

router = APIRouter(tags=["exercise"])
session_manager = SessionManager()
backend_client = BackendClient()
logger = logging.getLogger(__name__)


def _summary(
    session_id: str,
    result: tuple[SessionState, Path | None] | None,
) -> SessionSummaryResponse | None:
    if result is None:
        return None
    state, recording_path = result
    return SessionSummaryResponse(
        session_id=session_id,
        exercise_code=state.exercise_code,
        rep_count=state.rep_count,
        left_rep_count=state.left_rep_count,
        right_rep_count=state.right_rep_count,
        duration_sec=state.duration_sec,
        accuracy=state.accuracy,
        rep_scores=state.rep_scores,
        recording_path=str(recording_path) if recording_path else None,
    )


async def _finish_session(session_id: str) -> SessionSummaryResponse | None:
    # 녹화를 닫고 전송 대기 시간에 영향받지 않도록 운동 요약을 먼저 확정
    summary = _summary(session_id, session_manager.end(session_id))
    if summary is None:
        return None

    if not backend_client.enabled:
        summary.backend_error = "BACKEND_DISABLED"
        return summary

    try:
        summary.backend_sent = await backend_client.end_session(
            session_id=int(session_id),
            rep_count=summary.rep_count,
            duration_sec=summary.duration_sec,
            rep_scores=summary.rep_scores,
        )
    except httpx.HTTPStatusError as exc:
        summary.backend_error = f"BACKEND_HTTP_{exc.response.status_code}"
        logger.error(
            "백엔드 종료 요청 실패: session_id=%s, status=%s",
            session_id,
            exc.response.status_code,
        )
    except httpx.RequestError:
        summary.backend_error = "BACKEND_CONNECTION_FAILED"
        logger.exception("백엔드 연결 실패: session_id=%s", session_id)
    except (ValueError, RuntimeError):
        summary.backend_error = "BACKEND_INVALID_RESULT_OR_CONFIG"
        logger.exception("백엔드 전송 값 또는 설정 오류: session_id=%s", session_id)

    # 결과 전송과 영상 업로드의 실패를 독립적으로 처리
    if summary.recording_path:
        try:
            await wait_for(
                backend_client.upload_video(
                    session_id=int(session_id),
                    video_path=summary.recording_path,
                ),
                timeout=60.0,
            )
        except httpx.HTTPStatusError as exc:
            logger.error(
                "영상 업로드 실패: session_id=%s, status=%s",
                session_id,
                exc.response.status_code,
            )
        except (httpx.RequestError, TimeoutError):
            logger.exception("영상 업로드 연결 실패 또는 시간 초과: session_id=%s", session_id)
        except (OSError, ValueError, RuntimeError):
            logger.exception("영상 파일 또는 업로드 설정 오류: session_id=%s", session_id)

    return summary


@router.websocket("/ws/exercise/{session_id}")
async def exercise_websocket(
    websocket: WebSocket, session_id: str, exercise_code: str = "shoulder_open_close"
) -> None:
    origin = websocket.headers.get("origin")
    if origin and origin not in FRONTEND_ORIGINS:
        await websocket.close(code=1008, reason="허용되지 않은 프론트엔드 주소입니다.")
        return

    await websocket.accept()
    # 연동을 켠 경우 백엔드가 발급한 양의 정수 세션 번호만 허용
    if backend_client.enabled and (
        not session_id.isascii()
        or not session_id.isdecimal()
        or int(session_id) <= 0
    ):
        await websocket.send_json(
            ErrorResponse(
                code="INVALID_SESSION_ID",
                message="백엔드에서 발급한 1 이상의 정수 세션 번호를 사용하세요.",
            ).model_dump()
        )
        await websocket.close(code=1008)
        return

    try:
        spec = get_exercise(exercise_code)
    except ValueError as exc:
        await websocket.send_json(
            ErrorResponse(code="UNSUPPORTED_EXERCISE", message=str(exc)).model_dump()
        )
        await websocket.close(code=1008)
        return
    estimator: BlazePoseEstimator | None = None
    session_started = False

    try:
        profile = ReferenceRepository(spec.profile_path).load()
        if profile.exercise_code != spec.code:
            raise ValueError("선택한 운동과 기준 프로필의 운동 코드가 다릅니다.")
        estimator = BlazePoseEstimator(POSE_MODEL_PATH)
        session = session_manager.start(session_id, profile)
        session_started = True
        clock_started = monotonic()

        await websocket.send_json(
            {
                "type": "ready",
                "session_id": session_id,
                "exercise_code": profile.exercise_code,
                "reference_rep_count": profile.reference_rep_count,
            }
        )

        while True:
            message = await websocket.receive()
            if message.get("type") == "websocket.disconnect":
                break

            text_message = message.get("text")
            if text_message is not None:
                try:
                    command = json.loads(text_message)
                except json.JSONDecodeError:
                    command = {"type": text_message}
                if not isinstance(command, dict):
                    await websocket.send_json(
                        ErrorResponse(
                            code="INVALID_COMMAND", message="명령은 JSON 객체여야 합니다."
                        ).model_dump()
                    )
                    continue
                if command.get("type") == "stop":
                    # 프론트 응답이 실패해도 종료 요청을 다시 보내지 않도록 표시
                    session_started = False
                    summary = await _finish_session(session_id)
                    if summary is not None:
                        await websocket.send_json(summary.model_dump())
                    await websocket.close(code=1000)
                    return
                if command.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                continue

            frame_bytes = message.get("bytes")
            if not frame_bytes:
                continue

            encoded = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
            if frame is None:
                await websocket.send_json(
                    ErrorResponse(
                        code="INVALID_FRAME",
                        message="JPEG 프레임을 해석할 수 없습니다.",
                    ).model_dump()
                )
                continue

            timestamp_ms = int((monotonic() - clock_started) * 1000)
            timestamp_ms = max(timestamp_ms, session.state.last_pose_timestamp_ms + 1)
            session.state.last_pose_timestamp_ms = timestamp_ms
            session.state.frame_count += 1

            pose = estimator.detect(frame, timestamp_ms)
            if pose is None:
                analysis = session_manager.pose_missing(session_id, timestamp_ms)
            else:
                analysis = session_manager.process_pose(session_id, pose, timestamp_ms)

            rendered = draw_pose(
                frame=frame,
                pose=pose,
                phase=session.state.phase,
                rep_count=session.state.rep_count,
                accuracy=session.state.accuracy,
                features=analysis.features,
                exercise_code=profile.exercise_code,
            )
            session_manager.record(session_id, rendered)

            response = AnalysisResponse(
                session_id=session_id,
                frame_id=session.state.frame_count,
                timestamp_ms=timestamp_ms,
                pose_detected=pose is not None and analysis.features is not None,
                phase=session.state.phase,
                rep_count=session.state.rep_count,
                accuracy=session.state.accuracy,
                left_rep_count=session.state.left_rep_count,
                right_rep_count=session.state.right_rep_count,
                feedback_code=analysis.feedback_code,
                feedback=analysis.feedback,
                features=analysis.features,
            )
            await websocket.send_json(response.model_dump())

            ok, annotated_jpeg = cv2.imencode(
                ".jpg", rendered, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
            )
            if ok:
                await websocket.send_bytes(annotated_jpeg.tobytes())

            # 목표 달성 시 자동 종료
            if session.state.rep_count >= TARGET_REP_COUNT:
                session_started = False
                summary = await _finish_session(session_id)
                if summary is not None:
                    if hasattr(summary, "end_reason"):
                        summary.end_reason = "target_reached"
                    await websocket.send_json(summary.model_dump())
                await websocket.close(code=1000)
                return

    except FileNotFoundError as exc:
        await websocket.send_json(
            ErrorResponse(code="REFERENCE_NOT_READY", message=str(exc)).model_dump()
        )
        await websocket.close(code=1011)
    except SessionAlreadyActiveError as exc:
        await websocket.send_json(
            ErrorResponse(code="SESSION_ALREADY_ACTIVE", message=str(exc)).model_dump()
        )
        await websocket.close(code=1008)
    except ValueError as exc:
        await websocket.send_json(
            ErrorResponse(code="INVALID_REFERENCE_OR_MESSAGE", message=str(exc)).model_dump()
        )
        await websocket.close(code=1008)
    except WebSocketDisconnect:
        pass
    finally:
        # 연결 해제 시에도 결과를 한 번 전송하고 자세 추정기 자원을 정리
        try:
            if session_started:
                await _finish_session(session_id)
        finally:
            if estimator is not None:
                estimator.close()
