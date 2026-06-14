"""Shared API test fixtures."""
import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Accident, ImportRun, Region, RegionLevel

@pytest_asyncio.fixture(scope="session", autouse=True)
async def database() -> None:
    """Create a fixture database populated with representative records."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        run = ImportRun(source_name="fixture", source_url="test", license="test", record_count=10, checksum="fixture", status="success")
        state = Region(ags="14", name="Sachsen", level=RegionLevel.state, population=4_000_000)
        d1 = Region(ags="14521", name="District A", level=RegionLevel.district, population=100_000)
        d2 = Region(ags="14522", name="District B", level=RegionLevel.district, population=None)
        session.add_all([run, state, d1, d2]); await session.flush()
        session.add_all([Accident(source_id=f"A{i}", year=2021 if i < 3 else 2023, month=1, hour=12, weekday=2, category=(i % 3) + 1, accident_type=1, light_condition=1, ist_rad=False, ist_pkw=True, ist_fuss=i < 2, ist_krad=False, ist_gkfz=False, lon=13.0, lat=51.0, region_id=d1.region_id if i < 7 else d2.region_id, import_run_id=run.run_id) for i in range(10)])
        await session.commit()
    yield
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client(database: None) -> AsyncClient:
    """Return an in-process API client."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as value:
        yield value
