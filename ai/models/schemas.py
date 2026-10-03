# WebSocket 응답 형식
from typing import Literal

from pydantic import BaseModel, Field

from models.reference_profile import MotionFeatures


class AnalysisResponse(BaseModel):
    type: Literal["analysis"] = "analysis"
    session_id: str
    frame_id: int
    timestamp_ms: int
    pose_detected: bool
    phase: str
    left_rep_count: int = 0
    right_rep_count: int = 0
    rep_count: int
    accuracy: float = Field(
        ge=0.0,
        le=100.0,
        description="완료한 반복의 평균 기준 자세 유사도. 모델 인식 정확도가 아닙니다.",
    )
    feedback_code: str
    feedback: str
    features: MotionFeatures | None = None


class SessionSummaryResponse(BaseModel):
    type: Literal["summary"] = "summary"
    session_id: str
    exercise_code: str
    left_rep_count: int = 0
    right_rep_count: int = 0
    rep_count: int
    duration_sec: int
    accuracy: float = Field(
        ge=0.0,
        le=100.0,
        description="완료한 반복의 평균 기준 자세 유사도. 모델 인식 정확도가 아닙니다.",
    )
    rep_scores: list[float]
    recording_path: str | None
    # 결과 전송 상태
    backend_sent: bool = False
    backend_error: str | None = None
    # 운동 종료 사유
    end_reason: Literal["target_reached", "manual_stop", "disconnected"] = "manual_stop"


class ErrorResponse(BaseModel):
    type: Literal["error"] = "error"
    code: str
    message: str
