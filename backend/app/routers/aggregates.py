"""Aggregate endpoints."""
from typing import Literal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.schemas.common import APIResponse
from app.services.aggregate_service import accident_aggregates, accident_rates, rate_comparison
router = APIRouter()
@router.get("/accidents", response_model=APIResponse[list[dict[str, object]]], summary="Aggregate accidents", description="Groups accident counts by region.", responses={200: {"description": "Aggregates"}, 422: {"description": "Invalid filter"}})
async def aggregates(level: Literal["state", "district"], year: int | None = Query(None, ge=2016, le=2030), category: int | None = Query(None, ge=1, le=3), session: AsyncSession = Depends(get_session)) -> APIResponse[list[dict[str, object]]]:
    """Return grouped accident counts."""
    return APIResponse(data=await accident_aggregates(session, level, year, category), sources=["Unfallatlas"])
@router.get("/rates", response_model=APIResponse[list[dict[str, object]]], summary="Rank accident rates", description="Ranks cross-source accident rates per 100,000 residents.", responses={200: {"description": "Rates"}, 422: {"description": "Invalid filter"}})
async def rates(year: int = Query(..., ge=2016, le=2030), level: Literal["state", "district"] = "district", top_n: int = Query(10, ge=1, le=100), session: AsyncSession = Depends(get_session)) -> APIResponse[list[dict[str, object]]]:
    """Return ranked accident rates."""
    return APIResponse(data=await accident_rates(session, level, year, top_n), sources=["Unfallatlas", "GENESIS Destatis"])

@router.get("/rate-comparison", response_model=APIResponse[list[dict[str, object]]], summary="Compare accident rates", description="Compares calculated accident rates with Regionalstatistik published rates.", responses={200: {"description": "Rate comparison"}, 422: {"description": "Invalid filter"}})
async def compare_rates(year: int = Query(2023, ge=2016, le=2030), top_n: int = Query(10, ge=1, le=100), session: AsyncSession = Depends(get_session)) -> APIResponse[list[dict[str, object]]]:
    """Return a three-source accident-rate comparison."""
    return APIResponse(data=await rate_comparison(session, year, top_n), sources=["Unfallatlas", "GENESIS Destatis", "Regionalstatistik"])
