"""실제 영상 표본에서 좌우 팔의 끝 자세와 여유 범위를 산출합니다."""

from statistics import mean, pstdev

from models.gaze_pull import GazePullReference, ReachMetrics, ReachSideReference, ReachTolerances
from models.reference_profile import (
    FeatureTolerances,
    PhaseTarget,
    PhaseThresholds,
    ReferenceProfile,
    ReferenceSample,
)
from models.session_state import SessionState
from services.exercises.gaze_pull import GazePullAnalyzer

# 허용 오차의 하한. 높이/가로 위치는 어깨 너비, 얼굴 지표는 귀 간격 기준입니다.
# 최종 허용 오차는 이 하한과 각 끝 자세 표본의 2×표준편차 중 최댓값입니다.
MIN_TOLERANCES = dict(height=0.25, cross=0.30, elbow_angle=20.0, head_turn=0.30, head_lift=0.20)
LOW_FRACTION = 0.25
HIGH_FRACTION = 0.75
HOLD_MS = 100


def build_gaze_profile(
    samples: list[ReferenceSample],
    source_video: str,
    source_sha256: str,
    source_fps: float,
    model_variant: str,
) -> ReferenceProfile:
    samples = [s for s in samples if s.features.gaze_pull is not None]
    if len(samples) < 30:
        raise ValueError(
            "시선당기기 기준 표본이 부족합니다. 얼굴과 양팔이 모두 보이는 영상을 사용하세요."
        )
    sides = {}
    for side in ("left", "right"):
        ordered = sorted(
            (getattr(s.features.gaze_pull, side) for s in samples), key=lambda m: m.height
        )
        n = max(5, int(len(ordered) * 0.12))
        low_samples, high_samples = ordered[:n], ordered[-n:]

        def average(rows: list[ReachMetrics]) -> ReachMetrics:
            return ReachMetrics(**{k: mean(getattr(m, k) for m in rows) for k in MIN_TOLERANCES})

        low, high = average(low_samples), average(high_samples)
        span = high.height - low.height
        if span < 0.6:
            raise ValueError(f"{side}: 위로 뻗고 아래로 내리는 범위가 충분하지 않습니다.")
        tol = ReachTolerances(
            **{
                k: max(
                    floor,
                    2 * pstdev(getattr(m, k) for m in low_samples),
                    2 * pstdev(getattr(m, k) for m in high_samples),
                )
                for k, floor in MIN_TOLERANCES.items()
            }
        )
        sides[side] = ReachSideReference(
            high=high,
            low=low,
            high_threshold=low.height + HIGH_FRACTION * span,
            low_threshold=low.height + LOW_FRACTION * span,
            cross_threshold=high.cross - max(0.4, tol.cross * 1.5),
            tolerances=tol,
        )
    # 공통 API 호환용 필드도 영상에서 계산합니다. 실제 판정은 gaze_pull 필드만 사용합니다.
    common = {k: mean(getattr(s.features, k) for s in samples) for k in PhaseTarget.model_fields}
    profile = ReferenceProfile(
        exercise_code="gaze_pull",
        version="2.0",
        description="시선당기기: 한쪽 팔을 반대 대각선 위로 뻗고 자기 쪽 아래로 내린 뒤 좌우 교대. 얼굴 지표는 실제 시선이 아닌 고개 움직임의 보조 지표.",
        source_video=source_video,
        source_sha256=source_sha256,
        model_variant=model_variant,
        source_fps=source_fps,
        valid_frame_count=len(samples),
        reference_rep_count=0,
        closed_target=PhaseTarget(**common),
        open_target=PhaseTarget(**common),
        thresholds=PhaseThresholds(
            closed_elbow_ratio=common["elbow_spread_ratio"],
            open_elbow_ratio=common["elbow_spread_ratio"],
        ),
        tolerances=FeatureTolerances(
            **{k: max(0.1, 2 * pstdev(getattr(s.features, k) for s in samples)) for k in common}
        ),
        gaze_pull=GazePullReference(**sides, hold_ms=HOLD_MS),
        sequence=samples,
    )
    analyzer = GazePullAnalyzer()
    state = SessionState("reference", exercise_code="gaze_pull", phase="waiting_high")
    for sample in samples:
        state.last_pose_timestamp_ms = sample.timestamp_ms
        analyzer.update(state, sample.features, profile)
    if not state.left_rep_count or not state.right_rep_count:
        raise ValueError("기준 구간에서 좌우 양쪽의 완전한 반복을 확인하지 못했습니다.")
    profile.reference_rep_count = state.rep_count
    profile.gaze_pull.left_reference_reps = state.left_rep_count
    profile.gaze_pull.right_reference_reps = state.right_rep_count
    return profile
