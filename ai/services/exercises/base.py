# 운동 분석기가 따라야 할 특징 추출과 상태 갱신 인터페이스를 정의합니다.
# 운동 종류가 늘어나도 세션과 WebSocket 계층을 재사용하기 위한 경계입니다.
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from models.reference_profile import MotionFeatures, ReferenceProfile
from models.session_state import SessionState
from services.pose.base import PoseResult


@dataclass
class ExerciseEvaluation:
    phase: str
    feedback_codes: list[str] = field(default_factory=list)
    rep_completed: bool = False
    rep_score: float | None = None


class ExerciseAnalyzer(ABC):
    @abstractmethod
    def extract_features(self, pose: PoseResult) -> MotionFeatures | None:
        """관절 좌표에서 해당 운동에 필요한 특징을 계산합니다."""

    @abstractmethod
    def update(
        self,
        state: SessionState,
        features: MotionFeatures,
        profile: ReferenceProfile,
    ) -> ExerciseEvaluation:
        """특징을 이용해 단계, 반복 횟수와 피드백 조건을 갱신합니다."""

    @abstractmethod
    def reset_motion(self, state: SessionState) -> None:
        """미완료 동작을 초기화합니다. 이미 완료한 횟수와 점수는 유지합니다."""

    @abstractmethod
    def current_feedback(
        self, features: MotionFeatures | None, profile: ReferenceProfile, state: SessionState
    ) -> list[str]:
        """쿨다운 없이 현재 자세 오류를 반환합니다. 로컬 화면에서 매 프레임 사용합니다."""
