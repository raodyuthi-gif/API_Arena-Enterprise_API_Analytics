"""Application configuration using Pydantic BaseSettings."""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # ── Application ───────────────────────────────────────────────
    APP_NAME: str = "Enterprise API Analytics Platform"
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-to-a-very-long-random-secret-key"

    # ── Database ─────────────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/api_analytics"
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # ── Redis ─────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── JWT Auth ──────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-jwt-secret-256bit"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── ML / Forecasting ─────────────────────────────────────────
    FORECAST_MODEL_DIR: str = "app/ml/models"
    FORECAST_RETRAIN_INTERVAL_HOURS: int = 24
    FORECAST_HORIZON_HOURS: int = 168

    # ── CORS ──────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── Rate Limiting ─────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 120

    # ── Monitoring ────────────────────────────────────────────────
    PROMETHEUS_ENABLED: bool = True
    GRAFANA_ADMIN_PASSWORD: str = "admin"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            import json

            return json.loads(v)
        return v

    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}


settings = Settings()
