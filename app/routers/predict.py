from fastapi import APIRouter
from app.schemas.prediction import AnomalyRequest, AnomalyResponse, RULRequest, RULResponse, ModelInfoResponse
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

@router.post("/rul", response_model=RULResponse)
def predict_rul(payload: RULRequest):
    design_life_days = 3650

    if payload.age_days < 0 or payload.usage_rate <= 0:
        estimated_rul_days = design_life_days
        confidence = 1.0
    else:
        degradation = payload.age_days * payload.usage_rate
        remaining_life = design_life_days - degradation
        estimated_rul_days = int(max(remaining_life, 0))
        confidence = estimated_rul_days / design_life_days

        if confidence < 0.0:
            confidence = 0.0
        elif confidence > 1.0:
            confidence = 1.0

    return {
        "estimated_rul_days": estimated_rul_days,
        "confidence": confidence
    }

@router.get("/model/info", response_model=ModelInfoResponse)
def model_info():
    return {
        "model_name": "PrimeModel Predictive Engine",
        "model_version": "0.1.0",
        "model_type": "deterministic-rule-based",
        "description": "Baseline predictive analytics engine for anomaly detection and remaining useful life estimation.",
        "last_updated": "2026-02-01T00:00:00Z",
        "assumptions": [
            "Asset degradation is linear with usage",
            "Sensor inputs are pre-cleaned"
        ],
        "limitations": [
            "Does not account for environmental acceleration",
            "Not trained on historical failure labels"
        ]
    }
