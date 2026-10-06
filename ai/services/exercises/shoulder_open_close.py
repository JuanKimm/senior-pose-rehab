# 귀에 손을 댄 채 팔꿈치와 고개를 함께 펼치고 오므리는 운동을 판정합니다.
# 팔꿈치 간격, 고개 높이, 손-귀 거리, 팔 굽힘과 좌우 대칭을 함께 사용합니다.
from math import isfinite
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


def _as_metrics(features: MotionFeatures) -> dict[str, float]:
    return {
        "elbow_spread_ratio": features.elbow_spread_ratio,
        "head_lift_ratio": features.head_lift_ratio,
        "wrist_ear_ratio": features.wrist_ear_ratio,
        "elbow_angle_deg": features.elbow_angle_deg,
        "symmetry_ratio": features.symmetry_ratio,
    }


class ShoulderOpenCloseAnalyzer(ExerciseAnalyzer):
    def reset_motion(self, state: SessionState) -> None:
        state.phase = "waiting_closed"
        state.best_open_metrics = None
        state.best_closed_metrics = None
        state.saw_open = False

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
        if (
            state.phase == "waiting_closed"
            and features.elbow_spread_ratio > profile.thresholds.closed_elbow_ratio
        ):
            codes.append("START_WITH_ELBOWS_CLOSED")
        return codes

    @staticmethod
    def _point(points: list[LandmarkPoint], index: L) -> LandmarkPoint:
        return points[int(index)]

    def extract_features(self, pose: PoseResult) -> MotionFeatures | None:
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
        return max(0.0, 100.0 * (1.0 - abs(value - target) / scale))

    def _rep_score(
        self,
        open_metrics: dict[str, float],
        closed_metrics: dict[str, float],
        profile: ReferenceProfile,
    ) -> float:
        tolerance = profile.tolerances
        open_target = profile.open_target
        closed_target = profile.closed_target
        components = (
            (
                0.30,
                self._closeness(
                    open_metrics["elbow_spread_ratio"],
                    open_target.elbow_spread_ratio,
                    tolerance.elbow_spread_ratio,
                ),
            ),
            (
                0.20,
                self._closeness(
                    closed_metrics["elbow_spread_ratio"],
                    closed_target.elbow_spread_ratio,
                    tolerance.elbow_spread_ratio,
                ),
            ),
            (
                0.15,
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
        return round(sum(weight * score for weight, score in components), 1)

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
        value = features.elbow_spread_ratio
        closed_threshold = profile.thresholds.closed_elbow_ratio
        open_threshold = profile.thresholds.open_elbow_ratio
        metrics = _as_metrics(features)

        if not features.hands_near_ears:
            codes.append("KEEP_HANDS_BY_EARS")

        if state.phase == "waiting_closed":
            if value <= closed_threshold:
                state.phase = "closed"
                state.best_closed_metrics = metrics
            else:
                codes.append("START_WITH_ELBOWS_CLOSED")

        elif state.phase == "closed":
            if (
                state.best_closed_metrics is None
                or value < state.best_closed_metrics["elbow_spread_ratio"]
            ):
                state.best_closed_metrics = metrics
            if value > closed_threshold:
                state.phase = "opening"
                state.best_open_metrics = metrics

        elif state.phase == "opening":
            if (
                state.best_open_metrics is None
                or value > state.best_open_metrics["elbow_spread_ratio"]
            ):
                state.best_open_metrics = metrics
            if value >= open_threshold:
                state.phase = "open"
                state.saw_open = True
            elif value <= closed_threshold:
                state.phase = "closed"
                state.best_open_metrics = None

        elif state.phase == "open":
            if (
                state.best_open_metrics is None
                or value > state.best_open_metrics["elbow_spread_ratio"]
            ):
                state.best_open_metrics = metrics
            if value < open_threshold:
                state.phase = "closing"
                if state.best_open_metrics is not None:
                    codes.extend(
                        self._phase_feedback(
                            state.best_open_metrics,
                            profile.open_target,
                            profile,
                            "open",
                        )
                    )

        elif state.phase == "closing":
            if value >= open_threshold:
                state.phase = "open"
            elif value <= closed_threshold:
                state.best_closed_metrics = metrics
                state.phase = "closed"
                if state.saw_open and state.best_open_metrics is not None:
                    codes.extend(
                        self._phase_feedback(
                            state.best_closed_metrics,
                            profile.closed_target,
                            profile,
                            "closed",
                        )
                    )
                    rep_score = self._rep_score(
                        state.best_open_metrics,
                        state.best_closed_metrics,
                        profile,
                    )
                    state.rep_count += 1
                    state.rep_scores.append(rep_score)
                    state.saw_open = False
                    state.best_open_metrics = None
                    if not codes:
                        codes.append("GOOD_REP")
                    return ExerciseEvaluation(
                        phase=state.phase,
                        feedback_codes=list(dict.fromkeys(codes)),
                        rep_completed=True,
                        rep_score=rep_score,
                    )

        return ExerciseEvaluation(
            phase=state.phase,
            feedback_codes=list(dict.fromkeys(codes)),
        )
