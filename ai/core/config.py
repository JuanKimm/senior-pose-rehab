# AI 서버에서 사용하는 모든 파일 경로와 실행 설정을 한곳에서 관리합니다.
# 코드 내부에 절대경로를 흩어 쓰지 않도록 다른 모듈은 이 값을 가져다 씁니다.
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
STORAGE_DIR = BASE_DIR / "storage"
REFERENCE_VIDEO_DIR = STORAGE_DIR / "reference_videos"
REFERENCE_CACHE_DIR = STORAGE_DIR / "reference_cache"
RECORDING_DIR = STORAGE_DIR / "recordings"
WEIGHTS_DIR = BASE_DIR / "weights"

POSE_MODEL_VARIANT = os.getenv("POSE_MODEL_VARIANT", "lite").strip().lower()
POSE_MODEL_FILENAME = f"pose_landmarker_{POSE_MODEL_VARIANT}.task"
POSE_MODEL_PATH = WEIGHTS_DIR / POSE_MODEL_FILENAME
POSE_MODEL_URLS = {
    "lite": (
        "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
        "pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
    ),
    "full": (
        "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
        "pose_landmarker_full/float16/latest/pose_landmarker_full.task"
    ),
    "heavy": (
        "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
        "pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task"
    ),
}
if POSE_MODEL_VARIANT not in POSE_MODEL_URLS:
    raise ValueError("POSE_MODEL_VARIANT는 lite, full, heavy 중 하나여야 합니다.")
POSE_MODEL_URL = POSE_MODEL_URLS[POSE_MODEL_VARIANT]

FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]


def _get_env_bool(name: str, default: bool = False) -> bool:
    """환경변수의 일반적인 참/거짓 문자열을 bool로 변환합니다."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# 백엔드 연동은 기본적으로 비활성화합니다.
# 활성화할 때는 실행 환경에서 BACKEND_ENABLED와 BACKEND_BASE_URL을 설정합니다.
BACKEND_ENABLED = _get_env_bool("BACKEND_ENABLED", False)
BACKEND_BASE_URL = os.getenv(
    "BACKEND_BASE_URL",
    "http://localhost:8080",
).strip()

RECORDING_FPS = float(os.getenv("RECORDING_FPS", "24"))
VIDEO_CODEC = os.getenv("VIDEO_CODEC", "mp4v")
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
JPEG_QUALITY = int(os.getenv("JPEG_QUALITY", "85"))
MIN_LANDMARK_VISIBILITY = float(os.getenv("MIN_LANDMARK_VISIBILITY", "0.45"))
FEEDBACK_COOLDOWN_MS = int(os.getenv("FEEDBACK_COOLDOWN_MS", "1400"))
REFERENCE_SEQUENCE_FPS = float(os.getenv("REFERENCE_SEQUENCE_FPS", "6"))
REFERENCE_START_SEC = float(os.getenv("REFERENCE_START_SEC", "10.0"))
REFERENCE_END_SEC = float(os.getenv("REFERENCE_END_SEC", "0.0"))


def ensure_directories() -> None:
    """실행에 필요한 로컬 폴더를 생성합니다."""
    for directory in (
        REFERENCE_VIDEO_DIR,
        REFERENCE_CACHE_DIR,
        RECORDING_DIR,
        WEIGHTS_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)
