# 기준 영상에서 추출한 자세 특징, 단계 기준과 시퀀스를 표현합니다.
# JSON 캐시를 저장하고 다시 검증해서 불러올 때 사용하는 Pydantic 모델입니다.
from pydantic import BaseModel, ConfigDict, Field, model_validator

from models.gaze_pull import GazePullFeatures, GazePullReference


class MotionFeatures(BaseModel):
    """공통 응답 형식. 시선당기기 판정은 gaze_pull, 어깨 판정은 최상위 특징을 사용합니다."""

    gaze_pull: GazePullFeatures | None = None
    elbow_spread_ratio: float
    head_lift_ratio: float
    wrist_ear_ratio: float
    elbow_angle_deg: float
    symmetry_ratio: float
    shoulder_level_ratio: float
    confidence: float = Field(ge=0.0, le=1.0)
    hands_near_ears: bool


class PhaseTarget(BaseModel):
    elbow_spread_ratio: float
    head_lift_ratio: float
    wrist_ear_ratio: float
    elbow_angle_deg: float
    symmetry_ratio: float


class PhaseThresholds(BaseModel):
    closed_elbow_ratio: float
    open_elbow_ratio: float


class FeatureTolerances(BaseModel):
    elbow_spread_ratio: float
    head_lift_ratio: float
    wrist_ear_ratio: float
    elbow_angle_deg: float
    symmetry_ratio: float


class ReferenceSample(BaseModel):
    timestamp_ms: int
    features: MotionFeatures


class ReferenceProfile(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    description: str = Field(
        default="귀를 잡고 팔꿈치와 고개를 함께 펼치고 오므리는 기준 동작입니다.",
        alias="_description",
    )
    version: str = "1.0"
    gaze_pull: GazePullReference | None = None
    start_sec: float | None = None
    end_sec: float | None = None
    exercise_code: str = "shoulder_open_close"
    source_video: str
    source_sha256: str
    model_variant: str
    source_fps: float
    valid_frame_count: int
    reference_rep_count: int
    # 어깨 판정용 필드. 시선당기기에서도 기존 JSON/API 형식 호환을 위해 유지합니다.
    closed_target: PhaseTarget
    open_target: PhaseTarget
    thresholds: PhaseThresholds
    tolerances: FeatureTolerances
    sequence: list[ReferenceSample] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_gaze_reference(self):
        if self.exercise_code == "gaze_pull" and self.gaze_pull is None:
            raise ValueError("시선당기기 기준이 없습니다. 전처리를 다시 실행하세요.")
        return self
