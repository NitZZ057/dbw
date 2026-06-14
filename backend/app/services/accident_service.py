"""Accident query service."""
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Accident, Region

def apply_filters(stmt: Select, filters: dict[str, object]) -> Select:
    """Apply supported accident filters to a statement."""
    for key in ("year", "month", "weekday", "hour", "category", "ist_rad", "ist_fuss", "ist_krad"):
        if filters.get(key) is not None:
            stmt = stmt.where(getattr(Accident, key) == filters[key])
    if filters.get("state_ags"):
        stmt = stmt.where(Region.ags.startswith(str(filters["state_ags"])))
    if filters.get("district_ags"):
        stmt = stmt.where(Region.ags.startswith(str(filters["district_ags"])))
    return stmt

async def count_accidents(session: AsyncSession, filters: dict[str, object]) -> int:
    """Count accidents with a single SQL COUNT query."""
    stmt = apply_filters(select(func.count(Accident.accident_id)).outerjoin(Region), filters)
    return int((await session.execute(stmt)).scalar_one())

async def list_accidents(session: AsyncSession, filters: dict[str, object], page: int, page_size: int) -> tuple[list[dict[str, object]], int]:
    """Return joined, paginated accidents and total count."""
    total = await count_accidents(session, filters)
    stmt = select(
        Accident.accident_id, Accident.source_id, Accident.year, Accident.month, Accident.hour,
        Accident.weekday, Accident.category, Accident.accident_type, Accident.light_condition,
        Accident.ist_rad, Accident.ist_pkw, Accident.ist_fuss, Accident.ist_krad,
        Accident.lon, Accident.lat, Region.ags.label("region_ags"), Region.name.label("region_name"),
    ).outerjoin(Region).order_by(Accident.accident_id).offset((page - 1) * page_size).limit(page_size)
    rows = (await session.execute(apply_filters(stmt, filters))).mappings().all()
    return [dict(row) for row in rows], total
