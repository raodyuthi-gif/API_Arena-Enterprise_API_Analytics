"""Pydantic schemas for telemetry ingestion."""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class RequestLogIngest(BaseModel):
    """Single request log record for telemetry ingestion."""

    api_id: uuid.UUID
    endpoint_path: str = Field(..., max_length=500)
    method: str = Field(..., pattern=r"^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)$")
    status_code: int = Field(..., ge=100, le=599)
    latency_ms: float = Field(..., ge=0)
    request_size_bytes: int | None = None
    response_size_bytes: int | None = None
    user_id: uuid.UUID | None = None
    client_ip: str | None = None
    user_agent: str | None = None
    trace_id: str | None = None
    timestamp: datetime | None = None  # defaults to now if not provided
    extra: dict | None = None


class BatchIngestRequest(BaseModel):
    """Batch of request log records."""

    logs: list[RequestLogIngest] = Field(..., min_length=1, max_length=1000)


class IngestResponse(BaseModel):
    accepted: int
    rejected: int
    errors: list[str] = []
