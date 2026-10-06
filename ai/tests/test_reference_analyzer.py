# 합성 기준 시퀀스에서 단계 임계값과 반복 횟수가 생성되는지 검증합니다.
from models.reference_profile import MotionFeatures, ReferenceSample
from services.reference.reference_analyzer import ReferenceAnalyzer


class UnusedEstimator:
    pass


def features(elbow: float, head: float) -> MotionFeatures:
    return MotionFeatures(
        elbow_spread_ratio=elbow,
        head_lift_ratio=head,
        wrist_ear_ratio=0.30,
        elbow_angle_deg=70.0,
        symmetry_ratio=0.04,
        shoulder_level_ratio=0.02,
        confidence=0.95,
        hands_near_ears=True,
    )


def test_profile_from_two_cycles() -> None:
    values = [0.55] * 8 + [1.00] * 4 + [1.75] * 8 + [1.00] * 4 + [0.55] * 8
    values += [1.00] * 4 + [1.75] * 8 + [1.00] * 4 + [0.55] * 8
    samples = [
        ReferenceSample(
            timestamp_ms=index * 100,
            features=features(value, 0.85 + (value - 0.55) * 0.29),
        )
        for index, value in enumerate(values)
    ]

    analyzer = ReferenceAnalyzer(UnusedEstimator())  # type: ignore[arg-type]
    profile = analyzer.build_profile_from_samples(
        samples,
        source_video="test.mp4",
        source_sha256="test",
        source_fps=10.0,
    )

    assert profile.reference_rep_count == 2
    assert profile.closed_target.elbow_spread_ratio < profile.open_target.elbow_spread_ratio
    assert profile.thresholds.closed_elbow_ratio < profile.thresholds.open_elbow_ratio
