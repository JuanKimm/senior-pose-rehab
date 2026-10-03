"""선택한 운동이 WebSocket ready/summary, 분석기, 녹화까지 전달되는지 검증합니다."""

import cv2
import numpy as np
from fastapi.testclient import TestClient

from core.exercise_catalog import get_exercise
from main import app
from routers import exercise_ws
from services.exercises.gaze_pull import GazePullAnalyzer
from services.exercises.shoulder_open_close import ShoulderOpenCloseAnalyzer
from services.reference.reference_repository import ReferenceRepository
from services.session import session_manager


class NoPoseEstimator:
    def __init__(self, *args):
        pass

    def detect(self, frame, timestamp_ms):
        return None

    def close(self):
        pass


def test_gaze_websocket_frame_stop_and_recording(monkeypatch, tmp_path):
    monkeypatch.setattr(exercise_ws, "BlazePoseEstimator", NoPoseEstimator)
    monkeypatch.setattr(session_manager, "RECORDING_DIR", tmp_path)
    with TestClient(app).websocket_connect("/ws/exercise/gaze-test?exercise_code=gaze_pull") as ws:
        assert ws.receive_json()["exercise_code"] == "gaze_pull"
        assert isinstance(exercise_ws.session_manager.get("gaze-test").analyzer, GazePullAnalyzer)
        ok, jpg = cv2.imencode(".jpg", np.zeros((240, 320, 3), dtype=np.uint8))
        assert ok
        ws.send_bytes(jpg.tobytes())
        result = ws.receive_json()
        assert result["type"] == "analysis"
        assert result["feedback_code"] == "POSE_NOT_DETECTED"
        assert (
            cv2.imdecode(np.frombuffer(ws.receive_bytes(), dtype=np.uint8), cv2.IMREAD_COLOR)
            is not None
        )
        ws.send_json({"type": "stop"})
        summary = ws.receive_json()
        assert summary["exercise_code"] == "gaze_pull"
        assert summary["recording_path"]
    assert len(list(tmp_path.glob("*.mp4"))) == 1
    assert "gaze-test" not in exercise_ws.session_manager._sessions


def test_default_websocket_keeps_shoulder(monkeypatch, tmp_path):
    monkeypatch.setattr(exercise_ws, "BlazePoseEstimator", NoPoseEstimator)
    monkeypatch.setattr(session_manager, "RECORDING_DIR", tmp_path)
    with TestClient(app).websocket_connect("/ws/exercise/shoulder-test") as ws:
        assert ws.receive_json()["exercise_code"] == "shoulder_open_close"
        assert isinstance(
            exercise_ws.session_manager.get("shoulder-test").analyzer, ShoulderOpenCloseAnalyzer
        )
        ws.send_json({"type": "stop"})
        assert ws.receive_json()["exercise_code"] == "shoulder_open_close"


def test_unknown_exercise_returns_error():
    with TestClient(app).websocket_connect("/ws/exercise/bad?exercise_code=unknown") as ws:
        assert ws.receive_json()["code"] == "UNSUPPORTED_EXERCISE"


def test_old_shoulder_cache_still_loads():
    profile = ReferenceRepository(get_exercise("shoulder_open_close").profile_path).load()
    assert profile.exercise_code == "shoulder_open_close"
    assert profile.gaze_pull is None


def test_duplicate_websocket_leaves_original_session_alive(monkeypatch, tmp_path):
    monkeypatch.setattr(exercise_ws, "BlazePoseEstimator", NoPoseEstimator)
    monkeypatch.setattr(session_manager, "RECORDING_DIR", tmp_path)
    with TestClient(app) as client:
        with client.websocket_connect("/ws/exercise/shared") as first:
            assert first.receive_json()["type"] == "ready"
            with client.websocket_connect("/ws/exercise/shared") as second:
                assert second.receive_json()["code"] == "SESSION_ALREADY_ACTIVE"
            first.send_json({"type": "ping"})
            assert first.receive_json()["type"] == "pong"
            first.send_json({"type": "stop"})
            assert first.receive_json()["type"] == "summary"
