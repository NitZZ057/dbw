"""Shared response envelopes."""
from typing import Generic, TypeVar
from pydantic import BaseModel
from app.config import LICENSE
T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    """Scalar response with provenance."""
    data: T
    license: str = LICENSE
    sources: list[str]

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response with provenance."""
    data: list[T]
    total: int
    page: int
    page_size: int
    license: str = LICENSE
    sources: list[str]
