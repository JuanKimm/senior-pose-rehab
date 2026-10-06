# 실시간 세션별 상태와 분석 객체를 생성하고 프레임 처리 및 종료를 담당합니다.
# 반복 판정 로직 자체는 운동 분석기에 두고 이 파일은 생명주기만 관리합니다.
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from core.config import RECORDING_DIR, RECORDING_FPS
from models.reference_profile import MotionFeatures, ReferenceProfile
from models.session_state import SessionState
from services.analysis.smoother import FeatureSmoother
from services.exercises.base import ExerciseAnalyzer, ExerciseEvaluation
from services.exercises.registry import create_analyzer
from services.feedback.feedback_engine import FeedbackEngine
from services.pose.base import PoseResult
from services.recorder.video_recorder import VideoRecorder


@dataclass
class FrameAnalysis:
    features: MotionFeatures | None
    evaluation: ExerciseEvaluation | None
    feedback_code: str
    feedback: str


@dataclass
class ActiveSession:
    state: SessionState
    profile: ReferenceProfile
    analyzer: ExerciseAnalyzer
    smoother: FeatureSmoother
    feedback_engine: FeedbackEngine
    recorder: VideoRecorder


class SessionAlreadyActiveError(ValueError):
    """다른 연결이 사용 중인 세션 ID를 재사용했습니다."""


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, ActiveSession] = {}

    def start(self, session_id: str, profile: ReferenceProfile) -> ActiveSession:
        if session_id in self._sessions:
            raise SessionAlreadyActiveError(f"이미 사용 중인 세션 ID입니다: {session_id}")
        session = ActiveSession(
            state=SessionState(session_id=session_id, exercise_code=profile.exercise_code),
            profile=profile,
            analyzer=create_analyzer(profile.exercise_code),
            smoother=FeatureSmoother(),
            feedback_engine=FeedbackEngine(),
            recorder=VideoRecorder(RECORDING_DIR, session_id, RECORDING_FPS),
        )
        session.analyzer.reset_motion(session.state)
        self._sessions[session_id] = session
        return session

    def get(self, session_id: str) -> ActiveSession:
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise KeyError(f"존재하지 않는 운동 세션입니다: {session_id}") from exc

    def process_pose(
        self,
        session_id: str,
        pose: PoseResult,
        timestamp_ms: int,
    ) -> FrameAnalysis:
        session = self.get(session_id)
        session.state.last_pose_timestamp_ms = timestamp_ms
        features = session.analyzer.extract_features(pose)
        if features is None:
            return self.pose_missing(session_id, timestamp_ms)

        features = session.smoother.update(features)
        evaluation = session.analyzer.update(session.state, features, session.profile)
        code, message = session.feedback_engine.select(
            evaluation.feedback_codes, session.state, timestamp_ms
        )
        return FrameAnalysis(features, evaluation, code, message)

    def pose_missing(self, session_id: str, timestamp_ms: int) -> FrameAnalysis:
        session = self.get(session_id)
        session.state.last_pose_timestamp_ms = timestamp_ms
        session.analyzer.reset_motion(session.state)
        session.smoother = FeatureSmoother()
        code, message = session.feedback_engine.select(
            ["POSE_NOT_DETECTED"], session.state, timestamp_ms
        )
        return FrameAnalysis(None, None, code, message)

    def record(self, session_id: str, frame: np.ndarray) -> None:
        self.get(session_id).recorder.write(frame)

    def end(self, session_id: str) -> tuple[SessionState, Path | None] | None:
        session = self._sessions.pop(session_id, None)
        if session is None:
            return None
        recording_path = session.recorder.close()
        return session.state, recording_path
