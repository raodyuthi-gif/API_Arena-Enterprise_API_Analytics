"""Tests for the API Registry module."""

import pytest

pytestmark = pytest.mark.asyncio


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


async def test_create_and_list_api(client, admin_token):
    resp = await client.post(
        "/apis",
        json={
            "name": "Orders Service",
            "base_url": "https://api.example.com",
            "path": "/v1/orders",
            "method": "GET",
        },
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 201
    created = resp.json()
    assert created["name"] == "Orders Service"
    assert created["status"] == "active"

    list_resp = await client.get("/apis", headers=auth_headers(admin_token))
    assert list_resp.status_code == 200
    body = list_resp.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == created["id"]


async def test_get_api_not_found(client, admin_token):
    import uuid

    resp = await client.get(f"/apis/{uuid.uuid4()}", headers=auth_headers(admin_token))
    assert resp.status_code == 404


async def test_update_api_status(client, admin_token):
    create_resp = await client.post(
        "/apis",
        json={
            "name": "Payments API",
            "base_url": "https://api.example.com",
            "path": "/v1/pay",
            "method": "POST",
        },
        headers=auth_headers(admin_token),
    )
    api_id = create_resp.json()["id"]

    update_resp = await client.patch(
        f"/apis/{api_id}",
        json={"status": "deprecated"},
        headers=auth_headers(admin_token),
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "deprecated"


async def test_delete_api(client, admin_token):
    create_resp = await client.post(
        "/apis",
        json={
            "name": "Temp API",
            "base_url": "https://api.example.com",
            "path": "/v1/temp",
            "method": "GET",
        },
        headers=auth_headers(admin_token),
    )
    api_id = create_resp.json()["id"]

    delete_resp = await client.delete(
        f"/apis/{api_id}", headers=auth_headers(admin_token)
    )
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/apis/{api_id}", headers=auth_headers(admin_token))
    assert get_resp.status_code == 404


async def test_create_and_list_tags(client, admin_token):
    resp = await client.post(
        "/apis/tags",
        json={"name": "critical", "color": "#ff0000"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 201

    list_resp = await client.get("/apis/tags", headers=auth_headers(admin_token))
    assert list_resp.status_code == 200
    assert any(t["name"] == "critical" for t in list_resp.json())
