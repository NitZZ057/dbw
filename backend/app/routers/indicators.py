"""Indicator endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Indicator, IndicatorValue, Region
from app.schemas.common import PaginatedResponse
router = APIRouter()
@router.get("", response_model=PaginatedResponse[dict[str, object]], summary="List indicators", description="Lists indicator metadata.", responses={200: {"description": "Indicators"}, 422: {"description": "Invalid pagination"}})
async def indicators(page: int = Query(1, ge=1), page_size: int = Query(100, ge=1, le=500), session: AsyncSession = Depends(get_session)) -> PaginatedResponse[dict[str, object]]:
    """List indicator metadata."""
    total = int((await session.execute(select(func.count(Indicator.indicator_id)))).scalar_one())
    stmt = select(Indicator.code, Indicator.name, Indicator.unit, Indicator.source_system).order_by(Indicator.code).offset((page - 1) * page_size).limit(page_size)
    return PaginatedResponse(data=[dict(r) for r in (await session.execute(stmt)).mappings().all()], total=total, page=page, page_size=page_size, sources=["Regionalstatistik", "GENESIS Destatis"])
@router.get("/values", response_model=PaginatedResponse[dict[str, object]], summary="List indicator values", description="Lists indicator values joined to regions.", responses={200: {"description": "Values"}, 422: {"description": "Invalid filter"}})
async def values(code: str, ags: str | None = None, year: int | None = None, page: int = Query(1, ge=1), page_size: int = Query(100, ge=1, le=500), session: AsyncSession = Depends(get_session)) -> PaginatedResponse[dict[str, object]]:
    """List filtered indicator values."""
    conditions = [Indicator.code == code]
    if ags: conditions.append(Region.ags == ags)
    if year is not None: conditions.append(IndicatorValue.year == year)
    base = select(Indicator.code, Region.ags, Region.name.label("region_name"), IndicatorValue.year, IndicatorValue.value).join(IndicatorValue).join(Region).where(*conditions)
    rows = (await session.execute(base.offset((page - 1) * page_size).limit(page_size))).mappings().all()
    total = int((await session.execute(select(func.count()).select_from(base.subquery()))).scalar_one())
    return PaginatedResponse(data=[dict(r) for r in rows], total=total, page=page, page_size=page_size, sources=["Regionalstatistik", "GENESIS Destatis"])
