"""Analytics service - latency percentiles, error grouping, traffic aggregation."""

import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, select, and_, case, cast, Text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.telemetry import RequestLog
from app.schemas.analytics import (
    LatencyPoint,
    LatencyAnalyticsResponse,
    ErrorPoint,
    TopFailingEndpoint,
    ErrorAnalyticsResponse,
    TrafficPoint,
    TrafficAnalyticsResponse,
    DashboardSummary,
)

WINDOW_MAP = {
    "1h": timedelta(hours=1),
    "6h": timedelta(hours=6),
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
}


class AnalyticsService:
    @staticmethod
    def _window_to_delta(window: str) -> timedelta:
        return WINDOW_MAP.get(window, timedelta(hours=24))

    @staticmethod
    def _bucket_size(window: str) -> str:
        """Return PostgreSQL date_trunc bucket size based on window."""
        if window in ("1h", "6h"):
            return "minute"
        if window == "24h":
            return "hour"
        return "day"

    @staticmethod
    async def get_latency_analytics(
        api_id: uuid.UUID, window: str, db: AsyncSession
    ) -> LatencyAnalyticsResponse:
        delta = AnalyticsService._window_to_delta(window)
        since = datetime.now(timezone.utc) - delta
        bucket = AnalyticsService._bucket_size(window)

        stmt = (
            select(
                func.date_trunc(cast(bucket, Text), RequestLog.timestamp).label(
                    "bucket"
                ),
                func.percentile_cont(0.50)
                .within_group(RequestLog.latency_ms)
                .label("p50"),
                func.percentile_cont(0.90)
                .within_group(RequestLog.latency_ms)
                .label("p90"),
                func.percentile_cont(0.99)
                .within_group(RequestLog.latency_ms)
                .label("p99"),
                func.avg(RequestLog.latency_ms).label("avg"),
                func.count(RequestLog.id).label("count"),
            )
            .where(and_(RequestLog.api_id == api_id, RequestLog.timestamp >= since))
            .group_by(func.date_trunc(cast(bucket, Text), RequestLog.timestamp))
            .order_by(func.date_trunc(cast(bucket, Text), RequestLog.timestamp))
        )
        result = await db.execute(stmt)
        rows = result.all()

        data = [
            LatencyPoint(
                timestamp=r.bucket,
                p50=round(r.p50 or 0, 2),
                p90=round(r.p90 or 0, 2),
                p99=round(r.p99 or 0, 2),
                avg=round(float(r.avg or 0), 2),
                count=r.count,
            )
            for r in rows
        ]

        # Overall percentiles
        all_stmt = select(
            func.percentile_cont(0.50).within_group(RequestLog.latency_ms).label("p50"),
            func.percentile_cont(0.90).within_group(RequestLog.latency_ms).label("p90"),
            func.percentile_cont(0.99).within_group(RequestLog.latency_ms).label("p99"),
            func.count(RequestLog.id).label("total"),
        ).where(and_(RequestLog.api_id == api_id, RequestLog.timestamp >= since))
        overall = (await db.execute(all_stmt)).one()

        return LatencyAnalyticsResponse(
            api_id=api_id,
            window=window,
            data=data,
            overall_p50=round(overall.p50 or 0, 2),
            overall_p90=round(overall.p90 or 0, 2),
            overall_p99=round(overall.p99 or 0, 2),
            total_requests=overall.total or 0,
        )

    @staticmethod
    async def get_error_analytics(
        api_id: uuid.UUID, window: str, db: AsyncSession
    ) -> ErrorAnalyticsResponse:
        delta = AnalyticsService._window_to_delta(window)
        since = datetime.now(timezone.utc) - delta
        bucket = AnalyticsService._bucket_size(window)

        stmt = (
            select(
                func.date_trunc(cast(bucket, Text), RequestLog.timestamp).label(
                    "bucket"
                ),
                func.count(RequestLog.id).label("total"),
                func.sum(
                    case((RequestLog.status_code.between(400, 499), 1), else_=0)
                ).label("errors_4xx"),
                func.sum(
                    case((RequestLog.status_code.between(500, 599), 1), else_=0)
                ).label("errors_5xx"),
            )
            .where(and_(RequestLog.api_id == api_id, RequestLog.timestamp >= since))
            .group_by(func.date_trunc(cast(bucket, Text), RequestLog.timestamp))
            .order_by(func.date_trunc(cast(bucket, Text), RequestLog.timestamp))
        )
        rows = (await db.execute(stmt)).all()

        data = [
            ErrorPoint(
                timestamp=r.bucket,
                total_requests=r.total,
                errors_4xx=r.errors_4xx or 0,
                errors_5xx=r.errors_5xx or 0,
                error_rate_percent=round(
                    ((r.errors_4xx or 0) + (r.errors_5xx or 0)) / max(r.total, 1) * 100,
                    2,
                ),
            )
            for r in rows
        ]

        total_errors = sum(r.errors_4xx + r.errors_5xx for r in data)
        total_reqs = sum(r.total_requests for r in data)
        overall_error_rate = round(total_errors / max(total_reqs, 1) * 100, 2)

        # Top failing endpoints
        top_stmt = (
            select(
                RequestLog.endpoint_path,
                RequestLog.method,
                func.count(RequestLog.id).label("error_count"),
                func.max(RequestLog.status_code).label("top_status_code"),
            )
            .where(
                and_(
                    RequestLog.api_id == api_id,
                    RequestLog.timestamp >= since,
                    RequestLog.status_code >= 400,
                )
            )
            .group_by(RequestLog.endpoint_path, RequestLog.method)
            .order_by(func.count(RequestLog.id).desc())
            .limit(5)
        )
        top_rows = (await db.execute(top_stmt)).all()

        top_failing = [
            TopFailingEndpoint(
                endpoint_path=r.endpoint_path,
                method=r.method,
                error_count=r.error_count,
                error_rate_percent=0.0,
                top_status_code=r.top_status_code,
            )
            for r in top_rows
        ]

        return ErrorAnalyticsResponse(
            api_id=api_id,
            window=window,
            data=data,
            total_errors=total_errors,
            overall_error_rate=overall_error_rate,
            top_failing_endpoints=top_failing,
        )

    @staticmethod
    async def get_traffic_analytics(
        api_id: uuid.UUID, window: str, db: AsyncSession
    ) -> TrafficAnalyticsResponse:
        delta = AnalyticsService._window_to_delta(window)
        since = datetime.now(timezone.utc) - delta
        bucket = AnalyticsService._bucket_size(window)

        stmt = (
            select(
                func.date_trunc(cast(bucket, Text), RequestLog.timestamp).label(
                    "bucket"
                ),
                func.count(RequestLog.id).label("request_count"),
                func.count(func.distinct(RequestLog.user_id)).label("unique_users"),
            )
            .where(and_(RequestLog.api_id == api_id, RequestLog.timestamp >= since))
            .group_by(func.date_trunc(cast(bucket, Text), RequestLog.timestamp))
            .order_by(func.date_trunc(cast(bucket, Text), RequestLog.timestamp))
        )
        rows = (await db.execute(stmt)).all()

        data = [
            TrafficPoint(
                timestamp=r.bucket,
                request_count=r.request_count,
                unique_users=r.unique_users,
            )
            for r in rows
        ]

        return TrafficAnalyticsResponse(
            api_id=api_id,
            window=window,
            data=data,
            total_requests=sum(r.request_count for r in data),
            peak_requests_per_hour=max((r.request_count for r in data), default=0),
        )

    @staticmethod
    async def get_dashboard_summary(db: AsyncSession) -> DashboardSummary:
        since_24h = datetime.now(timezone.utc) - timedelta(hours=24)

        # Total requests + latency stats last 24h
        stats_stmt = select(
            func.count(RequestLog.id).label("total"),
            func.avg(RequestLog.latency_ms).label("avg_latency"),
            func.percentile_cont(0.99).within_group(RequestLog.latency_ms).label("p99"),
            func.sum(case((RequestLog.status_code >= 400, 1), else_=0)).label("errors"),
        ).where(RequestLog.timestamp >= since_24h)

        stats = (await db.execute(stats_stmt)).one()

        return DashboardSummary(
            total_apis=0,  # filled by health service
            healthy_apis=0,
            degraded_apis=0,
            critical_apis=0,
            total_requests_24h=stats.total or 0,
            avg_latency_ms_24h=round(float(stats.avg_latency or 0), 2),
            error_rate_24h=round(
                (stats.errors or 0) / max(stats.total or 1, 1) * 100, 2
            ),
            p99_latency_ms_24h=round(float(stats.p99 or 0), 2),
            top_apis_by_traffic=[],
            recent_alerts=[],
        )