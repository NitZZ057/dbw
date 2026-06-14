"""Region endpoints."""
from typing import Literal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.exceptions import RecordNotFoundError
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.region import RegionSchema
from app.services.region_service import list_regions
router = APIRouter()
@router.get("", response_model=PaginatedResponse[RegionSchema], summary="List regions", description="Lists administrative regions with filters.", responses={200: {"description": "Regions"}, 422: {"description": "Invalid query"}})
async def regions(level: Literal["state", "district", "municipality"] | None = None, name: str | None = None, ags: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(100, ge=1, le=500), session: AsyncSession = Depends(get_session)) -> PaginatedResponse[RegionSchema]:
    """List regions."""
    rows, total = await list_regions(session, level, name, ags, page, page_size)
    return PaginatedResponse(data=rows, total=total, page=page, page_size=page_size, sources=["Unfallatlas", "GENESIS Destatis"])
@router.get("/{ags}", response_model=APIResponse[RegionSchema], summary="Get region", description="Gets one region by AGS.", responses={200: {"description": "Region"}, 404: {"description": "Not found"}})
async def region(ags: str, session: AsyncSession = Depends(get_session)) -> APIResponse[RegionSchema]:
    """Get a region."""
    rows, _ = await list_regions(session, None, None, ags, 1, 1)
    if not rows:
        raise RecordNotFoundError(f"Region {ags} not found.")
    return APIResponse(data=rows[0], sources=["Unfallatlas", "GENESIS Destatis"])
