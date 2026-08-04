"""Admin router - system stats and admin-only operations."""

from fastapi import APIRouter
from sqlalchemy import select, func

from app.dependencies import DbSession, CurrentAdmin
from app.models.user import User
from app.models.api_registry import APIEndpoint
from app.models.telemetry import RequestLog

router = APIRouter()


@router.get("/stats", summary="Get system-wide statistics (Admin only)")
async def get_system_stats(db: DbSession, _: CurrentAdmin):
    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
    total_apis = (await db.execute(select(func.count(APIEndpoint.id)))).scalar_one()
    total_requests = (await db.execute(select(func.count(RequestLog.id)))).scalar_one()

    return {
        "total_users": total_users,
        "total_apis": total_apis,
        "total_request_logs": total_requests,
        "platform": "Enterprise API Analytics Platform",
        "version": "1.0.0",
    }
