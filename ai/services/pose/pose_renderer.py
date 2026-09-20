# 추정된 관절과 운동 단계, 반복 횟수 및 기준 자세 유사도를 프레임에 표시합니다.
# 완성된 프레임은 화면 전송과 스켈레톤 오버레이 영상 저장에 함께 사용됩니다.
import cv2
import numpy as np

from core.config import MIN_LANDMARK_VISIBILITY
from core.landmarks import POSE_CONNECTIONS
from models.reference_profile import MotionFeatures
from services.pose.base import PoseResult

PHASE_LABELS = {
    "waiting_closed": "READY - CLOSE ELBOWS",
    "closed": "CLOSED",
    "opening": "OPENING",
    "open": "OPEN",
    "closing": "CLOSING",
}


def draw_pose(
    frame: np.ndarray,
    pose: PoseResult | None,
    phase: str,
    rep_count: int,
    accuracy: float,
    features: MotionFeatures | None = None,
    exercise_code: str = "shoulder_open_close",
) -> np.ndarray:
    rendered = frame.copy()
    height, width = rendered.shape[:2]

    if pose is not None:
        for start_idx, end_idx in POSE_CONNECTIONS:
            start = pose.normalized[int(start_idx)]
            end = pose.normalized[int(end_idx)]
            if min(start.visibility, end.visibility) < MIN_LANDMARK_VISIBILITY:
                continue
            start_px = (int(start.x * width), int(start.y * height))
            end_px = (int(end.x * width), int(end.y * height))
            cv2.line(rendered, start_px, end_px, (40, 220, 255), 3, cv2.LINE_AA)

        for point in pose.normalized:
            if point.visibility < MIN_LANDMARK_VISIBILITY:
                continue
            center = (int(point.x * width), int(point.y * height))
            cv2.circle(rendered, center, 4, (30, 80, 255), -1, cv2.LINE_AA)

    phase_label = PHASE_LABELS.get(phase, phase.upper())
    if exercise_code == "gaze_pull" and phase == "waiting_high":
        phase_label = "READY - DIAGONAL REACH"
    cv2.rectangle(rendered, (10, 10), (430, 114), (20, 20, 20), -1)
    cv2.putText(
        rendered,
        f"PHASE: {phase_label}",
        (22, 38),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        rendered,
        f"REPS: {rep_count}   SIM: {accuracy:.1f}",
        (22, 67),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    if features is not None:
        cv2.putText(
            rendered,
            (
                f"HAND HEIGHT L/R: {features.gaze_pull.left.height:.2f}/{features.gaze_pull.right.height:.2f}"
                if features.gaze_pull is not None
                else f"ELBOW SPREAD: {features.elbow_spread_ratio:.2f}"
            ),
            (22, 96),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (80, 235, 150),
            2,
            cv2.LINE_AA,
        )
    return rendered
