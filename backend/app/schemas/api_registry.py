"""Pydantic schemas for API Registry."""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from app.models.api_registry import APIStatus


class APITagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#6366f1", pattern=r"^#[0-9A-Fa-f]{6}$")


class APITagResponse(BaseModel):
    id: uuid.UUID
    name: str
    color: str
    model_config = {"from_attributes": True}


class APIVersionCreate(BaseModel):
    version: str = Field(..., max_length=50)
    changelog: str | None = None


class APIVersionResponse(BaseModel):
    id: uuid.UUID
    version: str
    changelog: str | None
    is_deprecated: bool
    deprecated_at: datetime | None
    created_at: datetime
    model_config = {"from_attributes": True}


class APIEndpointCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    base_url: str = Field(..., max_length=500)
    path: str = Field(..., max_length=500)
    method: str = Field(default="GET", pattern=r"^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)$")
    owner_team: str | None = None
    owner_email: str | None = None
    status: APIStatus = APIStatus.ACTIVE
    sla_latency_p99_ms: float | None = None
    sla_uptime_percent: float = 99.9
    sla_error_rate_max: float = 1.0
    is_public: bool = False
    tag_ids: list[uuid.UUID] = []


class APIEndpointUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: APIStatus | None = None
    owner_team: str | None = None
    owner_email: str | None = None
    sla_latency_p99_ms: float | None = None
    sla_uptime_percent: float | None = None
    sla_error_rate_max: float | None = None
    is_public: bool | None = None
    tag_ids: list[uuid.UUID] | None = None


class APIEndpointResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    base_url: str
    path: str
    method: str
    owner_team: str | None
    owner_email: str | None
    status: APIStatus
    sla_latency_p99_ms: float | None
    sla_uptime_percent: float
    sla_error_rate_max: float
    is_public: bool
    tags: list[APITagResponse]
    versions: list[APIVersionResponse]
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class APIEndpointListResponse(BaseModel):
    total: int
    items: list[APIEndpointResponse]
    page: int
    page_size: int
