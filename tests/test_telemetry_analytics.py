"""Tests for telemetry ingestion, analytics, and health scoring."""

import pytest

pytestmark = pytest.mark.asyncio


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


async def _register_api(client, token):
    resp = await client.post(
        "/apis",
        json={
            "name": "Cart Service",
            "base_url": "https://api.example.com",
            "path": "/v1/cart",
            "method": "GET",
        },
        headers=auth_headers(token),
    )
    return resp.json()["id"]


async def test_ingest_telemetry_batch(client, admin_token):
    api_id = await _register_api(client, admin_token)

    logs = [
        {
            "api_id": api_id,
            "endpoint_path": "/v1/cart",
            "method": "GET",
            "status_code": 200,
            "latency_ms": 42.5,
        },
        {
            "api_id": api_id,
            "endpoint_path": "/v1/cart",
            "method": "GET",
            "status_code": 500,
            "latency_ms": 900.0,
        },
    ]
    resp = await client.post(
        "/telemetry/ingest", json={"logs": logs}, headers=auth_headers(admin_token)
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["accepted"] == 2
    assert body["rejected"] == 0


async def test_ingest_rejects_empty_batch(client, admin_token):
    resp = await client.post(
        "/telemetry/ingest", json={"logs": []}, headers=auth_headers(admin_token)
    )
    assert resp.status_code == 422


async def test_latency_analytics_after_ingest(client, admin_token):
    api_id = await _register_api(client, admin_token)
    logs = [
        {
            "api_id": api_id,
            "endpoint_path": "/v1/cart",
            "method": "GET",
            "status_code": 200,
            "latency_ms": lat,
        }
        for lat in [10, 20, 30, 40, 50]
    ]
    await client.post(
        "/telemetry/ingest", json={"logs": logs}, headers=auth_headers(admin_token)
    )

    resp = await client.get(
        "/analytics/latency",
        params={"api_id": api_id, "window": "24h"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200


async def test_latency_analytics_invalid_window(client, admin_token):
    api_id = await _register_api(client, admin_token)
    resp = await client.get(
        "/analytics/latency",
        params={"api_id": api_id, "window": "3y"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 400


async def test_error_analytics(client, admin_token):
    api_id = await _register_api(client, admin_token)
    logs = [
        {
            "api_id": api_id,
            "endpoint_path": "/v1/cart",
            "method": "GET",
            "status_code": 500,
            "latency_ms": 5,
        }
    ]
    await client.post(
        "/telemetry/ingest", json={"logs": logs}, headers=auth_headers(admin_token)
    )

    resp = await client.get(
        "/analytics/errors",
        params={"api_id": api_id, "window": "24h"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200


async def test_dashboard_summary(client, admin_token):
    resp = await client.get("/analytics/summary", headers=auth_headers(admin_token))
    assert resp.status_code == 200


async def test_health_for_all_apis(client, admin_token):
    await _register_api(client, admin_token)
    resp = await client.get("/health", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_apis"] >= 1


async def test_health_for_single_api(client, admin_token):
    api_id = await _register_api(client, admin_token)
    resp = await client.get(f"/health/{api_id}", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert resp.json()["status"] in ("healthy", "degraded", "critical")
