"""Users router - CRUD for users and roles."""
import uuid
from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import CurrentUser, CurrentAdmin, DbSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("/me", response_model=UserResponse, summary="Get current user profile")
async def get_me(current_user: CurrentUser):
    return current_user


@router.get("", response_model=UserListResponse, summary="List all users (Admin only)")
async def list_users(
    _: CurrentAdmin,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    offset = (page - 1) * page_size
    total_result = await db.execute(select(func.count(User.id)))
    total = total_result.scalar_one()

    result = await db.execute(select(User).offset(offset).limit(page_size))
    users = result.scalars().all()

    return UserListResponse(total=total, items=users, page=page, page_size=page_size)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create a new user (Admin only)")
async def create_user(payload: UserCreate, _: CurrentAdmin, db: DbSession):
    # Check uniqueness
    existing = await db.execute(select(User).where(
        (User.email == payload.email) | (User.username == payload.username)
    ))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or username already exists")

    user = User(
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=AuthService.hash_password(payload.password),
        role=payload.role,
        team_id=payload.team_id,
    )
    db.add(user)
    await db.flush()
    return user


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID (Admin only)")
async def get_user(user_id: uuid.UUID, _: CurrentAdmin, db: DbSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserResponse, summary="Update user (Admin only)")
async def update_user(user_id: uuid.UUID, payload: UserUpdate, _: CurrentAdmin, db: DbSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(user, field, value)

    await db.flush()
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user (Admin only)")
async def delete_user(user_id: uuid.UUID, _: CurrentAdmin, db: DbSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(user)
