"""Telemetry router - ingest request logs."""

from fastapi import APIRouter

from app.dependencies import DbSession, CurrentUser
from app.schemas.telemetry import BatchIngestRequest, IngestResponse
from app.services.telemetry_service import TelemetryService

router = APIRouter()


@router.post(
    "/ingest",
    response_model=IngestResponse,
    summary="Ingest a batch of API request logs",
    description="Accepts up to 1000 request logs per call. Use this from your API gateway or SDK.",
)
async def ingest_batch(payload: BatchIngestRequest, db: DbSession, _: CurrentUser):
    return await TelemetryService.ingest_batch(payload, db)
