import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class ForecastModel(Base):
    __tablename__ = "forecast_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_id = Column(UUID(as_uuid=True), ForeignKey("api_registry.id", ondelete="CASCADE"), nullable=False)
    model_type = Column(String(50), nullable=False)
    model_path = Column(String(255), nullable=True)
    training_start = Column(DateTime(timezone=True), nullable=False)
    training_end = Column(DateTime(timezone=True), nullable=False)
    training_samples = Column(Integer, nullable=False)
    mae = Column(Float, nullable=True)
    mape = Column(Float, nullable=True)
    
    # Explicitly mapped as Boolean so asyncpg handles PostgreSQL boolean type correctly
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    metadata_json = Column("metadata", JSON, nullable=True)

    # Relationship
    api = relationship("APIRegistry", back_populates="forecast_models")