"""Indicator schemas."""
from pydantic import BaseModel
class IndicatorSchema(BaseModel):
    """Indicator metadata response."""
    code: str
    name: str
    unit: str
    source_system: str
class IndicatorValueSchema(BaseModel):
    """Indicator value response."""
    code: str
    ags: str
    region_name: str
    year: int
    value: float
