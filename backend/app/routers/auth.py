"""Authentication router - login, refresh, logout, API keys."""

from datetime import timedelta
from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.dependencies import DbSession, CurrentUser
from app.services.auth_service import AuthService
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    APIKeyCreate,
    APIKeyResponse,
)
from app.models.user import APIKey

router = APIRouter()


@router.post(
    "/login", response_model=TokenResponse, summary="Login with email and password"
)
async def login(payload: LoginRequest, db: DbSession):
    user = await AuthService.authenticate_user(payload.email, payload.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated"
        )

    access_token = AuthService.create_access_token(str(user.id), user.role)
    refresh_token = AuthService.create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
async def refresh_token(payload: RefreshRequest, db: DbSession):
    token_data = AuthService.decode_token(payload.refresh_token)
    if not token_data or token_data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    user_id = token_data.get("sub")
    from sqlalchemy import select
    from app.models.user import User

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    access_token = AuthService.create_access_token(str(user.id), user.role)
    new_refresh = AuthService.create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/api-keys", response_model=APIKeyResponse, summary="Create a new API key")
async def create_api_key(
    payload: APIKeyCreate, current_user: CurrentUser, db: DbSession
):
    from datetime import datetime, timezone

    raw_key, hashed_key = AuthService.generate_api_key()

    expires_at = None
    if payload.expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=payload.expires_in_days
        )

    api_key = APIKey(
        user_id=current_user.id,
        key_hash=hashed_key,
        name=payload.name,
        expires_at=expires_at,
    )
    db.add(api_key)
    await db.flush()

    return APIKeyResponse(
        id=str(api_key.id),
        name=api_key.name,
        key=raw_key,
        created_at=api_key.created_at.isoformat(),
        expires_at=expires_at.isoformat() if expires_at else None,
    )
