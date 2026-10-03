# 기준 프로필 JSON을 지정 경로에 저장하고 Pydantic 검증 후 불러옵니다.
# 원본 영상이 바뀐 경우 SHA-256 값으로 오래된 캐시인지 확인할 수 있습니다.
import hashlib
from pathlib import Path

from models.reference_profile import ReferenceProfile


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ReferenceRepository:
    def __init__(self, profile_path: Path) -> None:
        self.profile_path = profile_path

    def save(self, profile: ReferenceProfile) -> None:
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        self.profile_path.write_text(
            profile.model_dump_json(indent=2, by_alias=True),
            encoding="utf-8",
        )

    def load(self) -> ReferenceProfile:
        if not self.profile_path.exists():
            raise FileNotFoundError(
                f"기준 프로필이 없습니다: {self.profile_path}. "
                f"먼저 python -m scripts.preprocess_reference --exercise {self.profile_path.stem} 를 실행하세요."
            )
        return ReferenceProfile.model_validate_json(self.profile_path.read_text(encoding="utf-8"))
