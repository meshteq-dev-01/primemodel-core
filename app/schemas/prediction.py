from pydantic import BaseModel
from typing import Dict, Any

class AnomalyRequest(BaseModel):
    asset_id: str
    measurements: Dict[str, Any]

class AnomalyResponse(BaseModel):
    anomaly_score: float
    is_anomaly: bool
    confidence: float
