"""Health endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
router = APIRouter()
@router.get("/health", summary="Health check", description="Checks API and database connectivity.", responses={200: {"description": "Healthy"}, 503: {"description": "Unavailable"}})
async def health(session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    """Return service health."""
    await session.execute(text("SELECT 1"))
    return {"status": "ok", "db": "connected", "version": "1.0.0"}
