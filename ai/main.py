# FastAPI AI 서버를 생성하고 공통 미들웨어와 라우터를 등록합니다.
# 실행 진입점이며 자세 분석 로직은 services 폴더에 분리되어 있습니다.
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import FRONTEND_ORIGINS, ensure_directories
from routers.exercise_ws import router as exercise_router
from routers.health import router as health_router

ensure_directories()

app = FastAPI(
    title="Senior Pose Rehab AI Server",
    version="0.1.0",
    description="BlazePose 기반 실시간 재활 운동 자세 분석 서버",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(exercise_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "AI server is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
