"""Routers package."""

from app.routers import (
    auth,
    users,
    registry,
    telemetry,
    analytics,
    health,
    forecast,
    dashboard,
    admin,
)

__all__ = [
    "auth",
    "users",
    "registry",
    "telemetry",
    "analytics",
    "health",
    "forecast",
    "dashboard",
    "admin",
]
