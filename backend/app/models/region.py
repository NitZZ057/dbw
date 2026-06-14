"""Region model."""
from enum import Enum
from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class RegionLevel(str, Enum):
    """Administrative region level."""
    state = "state"
    district = "district"
    municipality = "municipality"

class Region(Base):
    """German administrative region."""
    __tablename__ = "regions"
    region_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ags: Mapped[str] = mapped_column(String(8), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[RegionLevel] = mapped_column(SAEnum(RegionLevel, name="region_level"), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("regions.region_id"), nullable=True)
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parent: Mapped["Region | None"] = relationship(remote_side=[region_id])
