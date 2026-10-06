"""대각선 위로 뻗기→자기 쪽 아래로 내리기, 좌우 교대 운동.

한 팔의 위→아래 완료를 1회로 셉니다. 얼굴 지표는 눈의 실제 시선이 아닙니다.
"""

from math import isfinite
from statistics import mean

from core.config import MIN_LANDMARK_VISIBILITY
from core.landmarks import PoseLandmark as L
from models.gaze_pull import GazePullFeatures, ReachMetrics, ReachSideReference
from models.reference_profile import MotionFeatures, ReferenceProfile
from models.session_state import SessionState
from services.analysis.angle_calculator import angle_degrees, distance_2d
from services.exercises.base import ExerciseAnalyzer, ExerciseEvaluation
from services.pose.base import PoseResult

# 전체 점수 비중입니다. 합계 1.0을 유지하며, 위/아래 자세에는 각각 절반씩 적용합니다.
SCORE_WEIGHTS = {"height": 0.50, "cross": 0.40, "elbow_angle": 0.05, "head_turn": 0.05}
MIN_REACH_ELBOW_ANGLE = 100.0


class GazePullAnalyzer(ExerciseAnalyzer):
    def __init__(self) -> None:
        self.active_side = None
        self.expected_side = None
        self.best_high = None
        self._candidate = ""
        self._candidate_since = 0

    def reset_motion(self, state: SessionState) -> None:
        self.active_side = None
        self.best_high = None
        self._candidate = ""
        state.phase = "waiting_high"

    def extract_features(self, pose: PoseResult) -> MotionFeatures | None:
        if len(pose.normalized) < 33:
            return None
        p = pose.normalized
        required = [
            L.NOSE,
            L.LEFT_EAR,
            L.RIGHT_EAR,
            L.LEFT_SHOULDER,
            L.RIGHT_SHOULDER,
            L.LEFT_ELBOW,
            L.RIGHT_ELBOW,
            L.LEFT_WRIST,
            L.RIGHT_WRIST,
        ]
        if any(p[i].visibility < MIN_LANDMARK_VISIBILITY for i in required):
            return None
        if any(
            not all(isfinite(v) for v in (p[i].x, p[i].y, p[i].z, p[i].visibility))
            for i in required
        ):
            return None
        if any(not (0 <= p[i].x <= 1 and 0 <= p[i].y <= 1) for i in required):
            return None

        def xy(i: int) -> tuple[float, float, float]:
            # x/y를 같은 픽셀 단위로 맞춰 영상 종횡비의 영향을 보정합니다.
            return (p[i].x * pose.image_width, p[i].y * pose.image_height, 0.0)

        ls, rs = xy(L.LEFT_SHOULDER), xy(L.RIGHT_SHOULDER)
        le, re = xy(L.LEFT_ELBOW), xy(L.RIGHT_ELBOW)
        lw, rw = xy(L.LEFT_WRIST), xy(L.RIGHT_WRIST)
        nose, el, er = xy(L.NOSE), xy(L.LEFT_EAR), xy(L.RIGHT_EAR)
        width, ear_width = distance_2d(ls, rs), distance_2d(el, er)
        if min(width, ear_width) < 1e-5:
            return None
        left_direction = 1.0 if rs[0] > ls[0] else -1.0
        turn = (nose[0] - (el[0] + er[0]) / 2) / ear_width
        lift = ((el[1] + er[1]) / 2 - nose[1]) / ear_width
        coords = pose.world if len(pose.world) >= 33 else [xy(i) for i in range(33)]
        try:
            la = angle_degrees(coords[L.LEFT_SHOULDER], coords[L.LEFT_ELBOW], coords[L.LEFT_WRIST])
            ra = angle_degrees(
                coords[L.RIGHT_SHOULDER], coords[L.RIGHT_ELBOW], coords[L.RIGHT_WRIST]
            )
        except ValueError:
            return None
        if not all(isfinite(a) for a in (la, ra)):
            return None

        def arm(shoulder, wrist, direction, elbow):
            return ReachMetrics(
                height=(shoulder[1] - wrist[1]) / width,
                cross=direction * (wrist[0] - shoulder[0]) / width,
                elbow_angle=elbow,
                head_turn=direction * turn,
                head_lift=lift,
            )

        return MotionFeatures(
            gaze_pull=GazePullFeatures(
                left=arm(ls, lw, left_direction, la), right=arm(rs, rw, -left_direction, ra)
            ),
            # 기존 API의 공통 필드. 이 운동의 판정에는 gaze_pull의 좌우 특징만 사용합니다.
            elbow_spread_ratio=distance_2d(le, re) / width,
            head_lift_ratio=((ls[1] + rs[1]) / 2 - nose[1]) / width,
            wrist_ear_ratio=mean((distance_2d(lw, el), distance_2d(rw, er))) / width,
            elbow_angle_deg=mean((la, ra)),
            symmetry_ratio=abs(lw[1] - rw[1]) / width,
            shoulder_level_ratio=abs(ls[1] - rs[1]) / width,
            confidence=min(p[i].visibility for i in required),
            hands_near_ears=False,
        )

    @staticmethod
    def is_reference_pose(features):
        return features.gaze_pull is not None

    def _stable(self, key, now, hold_ms):
        if key != self._candidate:
            self._candidate, self._candidate_since = key, now
            return hold_ms == 0
        return now - self._candidate_since >= hold_ms

    @staticmethod
    def _endpoint_feedback(metrics, reference, high):
        target = reference.high if high else reference.low
        tol = reference.tolerances
        codes = []
        if high:
            if metrics.height < target.height - tol.height:
                codes.append("GAZE_REACH_HIGHER")
            if metrics.cross < target.cross - tol.cross:
                codes.append("GAZE_REACH_DIAGONALLY")
            if metrics.elbow_angle < target.elbow_angle - tol.elbow_angle:
                codes.append("GAZE_EXTEND_ELBOW")
        else:
            if metrics.height > target.height + tol.height:
                codes.append("GAZE_LOWER_HAND")
            if metrics.cross > target.cross + tol.cross:
                codes.append("GAZE_LOWER_TO_OWN_SIDE")
        if abs(metrics.head_turn - target.head_turn) > tol.head_turn:
            codes.append("GAZE_FOLLOW_HAND")
        if abs(metrics.head_lift - target.head_lift) > tol.head_lift:
            codes.append("GAZE_CHECK_HEAD_HEIGHT")
        return codes

    def current_feedback(
        self, features: MotionFeatures | None, profile: ReferenceProfile, state: SessionState
    ) -> list[str]:
        """끝 자세 근처에서 현재 값만 비교합니다. 이동 중에는 완성 자세를 요구하지 않습니다."""
        if features is None or features.gaze_pull is None:
            return ["POSE_NOT_DETECTED"]
        data, refs = features.gaze_pull, profile.gaze_pull
        high_sides = [
            s
            for s in ("left", "right")
            if getattr(data, s).height >= getattr(refs, s).high_threshold
        ]
        if len(high_sides) == 2:
            return ["GAZE_ONE_ARM"]
        if self.active_side:
            side = self.active_side
        elif high_sides:
            side = high_sides[0]
            if self.expected_side and side != self.expected_side:
                return ["GAZE_SWITCH_SIDE"]
        elif state.phase in ("left_low", "right_low"):
            side = state.phase.split("_")[0]
        else:
            return []
        metrics, ref = getattr(data, side), getattr(refs, side)
        if metrics.height >= ref.high_threshold:
            return self._endpoint_feedback(metrics, ref, True)
        if metrics.height <= ref.low_threshold:
            return self._endpoint_feedback(metrics, ref, False)
        return []

    @staticmethod
    def _score(high: ReachMetrics, low: ReachMetrics, reference: ReachSideReference) -> float:
        """최고 손 높이 표본과 아래 완료 표본을 50:50으로 비교합니다."""
        total = 0.0
        for current, target in ((high, reference.high), (low, reference.low)):
            for key, weight in SCORE_WEIGHTS.items():
                diff = abs(getattr(current, key) - getattr(target, key))
                total += (
                    0.5
                    * weight
                    * max(0, 100 * (1 - diff / (3.5 * getattr(reference.tolerances, key))))
                )
        return round(total, 1)

    def update(
        self, state: SessionState, features: MotionFeatures, profile: ReferenceProfile
    ) -> ExerciseEvaluation:
        if features.gaze_pull is None or profile.gaze_pull is None:
            self.reset_motion(state)
            return ExerciseEvaluation(state.phase, ["POSE_NOT_DETECTED"])
        data, refs = features.gaze_pull, profile.gaze_pull
        now = max(0, state.last_pose_timestamp_ms)
        high_sides = [
            s
            for s in ("left", "right")
            if getattr(data, s).height >= getattr(refs, s).high_threshold
        ]
        if len(high_sides) > 1:
            self.reset_motion(state)
            return ExerciseEvaluation(state.phase, ["GAZE_ONE_ARM"])
        if self.active_side is None:
            if high_sides:
                side = high_sides[0]
                metrics, ref = getattr(data, side), getattr(refs, side)
                if self.expected_side and side != self.expected_side:
                    self._candidate = ""
                    return ExerciseEvaluation(state.phase, ["GAZE_SWITCH_SIDE"])
                state.phase = f"{side}_raising"
                if metrics.cross < ref.cross_threshold:
                    self._candidate = ""
                    return ExerciseEvaluation(state.phase, ["GAZE_REACH_DIAGONALLY"])
                if metrics.elbow_angle < MIN_REACH_ELBOW_ANGLE:
                    self._candidate = ""
                    return ExerciseEvaluation(state.phase, ["GAZE_EXTEND_ELBOW"])
                if self._stable(f"{side}_high", now, refs.hold_ms):
                    self.active_side, self.best_high = side, metrics
                    state.phase, self._candidate = f"{side}_high", ""
            else:
                self._candidate = ""
                if state.phase in ("left_low", "right_low"):
                    prev = state.phase.split("_")[0]
                    if getattr(data, prev).height > getattr(refs, prev).low_threshold:
                        state.phase = "waiting_high"
                else:
                    state.phase = "waiting_high"
        else:
            side = self.active_side
            metrics, ref = getattr(data, side), getattr(refs, side)
            if metrics.height > self.best_high.height:
                self.best_high = metrics
            state.phase = (
                f"{side}_high" if metrics.height >= ref.high_threshold else f"{side}_lowering"
            )
            if metrics.height <= ref.low_threshold:
                if metrics.cross > ref.low.cross + ref.tolerances.cross:
                    self._candidate = ""
                    return ExerciseEvaluation(state.phase, ["GAZE_LOWER_TO_OWN_SIDE"])
                if self._stable(f"{side}_low", now, refs.hold_ms):
                    score = self._score(self.best_high, metrics, ref)
                    codes = self._endpoint_feedback(metrics, ref, False)
                    state.rep_count += 1
                    if side == "left":
                        state.left_rep_count += 1
                    else:
                        state.right_rep_count += 1
                    state.rep_scores.append(score)
                    self.expected_side = "right" if side == "left" else "left"
                    self.active_side, self.best_high, self._candidate = None, None, ""
                    state.phase = f"{side}_low"
                    return ExerciseEvaluation(state.phase, codes or ["GOOD_REP"], True, score)
            else:
                self._candidate = ""
        return ExerciseEvaluation(state.phase, self.current_feedback(features, profile, state))
