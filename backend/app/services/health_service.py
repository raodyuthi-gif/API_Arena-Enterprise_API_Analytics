"""Health service - composite health score calculation per API."""

import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, select, and_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.telemetry import RequestLog, HealthCheck
from app.models.api_registry import APIEndpoint


class HealthService:
    """Calculates a composite health score (0-100) for each API."""

    WEIGHTS = {
        "uptime": 0.35,
        "error_rate": 0.30,
        "latency": 0.25,
        "trend": 0.10,
    }

    @staticmethod
    async def calculate_health_score(api_id: uuid.UUID, db: AsyncSession) -> dict:
        """Compute health score from last 1 hour of telemetry."""
        since = datetime.now(timezone.utc) - timedelta(hours=1)

        stmt = select(
            func.count(RequestLog.id).label("total"),
            func.avg(RequestLog.latency_ms).label("avg_latency"),
            func.percentile_cont(0.99).within_group(RequestLog.latency_ms).label("p99"),
            func.sum(case((RequestLog.status_code >= 500, 1), else_=0)).label(
                "server_errors"
            ),
            func.sum(case((RequestLog.status_code >= 400, 1), else_=0)).label(
                "all_errors"
            ),
        ).where(and_(RequestLog.api_id == api_id, RequestLog.timestamp >= since))

        stats = (await db.execute(stmt)).one()

        total = stats.total or 0
        if total == 0:
            return {
                "health_score": 100.0,
                "is_healthy": True,
                "details": {"message": "No traffic in the last hour"},
                "uptime_percent": 100.0,
                "error_rate_percent": 0.0,
                "p99_latency_ms": 0.0,
            }

        error_rate = (stats.all_errors or 0) / total * 100
        avg_latency = float(stats.avg_latency or 0)
        p99 = float(stats.p99 or 0)

        # Fetch API SLA targets
        api_result = await db.execute(
            select(APIEndpoint).where(APIEndpoint.id == api_id)
        )
        api = api_result.scalar_one_or_none()

        sla_p99 = (api.sla_latency_p99_ms if api else None) or 1000.0
        sla_error_rate_max = api.sla_error_rate_max if api else 1.0

        # Component scores (0-100 each)
        error_score = (
            max(0, 100 - (error_rate / sla_error_rate_max) * 100)
            if sla_error_rate_max
            else 100
        )
        latency_score = max(0, 100 - (p99 / sla_p99) * 100) if sla_p99 else 100
        uptime_score = 100.0  # simplified: based on 5xx rate
        if total > 0:
            server_error_rate = (stats.server_errors or 0) / total * 100
            uptime_score = max(0, 100 - server_error_rate * 5)

        composite = (
            HealthService.WEIGHTS["uptime"] * uptime_score
            + HealthService.WEIGHTS["error_rate"] * error_score
            + HealthService.WEIGHTS["latency"] * latency_score
            + HealthService.WEIGHTS["trend"]
            * 100  # trend = always full unless we track degradation
        )
        composite = round(min(100.0, max(0.0, composite)), 2)

        is_healthy = composite >= 70

        return {
            "health_score": composite,
            "is_healthy": is_healthy,
            "uptime_percent": round(uptime_score, 2),
            "error_rate_percent": round(error_rate, 2),
            "p99_latency_ms": round(p99, 2),
            "details": {
                "total_requests": total,
                "avg_latency_ms": round(avg_latency, 2),
                "error_score": round(error_score, 2),
                "latency_score": round(latency_score, 2),
                "uptime_score": round(uptime_score, 2),
            },
        }

    @staticmethod
    def score_to_status(score: float) -> str:
        if score >= 85:
            return "healthy"
        if score >= 60:
            return "degraded"
        return "critical"

    @staticmethod
    async def save_health_check(
        api_id: uuid.UUID, health_data: dict, db: AsyncSession
    ) -> HealthCheck:
        check = HealthCheck(
            api_id=api_id,
            is_healthy=health_data["is_healthy"],
            health_score=health_data["health_score"],
            latency_ms=health_data.get("p99_latency_ms"),
            uptime_percent=health_data.get("uptime_percent"),
            error_rate_percent=health_data.get("error_rate_percent"),
            p99_latency_ms=health_data.get("p99_latency_ms"),
            details=health_data.get("details"),
        )
        db.add(check)
        await db.flush()
        return check
