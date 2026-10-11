import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

import imageio_ffmpeg
import numpy as np


class VideoRecorder:
    def __init__(self, output_dir: Path, session_id: str, fps: float) -> None:
        safe_session_id = re.sub(r"[^A-Za-z0-9_-]", "_", session_id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.output_path = output_dir / f"{safe_session_id}_{timestamp}.mp4"
        self._partial_path = self.output_path.with_suffix(".partial.mp4")
        self.fps = fps
        self._writer: subprocess.Popen | None = None
        self._log = None
        self._size = None
        self._closed = False

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
        if self._writer is None:
            self._open(frame)
        if frame.shape[:2] != self._size:
            raise ValueError("녹화 중 프레임 크기를 변경할 수 없습니다.")
        self._writer.stdin.write(frame.tobytes())

    def close(self) -> Path | None:
        if self._closed:
            return self.output_path if self.output_path.exists() else None
        self._closed = True
        if self._writer is None:
            return None
        writer = self._writer
        self._writer = None
        try:
            try:
                writer.stdin.close()
            except BrokenPipeError:
                pass
            result = writer.wait()
            self._log.seek(0)
            error = self._log.read().decode("utf-8", errors="replace")
            if result != 0 or not self._partial_path.exists():
                raise RuntimeError(f"H.264 영상 저장에 실패했습니다: {error}")
            # 인코딩과 MP4 마무리가 끝난 파일만 경로 전달 대상으로 공개합니다.
            self._partial_path.replace(self.output_path)
        finally:
            self._log.close()
            self._log = None
            self._partial_path.unlink(missing_ok=True)
        return self.output_path
