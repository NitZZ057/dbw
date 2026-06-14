"""Accident response schemas."""
from pydantic import BaseModel
class AccidentSchema(BaseModel):
    """Accident API representation."""
    accident_id: int
    source_id: str
    year: int
    month: int
    hour: int
    weekday: int
    category: int
    accident_type: int
    light_condition: int
    ist_rad: bool
    ist_pkw: bool
    ist_fuss: bool
    ist_krad: bool
    lon: float | None
    lat: float | None
    region_ags: str | None
    region_name: str | None

class AccidentCountResponse(BaseModel):
    """Filtered accident count."""
    count: int
    filters_applied: dict[str, object]
