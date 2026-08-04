"""Tests for authentication: login, refresh, API keys."""

import pytest

from app.services.auth_service import AuthService

pytestmark = pytest.mark.asyncio


def test_password_hashing_round_trip():
    password = "StrongPassword123!"
    hashed = AuthService.hash_password(password)

    assert hashed != password
    assert AuthService.verify_password(password, hashed) is True
    assert AuthService.verify_password("wrong-password", hashed) is False


async def test_login_success(client, admin_user):
    resp = await client.post(
        "/auth/login", json={"email": "admin@test.com", "password": "password123"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password(client, admin_user):
    resp = await client.post(
        "/auth/login", json={"email": "admin@test.com", "password": "wrong-password"}
    )
    assert resp.status_code == 401


async def test_login_unknown_user(client):
    resp = await client.post(
        "/auth/login", json={"email": "nobody@test.com", "password": "whatever"}
    )
    assert resp.status_code == 401


async def test_refresh_token(client, admin_user):
    login_resp = await client.post(
        "/auth/login", json={"email": "admin@test.com", "password": "password123"}
    )
    refresh_token = login_resp.json()["refresh_token"]

    resp = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_refresh_with_access_token_rejected(client, admin_token):
    resp = await client.post("/auth/refresh", json={"refresh_token": admin_token})
    assert resp.status_code == 401


async def test_create_api_key(client, admin_token):
    resp = await client.post(
        "/auth/api-keys",
        json={"name": "ci-key", "expires_in_days": 30},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "ci-key"
    assert body["key"].startswith("eaa_")


async def test_protected_route_requires_token(client):
    resp = await client.get("/users/me")
    assert resp.status_code in (401, 403)
