"""Data provenance endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import ImportRun
from app.schemas.common import PaginatedResponse
router = APIRouter()
@router.get("/sources", response_model=PaginatedResponse[dict[str, object]], summary="List source imports", description="Lists ETL provenance records.", responses={200: {"description": "Import runs"}, 422: {"description": "Invalid pagination"}})
async def sources(page: int = Query(1, ge=1), page_size: int = Query(100, ge=1, le=500), session: AsyncSession = Depends(get_session)) -> PaginatedResponse[dict[str, object]]:
    """List import runs."""
    total = int((await session.execute(select(func.count(ImportRun.run_id)))).scalar_one())
    stmt = select(ImportRun.run_id, ImportRun.source_name, ImportRun.source_url, ImportRun.license, ImportRun.retrieved_at, ImportRun.record_count, ImportRun.checksum, ImportRun.status).order_by(ImportRun.run_id.desc()).offset((page - 1) * page_size).limit(page_size)
    return PaginatedResponse(data=[dict(r) for r in (await session.execute(stmt)).mappings().all()], total=total, page=page, page_size=page_size, sources=["UnfallAtlas ETL"])
