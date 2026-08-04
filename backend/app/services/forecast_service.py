"""Forecast service - train ML models and generate traffic predictions."""

import os
import uuid
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.telemetry import RequestLog
from app.models.forecast import ForecastModel, ForecastModelType
from app.schemas.forecast import (
    ForecastResponse,
    ForecastPoint,
    TrainResponse,
    AnomalyPoint,
)


class ForecastService:
    @staticmethod
    async def _fetch_training_data(
        api_id: uuid.UUID, lookback_days: int, db: AsyncSession
    ) -> pd.DataFrame:
        """Fetch hourly aggregated request counts for training."""
        since = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        stmt = (
            select(
                func.date_trunc("hour", RequestLog.timestamp).label("ds"),
                func.count(RequestLog.id).label("y"),
            )
            .where(and_(RequestLog.api_id == api_id, RequestLog.timestamp >= since))
            .group_by(func.date_trunc("hour", RequestLog.timestamp))
            .order_by(func.date_trunc("hour", RequestLog.timestamp))
        )
        rows = (await db.execute(stmt)).all()
        df = pd.DataFrame(rows, columns=["ds", "y"])
        df["ds"] = pd.to_datetime(df["ds"], utc=True)
        return df

    @staticmethod
    async def train_model(
        api_id: uuid.UUID,
        model_type: ForecastModelType,
        lookback_days: int,
        db: AsyncSession,
    ) -> TrainResponse:
        """Train a forecast model on historical telemetry."""
        df = await ForecastService._fetch_training_data(api_id, lookback_days, db)
        if len(df) < 10:
            raise ValueError(
                "Not enough historical data to train a model (need ≥10 hourly data points)"
            )

        training_start = df["ds"].min().to_pydatetime()
        training_end = df["ds"].max().to_pydatetime()

        model_dir = settings.FORECAST_MODEL_DIR
        os.makedirs(model_dir, exist_ok=True)
        model_filename = f"{model_dir}/{api_id}_{model_type.value}.pkl"

        mae = None
        mape = None

        if model_type == ForecastModelType.PROPHET:
            from prophet import Prophet

            m = Prophet(
                yearly_seasonality=False,
                weekly_seasonality=True,
                daily_seasonality=True,
            )
            train_df = df[["ds", "y"]].copy()
            train_df["ds"] = train_df["ds"].dt.tz_localize(None)
            m.fit(train_df)
            joblib.dump(m, model_filename)

            # Evaluate on last 10% holdout
            split = max(int(len(train_df) * 0.9), 1)
            holdout = train_df.iloc[split:].copy()
            if not holdout.empty:
                forecast = m.predict(holdout[["ds"]])
                actuals = holdout["y"].values
                preds = forecast["yhat"].values[: len(actuals)]
                mae = float(np.mean(np.abs(actuals - preds)))
                mape = float(
                    np.mean(np.abs((actuals - preds) / np.maximum(actuals, 1))) * 100
                )

        elif model_type == ForecastModelType.LINEAR:
            from sklearn.linear_model import Ridge
            from app.ml.features import build_time_features

            X, y = build_time_features(df)
            model = Ridge()
            model.fit(X, y)
            joblib.dump(model, model_filename)

        # Mark all previous models inactive
        old_models = (
            (
                await db.execute(
                    select(ForecastModel).where(
                        and_(
                            ForecastModel.api_id == api_id,
                            ForecastModel.is_active is True,
                        )
                    )
                )
            )
            .scalars()
            .all()
        )
        for old in old_models:
            old.is_active = False

        # Persist model metadata
        forecast_model = ForecastModel(
            api_id=api_id,
            model_type=model_type,
            model_path=model_filename,
            training_start=training_start,
            training_end=training_end,
            training_samples=len(df),
            mae=mae,
            mape=mape,
            is_active=True,
        )
        db.add(forecast_model)
        await db.flush()

        return TrainResponse(
            model_id=forecast_model.id,
            api_id=api_id,
            model_type=model_type,
            training_samples=len(df),
            mae=mae,
            mape=mape,
            status="trained",
            created_at=datetime.now(timezone.utc),
        )

    @staticmethod
    async def predict(
        api_id: uuid.UUID, horizon_hours: int, db: AsyncSession
    ) -> ForecastResponse:
        """Load the active model and generate a forecast."""
        result = await db.execute(
            select(ForecastModel)
            .where(
                and_(ForecastModel.api_id == api_id, ForecastModel.is_active is True)
            )
            .order_by(ForecastModel.created_at.desc())
            .limit(1)
        )
        model_record = result.scalar_one_or_none()
        if not model_record:
            raise ValueError(
                f"No trained model found for api_id={api_id}. Please train first."
            )

        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        future_dates = [now + timedelta(hours=i) for i in range(1, horizon_hours + 1)]
        model = joblib.load(model_record.model_path)

        data: list[ForecastPoint] = []

        if model_record.model_type == ForecastModelType.PROPHET:
            future_df = pd.DataFrame(
                {"ds": [d.replace(tzinfo=None) for d in future_dates]}
            )
            forecast = model.predict(future_df)
            for i, row in forecast.iterrows():
                data.append(
                    ForecastPoint(
                        timestamp=future_dates[i],
                        predicted_requests=max(0, round(float(row["yhat"]), 2)),
                        lower_bound=max(0, round(float(row["yhat_lower"]), 2)),
                        upper_bound=max(0, round(float(row["yhat_upper"]), 2)),
                    )
                )
        elif model_record.model_type == ForecastModelType.LINEAR:
            from app.ml.features import build_time_features_for_dates

            X = build_time_features_for_dates(future_dates)
            preds = model.predict(X)
            for ts, pred in zip(future_dates, preds):
                data.append(
                    ForecastPoint(
                        timestamp=ts,
                        predicted_requests=max(0, round(float(pred), 2)),
                        lower_bound=None,
                        upper_bound=None,
                    )
                )

        return ForecastResponse(
            api_id=api_id,
            model_type=model_record.model_type,
            horizon_hours=horizon_hours,
            generated_at=datetime.now(timezone.utc),
            data=data,
            model_mae=model_record.mae,
            model_mape=model_record.mape,
        )

    @staticmethod
    async def detect_anomalies(
        api_id: uuid.UUID, lookback_hours: int, sigma_threshold: float, db: AsyncSession
    ) -> list[AnomalyPoint]:
        """Compare actual traffic against the active model's in-sample prediction
        for the recent window and flag points that deviate by more than
        `sigma_threshold` standard deviations of the residuals — a standard
        statistical anomaly-detection approach for time series.
        """
        result = await db.execute(
            select(ForecastModel)
            .where(
                and_(ForecastModel.api_id == api_id, ForecastModel.is_active is True)
            )
            .order_by(ForecastModel.created_at.desc())
            .limit(1)
        )
        model_record = result.scalar_one_or_none()
        if not model_record:
            raise ValueError(
                f"No trained model found for api_id={api_id}. Please train first."
            )

        lookback_days = max(1, lookback_hours // 24 + 1)
        df = await ForecastService._fetch_training_data(api_id, lookback_days, db)
        if df.empty:
            return []

        # Keep only the requested lookback window
        cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
        df = df[df["ds"] >= cutoff].reset_index(drop=True)
        if df.empty:
            return []

        model = joblib.load(model_record.model_path)
        predicted: np.ndarray

        if model_record.model_type == ForecastModelType.PROPHET:
            predict_df = df[["ds"]].copy()
            predict_df["ds"] = predict_df["ds"].dt.tz_localize(None)
            forecast = model.predict(predict_df)
            predicted = forecast["yhat"].values
        else:
            from app.ml.features import build_time_features_for_dates

            X = build_time_features_for_dates(list(df["ds"].dt.to_pydatetime()))
            predicted = model.predict(X)

        actual = df["y"].values.astype(float)
        residuals = actual - predicted
        std = float(np.std(residuals)) or 1.0  # avoid div-by-zero on flat series

        points: list[AnomalyPoint] = []
        for i, row in df.iterrows():
            deviation_sigma = float(residuals[i] / std)
            points.append(
                AnomalyPoint(
                    timestamp=row["ds"].to_pydatetime(),
                    actual_requests=int(row["y"]),
                    predicted_requests=round(float(predicted[i]), 2),
                    deviation_sigma=round(deviation_sigma, 2),
                    is_anomaly=abs(deviation_sigma) > sigma_threshold,
                )
            )
        return points
