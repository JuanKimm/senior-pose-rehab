from types import SimpleNamespace

import numpy as np
import pytest
from PIL import ImageFont

from core.exercise_catalog import get_exercise
from models.session_state import SessionState
from scripts.run_local_demo import _current_feedback, _draw_local_feedback
from services.exercises.gaze_pull import GazePullAnalyzer
from services.reference.reference_repository import ReferenceRepository
from services.session.session_manager import SessionManager


@pytest.fixture
def profile():
    return ReferenceRepository(get_exercise("gaze_pull").profile_path).load()


def sample(profile, side=None, high=False):
    result = profile.sequence[0].features.model_copy(deep=True)
    for s in ("left", "right"):
        ref = getattr(profile.gaze_pull, s)
        setattr(result.gaze_pull, s, (ref.high if s == side and high else ref.low).model_copy())
    return result


def hold(analyzer, state, profile, features, start):
    for t in (start, start + 110):
        state.last_pose_timestamp_ms = t
        analyzer.update(state, features, profile)


@pytest.mark.parametrize("first", ["left", "right"])
def test_alternating_repetitions_and_wrong_side(profile, first):
    a = GazePullAnalyzer()
    s = SessionState("test")
    second = "right" if first == "left" else "left"
    hold(a, s, profile, sample(profile, first, True), 0)
    hold(a, s, profile, sample(profile), 200)
    assert s.rep_count == 1
    hold(a, s, profile, sample(profile, first, True), 400)
    assert a.current_feedback(sample(profile, first, True), profile, s) == ["GAZE_SWITCH_SIDE"]
    hold(a, s, profile, sample(profile), 600)
    assert s.rep_count == 1
    hold(a, s, profile, sample(profile, second, True), 800)
    hold(a, s, profile, sample(profile), 1000)
    assert (s.rep_count, s.left_rep_count, s.right_rep_count) == (2, 1, 1)


def test_no_count_for_partial_wrong_direction_or_both_arms(profile):
    for mode in ("partial", "direction", "both"):
        a = GazePullAnalyzer()
        s = SessionState("test")
        f = sample(profile, "left", True)
        if mode == "partial":
            f.gaze_pull.left.height = profile.gaze_pull.left.high_threshold - 0.01
        elif mode == "direction":
            f.gaze_pull.left.cross = profile.gaze_pull.left.cross_threshold - 0.2
        else:
            f.gaze_pull.right = profile.gaze_pull.right.high.model_copy()
        hold(a, s, profile, f, 0)
        hold(a, s, profile, sample(profile), 200)
        assert s.rep_count == 0


def test_pose_loss_cannot_bridge_a_repetition(profile):
    manager = SessionManager()
    session = manager.start("test", profile)
    hold(session.analyzer, session.state, profile, sample(profile, "left", True), 0)
    manager.pose_missing("test", 150)
    hold(session.analyzer, session.state, profile, sample(profile), 200)
    assert session.state.rep_count == 0
    manager.end("test")


def test_hold_requires_elapsed_time(profile):
    a = GazePullAnalyzer()
    s = SessionState("test")
    f = sample(profile, "left", True)
    for t in range(100):
        s.last_pose_timestamp_ms = t
        a.update(s, f, profile)
    assert a.active_side is None
    s.last_pose_timestamp_ms = 100
    a.update(s, f, profile)
    assert a.active_side == "left"


def test_local_feedback_persists_then_clears_independent_of_log_cooldown(profile):
    a = GazePullAnalyzer()
    s = SessionState("test")
    session = SimpleNamespace(analyzer=a, state=s, profile=profile)
    f = sample(profile, "left", True)
    f.gaze_pull.left.elbow_angle = (
        profile.gaze_pull.left.high.elbow_angle - profile.gaze_pull.left.tolerances.elbow_angle - 1
    )
    for t in (0, 100, 5000):
        s.last_feedback_at_ms = t
        assert _current_feedback(session, f)[0] == "GAZE_EXTEND_ELBOW"
    assert _current_feedback(session, sample(profile, "left", True)) == ("", "")


def test_overlay_only_changes_returned_copy():
    frame = np.zeros((360, 640, 3), dtype=np.uint8)
    output = _draw_local_feedback(frame, "feedback", ImageFont.load_default(size=28))
    assert not frame.any()
    assert output.any()
    assert _draw_local_feedback(frame, "", None) is frame


def test_removed_exercise_is_rejected():
    with pytest.raises(ValueError):
        get_exercise("chest_open_close")


@pytest.mark.parametrize(
    "key,maximum_loss", [("height", 50), ("cross", 40), ("elbow_angle", 5), ("head_turn", 5)]
)
def test_score_uses_requested_total_weights(profile, key, maximum_loss):
    ref = profile.gaze_pull.left
    high, low = ref.high.model_copy(), ref.low.model_copy()
    assert GazePullAnalyzer._score(high, low, ref) == 100
    # 두 끝 자세에서 해당 항목만 0점으로 만들면 전체 비중만큼 감소해야 합니다.
    for metrics in (high, low):
        setattr(metrics, key, getattr(metrics, key) + 4 * getattr(ref.tolerances, key))
    assert GazePullAnalyzer._score(high, low, ref) == pytest.approx(100 - maximum_loss)


def test_head_height_only_affects_feedback(profile):
    ref = profile.gaze_pull.left
    high = ref.high.model_copy()
    high.head_lift += 10
    assert GazePullAnalyzer._score(high, ref.low, ref) == 100
    assert "GAZE_CHECK_HEAD_HEIGHT" in GazePullAnalyzer._endpoint_feedback(high, ref, True)


def test_duplicate_session_does_not_replace_existing_state(profile):
    from services.session.session_manager import SessionAlreadyActiveError

    manager = SessionManager()
    original = manager.start("same", profile)
    original.state.rep_count = 3
    with pytest.raises(SessionAlreadyActiveError):
        manager.start("same", profile)
    assert manager.get("same") is original
    assert original.state.rep_count == 3
    manager.end("same")
