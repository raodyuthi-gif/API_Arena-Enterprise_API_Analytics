"""Analytics router - latency, errors, traffic, and dashboard summary."""

import uuid
from fastapi import APIRouter, Query

from app.dependencies import DbSession, CurrentUser
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    LatencyAnalyticsResponse,
    ErrorAnalyticsResponse,
    TrafficAnalyticsResponse,
    DashboardSummary,
)

router = APIRouter()

VALID_WINDOWS = {"1h", "6h", "24h", "7d", "30d"}


@router.get(
    "/latency",
    response_model=LatencyAnalyticsResponse,
    summary="Get P50/P90/P99 latency percentiles over time",
)
async def get_latency(
    api_id: uuid.UUID,
    window: str = Query("24h", description="Time window: 1h | 6h | 24h | 7d | 30d"),
    db: DbSession = ...,
    _: CurrentUser = ...,
):
    if window not in VALID_WINDOWS:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400, detail=f"Invalid window. Choose from {VALID_WINDOWS}"
        )
    return await AnalyticsService.get_latency_analytics(api_id, window, db)


@router.get(
    "/errors",
    response_model=ErrorAnalyticsResponse,
    summary="Get error rates and top failing endpoints",
)
async def get_errors(
    api_id: uuid.UUID,
    window: str = Query("24h"),
    db: DbSession = ...,
    _: CurrentUser = ...,
):
    return await AnalyticsService.get_error_analytics(api_id, window, db)


@router.get(
    "/traffic",
    response_model=TrafficAnalyticsResponse,
    summary="Get request volume over time",
)
async def get_traffic(
    api_id: uuid.UUID,
    window: str = Query("24h"),
    db: DbSession = ...,
    _: CurrentUser = ...,
):
    return await AnalyticsService.get_traffic_analytics(api_id, window, db)


@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="Get overall platform KPI summary",
)
async def get_summary(db: DbSession, _: CurrentUser):
    return await AnalyticsService.get_dashboard_summary(db)
