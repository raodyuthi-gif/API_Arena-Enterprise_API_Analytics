"""SQLAlchemy ORM models for API Registry (endpoints, versions, tags)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Float, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base

# Many-to-many: APIEndpoint <-> APITag
api_endpoint_tags = Table(
    "api_endpoint_tags",
    Base.metadata,
    Column(
        "api_id", UUID(as_uuid=True), ForeignKey("api_endpoints.id"), primary_key=True
    ),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("api_tags.id"), primary_key=True),
)


class APIStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class APIEndpoint(Base):
    __tablename__ = "api_endpoints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False, default="GET")
    owner_team: Mapped[str | None] = mapped_column(String(100), nullable=True)
    owner_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[APIStatus] = mapped_column(
        String(20), default=APIStatus.ACTIVE, nullable=False
    )

    # SLA targets
    sla_latency_p99_ms: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )  # Target P99 latency in ms
    sla_uptime_percent: Mapped[float] = mapped_column(
        Float, default=99.9
    )  # Target uptime %
    sla_error_rate_max: Mapped[float] = mapped_column(
        Float, default=1.0
    )  # Max error rate %

    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    versions: Mapped[list["APIVersion"]] = relationship(
        "APIVersion", back_populates="api", cascade="all, delete-orphan"
    )
    tags: Mapped[list["APITag"]] = relationship(
        "APITag", secondary=api_endpoint_tags, back_populates="apis"
    )

    def __repr__(self) -> str:
        return f"<APIEndpoint {self.method} {self.base_url}{self.path}>"


class APIVersion(Base):
    __tablename__ = "api_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    api_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("api_endpoints.id"), nullable=False
    )
    version: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # e.g. "v1", "v2.1"
    changelog: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_deprecated: Mapped[bool] = mapped_column(Boolean, default=False)
    deprecated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    api: Mapped["APIEndpoint"] = relationship("APIEndpoint", back_populates="versions")

    def __repr__(self) -> str:
        return f"<APIVersion {self.version} for {self.api_id}>"


class APITag(Base):
    __tablename__ = "api_tags"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#6366f1")  # Hex color
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    apis: Mapped[list["APIEndpoint"]] = relationship(
        "APIEndpoint", secondary=api_endpoint_tags, back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<APITag {self.name}>"
