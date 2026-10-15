from math import hypot, isfinite
from statistics import mean

from core.config import MIN_LANDMARK_VISIBILITY
from core.landmarks import PoseLandmark as L
from models.reference_profile import MotionFeatures, PhaseTarget, ReferenceProfile
from models.session_state import SessionState
from services.analysis.angle_calculator import angle_degrees, distance_2d, midpoint
from services.exercises.base import ExerciseAnalyzer, ExerciseEvaluation
from services.pose.base import LandmarkPoint, PoseResult

REQUIRED_LANDMARKS = (
    L.NOSE,
    L.LEFT_EAR,
    L.RIGHT_EAR,
    L.LEFT_SHOULDER,
    L.RIGHT_SHOULDER,
    L.LEFT_ELBOW,
    L.RIGHT_ELBOW,
    L.LEFT_WRIST,
    L.RIGHT_WRIST,
)

CLOSE_REDUCTION_RATIO = 0.25
REOPEN_INCREASE_RATIO = 0.15
MIN_COUNT_DISTANCE_DELTA = 0.015
CLOSED_SETTLE_MS = 150
SETTLE_MOVEMENT_RATIO = 0.01


def _as_metrics(features: MotionFeatures) -> dict[str, float]:
    return {
        "elbow_spread_ratio": features.elbow_spread_ratio,
        "head_lift_ratio": features.head_lift_ratio,
        "wrist_ear_ratio": features.wrist_ear_ratio,
        "elbow_angle_deg": features.elbow_angle_deg,
        "symmetry_ratio": features.symmetry_ratio,
    }


class ShoulderOpenCloseAnalyzer(ExerciseAnalyzer):
    def __init__(self) -> None:
        self._reset_counter()

    def _reset_counter(self) -> None:
        self._closed_distance: float | None = None
        self._peak_distance: float | None = None
        self._trough_distance: float | None = None
        self._settle_anchor: float | None = None
        self._settle_since_ms: int | None = None
        self._closing_since_ms: int | None = None

    def reset_motion(self, state: SessionState) -> None:
        state.phase = "waiting_closed"
        state.best_open_metrics = None
        state.best_closed_metrics = None
        state.saw_open = False
        self._reset_counter()

    def current_feedback(
        self, features: MotionFeatures | None, profile: ReferenceProfile, state: SessionState
    ) -> list[str]:
        if features is None:
            return ["POSE_NOT_DETECTED"]
        opened = state.phase in ("opening", "open")
        target = profile.open_target if opened else profile.closed_target
        codes = self._phase_feedback(
            _as_metrics(features), target, profile, "open" if opened else "closed"
        )
        if not features.hands_near_ears:
            codes.append("KEEP_HANDS_BY_EARS")
        return codes

    @staticmethod
    def _point(points: list[LandmarkPoint], index: L) -> LandmarkPoint:
        return points[int(index)]

    def extract_features(self, pose: PoseResult) -> MotionFeatures | None:
        if pose.image_width <= 0 or pose.image_height <= 0:
            return None
        points = pose.normalized
        if len(points) < 33:
            return None

        relevant = [self._point(points, index) for index in REQUIRED_LANDMARKS]
        if any(
            not all(isfinite(v) for v in (point.x, point.y, point.z, point.visibility))
            for point in relevant
        ):
            return None
        confidence = mean(point.visibility for point in relevant)
        if confidence < MIN_LANDMARK_VISIBILITY:
            return None

        left_shoulder = self._point(points, L.LEFT_SHOULDER)
        right_shoulder = self._point(points, L.RIGHT_SHOULDER)
        left_elbow = self._point(points, L.LEFT_ELBOW)
        right_elbow = self._point(points, L.RIGHT_ELBOW)
        left_wrist = self._point(points, L.LEFT_WRIST)
        right_wrist = self._point(points, L.RIGHT_WRIST)
        left_ear = self._point(points, L.LEFT_EAR)
        right_ear = self._point(points, L.RIGHT_EAR)
        nose = self._point(points, L.NOSE)

        shoulder_width = distance_2d(left_shoulder, right_shoulder)
        if shoulder_width < 1e-5:
            return None

        shoulder_mid = midpoint(left_shoulder, right_shoulder)
        elbow_distance = hypot(
            left_elbow.x - right_elbow.x,
            (left_elbow.y - right_elbow.y) * pose.image_height / pose.image_width,
        )
        elbow_spread_ratio = distance_2d(left_elbow, right_elbow) / shoulder_width
        wrist_ear_left = distance_2d(left_wrist, left_ear) / shoulder_width
        wrist_ear_right = distance_2d(right_wrist, right_ear) / shoulder_width
        wrist_ear_ratio = mean((wrist_ear_left, wrist_ear_right))

        center_x = shoulder_mid[0]
        left_extent = abs(center_x - left_elbow.x)
        right_extent = abs(right_elbow.x - center_x)
        symmetry_ratio = abs(left_extent - right_extent) / shoulder_width
        shoulder_level_ratio = abs(left_shoulder.y - right_shoulder.y) / shoulder_width
        head_lift_ratio = (shoulder_mid[1] - nose.y) / shoulder_width

        angle_points = pose.world if len(pose.world) >= 33 else pose.normalized
        try:
            left_elbow_angle = angle_degrees(
                self._point(angle_points, L.LEFT_SHOULDER),
                self._point(angle_points, L.LEFT_ELBOW),
                self._point(angle_points, L.LEFT_WRIST),
            )
            right_elbow_angle = angle_degrees(
                self._point(angle_points, L.RIGHT_SHOULDER),
                self._point(angle_points, L.RIGHT_ELBOW),
                self._point(angle_points, L.RIGHT_WRIST),
            )
        except ValueError:
            return None

        return MotionFeatures(
            elbow_distance=elbow_distance,
            elbow_spread_ratio=elbow_spread_ratio,
            head_lift_ratio=head_lift_ratio,
            wrist_ear_ratio=wrist_ear_ratio,
            elbow_angle_deg=mean((left_elbow_angle, right_elbow_angle)),
            symmetry_ratio=symmetry_ratio,
            shoulder_level_ratio=shoulder_level_ratio,
            confidence=max(0.0, min(1.0, confidence)),
            hands_near_ears=max(wrist_ear_left, wrist_ear_right) <= 1.05,
        )

    @staticmethod
    def _closeness(value: float, target: float, tolerance: float) -> float:
        scale = max(tolerance * 3.5, 1e-5)
        excess = max(0.0, abs(value - target) - tolerance)
        return max(0.0, 100.0 * (1.0 - excess / scale))

    def _rep_score(
        self,
        open_metrics: dict[str, float],
        closed_metrics: dict[str, float],
        profile: ReferenceProfile,
    ) -> float:
        tolerance = profile.tolerances
        open_target = profile.open_target
        closed_target = profile.closed_target
        
        elbow_tolerance = max(
            tolerance.elbow_spread_ratio,
            abs(profile.thresholds.closed_elbow_ratio - closed_target.elbow_spread_ratio),
            abs(open_target.elbow_spread_ratio - profile.thresholds.open_elbow_ratio),
        )
        components = (
            (
                0.40,
                self._closeness(
                    open_metrics["elbow_spread_ratio"],
                    open_target.elbow_spread_ratio,
                    elbow_tolerance,
                ),
            ),
            (
                0.20,
                self._closeness(
                    closed_metrics["elbow_spread_ratio"],
                    closed_target.elbow_spread_ratio,
                    elbow_tolerance,
                ),
            ),
            (
                0.30,
                self._closeness(
                    open_metrics["head_lift_ratio"],
                    open_target.head_lift_ratio,
                    tolerance.head_lift_ratio,
                ),
            ),
            (
                0.10,
                self._closeness(
                    closed_metrics["head_lift_ratio"],
                    closed_target.head_lift_ratio,
                    tolerance.head_lift_ratio,
                ),
            ),
            (
                0.10,
                self._closeness(
                    mean(
                        (
                            open_metrics["wrist_ear_ratio"],
                            closed_metrics["wrist_ear_ratio"],
                        )
                    ),
                    mean((open_target.wrist_ear_ratio, closed_target.wrist_ear_ratio)),
                    tolerance.wrist_ear_ratio,
                ),
            ),
            (
                0.10,
                self._closeness(
                    mean(
                        (
                            open_metrics["elbow_angle_deg"],
                            closed_metrics["elbow_angle_deg"],
                        )
                    ),
                    mean((open_target.elbow_angle_deg, closed_target.elbow_angle_deg)),
                    tolerance.elbow_angle_deg,
                ),
            ),
            (
                0.05,
                self._closeness(
                    mean(
                        (
                            open_metrics["symmetry_ratio"],
                            closed_metrics["symmetry_ratio"],
                        )
                    ),
                    mean((open_target.symmetry_ratio, closed_target.symmetry_ratio)),
                    tolerance.symmetry_ratio,
                ),
            ),
        )
        total_weight = sum(weight for weight, _ in components)
        return round(
        sum(weight * score for weight, score in components) / total_weight, 1,)

    @staticmethod
    def _phase_feedback(
        metrics: dict[str, float],
        target: PhaseTarget,
        profile: ReferenceProfile,
        phase: str,
    ) -> list[str]:
        codes: list[str] = []
        tolerance = profile.tolerances

        if phase == "open":
            if metrics["elbow_spread_ratio"] < (
                target.elbow_spread_ratio - tolerance.elbow_spread_ratio
            ):
                codes.append("OPEN_ELBOWS_MORE")
            if metrics["head_lift_ratio"] < (target.head_lift_ratio - tolerance.head_lift_ratio):
                codes.append("LIFT_HEAD_MORE")
        else:
            if metrics["elbow_spread_ratio"] > (
                target.elbow_spread_ratio + tolerance.elbow_spread_ratio
            ):
                codes.append("CLOSE_ELBOWS_MORE")
            if metrics["head_lift_ratio"] > (target.head_lift_ratio + tolerance.head_lift_ratio):
                codes.append("LOWER_HEAD_MORE")

        if metrics["wrist_ear_ratio"] > (target.wrist_ear_ratio + tolerance.wrist_ear_ratio):
            codes.append("KEEP_HANDS_BY_EARS")
        if metrics["symmetry_ratio"] > (target.symmetry_ratio + tolerance.symmetry_ratio):
            codes.append("MOVE_SYMMETRICALLY")
        return codes

    def update(
        self,
        state: SessionState,
        features: MotionFeatures,
        profile: ReferenceProfile,
    ) -> ExerciseEvaluation:
        codes: list[str] = []
        value = (
            features.elbow_distance
            if features.elbow_distance is not None
            else features.elbow_spread_ratio
        )
        metrics = _as_metrics(features)
        now = max(0, state.last_pose_timestamp_ms)

        if not features.hands_near_ears:
            self.reset_motion(state)
            return ExerciseEvaluation(
                phase=state.phase,
                feedback_codes=["KEEP_HANDS_BY_EARS"],
            )

        if state.phase == "waiting_closed":
            self._closed_distance = value
            state.phase = "closed"
            state.best_closed_metrics = metrics

        elif state.phase == "closed":
            if self._closed_distance is None or value < self._closed_distance:
                self._closed_distance = value
                state.best_closed_metrics = metrics
            baseline = self._closed_distance if self._closed_distance is not None else value
            reopen_delta = max(
                baseline * REOPEN_INCREASE_RATIO,
                MIN_COUNT_DISTANCE_DELTA,
            )
            if value >= baseline + reopen_delta:
                state.phase = "open"
                state.saw_open = True
                self._peak_distance = value
                state.best_open_metrics = metrics

        elif state.phase in ("opening", "open"):
            if self._peak_distance is None or value > self._peak_distance:
                self._peak_distance = value
                state.best_open_metrics = metrics
            peak = self._peak_distance if self._peak_distance is not None else value
            close_delta = max(peak * CLOSE_REDUCTION_RATIO, MIN_COUNT_DISTANCE_DELTA)
            if peak - value + 1e-9 >= close_delta:
                state.phase = "closing"
                self._trough_distance = value
                self._settle_anchor = value
                self._settle_since_ms = now
                self._closing_since_ms = now
                state.best_closed_metrics = metrics

        elif state.phase == "closing":
            peak = self._peak_distance if self._peak_distance is not None else value
            if self._trough_distance is None or value < self._trough_distance:
                self._trough_distance = value
                state.best_closed_metrics = metrics
            movement_delta = max(peak * SETTLE_MOVEMENT_RATIO, 1e-9)
            if self._settle_anchor is None or value <= self._settle_anchor - movement_delta:
                self._settle_anchor = value
                self._settle_since_ms = now

            trough = self._trough_distance if self._trough_distance is not None else value
            close_delta = max(peak * CLOSE_REDUCTION_RATIO, MIN_COUNT_DISTANCE_DELTA)
            reopen_delta = max(trough * REOPEN_INCREASE_RATIO, MIN_COUNT_DISTANCE_DELTA)
            still_closed = peak - value + 1e-9 >= close_delta
            settled = (
                still_closed
                and self._settle_since_ms is not None
                and now - self._settle_since_ms >= CLOSED_SETTLE_MS
            )
            reopening = value - trough + 1e-9 >= reopen_delta
            turned_back = (
                reopening
                and self._closing_since_ms is not None
                and now - self._closing_since_ms >= CLOSED_SETTLE_MS
            )

            if settled or turned_back:
                best_open = state.best_open_metrics
                best_closed = state.best_closed_metrics
                if state.saw_open and best_open is not None and best_closed is not None:
                    codes.extend(
                        self._phase_feedback(best_open, profile.open_target, profile, "open")
                    )
                    codes.extend(
                        self._phase_feedback(best_closed, profile.closed_target, profile, "closed")
                    )
                    rep_score = self._rep_score(best_open, best_closed, profile)
                    state.rep_count += 1
                    state.rep_scores.append(rep_score)
                    state.phase = "closed"
                    state.saw_open = False
                    state.best_open_metrics = None
                    self._closed_distance = trough
                    self._peak_distance = None
                    self._trough_distance = None
                    self._settle_anchor = None
                    self._settle_since_ms = None
                    self._closing_since_ms = None

                    if reopening:
                        state.phase = "open"
                        state.saw_open = True
                        self._peak_distance = value
                        state.best_open_metrics = metrics

                    if not codes:
                        codes.append("GOOD_REP")
                    return ExerciseEvaluation(
                        phase=state.phase,
                        feedback_codes=list(dict.fromkeys(codes)),
                        rep_completed=True,
                        rep_score=rep_score,
                    )

            elif reopening:

                state.phase = "open"
                self._peak_distance = max(peak, value)
                if value >= peak:
                    state.best_open_metrics = metrics
                self._trough_distance = None
                self._settle_anchor = None
                self._settle_since_ms = None
                self._closing_since_ms = None

            elif not still_closed:
                self._settle_anchor = value
                self._settle_since_ms = now

        return ExerciseEvaluation(
            phase=state.phase,
            feedback_codes=list(dict.fromkeys(codes)),
        )
