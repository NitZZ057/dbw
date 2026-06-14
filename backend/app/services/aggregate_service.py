"""Database-side aggregate queries."""
import logging
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Accident, Indicator, IndicatorValue, Region
logger = logging.getLogger(__name__)

async def accident_aggregates(session: AsyncSession, level: str, year: int | None, category: int | None) -> list[dict[str, object]]:
    """Aggregate accidents by state or district using SQL GROUP BY."""
    prefix_length = 2 if level == "state" else 5
    target = Region.__table__.alias("target")
    stmt = select(
        target.c.ags, target.c.name.label("region_name"), target.c.level,
        func.count(Accident.accident_id).label("accident_count"),
        func.sum(case((Accident.category == 1, 1), else_=0)).label("fatal_count"),
        func.sum(case((Accident.category == 2, 1), else_=0)).label("serious_count"),
        func.sum(case((Accident.category == 3, 1), else_=0)).label("light_count"),
    ).join(Region, Accident.region_id == Region.region_id).join(target, func.substr(Region.ags, 1, prefix_length) == target.c.ags).where(target.c.level == level)
    if year is not None:
        stmt = stmt.where(Accident.year == year)
    if category is not None:
        stmt = stmt.where(Accident.category == category)
    stmt = stmt.group_by(target.c.ags, target.c.name, target.c.level).order_by(func.count(Accident.accident_id).desc())
    rows = (await session.execute(stmt)).mappings().all()
    return [{**dict(row), "level": level, "year": year} for row in rows]

async def accident_rates(session: AsyncSession, level: str, year: int, top_n: int) -> list[dict[str, object]]:
    """Calculate ranked accident rates using accident and population sources."""
    prefix_length = 2 if level == "state" else 5
    target = Region.__table__.alias("target")
    count = func.count(Accident.accident_id)
    stmt = select(target.c.ags, target.c.name.label("region_name"), target.c.population, count.label("accident_count")).join(Region, Accident.region_id == Region.region_id).join(target, func.substr(Region.ags, 1, prefix_length) == target.c.ags).where(target.c.level == level, target.c.population.is_not(None), Accident.year == year).group_by(target.c.ags, target.c.name, target.c.population).order_by((count * 100000.0 / target.c.population).desc()).limit(top_n)
    rows = (await session.execute(stmt)).mappings().all()
    return [{**dict(row), "rate_per_100k": round(row["accident_count"] * 100000 / row["population"], 2), "rank": rank} for rank, row in enumerate(rows, 1)]

async def rate_comparison(session: AsyncSession, year: int, top_n: int) -> list[dict[str, object]]:
    """Compare calculated rates with Regionalstatistik published rates."""
    accident_region = Region.__table__.alias("accident_region")
    district = Region.__table__.alias("district")
    published_region = Region.__table__.alias("published_region")
    accident_count = func.count(Accident.accident_id)
    calculated = (
        select(
            district.c.ags.label("ags"),
            district.c.name.label("region_name"),
            accident_count.label("accident_count"),
            district.c.population.label("population"),
            (accident_count * 10000.0 / district.c.population).label("calculated_rate"),
        )
        .join(accident_region, Accident.region_id == accident_region.c.region_id)
        .join(district, func.substr(accident_region.c.ags, 1, 5) == district.c.ags)
        .where(Accident.year == year, district.c.level == "district", district.c.population.is_not(None))
        .group_by(district.c.ags, district.c.name, district.c.population)
        .subquery()
    )
    stmt = (
        select(
            calculated.c.ags,
            calculated.c.region_name,
            calculated.c.accident_count,
            calculated.c.population,
            calculated.c.calculated_rate,
            IndicatorValue.value.label("published_rate"),
        )
        .join(published_region, published_region.c.ags == calculated.c.ags)
        .join(IndicatorValue, IndicatorValue.region_id == published_region.c.region_id)
        .join(Indicator, Indicator.indicator_id == IndicatorValue.indicator_id)
        .where(Indicator.code == "UNFALL_10000_EW", IndicatorValue.year == 0)
        .order_by(func.abs(calculated.c.calculated_rate - IndicatorValue.value).desc())
        .limit(top_n)
    )
    rows = (await session.execute(stmt)).mappings().all()
    return [
        {
            **dict(row),
            "calculated_rate": round(float(row["calculated_rate"]), 2),
            "published_rate": round(float(row["published_rate"]), 2),
            "difference": round(float(row["calculated_rate"] - row["published_rate"]), 2),
        }
        for row in rows
    ]
