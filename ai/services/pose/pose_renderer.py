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

    return rendered
