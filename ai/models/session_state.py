# 한 운동 세션의 단계, 반복 횟수, 점수와 피드백 상태를 저장합니다.
# 분석 함수가 매 프레임 동일한 상태를 이어서 사용할 수 있게 합니다.
from dataclasses import dataclass, field
from time import monotonic


@dataclass
class SessionState:
    session_id: str
    exercise_code: str = "shoulder_open_close"
    phase: str = "waiting_closed"
    rep_count: int = 0
    left_rep_count: int = 0
    right_rep_count: int = 0
    frame_count: int = 0
    started_at: float = field(default_factory=monotonic)
    rep_scores: list[float] = field(default_factory=list)
    best_open_metrics: dict[str, float] | None = None
    best_closed_metrics: dict[str, float] | None = None
    saw_open: bool = False
    last_feedback_code: str = ""
    last_feedback_at_ms: int = -10_000
    last_pose_timestamp_ms: int = -1

    @property
    def duration_sec(self) -> int:
        return max(0, int(monotonic() - self.started_at))

    @property
    def accuracy(self) -> float:
        """완료한 반복의 평균 자세 유사도(0~100). 기존 API 필드명을 유지합니다."""
        if not self.rep_scores:
            return 0.0
        return round(sum(self.rep_scores) / len(self.rep_scores), 1)
