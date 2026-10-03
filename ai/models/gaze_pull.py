"""시선당기기의 좌우 팔 특징과 영상에서 추출한 기준값."""

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReachMetrics(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    height: float  # (어깨 y - 손목 y) / 어깨 너비: 위로 갈수록 큼
    cross: float  # 자기 어깨에서 반대 어깨 방향으로 이동한 손목 거리 / 어깨 너비
    elbow_angle: float  # 팔꿈치 각도(도)
    head_turn: float
    head_lift: float  # 귀 중심 대비 코 높이 / 귀 간격. 피드백에만 사용


class GazePullFeatures(BaseModel):
    left: ReachMetrics
    right: ReachMetrics


class ReachTolerances(BaseModel):
    height: float = Field(default=0.25, gt=0)
    cross: float = Field(default=0.30, gt=0)
    elbow_angle: float = Field(default=20.0, gt=0)
    head_turn: float = Field(default=0.30, gt=0)
    head_lift: float = Field(default=0.20, gt=0)


class ReachSideReference(BaseModel):
    high: ReachMetrics
    low: ReachMetrics
    high_threshold: float
    low_threshold: float
    cross_threshold: float
    tolerances: ReachTolerances

    @model_validator(mode="after")
    def check_range(self):
        if not self.low.height < self.low_threshold < self.high_threshold < self.high.height:
            raise ValueError("팔 높이는 low < low_threshold < high_threshold < high여야 합니다.")
        return self


class GazePullReference(BaseModel):
    left: ReachSideReference
    right: ReachSideReference
    hold_ms: int = Field(default=100, ge=0)
    left_reference_reps: int = Field(default=0, ge=0)
    right_reference_reps: int = Field(default=0, ge=0)
