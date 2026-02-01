from pydantic import BaseModel
from typing import Dict, Any

class AnomalyRequest(BaseModel):
    asset_id: str
    asset_type: str
    measurements: Dict[str, Any]

class AnomalyResponse(BaseModel):
    anomaly_score: float
    is_anomaly: bool
    confidence: float
    explanation: str
    contributing_factors: list[str]

class RULRequest(BaseModel):
    asset_id: str
    age_days: int
    usage_rate: float

class RULResponse(BaseModel):
    estimated_rul_days: int
    confidence: float
    explanation: str

class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str
    model_type: str
    description: str
    last_updated: str
    assumptions: list[str]
    limitations: list[str]
