from fastapi import FastAPI

app = FastAPI(title="Senior Pose Rehab AI Server")


@app.get("/")
def root():
    return {"message": "AI server is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}