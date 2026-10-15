"""운동별 파일과 기준 영상 구간. 기존 어깨 운동이 기본값입니다."""

from dataclasses import dataclass
from pathlib import Path

from core.config import (
    REFERENCE_CACHE_DIR,
    REFERENCE_END_SEC,
    REFERENCE_START_SEC,
    REFERENCE_VIDEO_DIR,
)


@dataclass(frozen=True)
class ExerciseSpec:
    code: str
    name: str
    start_sec: float
    end_sec: float

    @property
    def video_path(self) -> Path:
        return REFERENCE_VIDEO_DIR / f"{self.code}.mp4"

    @property
    def profile_path(self) -> Path:
        return REFERENCE_CACHE_DIR / f"{self.code}.json"


EXERCISES = {
    "shoulder_open_close": ExerciseSpec(
        "shoulder_open_close", "어깨 운동", REFERENCE_START_SEC, REFERENCE_END_SEC
    ),
    # 약 20초 이후 구도가 바뀌므로 앞쪽의 일정한 구도만 기준으로 사용합니다.
    "gaze_pull": ExerciseSpec("gaze_pull", "시선당기기", 0.0, 19.0),
}


def get_exercise(code: str) -> ExerciseSpec:
    try:
        return EXERCISES[code]
    except KeyError as exc:
        raise ValueError(f"지원하지 않는 운동입니다: {code}") from exc
