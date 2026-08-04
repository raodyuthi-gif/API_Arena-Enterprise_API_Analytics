"""API Registry router - CRUD for API endpoints, versions, and tags."""

import uuid
from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.dependencies import CurrentUser, CurrentAnalyst, DbSession
from app.models.api_registry import APIEndpoint, APIVersion, APITag
from app.schemas.api_registry import (
    APIEndpointCreate,
    APIEndpointUpdate,
    APIEndpointResponse,
    APIEndpointListResponse,
    APITagCreate,
    APITagResponse,
    APIVersionCreate,
    APIVersionResponse,
)

router = APIRouter()


# ── Tags ─────────────────────────────────────────────────────────


@router.get("/tags", response_model=list[APITagResponse], summary="List all tags")
async def list_tags(db: DbSession, _: CurrentUser):
    result = await db.execute(select(APITag).order_by(APITag.name))
    return result.scalars().all()


@router.post(
    "/tags",
    response_model=APITagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a tag",
)
async def create_tag(payload: APITagCreate, db: DbSession, _: CurrentAnalyst):
    tag = APITag(name=payload.name, color=payload.color)
    db.add(tag)
    await db.flush()
    return tag


# ── API Endpoints ─────────────────────────────────────────────────


@router.get("", response_model=APIEndpointListResponse, summary="List all APIs")
async def list_apis(
    db: DbSession,
    _: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
):
    stmt = select(APIEndpoint).options(
        selectinload(APIEndpoint.tags),
        selectinload(APIEndpoint.versions),
    )
    if search:
        stmt = stmt.where(APIEndpoint.name.ilike(f"%{search}%"))
    if status_filter:
        stmt = stmt.where(APIEndpoint.status == status_filter)

    total_result = await db.execute(select(func.count(APIEndpoint.id)))
    total = total_result.scalar_one()

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    apis = result.scalars().all()

    return APIEndpointListResponse(
        total=total, items=apis, page=page, page_size=page_size
    )


@router.post(
    "",
    response_model=APIEndpointResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new API",
)
async def create_api(payload: APIEndpointCreate, db: DbSession, _: CurrentAnalyst):
    api = APIEndpoint(
        name=payload.name,
        description=payload.description,
        base_url=payload.base_url,
        path=payload.path,
        method=payload.method,
        owner_team=payload.owner_team,
        owner_email=payload.owner_email,
        status=payload.status,
        sla_latency_p99_ms=payload.sla_latency_p99_ms,
        sla_uptime_percent=payload.sla_uptime_percent,
        sla_error_rate_max=payload.sla_error_rate_max,
        is_public=payload.is_public,
    )
    # Attach tags
    if payload.tag_ids:
        tags_result = await db.execute(
            select(APITag).where(APITag.id.in_(payload.tag_ids))
        )
        api.tags = tags_result.scalars().all()

    db.add(api)
    await db.flush()
    await db.refresh(api, ["tags", "versions"])
    return api


@router.get("/{api_id}", response_model=APIEndpointResponse, summary="Get API by ID")
async def get_api(api_id: uuid.UUID, db: DbSession, _: CurrentUser):
    result = await db.execute(
        select(APIEndpoint)
        .options(selectinload(APIEndpoint.tags), selectinload(APIEndpoint.versions))
        .where(APIEndpoint.id == api_id)
    )
    api = result.scalar_one_or_none()
    if not api:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API not found"
        )
    return api


@router.patch("/{api_id}", response_model=APIEndpointResponse, summary="Update API")
async def update_api(
    api_id: uuid.UUID, payload: APIEndpointUpdate, db: DbSession, _: CurrentAnalyst
):
    result = await db.execute(
        select(APIEndpoint)
        .options(selectinload(APIEndpoint.tags), selectinload(APIEndpoint.versions))
        .where(APIEndpoint.id == api_id)
    )
    api = result.scalar_one_or_none()
    if not api:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API not found"
        )

    for field, value in payload.model_dump(
        exclude_none=True, exclude={"tag_ids"}
    ).items():
        setattr(api, field, value)

    if payload.tag_ids is not None:
        tags_result = await db.execute(
            select(APITag).where(APITag.id.in_(payload.tag_ids))
        )
        api.tags = tags_result.scalars().all()

    await db.flush()
    return api


@router.delete(
    "/{api_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete API"
)
async def delete_api(api_id: uuid.UUID, db: DbSession, _: CurrentAnalyst):
    result = await db.execute(select(APIEndpoint).where(APIEndpoint.id == api_id))
    api = result.scalar_one_or_none()
    if not api:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API not found"
        )
    await db.delete(api)


# ── Versions ─────────────────────────────────────────────────────


@router.post(
    "/{api_id}/versions",
    response_model=APIVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_version(
    api_id: uuid.UUID, payload: APIVersionCreate, db: DbSession, _: CurrentAnalyst
):
    result = await db.execute(select(APIEndpoint).where(APIEndpoint.id == api_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API not found"
        )

    version = APIVersion(
        api_id=api_id, version=payload.version, changelog=payload.changelog
    )
    db.add(version)
    await db.flush()
    return version
