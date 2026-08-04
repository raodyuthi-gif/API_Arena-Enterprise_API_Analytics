# ML Approach: Traffic Forecasting & Anomaly Detection

## Problem framing

For each registered API, forecast future request volume (hourly granularity)
and flag traffic points that deviate abnormally from the model's expectation.
This is a **per-API time-series forecasting** problem, not a classification
problem on a static external dataset — the "dataset" is each API's own
`request_logs` history, aggregated to hourly counts.

## Models implemented

| Model | Library | Notes |
|---|---|---|
| **Prophet** (default) | `prophet` | Additive model: trend + daily seasonality + weekly seasonality. Returns native confidence intervals (`yhat_lower`/`yhat_upper`). |
| **Ridge regression** (baseline) | `scikit-learn` | Linear model on hand-engineered cyclical features: hour-of-day and day-of-week encoded as sin/cos pairs, plus a weekend flag and month. |

Both are selectable via `model_type` on `POST /forecast/train` so the two
can be compared (MAE/MAPE) rather than presenting a single black-box choice.

### Why Prophet over the alternatives

| Alternative | Why not the default |
|---|---|
| ARIMA/SARIMA | Requires manual (p,d,q) tuning per series; handles one seasonality well, not overlapping daily+weekly patterns |
| LSTM/GRU | Needs far more data than a newly onboarded API has, needs a GPU to train quickly, and is a black box for an operational metric where interpretability matters |
| XGBoost/LightGBM | Competitive, but needs the same manual feature engineering as the Ridge baseline and doesn't natively output confidence intervals |
| Holt-Winters | Similar strengths to Prophet, but weaker with irregular/missing hours (e.g. an API with overnight silence) and no native uncertainty bounds |

Prophet was chosen because it directly matches the data's shape (hourly,
strong daily+weekly seasonality, occasionally irregular), trains in seconds
on CPU, and its output already includes the confidence bounds the API
contract exposes.

## Training pipeline

1. `RequestLog` rows for the API are aggregated to hourly counts
   (`date_trunc('hour', timestamp)`, `count(*)`) directly in PostgreSQL.
2. Minimum 10 hourly data points required to train (guards against
   training on noise).
3. Prophet: last 10% of the window held out for evaluation; MAE/MAPE
   computed against that holdout. Ridge: trained on the full window
   (evaluation via the holdout is a possible follow-up).
4. The trained model is serialized with `joblib` to `FORECAST_MODEL_DIR`.
5. Model metadata (`model_type`, `training_start/end`, `training_samples`,
   `mae`, `mape`, `is_active`) is persisted in the `forecast_models` table.
   Training a new model deactivates the previous one for that API — a
   simple version history without needing a full model registry.

## Automated retraining

`app/scheduler.py` runs an APScheduler job every
`FORECAST_RETRAIN_INTERVAL_HOURS` (default 24h) that retrains the active
model for every API that has one, using the freshest telemetry. This is
started in the FastAPI `lifespan` hook in `main.py` and is what makes
"auto-retrains daily" true rather than aspirational.

## Anomaly detection

`GET /forecast/{api_id}/anomalies` re-predicts over a recent lookback
window using the already-trained model and compares actual vs. predicted
hourly counts. The residuals' standard deviation is computed, and any
point where `|residual| / std > sigma_threshold` (default `2.0`) is
flagged `is_anomaly = true`. This is a standard, explainable approach
(vs. a second black-box anomaly model) and reuses the forecasting model
already in place rather than requiring a separate training pipeline.

## Training data

New deployments have no telemetry history, so nothing can train on day
one. `scripts/seed_synthetic_traffic.py` backfills historical
`request_logs`/`error_logs` with:
- Daily seasonality (business-hours peak) and weekly seasonality
  (lower weekend traffic)
- Gaussian noise on top of the seasonal base rate
- A handful of injected "incident windows" (elevated error rate +
  elevated latency for a few hours) so error analytics, health scoring,
  and anomaly detection all have real signal, not just clean data

Nothing about the **model outputs** is fabricated — MAE/MAPE/forecasts
are computed for real by Prophet/Ridge against whatever is in
`request_logs`, whether that came from the seeder, a load test, or real
production traffic ingested via `POST /telemetry/ingest`.

Run it with:
```bash
cd backend
python ../scripts/seed_synthetic_traffic.py --days 30 --apis 3 --incidents 3
```
