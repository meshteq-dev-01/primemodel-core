from fastapi import FastAPI
from app.routers import health, predict

app = FastAPI(title="PrimeModel AI Engine")

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(predict.router, prefix="/predict", tags=["Prediction"])


