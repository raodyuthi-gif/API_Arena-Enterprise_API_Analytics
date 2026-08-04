"""Dashboard router - overview + real-time WebSocket stream."""

import asyncio
import json
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.dependencies import DbSession, CurrentUser
from app.services.analytics_service import AnalyticsService
from app.services.health_service import HealthService
from app.models.api_registry import APIEndpoint
from sqlalchemy import select

router = APIRouter()


@router.get("/overview", summary="Get dashboard overview with KPIs and health summary")
async def get_overview(db: DbSession, _: CurrentUser):
    summary = await AnalyticsService.get_dashboard_summary(db)

    # Enrich with health counts
    apis_result = await db.execute(select(APIEndpoint))
    apis = apis_result.scalars().all()
    summary.total_apis = len(apis)

    health_counts = {"healthy": 0, "degraded": 0, "critical": 0}
    for api in apis:
        health_data = await HealthService.calculate_health_score(api.id, db)
        status = HealthService.score_to_status(health_data["health_score"])
        health_counts[status] = health_counts.get(status, 0) + 1

    summary.healthy_apis = health_counts["healthy"]
    summary.degraded_apis = health_counts["degraded"]
    summary.critical_apis = health_counts["critical"]

    return summary


@router.websocket("/realtime")
async def realtime_dashboard(websocket: WebSocket):
    """WebSocket endpoint that pushes live metrics every 5 seconds."""
    await websocket.accept()
    try:
        while True:
            data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": "heartbeat",
                "message": "Live dashboard connected. Telemetry events will appear here.",
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass
