# WebSocket으로 주고받는 실시간 분석 결과와 운동 종료 요약을 정의합니다.
# 프론트엔드가 안정적으로 필드를 해석할 수 있도록 출력 형식을 고정합니다.
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


class ErrorResponse(BaseModel):
    type: Literal["error"] = "error"
    code: str
    message: str
