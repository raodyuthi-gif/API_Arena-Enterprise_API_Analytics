"""Health router - composite health scores per API."""
import uuid
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.dependencies import DbSession, CurrentUser
from app.models.api_registry import APIEndpoint
from app.services.health_service import HealthService

router = APIRouter()


@router.get("", summary="Get health scores for all registered APIs")
async def get_all_health(db: DbSession, _: CurrentUser):
    result = await db.execute(select(APIEndpoint))
    apis = result.scalars().all()

    health_list = []
    for api in apis:
        health_data = await HealthService.calculate_health_score(api.id, db)
        health_list.append({
            "api_id": str(api.id),
            "api_name": api.name,
            "base_url": api.base_url,
            "path": api.path,
            "method": api.method,
            "status": HealthService.score_to_status(health_data["health_score"]),
            **health_data,
        })

    return {
        "total_apis": len(health_list),
        "healthy": sum(1 for h in health_list if h["status"] == "healthy"),
        "degraded": sum(1 for h in health_list if h["status"] == "degraded"),
        "critical": sum(1 for h in health_list if h["status"] == "critical"),
        "apis": health_list,
    }


@router.get("/{api_id}", summary="Get detailed health for a single API")
async def get_api_health(api_id: uuid.UUID, db: DbSession, _: CurrentUser):
    result = await db.execute(select(APIEndpoint).where(APIEndpoint.id == api_id))
    api = result.scalar_one_or_none()
    if not api:
        raise HTTPException(status_code=404, detail="API not found")

    health_data = await HealthService.calculate_health_score(api_id, db)
    await HealthService.save_health_check(api_id, health_data, db)

    return {
        "api_id": str(api_id),
        "api_name": api.name,
        "status": HealthService.score_to_status(health_data["health_score"]),
        **health_data,
    }
