"""Telemetry service - ingest, persist, and fan-out to Redis."""

import json
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.config import settings
from app.models.telemetry import RequestLog, ErrorLog
from app.schemas.telemetry import BatchIngestRequest, IngestResponse


class TelemetryService:
    _redis: aioredis.Redis | None = None

    @classmethod
    async def get_redis(cls) -> aioredis.Redis:
        if cls._redis is None:
            cls._redis = await aioredis.from_url(
                settings.REDIS_URL, decode_responses=True
            )
        return cls._redis

    @staticmethod
    async def ingest_batch(
        payload: BatchIngestRequest, db: AsyncSession
    ) -> IngestResponse:
        accepted = 0
        rejected = 0
        errors = []

        for log_data in payload.logs:
            try:
                ts = log_data.timestamp or datetime.now(timezone.utc)
                record = RequestLog(
                    api_id=log_data.api_id,
                    endpoint_path=log_data.endpoint_path,
                    method=log_data.method,
                    status_code=log_data.status_code,
                    latency_ms=log_data.latency_ms,
                    request_size_bytes=log_data.request_size_bytes,
                    response_size_bytes=log_data.response_size_bytes,
                    user_id=log_data.user_id,
                    client_ip=log_data.client_ip,
                    user_agent=log_data.user_agent,
                    trace_id=log_data.trace_id,
                    timestamp=ts,
                    extra=log_data.extra,
                )
                db.add(record)

                # Also log to ErrorLog if 4xx or 5xx
                if log_data.status_code >= 400:
                    err_record = ErrorLog(
                        api_id=log_data.api_id,
                        endpoint_path=log_data.endpoint_path,
                        method=log_data.method,
                        status_code=log_data.status_code,
                        timestamp=ts,
                    )
                    db.add(err_record)

                accepted += 1
            except Exception as e:
                rejected += 1
                errors.append(str(e))

        await db.flush()

        # Fan-out to Redis pub/sub for real-time dashboard
        try:
            redis = await TelemetryService.get_redis()
            await redis.publish(
                "telemetry:live",
                json.dumps(
                    {
                        "accepted": accepted,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                ),
            )
        except Exception:
            pass  # Non-fatal: Redis fan-out is best-effort

        return IngestResponse(accepted=accepted, rejected=rejected, errors=errors)
