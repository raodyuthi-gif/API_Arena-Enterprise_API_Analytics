"""Pydantic schemas for ML forecast responses."""
import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.forecast import ForecastModelType


class ForecastPoint(BaseModel):
    timestamp: datetime
    predicted_requests: float
    lower_bound: float | None
    upper_bound: float | None


class ForecastResponse(BaseModel):
    api_id: uuid.UUID
    model_type: ForecastModelType
    horizon_hours: int
    generated_at: datetime
    data: list[ForecastPoint]
    model_mae: float | None
    model_mape: float | None


class TrainRequest(BaseModel):
    model_type: ForecastModelType = ForecastModelType.PROPHET
    lookback_days: int = 30


class TrainResponse(BaseModel):
    model_id: uuid.UUID
    api_id: uuid.UUID
    model_type: ForecastModelType
    training_samples: int
    mae: float | None
    mape: float | None
    status: str
    created_at: datetime


class AnomalyPoint(BaseModel):
    timestamp: datetime
    actual_requests: int
    predicted_requests: float
    deviation_sigma: float
    is_anomaly: bool
