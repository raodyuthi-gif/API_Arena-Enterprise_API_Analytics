"""SQLAlchemy ORM models for ML forecast models and results."""
import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class ForecastModelType(str, Enum):
    PROPHET = "prophet"
    ARIMA = "arima"
    LINEAR = "linear_regression"


class ForecastModel(Base):
    """Trained ML model metadata for traffic forecasting."""
    __tablename__ = "forecast_models"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("api_endpoints.id"), nullable=False, index=True)
    model_type: Mapped[ForecastModelType] = mapped_column(String(30), default=ForecastModelType.PROPHET)
    model_path: Mapped[str] = mapped_column(String(500), nullable=False)   # path to .pkl file
    training_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    training_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    training_samples: Mapped[int] = mapped_column(Integer, nullable=False)
    mae: Mapped[float | None] = mapped_column(Float, nullable=True)        # Mean Absolute Error
    mape: Mapped[float | None] = mapped_column(Float, nullable=True)       # Mean Abs Percentage Error
    is_active: Mapped[bool] = mapped_column(String(5), default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    # Relationships
    results: Mapped[list["ForecastResult"]] = relationship("ForecastResult", back_populates="model", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ForecastModel {self.model_type} for api={self.api_id}>"


class ForecastResult(Base):
    """A single forecasted data point produced by a trained model."""
    __tablename__ = "forecast_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("forecast_models.id"), nullable=False, index=True)
    api_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("api_endpoints.id"), nullable=False, index=True)
    forecast_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)  # timestamp being predicted
    predicted_requests: Mapped[float] = mapped_column(Float, nullable=False)
    lower_bound: Mapped[float | None] = mapped_column(Float, nullable=True)
    upper_bound: Mapped[float | None] = mapped_column(Float, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    model: Mapped["ForecastModel"] = relationship("ForecastModel", back_populates="results")

    def __repr__(self) -> str:
        return f"<ForecastResult api={self.api_id} at={self.forecast_at} pred={self.predicted_requests}>"
