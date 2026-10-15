from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LandmarkPoint:
    x: float
    y: float
    z: float
    visibility: float
    presence: float


@dataclass(frozen=True)
class PoseResult:
    normalized: list[LandmarkPoint]
    world: list[LandmarkPoint]
    image_width: int = 1
    image_height: int = 1


class PoseEstimator(ABC):
    @abstractmethod
    def detect(self, frame_bgr: np.ndarray, timestamp_ms: int) -> PoseResult | None:
        """BGR 프레임에서 한 사람의 관절을 추정합니다."""

    @abstractmethod
    def close(self) -> None:
        """모델이 사용하던 네이티브 자원을 정리합니다."""
