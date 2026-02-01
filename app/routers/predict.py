from fastapi import APIRouter
from app.schemas.prediction import AnomalyRequest, AnomalyResponse

router = APIRouter()

@router.post("/anomaly", response_model=AnomalyResponse)
def predict_anomaly(payload: AnomalyRequest):
    return {
        "anomaly_score": 0.12,
        "is_anomaly": False,
        "confidence": 0.95
    }
