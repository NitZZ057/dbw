"""Temporal coverage endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import GERMAN_STATE_AGS
from app.database import get_session
from app.exceptions import RecordNotFoundError
from app.models import Accident, Region
from app.schemas.common import APIResponse
router = APIRouter()
@router.get("/earliest", response_model=APIResponse[dict[str, object]], summary="Earliest accident year", description="Returns earliest available accident year.", responses={200: {"description": "Earliest year"}, 404: {"description": "No data"}})
async def earliest(state_ags: str | None = Query(None, pattern=r"^\d{2}$"), session: AsyncSession = Depends(get_session)) -> APIResponse[dict[str, object]]:
    """Return earliest year for Germany or a state."""
    stmt = select(func.min(Accident.year)).join(Region)
    if state_ags:
        stmt = stmt.where(Region.ags.startswith(state_ags))
    value = (await session.execute(stmt)).scalar_one()
    if value is None:
        raise RecordNotFoundError("No accidents found matching the given filters.")
    return APIResponse(data={"earliest_year": value, "scope": GERMAN_STATE_AGS.get(state_ags, "Germany"), "state_ags": state_ags}, sources=["Unfallatlas"])
@router.get("/coverage", response_model=APIResponse[list[dict[str, object]]], summary="State year coverage", description="Returns temporal coverage by state.", responses={200: {"description": "Coverage"}, 404: {"description": "No data"}})
async def coverage(session: AsyncSession = Depends(get_session)) -> APIResponse[list[dict[str, object]]]:
    """Return coverage for every represented state."""
    state = Region.__table__.alias("state")
    stmt = select(state.c.ags.label("state_ags"), state.c.name.label("state_name"), func.min(Accident.year).label("earliest_year"), func.max(Accident.year).label("latest_year"), func.count(Accident.accident_id).label("total_accidents")).join(Region, func.substr(Region.ags, 1, 2) == state.c.ags).join(Accident, Accident.region_id == Region.region_id).where(state.c.level == "state").group_by(state.c.ags, state.c.name).order_by(state.c.ags)
    return APIResponse(data=[dict(row) for row in (await session.execute(stmt)).mappings().all()], sources=["Unfallatlas"])
