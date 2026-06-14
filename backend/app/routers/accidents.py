"""Accident endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.schemas.accident import AccidentCountResponse, AccidentSchema
from app.schemas.common import APIResponse, PaginatedResponse
from app.services.accident_service import count_accidents, list_accidents
router = APIRouter()

def filters(state_ags: str | None, district_ags: str | None, year: int | None, month: int | None, weekday: int | None, hour: int | None, category: int | None, ist_rad: bool | None, ist_fuss: bool | None, ist_krad: bool | None) -> dict[str, object]:
    """Return non-null accident filters."""
    return {k: v for k, v in locals().items() if v is not None}

@router.get("/count", response_model=APIResponse[AccidentCountResponse], summary="Count accidents", description="Counts accidents matching supplied filters.", responses={200: {"description": "Count"}, 422: {"description": "Invalid filter"}})
async def count(state_ags: str | None = Query(None, pattern=r"^\d{2}$"), district_ags: str | None = Query(None, pattern=r"^\d{5}$"), year: int | None = Query(None, ge=2016, le=2030), month: int | None = Query(None, ge=1, le=12), weekday: int | None = Query(None, ge=1, le=7), hour: int | None = Query(None, ge=0, le=23), category: int | None = Query(None, ge=1, le=3), ist_rad: bool | None = None, ist_fuss: bool | None = None, ist_krad: bool | None = None, session: AsyncSession = Depends(get_session)) -> APIResponse[AccidentCountResponse]:
    """Count filtered accidents."""
    applied = filters(state_ags, district_ags, year, month, weekday, hour, category, ist_rad, ist_fuss, ist_krad)
    return APIResponse(data=AccidentCountResponse(count=await count_accidents(session, applied), filters_applied=applied), sources=["Unfallatlas"])

@router.get("", response_model=PaginatedResponse[AccidentSchema], summary="List accidents", description="Lists point-level accidents matching supplied filters.", responses={200: {"description": "Accidents"}, 422: {"description": "Invalid filter"}})
async def accidents(state_ags: str | None = Query(None, pattern=r"^\d{2}$"), district_ags: str | None = Query(None, pattern=r"^\d{5}$"), year: int | None = Query(None, ge=2016, le=2030), month: int | None = Query(None, ge=1, le=12), weekday: int | None = Query(None, ge=1, le=7), hour: int | None = Query(None, ge=0, le=23), category: int | None = Query(None, ge=1, le=3), ist_rad: bool | None = None, ist_fuss: bool | None = None, ist_krad: bool | None = None, page: int = Query(1, ge=1), page_size: int = Query(100, ge=1, le=500), session: AsyncSession = Depends(get_session)) -> PaginatedResponse[AccidentSchema]:
    """List filtered accidents."""
    rows, total = await list_accidents(session, filters(state_ags, district_ags, year, month, weekday, hour, category, ist_rad, ist_fuss, ist_krad), page, page_size)
    return PaginatedResponse(data=rows, total=total, page=page, page_size=page_size, sources=["Unfallatlas"])
