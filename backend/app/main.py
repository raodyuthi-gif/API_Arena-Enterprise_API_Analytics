"""
Enterprise API Analytics Platform - FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.database import create_tables
from app.routers import auth, users, registry, telemetry, analytics, health, forecast, dashboard, admin
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events."""
    # Startup
    await create_tables()
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Enterprise API Analytics & Performance Management Platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # ── Prometheus Metrics ────────────────────────────────────────
    if settings.PROMETHEUS_ENABLED:
        Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    # ── Routers ───────────────────────────────────────────────────
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/users", tags=["Users"])
    app.include_router(registry.router, prefix="/apis", tags=["API Registry"])
    app.include_router(telemetry.router, prefix="/telemetry", tags=["Telemetry"])
    app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
    app.include_router(health.router, prefix="/health", tags=["Health"])
    app.include_router(forecast.router, prefix="/forecast", tags=["Forecast"])
    app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
    app.include_router(admin.router, prefix="/admin", tags=["Admin"])

    # ── Root Health Check ─────────────────────────────────────────
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "service": settings.APP_NAME,
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs",
        }

    return app


app = create_app()
