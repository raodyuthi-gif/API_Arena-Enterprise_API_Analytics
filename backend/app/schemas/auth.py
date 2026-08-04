"""Pydantic schemas for authentication."""
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    refresh_token: str


class APIKeyCreate(BaseModel):
    name: str
    expires_in_days: int | None = None


class APIKeyResponse(BaseModel):
    id: str
    name: str
    key: str          # Only returned once at creation
    created_at: str
    expires_at: str | None


class APIKeyListItem(BaseModel):
    id: str
    name: str
    is_active: bool
    last_used_at: str | None
    expires_at: str | None
    created_at: str
