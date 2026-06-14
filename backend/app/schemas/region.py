"""Region response schemas."""
from pydantic import BaseModel
class RegionSchema(BaseModel):
    """Region API representation."""
    region_id: int
    ags: str
    name: str
    level: str
    population: int | None
    parent_ags: str | None = None
