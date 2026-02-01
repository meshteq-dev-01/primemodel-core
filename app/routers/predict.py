from fastapi import APIRouter
from app.schemas.prediction import AnomalyRequest, AnomalyResponse, RULRequest, RULResponse, ModelInfoResponse
from app.db.database import save_prediction
import math

router = APIRouter()

PIPELINE_TEMPLATE = {
    "required_measurements": ["pressure", "temperature", "wall_thickness"]
}

PUMP_TEMPLATE = {
    "required_measurements": ["vibration_rms", "bearing_temp", "motor_current"]
}

DMA_TEMPLATE = {
    "required_measurements": ["flow_rate", "pressure_in", "pressure_out"]
}

@router.post("/anomaly", response_model=AnomalyResponse)
def predict_anomaly(payload: AnomalyRequest):
    asset_type = payload.asset_type.lower()
    if asset_type == "pipeline":
        template = PIPELINE_TEMPLATE
    elif asset_type == "pump":
        template = PUMP_TEMPLATE
    elif asset_type == "dma":
        template = DMA_TEMPLATE
    else:
        template = {"required_measurements": []}

    contributing_factors = []
    values = []
    for key in template["required_measurements"]:
        value = payload.measurements.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            contributing_factors.append(key)
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

    if asset_type == "pipeline":
        explanation = "Pipeline pressure and wall thickness behavior indicates stability." if not is_anomaly else "Pipeline pressure or wall thickness deviation indicates potential anomaly."
    elif asset_type == "pump":
        explanation = "Pump vibration and bearing condition are within expected range." if not is_anomaly else "Pump vibration or bearing condition shows significant deviation."
    elif asset_type == "dma":
        explanation = "DMA flow and pressure balance are within expected range." if not is_anomaly else "DMA flow and pressure balance show significant deviation."
    else:
        explanation = "Asset behavior is within expected operating range." if not is_anomaly else "Anomaly detected due to significant deviation in key measurements."

    response = {
        "anomaly_score": anomaly_score,
        "is_anomaly": is_anomaly,
        "confidence": confidence,
        "explanation": explanation,
        "contributing_factors": contributing_factors
    }
    save_prediction(payload.asset_id, payload.asset_type, "anomaly", response)
    return response

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

    response = {
        "estimated_rul_days": estimated_rul_days,
        "confidence": confidence,
        "explanation": f"RUL computed using design life of {design_life_days} days, age_days of {payload.age_days}, and usage_rate of {payload.usage_rate}."
    }
    save_prediction(payload.asset_id, "unknown", "rul", response)
    return response

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
