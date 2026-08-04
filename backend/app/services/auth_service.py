"""Authentication service - JWT creation/validation and password hashing."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User


class AuthService:
    @staticmethod
    def _normalize_password(password: str) -> bytes:
        return password.encode("utf-8")[:72]

    @staticmethod
    def hash_password(password: str) -> str:
        normalized_password = AuthService._normalize_password(password)
        return bcrypt.hashpw(normalized_password, bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        normalized_password = AuthService._normalize_password(plain)
        return bcrypt.checkpw(normalized_password, hashed.encode("utf-8"))

    @staticmethod
    def create_access_token(user_id: str, role: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload = {"sub": user_id, "role": role, "type": "access", "exp": expire}
        return jwt.encode(
            payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
        payload = {"sub": user_id, "type": "refresh", "exp": expire}
        return jwt.encode(
            payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def decode_token(token: str) -> dict | None:
        try:
            return jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
        except JWTError:
            return None

    @staticmethod
    async def authenticate_user(
        email: str, password: str, db: AsyncSession
    ) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def get_user_from_token(token: str, db: AsyncSession) -> User | None:
        payload = AuthService.decode_token(token)
        if not payload or payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    def generate_api_key() -> tuple[str, str]:
        """Generate a raw API key and its SHA-256 hash. Returns (raw_key, hashed_key)."""
        raw_key = f"eaa_{secrets.token_urlsafe(32)}"
        hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
        return raw_key, hashed_key
