from fastapi import APIRouter

router = APIRouter()

@router.post("/anomaly")
def predict_anomaly():
    return {
        "anomaly_score": 0.12,
        "is_anomaly": False,
        "confidence": 0.95
    }
