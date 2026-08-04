"""
Synthetic Traffic Generator
============================
Seeds realistic historical telemetry so the forecasting models have
something to train on, and the dashboard has something to show.

This does NOT fabricate model outputs — MAE/MAPE/forecasts are still
computed for real by Prophet/Ridge. It only backfills the *input*
history (request_logs / error_logs), the same way a load test or a
staging environment's traffic would.

Usage:
    cd backend
    python ../scripts/seed_synthetic_traffic.py --days 30 --apis 3

What it simulates, per API:
  - Daily seasonality: traffic ramps up 9am-6pm, quiet overnight
  - Weekly seasonality: ~40% lower traffic on weekends
  - Gaussian noise on top of the seasonal base rate
  - Baseline error rate (~1-2%) plus 2-4 injected incident windows
    (elevated 5xx rate for a few hours) so error analytics, health
    scoring, and anomaly detection all have real signal to work with
  - Latency correlated with load (busier hours run a bit slower),
    with the same incident windows causing latency spikes
"""
import argparse
import asyncio
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone

sys.path.insert(0, ".")  # run from backend/ so `app` package resolves

from app.database import AsyncSessionLocal
from app.models.api_registry import APIEndpoint, APIStatus
from app.models.telemetry import RequestLog, ErrorLog

DEMO_APIS = [
    {"name": "Orders API", "base_url": "https://api.internal.co", "path": "/v1/orders", "method": "GET"},
    {"name": "Payments API", "base_url": "https://api.internal.co", "path": "/v1/payments", "method": "POST"},
    {"name": "Inventory API", "base_url": "https://api.internal.co", "path": "/v1/inventory", "method": "GET"},
    {"name": "Auth API", "base_url": "https://api.internal.co", "path": "/v1/auth/token", "method": "POST"},
]

BATCH_SIZE = 2000


def hourly_base_rate(hour: int, weekday: int) -> float:
    """Requests/hour baseline: business-hours daily curve x weekday factor."""
    daily_curve = 8 + 42 * max(0.0, 1 - ((hour - 13) / 9) ** 2)  # peaks ~1pm
    weekend_factor = 0.55 if weekday >= 5 else 1.0
    return daily_curve * weekend_factor


async def seed_api(session, api: APIEndpoint, days: int, incident_windows: list[tuple[datetime, datetime]]):
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = now - timedelta(days=days)

    logs = []
    errors = []
    ts = start
    while ts < now:
        rate = hourly_base_rate(ts.hour, ts.weekday())
        rate *= random.gauss(1.0, 0.15)
        count = max(0, int(round(rate)))

        in_incident = any(w_start <= ts <= w_end for w_start, w_end in incident_windows)
        error_rate = random.uniform(0.15, 0.35) if in_incident else random.uniform(0.005, 0.02)
        base_latency = random.uniform(180, 320) if in_incident else random.uniform(25, 90)

        for _ in range(count):
            jitter_seconds = random.randint(0, 3599)
            request_ts = ts + timedelta(seconds=jitter_seconds)
            is_error = random.random() < error_rate
            status_code = random.choice([500, 502, 503]) if is_error else random.choice([200, 200, 200, 201, 204])
            latency = max(1.0, random.gauss(base_latency, base_latency * 0.3))

            log = RequestLog(
                id=uuid.uuid4(),
                api_id=api.id,
                endpoint_path=api.path,
                method=api.method,
                status_code=status_code,
                latency_ms=round(latency, 2),
                request_size_bytes=random.randint(100, 2000),
                response_size_bytes=random.randint(200, 5000),
                timestamp=request_ts,
            )
            logs.append(log)

            if status_code >= 400:
                errors.append(ErrorLog(
                    id=uuid.uuid4(),
                    api_id=api.id,
                    endpoint_path=api.path,
                    method=api.method,
                    status_code=status_code,
                    error_type="ServerError" if status_code >= 500 else "ClientError",
                    error_message=f"Synthetic {status_code} for load simulation",
                    timestamp=request_ts,
                ))

            if len(logs) >= BATCH_SIZE:
                session.add_all(logs)
                session.add_all(errors)
                await session.flush()
                logs, errors = [], []

        ts += timedelta(hours=1)

    if logs or errors:
        session.add_all(logs)
        session.add_all(errors)
        await session.flush()


async def get_or_create_demo_apis(session, n: int) -> list[APIEndpoint]:
    from sqlalchemy import select
    result = await session.execute(select(APIEndpoint))
    existing = result.scalars().all()
    if existing:
        return existing[:n] if n else existing

    apis = []
    for spec in DEMO_APIS[:n]:
        api = APIEndpoint(
            id=uuid.uuid4(),
            name=spec["name"],
            base_url=spec["base_url"],
            path=spec["path"],
            method=spec["method"],
            status=APIStatus.ACTIVE,
            sla_latency_p99_ms=500.0,
            sla_uptime_percent=99.9,
            sla_error_rate_max=1.0,
        )
        session.add(api)
        apis.append(api)
    await session.flush()
    return apis


async def main(days: int, n_apis: int, incidents_per_api: int):
    async with AsyncSessionLocal() as session:
        apis = await get_or_create_demo_apis(session, n_apis)
        print(f"Seeding {days} days of synthetic telemetry for {len(apis)} API(s)...")

        for api in apis:
            now = datetime.now(timezone.utc)
            start = now - timedelta(days=days)
            incident_windows = []
            for _ in range(incidents_per_api):
                incident_start = start + timedelta(
                    hours=random.uniform(0, days * 24 - 6)
                )
                incident_windows.append((incident_start, incident_start + timedelta(hours=random.uniform(1, 4))))

            print(f"  - {api.name}: incidents at {[w[0].strftime('%Y-%m-%d %H:%M') for w in incident_windows]}")
            await seed_api(session, api, days, incident_windows)

        await session.commit()
        print("Done. You can now call POST /forecast/train for each api_id.")
        for api in apis:
            print(f"    api_id={api.id}  name={api.name!r}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed synthetic API telemetry for ML training/demo.")
    parser.add_argument("--days", type=int, default=30, help="Days of history to generate (default: 30)")
    parser.add_argument("--apis", type=int, default=3, help="Number of demo APIs to seed (default: 3)")
    parser.add_argument("--incidents", type=int, default=3, help="Injected incident windows per API (default: 3)")
    args = parser.parse_args()

    asyncio.run(main(args.days, args.apis, args.incidents))
