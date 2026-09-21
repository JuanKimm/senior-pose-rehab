# 실시간 관절 특징에 중앙값과 EMA를 적용하여 프레임별 흔들림을 줄입니다.
# 상태 전환이 한두 프레임의 오검출로 반복되는 문제를 완화합니다.
from collections import defaultdict, deque
from statistics import median

from models.gaze_pull import GazePullFeatures, ReachMetrics
from models.reference_profile import MotionFeatures


class FeatureSmoother:
    def __init__(self, window_size: int = 5, ema_alpha: float = 0.45) -> None:
        self._window_size = window_size
        self._ema_alpha = ema_alpha
        self._windows: dict[str, deque[float]] = defaultdict(
            lambda: deque(maxlen=self._window_size)
        )
        self._ema: dict[str, float] = {}

    def _smooth_value(self, name: str, value: float) -> float:
        window = self._windows[name]
        window.append(float(value))
        median_value = float(median(window))
        previous = self._ema.get(name, median_value)
        smoothed = self._ema_alpha * median_value + (1.0 - self._ema_alpha) * previous
        self._ema[name] = smoothed
        return smoothed

    def _smooth_gaze(self, features: GazePullFeatures | None) -> GazePullFeatures | None:
        if features is None:
            return None
        sides = {}
        for side in ("left", "right"):
            values = getattr(features, side).model_dump()
            smoothed = {
                key: self._smooth_value(f"gaze_{side}_{key}", value)
                for key, value in values.items()
            }
            sides[side] = ReachMetrics(**smoothed)
        return GazePullFeatures(**sides)

    def update(self, features: MotionFeatures) -> MotionFeatures:
        return MotionFeatures(
            gaze_pull=self._smooth_gaze(features.gaze_pull),
            elbow_spread_ratio=self._smooth_value(
                "elbow_spread_ratio", features.elbow_spread_ratio
            ),
            head_lift_ratio=self._smooth_value("head_lift_ratio", features.head_lift_ratio),
            wrist_ear_ratio=self._smooth_value("wrist_ear_ratio", features.wrist_ear_ratio),
            elbow_angle_deg=self._smooth_value("elbow_angle_deg", features.elbow_angle_deg),
            symmetry_ratio=self._smooth_value("symmetry_ratio", features.symmetry_ratio),
            shoulder_level_ratio=self._smooth_value(
                "shoulder_level_ratio", features.shoulder_level_ratio
            ),
            confidence=features.confidence,
            hands_near_ears=features.hands_near_ears,
        )
