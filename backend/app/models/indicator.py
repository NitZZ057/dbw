"""Indicator models."""
from sqlalchemy import Double, ForeignKey, PrimaryKeyConstraint, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Indicator(Base):
    """Indicator metadata."""
    __tablename__ = "indicators"
    indicator_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    unit: Mapped[str] = mapped_column(String(50))
    source_system: Mapped[str] = mapped_column(String(100))

class IndicatorValue(Base):
    """Indicator value for a region and year; year zero means unknown."""
    __tablename__ = "indicator_values"
    __table_args__ = (PrimaryKeyConstraint("region_id", "indicator_id", "year"),)
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.region_id"))
    indicator_id: Mapped[int] = mapped_column(ForeignKey("indicators.indicator_id"))
    year: Mapped[int] = mapped_column(SmallInteger)
    value: Mapped[float] = mapped_column(Double)
