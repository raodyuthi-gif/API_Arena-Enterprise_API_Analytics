"""Pydantic schemas for analytics responses."""

import uuid
from datetime import datetime
from pydantic import BaseModel


class LatencyPoint(BaseModel):
    timestamp: datetime
    p50: float
    p90: float
    p99: float
    avg: float
    count: int


class LatencyAnalyticsResponse(BaseModel):
    api_id: uuid.UUID
    window: str
    data: list[LatencyPoint]
    overall_p50: float
    overall_p90: float
    overall_p99: float
    total_requests: int


class ErrorPoint(BaseModel):
    timestamp: datetime
    total_requests: int
    errors_4xx: int
    errors_5xx: int
    error_rate_percent: float


class TopFailingEndpoint(BaseModel):
    endpoint_path: str
    method: str
    error_count: int
    error_rate_percent: float
    top_status_code: int


class ErrorAnalyticsResponse(BaseModel):
    api_id: uuid.UUID
    window: str
    data: list[ErrorPoint]
    total_errors: int
    overall_error_rate: float
    top_failing_endpoints: list[TopFailingEndpoint]


class TrafficPoint(BaseModel):
    timestamp: datetime
    request_count: int
    unique_users: int


class TrafficAnalyticsResponse(BaseModel):
    api_id: uuid.UUID
    window: str
    data: list[TrafficPoint]
    total_requests: int
    peak_requests_per_hour: int


class DashboardSummary(BaseModel):
    total_apis: int
    healthy_apis: int
    degraded_apis: int
    critical_apis: int
    total_requests_24h: int
    avg_latency_ms_24h: float
    error_rate_24h: float
    p99_latency_ms_24h: float
    top_apis_by_traffic: list[dict]
    recent_alerts: list[dict]
