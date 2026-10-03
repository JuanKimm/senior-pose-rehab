# AI 서버가 정상적으로 실행 중인지 확인하는 간단한 상태 API입니다.
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
