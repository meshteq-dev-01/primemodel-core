from fastapi import APIRouter
from app.schemas.prediction import AnomalyRequest, AnomalyResponse
import math

router = APIRouter()

@router.post("/anomaly", response_model=AnomalyResponse)
def predict_anomaly(payload: AnomalyRequest):
    values = []
    for value in payload.measurements.values():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            values.append(float(value))

    if not values:
        anomaly_score = 0.0
        is_anomaly = False
        confidence = 1.0
    else:
        n = len(values)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n
        std = math.sqrt(variance)

        if std == 0.0:
            anomaly_score = 0.0
        else:
            max_z = max(abs((v - mean) / std) for v in values)
            anomaly_score = max_z / (max_z + 1.0)

        is_anomaly = anomaly_score > 0.7
        confidence = 1.0 - anomaly_score

        if confidence < 0.0:
            confidence = 0.0
        elif confidence > 1.0:
            confidence = 1.0

    return {
        "anomaly_score": anomaly_score,
        "is_anomaly": is_anomaly,
        "confidence": confidence
    }
