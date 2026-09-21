# 합성 특징 시퀀스로 팔꿈치 오므림-펼침-오므림 한 회가 계산되는지 검증합니다.
import pytest

from models.reference_profile import (
    FeatureTolerances,
    MotionFeatures,
    PhaseTarget,
    PhaseThresholds,
    ReferenceProfile,
)
from models.session_state import SessionState
from services.exercises.shoulder_open_close import ShoulderOpenCloseAnalyzer


def feature(elbow: float, head: float) -> MotionFeatures:
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


def profile() -> ReferenceProfile:
    return ReferenceProfile(
        source_video="test.mp4",
        source_sha256="test",
        model_variant="lite",
        source_fps=24.0,
        valid_frame_count=100,
        reference_rep_count=1,
        closed_target=PhaseTarget(
            elbow_spread_ratio=0.55,
            head_lift_ratio=0.85,
            wrist_ear_ratio=0.30,
            elbow_angle_deg=70.0,
            symmetry_ratio=0.04,
        ),
        open_target=PhaseTarget(
            elbow_spread_ratio=1.75,
            head_lift_ratio=1.20,
            wrist_ear_ratio=0.30,
            elbow_angle_deg=70.0,
            symmetry_ratio=0.04,
        ),
        thresholds=PhaseThresholds(
            closed_elbow_ratio=0.90,
            open_elbow_ratio=1.40,
        ),
        tolerances=FeatureTolerances(
            elbow_spread_ratio=0.15,
            head_lift_ratio=0.08,
            wrist_ear_ratio=0.12,
            elbow_angle_deg=10.0,
            symmetry_ratio=0.08,
        ),
    )


def test_one_complete_repetition() -> None:
    analyzer = ShoulderOpenCloseAnalyzer()
    state = SessionState(session_id="test")
    reference = profile()

    for current in (
        feature(0.55, 0.85),
        feature(1.00, 0.95),
        feature(1.75, 1.20),
        feature(1.20, 1.05),
        feature(0.55, 0.85),
    ):
        evaluation = analyzer.update(state, current, reference)

    assert evaluation.rep_completed is True
    assert state.rep_count == 1
    assert state.accuracy == pytest.approx(100.0)


def test_tracking_loss_discards_only_incomplete_shoulder_motion():
    from services.session.session_manager import SessionManager

    manager = SessionManager()
    session = manager.start("shoulder-loss", profile())
    for f in (feature(0.55, 0.85), feature(1, 0.95), feature(1.75, 1.2)):
        session.analyzer.update(session.state, f, session.profile)
    assert session.state.saw_open
    session.state.rep_count = 1
    session.state.rep_scores = [80]
    manager.pose_missing("shoulder-loss", 100)
    session.analyzer.update(session.state, feature(0.55, 0.85), session.profile)
    assert session.state.rep_count == 1
    assert session.state.accuracy == 80
    assert not session.state.saw_open
    assert session.state.best_open_metrics is None
    manager.end("shoulder-loss")
