# 공식 MediaPipe 저장소에서 설정된 Pose Landmarker 모델을 내려받습니다.
# 모델 파일은 대용량이므로 Git에 올리지 않고 개발 환경마다 한 번 실행합니다.
from pathlib import Path
from urllib.request import urlretrieve

from core.config import POSE_MODEL_PATH, POSE_MODEL_URL, ensure_directories


def main() -> None:
    ensure_directories()
    if POSE_MODEL_PATH.exists():
        print(f"이미 모델이 있습니다: {POSE_MODEL_PATH}")
        return

    temporary_path = Path(f"{POSE_MODEL_PATH}.download")
    print(f"모델 다운로드 중: {POSE_MODEL_URL}")
    try:
        urlretrieve(POSE_MODEL_URL, temporary_path)
        temporary_path.replace(POSE_MODEL_PATH)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()
    print(f"모델 저장 완료: {POSE_MODEL_PATH}")


if __name__ == "__main__":
    main()
