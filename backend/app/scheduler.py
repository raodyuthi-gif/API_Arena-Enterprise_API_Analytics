"""Background scheduler - periodic auto-retraining of active forecast models.

Wired into the FastAPI lifespan in main.py. Runs every
`settings.FORECAST_RETRAIN_INTERVAL_HOURS` hours (default 24) and
retrains the active model for every API that already has one, using
the freshest telemetry. This is what makes the "auto-retrains daily"
claim in the README actually true.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.forecast import ForecastModel
from app.services.forecast_service import ForecastService

logger = logging.getLogger("scheduler")

scheduler = AsyncIOScheduler()


async def retrain_all_active_models() -> None:
    """Retrain the active model for every API that has one, using its
    existing model_type. Failures for one API don't block the others.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ForecastModel).where(ForecastModel.is_active is True)
        )
        active_models = result.scalars().all()

        logger.info(
            "Scheduled retrain: %d active model(s) to refresh", len(active_models)
        )

        for model in active_models:
            try:
                lookback_days = (
                    max(1, (model.training_end - model.training_start).days) or 30
                )
                await ForecastService.train_model(
                    api_id=model.api_id,
                    model_type=model.model_type,
                    lookback_days=lookback_days,
                    db=db,
                )
                await db.commit()
                logger.info("Retrained model for api_id=%s", model.api_id)
            except Exception:
                await db.rollback()
                logger.exception("Retrain failed for api_id=%s", model.api_id)


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(
        retrain_all_active_models,
        "interval",
        hours=settings.FORECAST_RETRAIN_INTERVAL_HOURS,
        id="retrain_all_active_models",
        replace_existing=True,
        next_run_time=None,  # first run after one full interval, not immediately on boot
    )
    scheduler.start()
    logger.info(
        "Forecast auto-retrain scheduler started (every %sh)",
        settings.FORECAST_RETRAIN_INTERVAL_HOURS,
    )


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
