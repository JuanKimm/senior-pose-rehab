# 운동 결과 및 녹화 경로 전송

from collections.abc import Sequence
from math import isfinite
from pathlib import Path

import httpx

from core.config import BACKEND_BASE_URL, BACKEND_ENABLED


class BackendClient:
    def __init__(self) -> None:
        self.enabled = BACKEND_ENABLED
        self.base_url = BACKEND_BASE_URL.strip().rstrip("/")

    def _validate_request(self, session_id: int) -> None:
        # 세션 번호 및 백엔드 주소 검증
        if (
            isinstance(session_id, bool)
            or not isinstance(session_id, int)
            or session_id <= 0
        ):
            raise ValueError(
                "백엔드 세션 ID는 백엔드에서 발급한 1 이상의 정수여야 합니다."
            )

        if not self.base_url:
            raise RuntimeError("BACKEND_BASE_URL이 설정되지 않았습니다.")

    async def end_session(
        self,
        session_id: int,
        rep_count: int,
        duration_sec: int,
        rep_scores: Sequence[float],
    ) -> bool:
        # 운동 횟수/시간/점수 전송
        if not self.enabled:
            return False

        self._validate_request(session_id)

        if isinstance(rep_count, bool) or not isinstance(rep_count, int) or rep_count < 0:
            raise ValueError("운동 횟수는 0 이상의 정수여야 합니다.")

        if (
            isinstance(duration_sec, bool)
            or not isinstance(duration_sec, int)
            or duration_sec < 0
        ):
            raise ValueError("운동 시간은 0 이상의 정수(초)여야 합니다.")

        if rep_count != len(rep_scores):
            raise ValueError("운동 횟수와 회차별 점수 개수가 일치해야 합니다.")

        scores: list[dict[str, int]] = []

        for action_no, score in enumerate(rep_scores, start=1):
            numeric_score = float(score)

            if (
                not isfinite(numeric_score)
                or not 0.0 <= numeric_score <= 100.0
            ):
                raise ValueError(
                    "회차별 점수는 0~100 사이의 유한한 값이어야 합니다."
                )

            scores.append(
                {
                    "actionNo": action_no,
                    "actionScore": round(numeric_score),
                }
            )

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.put(
                f"{self.base_url}/api/exercise/session/{session_id}/end",
                json={
                    "totalCount": rep_count,
                    "durationSec": duration_sec,
                    "scores": scores,
                },
            )
            response.raise_for_status()

        return True

    async def send_video_path(
        self,
        session_id: int,
        video_path: str | Path,
    ) -> bool:
        # 영상 경로 전송
        if not self.enabled:
            return False

        self._validate_request(session_id)

        if not isinstance(video_path, (str, Path)):
            raise ValueError("영상 경로는 문자열 또는 Path여야 합니다.")

        video_path_text = str(video_path).strip()

        if not video_path_text or video_path_text == ".":
            raise ValueError("전송할 영상 경로가 비어 있습니다.")

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{self.base_url}/api/exercise/session/{session_id}/video-upload",
                json={"videoPath": video_path_text},
            )
            response.raise_for_status()

        return True
