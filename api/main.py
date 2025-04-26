from fastapi import FastAPI
from api.routes.video import router as video_router

app = FastAPI(title="SBD Analyzer API")

app.include_router(video_router, prefix="/analisar")
