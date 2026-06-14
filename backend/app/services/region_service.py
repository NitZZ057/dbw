"""Region query service."""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Region

async def list_regions(session: AsyncSession, level: str | None, name: str | None, ags: str | None, page: int, page_size: int) -> tuple[list[dict[str, object]], int]:
    """Return filtered regions with their parent AGS."""
    parent = Region.__table__.alias("parent")
    conditions = []
    if level:
        conditions.append(Region.level == level)
    if name:
        conditions.append(Region.name.ilike(f"%{name}%"))
    if ags:
        conditions.append(Region.ags == ags)
    total = int((await session.execute(select(func.count(Region.region_id)).where(*conditions))).scalar_one())
    stmt = select(Region.region_id, Region.ags, Region.name, Region.level, Region.population, parent.c.ags.label("parent_ags")).outerjoin(parent, Region.parent_id == parent.c.region_id).where(*conditions).order_by(Region.ags).offset((page - 1) * page_size).limit(page_size)
    rows = (await session.execute(stmt)).mappings().all()
    return [{**dict(row), "level": row["level"].value if hasattr(row["level"], "value") else row["level"]} for row in rows], total
