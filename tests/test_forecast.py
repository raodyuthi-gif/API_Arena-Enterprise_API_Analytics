"""Tests for the ML forecasting module (train / predict / anomalies)."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

pytestmark = pytest.mark.asyncio


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


async def _register_api(client, token):
    resp = await client.post(
        "/apis",
        json={
            "name": "Search API",
            "base_url": "https://api.example.com",
            "path": "/v1/search",
            "method": "GET",
        },
        headers=auth_headers(token),
    )
    return resp.json()["id"]


async def _seed_hourly_traffic(db, api_id: str, hours: int = 240):
    """Insert a simple synthetic hourly traffic pattern directly via the DB session."""
    from app.models.telemetry import RequestLog

    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    for h in range(hours):
        ts = now - timedelta(hours=hours - h)
        # simple daily sine-ish pattern so the model has real structure to fit
        base = 20 + 15 * (1 if 9 <= ts.hour <= 18 else 0)
        for _ in range(base):
            db.add(
                RequestLog(
                    api_id=uuid.UUID(api_id),
                    endpoint_path="/v1/search",
                    method="GET",
                    status_code=200,
                    latency_ms=50.0,
                    timestamp=ts,
                )
            )
    await db.flush()


async def test_train_requires_minimum_data(client, admin_token):
    api_id = await _register_api(client, admin_token)
    resp = await client.post(
        f"/forecast/train?api_id={api_id}",
        json={"model_type": "linear_regression", "lookback_days": 30},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 400


async def test_train_and_predict_linear_model(client, admin_token, db):
    api_id = await _register_api(client, admin_token)
    await _seed_hourly_traffic(db, api_id, hours=240)

    train_resp = await client.post(
        f"/forecast/train?api_id={api_id}",
        json={"model_type": "linear_regression", "lookback_days": 30},
        headers=auth_headers(admin_token),
    )
    assert train_resp.status_code == 200
    body = train_resp.json()
    assert body["status"] == "trained"
    assert body["training_samples"] > 0

    predict_resp = await client.get(
        f"/forecast/{api_id}",
        params={"horizon_hours": 24},
        headers=auth_headers(admin_token),
    )
    assert predict_resp.status_code == 200
    predicted = predict_resp.json()
    assert len(predicted["data"]) == 24
    assert all(p["predicted_requests"] >= 0 for p in predicted["data"])


async def test_predict_without_training_fails(client, admin_token):
    api_id = await _register_api(client, admin_token)
    resp = await client.get(f"/forecast/{api_id}", headers=auth_headers(admin_token))
    assert resp.status_code == 404


async def test_anomaly_detection_after_training(client, admin_token, db):
    api_id = await _register_api(client, admin_token)
    await _seed_hourly_traffic(db, api_id, hours=240)

    await client.post(
        f"/forecast/train?api_id={api_id}",
        json={"model_type": "linear_regression", "lookback_days": 30},
        headers=auth_headers(admin_token),
    )

    resp = await client.get(
        f"/forecast/{api_id}/anomalies",
        params={"lookback_hours": 48, "sigma_threshold": 2.0},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    points = resp.json()
    assert isinstance(points, list)
    if points:
        assert "deviation_sigma" in points[0]
        assert "is_anomaly" in points[0]
