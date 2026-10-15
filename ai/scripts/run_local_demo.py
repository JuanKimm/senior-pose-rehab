# 프론트엔드 없이 로컬 웹캠으로 선택한 운동 분석과 영상 저장을 시험합니다.
# q 키를 누르면 종료되고 storage/recordings에 스켈레톤 MP4가 남습니다.
import os
from pathlib import Path
from time import monotonic

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from core.config import (
    CAMERA_INDEX,
    POSE_MODEL_PATH,
    ensure_directories,
)
from core.exercise_cli import parse_exercise_args
from services.feedback.feedback_engine import FEEDBACK_MESSAGES, FEEDBACK_PRIORITY
from services.pose.blazepose_estimator import BlazePoseEstimator
from services.pose.pose_renderer import draw_pose
from services.reference.reference_repository import ReferenceRepository
from services.session.session_manager import SessionManager


def _load_korean_font(size: int = 28):
    """Windows 맑은 고딕을 우선 사용하며 LOCAL_FEEDBACK_FONT로 변경할 수 있습니다."""
    custom_path = os.getenv("LOCAL_FEEDBACK_FONT")
    candidates = (
        [Path(custom_path)]
        if custom_path
        else [
            Path(os.getenv("WINDIR", "C:/Windows")) / "Fonts/malgun.ttf",
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
            Path("/usr/share/fonts/truetype/nanum/NanumGothic.ttf"),
            Path("/System/Library/Fonts/AppleSDGothicNeo.ttc"),
        ]
    )
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    raise FileNotFoundError(
        "한글 폰트를 찾지 못했습니다. Windows의 맑은 고딕 설치를 확인하거나 "
        "LOCAL_FEEDBACK_FONT 환경변수에 한글 폰트 파일 경로를 지정하세요."
    )


def _current_feedback(session, features) -> tuple[str, str]:
    """화면용: 로그 쿨다운이나 과거 문구 없이 현재 자세를 매 프레임 재판정합니다."""
    if features is None:
        return "POSE_NOT_DETECTED", FEEDBACK_MESSAGES["POSE_NOT_DETECTED"]

    codes = session.analyzer.current_feedback(features, session.profile, session.state)

    # 오류가 없으면 즉시 비웁니다. 여러 오류는 기존 우선순위대로 한 개씩 표시합니다.
    code = next((item for item in FEEDBACK_PRIORITY if item in codes), "")
    return code, FEEDBACK_MESSAGES.get(code, "")


def _draw_local_feedback(frame, message: str, font):
    """로컬 화면의 복사본에만 한글을 표시합니다. 원본/녹화 프레임은 바꾸지 않습니다."""
    if not message:
        return frame

    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image)
    margin, padding = 12, 16
    max_width = image.width - 2 * (margin + padding)
    lines, line = [], ""
    for char in message:
        if line and draw.textlength(line + char, font=font) > max_width:
            lines.append(line.rstrip())
            line = char.lstrip()
        else:
            line += char
    if line:
        lines.append(line)

    line_height = font.size + 10
    box_height = 2 * padding + len(lines) * line_height
    top = max(margin, image.height - margin - box_height)
    draw.rounded_rectangle(
        (margin, top, image.width - margin, image.height - margin),
        radius=12,
        fill=(24, 37, 48),
    )
    for index, line in enumerate(lines):
        draw.text(
            (margin + padding, top + padding + index * line_height),
            line,
            font=font,
            fill=(255, 255, 255),
            anchor="lt",
        )
    return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)


def _read_reference_frame(capture: cv2.VideoCapture, start_sec: float, end_sec: float):
    """기준 영상의 분석 구간을 반복 재생하며 다음 프레임을 반환합니다."""
    if end_sec > start_sec and capture.get(cv2.CAP_PROP_POS_MSEC) >= end_sec * 1000:
        capture.set(cv2.CAP_PROP_POS_MSEC, start_sec * 1000)

    ok, frame = capture.read()
    if ok:
        return frame

    capture.set(cv2.CAP_PROP_POS_MSEC, start_sec * 1000)
    ok, frame = capture.read()
    return frame if ok else None


def _fit_to_panel(frame, target_width: int, target_height: int):
    """영상 비율을 유지한 채 지정된 패널 크기에 맞추고 빈 영역을 검게 채웁니다."""
    height, width = frame.shape[:2]
    scale = min(target_width / width, target_height / height)
    resized_width = max(1, int(width * scale))
    resized_height = max(1, int(height * scale))
    resized = cv2.resize(frame, (resized_width, resized_height))

    left = (target_width - resized_width) // 2
    right = target_width - resized_width - left
    top = (target_height - resized_height) // 2
    bottom = target_height - resized_height - top
    return cv2.copyMakeBorder(
        resized,
        top,
        bottom,
        left,
        right,
        cv2.BORDER_CONSTANT,
        value=(0, 0, 0),
    )


def main() -> None:
    spec, start_sec, end_sec = parse_exercise_args("운동별 로컬 웹캠 데모")
    ensure_directories()
    profile = ReferenceRepository(spec.profile_path).load()
    if profile.exercise_code != spec.code:
        raise ValueError("선택한 운동과 기준 프로필이 다릅니다.")
    feedback_font = _load_korean_font()
    print(f"선택한 운동: {spec.name} ({spec.code})")
    estimator = BlazePoseEstimator(POSE_MODEL_PATH)
    manager = SessionManager()
    session_id = f"local_{spec.code}_demo"
    session = manager.start(session_id, profile)
    capture = cv2.VideoCapture(CAMERA_INDEX)
    if not capture.isOpened():
        estimator.close()
        manager.end(session_id)
        raise RuntimeError(f"웹캠 {CAMERA_INDEX}번을 열 수 없습니다.")

    reference_capture = cv2.VideoCapture(str(spec.video_path))
    if not reference_capture.isOpened():
        capture.release()
        estimator.close()
        manager.end(session_id)
        raise RuntimeError(f"기준 영상을 열 수 없습니다. 다음 경로를 확인하세요: {spec.video_path}")
    reference_capture.set(
        cv2.CAP_PROP_POS_MSEC,
        start_sec * 1000,
    )

    window_name = "User Pose | Reference - press q to quit"
    clock_started = monotonic()
    try:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1600, 800)
        while True:
            ok, frame = capture.read()
            if not ok:
                break

            timestamp_ms = int((monotonic() - clock_started) * 1000)
            timestamp_ms = max(timestamp_ms, session.state.last_pose_timestamp_ms + 1)
            session.state.last_pose_timestamp_ms = timestamp_ms
            session.state.frame_count += 1

            pose = estimator.detect(frame, timestamp_ms)
            if pose is None:
                analysis = manager.pose_missing(session_id, timestamp_ms)
            else:
                analysis = manager.process_pose(session_id, pose, timestamp_ms)

            rendered = draw_pose(
                frame,
                pose,
                session.state.phase,
                session.state.rep_count,
                session.state.accuracy,
                analysis.features,
                exercise_code=spec.code,
            )
            manager.record(session_id, rendered)

            reference_frame = _read_reference_frame(reference_capture, start_sec, end_sec)
            if reference_frame is None:
                raise RuntimeError("기준 영상 프레임을 읽을 수 없습니다.")

            height, width = rendered.shape[:2]
            user_panel = rendered.copy()
            reference_panel = _fit_to_panel(reference_frame, width, height)
            cv2.putText(
                user_panel,
                "USER",
                (20, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                reference_panel,
                "REFERENCE",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )
            # 현재 프레임을 녹화한 다음 표시용 복사본에만 한글을 그립니다.
            _, display_feedback = _current_feedback(session, analysis.features)
            comparison_view = cv2.hconcat([user_panel, reference_panel])
            comparison_view = _draw_local_feedback(comparison_view, display_feedback, feedback_font)
            cv2.imshow(window_name, comparison_view)

            if analysis.feedback:
                print(f"피드백: {analysis.feedback}")

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        capture.release()
        reference_capture.release()
        cv2.destroyAllWindows()
        estimator.close()
        result = manager.end(session_id)

    if result is not None:
        state, recording_path = result
        print(f"반복 횟수: {state.rep_count}")
        print(f"평균 기준 자세 유사도: {state.accuracy:.1f}")
        print(f"저장 영상: {recording_path}")


if __name__ == "__main__":
    main()
