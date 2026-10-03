# 첫 프레임 크기에 맞춰 OpenCV VideoWriter를 열고 오버레이 영상을 저장합니다.
# 소리 없이 고정 FPS로 로컬 저장합니다. 프레임 처리 속도와 다르면 재생 시간이 달라집니다.
import re
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from core.config import VIDEO_CODEC


class VideoRecorder:
    def __init__(self, output_dir: Path, session_id: str, fps: float) -> None:
        safe_session_id = re.sub(r"[^A-Za-z0-9_-]", "_", session_id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.output_path = output_dir / f"{safe_session_id}_{timestamp}.mp4"
        self.fps = fps
        self._writer: cv2.VideoWriter | None = None

    def _open(self, frame: np.ndarray) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        height, width = frame.shape[:2]
        writer = cv2.VideoWriter(
            str(self.output_path),
            cv2.VideoWriter_fourcc(*VIDEO_CODEC),
            self.fps,
            (width, height),
        )
        if not writer.isOpened():
            writer.release()
            raise RuntimeError(
                f"MP4 VideoWriter를 열 수 없습니다. VIDEO_CODEC={VIDEO_CODEC} 설정을 확인하세요."
            )
        self._writer = writer

    def write(self, frame: np.ndarray) -> None:
        if self._writer is None:
            self._open(frame)
        self._writer.write(frame)

    def close(self) -> Path | None:
        if self._writer is not None:
            self._writer.release()
            self._writer = None
        return self.output_path if self.output_path.exists() else None
