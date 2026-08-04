"""Forecast router - train ML models and generate predictions."""

import uuid
from fastapi import APIRouter, HTTPException, Query

from app.dependencies import DbSession, CurrentUser, CurrentAnalyst
from app.schemas.forecast import (
    ForecastResponse,
    TrainRequest,
    TrainResponse,
    AnomalyPoint,
)
from app.services.forecast_service import ForecastService

router = APIRouter()


@router.post(
    "/train",
    response_model=TrainResponse,
    summary="Train a forecast model for an API",
    description="Trains a Prophet or Ridge regression model on the last N days of telemetry for the specified API.",
)
async def train_forecast(
    api_id: uuid.UUID,
    payload: TrainRequest,
    db: DbSession,
    _: CurrentAnalyst,
):
    try:
        return await ForecastService.train_model(
            api_id=api_id,
            model_type=payload.model_type,
            lookback_days=payload.lookback_days,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{api_id}",
    response_model=ForecastResponse,
    summary="Get traffic forecast for an API",
    description="Returns predicted hourly request volumes with confidence intervals for the next N hours.",
)
async def get_forecast(
    api_id: uuid.UUID,
    horizon_hours: int = Query(
        default=168, ge=1, le=720, description="Forecast horizon in hours (max 30 days)"
    ),
    db: DbSession = ...,
    _: CurrentUser = ...,
):
    try:
        return await ForecastService.predict(
            api_id=api_id, horizon_hours=horizon_hours, db=db
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/{api_id}/anomalies",
    response_model=list[AnomalyPoint],
    summary="Detect traffic anomalies for an API",
    description="Compares recent actual traffic against the trained model's prediction "
    "and flags hourly points that deviate by more than N standard deviations.",
)
async def get_anomalies(
    api_id: uuid.UUID,
    lookback_hours: int = Query(
        default=168,
        ge=1,
        le=720,
        description="Lookback window in hours (default 7 days)",
    ),
    sigma_threshold: float = Query(
        default=2.0, ge=1.0, le=5.0, description="Deviation threshold in std devs"
    ),
    db: DbSession = ...,
    _: CurrentUser = ...,
):
    try:
        return await ForecastService.detect_anomalies(
            api_id=api_id,
            lookback_hours=lookback_hours,
            sigma_threshold=sigma_threshold,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
