import math
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from time import monotonic

import imageio_ffmpeg
import numpy as np


class VideoRecorder:
    def __init__(self, output_dir: Path, session_id: str, fps: float) -> None:
        safe_session_id = re.sub(r"[^A-Za-z0-9_-]", "_", session_id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.output_path = output_dir / f"{safe_session_id}_{timestamp}.mp4"
        self._partial_path = self.output_path.with_suffix(".partial.mp4")
        if not math.isfinite(fps) or fps <= 0:
            raise ValueError("녹화 FPS는 0보다 큰 유한한 값이어야 합니다.")
        self.fps = fps
        self._writer: subprocess.Popen | None = None
        self._log = None
        self._size = None
        self._closed = False
        self._started_at: float | None = None
        self._last_frame: bytes | None = None
        self._frames_written = 0

    def _open(self, frame: np.ndarray) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        height, width = frame.shape[:2]
        command = [
            imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
            "-f", "rawvideo", "-pix_fmt", "bgr24",
            "-s", f"{width}x{height}", "-r", str(self.fps), "-i", "pipe:0",
            "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(self._partial_path),
        ]
        self._log = tempfile.TemporaryFile()
        try:
            self._writer = subprocess.Popen(
                command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                stderr=self._log,
            )
        except Exception:
            self._log.close()
            self._log = None
            raise
        self._size = (height, width)

    def write(self, frame: np.ndarray) -> None:
        if self._closed:
            raise RuntimeError("종료된 녹화에는 프레임을 추가할 수 없습니다.")
        if frame.dtype != np.uint8 or frame.ndim != 3 or frame.shape[2] != 3:
            raise ValueError("녹화 프레임은 uint8 BGR 이미지여야 합니다.")
        captured_at = monotonic()
        if self._writer is None:
            self._open(frame)
            self._started_at = captured_at
        if frame.shape[:2] != self._size:
            raise ValueError("녹화 중 프레임 크기를 변경할 수 없습니다.")

        self._fill_until(captured_at)
        self._last_frame = frame.tobytes()
        if self._frames_written == 0:
            self._writer.stdin.write(self._last_frame)
            self._frames_written = 1

    def _fill_until(self, timestamp: float) -> None:
        if self._last_frame is None:
            return
        elapsed = max(0.0, timestamp - self._started_at)

        target_count = max(1, math.ceil(elapsed * self.fps - 1e-9))
        while self._frames_written < target_count:
            self._writer.stdin.write(self._last_frame)
            self._frames_written += 1

    def close(self) -> Path | None:
        if self._closed:
            return self.output_path if self.output_path.exists() else None
        self._closed = True
        if self._writer is None:
            return None
        writer = self._writer
        try:
            try:
                try:
 
                    self._fill_until(monotonic())
                finally:
                    writer.stdin.close()
            except BrokenPipeError:
                pass
            result = writer.wait()
            self._log.seek(0)
            error = self._log.read().decode("utf-8", errors="replace")
            if result != 0 or not self._partial_path.exists():
                raise RuntimeError(f"H.264 영상 저장에 실패했습니다: {error}")

            self._partial_path.replace(self.output_path)
        finally:
            self._writer = None
            self._last_frame = None
            self._log.close()
            self._log = None
            self._partial_path.unlink(missing_ok=True)
        return self.output_path
