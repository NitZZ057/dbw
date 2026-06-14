"""Road accident model."""
from sqlalchemy import Boolean, Double, ForeignKey, Index, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Accident(Base):
    """Point-level road accident."""
    __tablename__ = "accidents"
    __table_args__ = (Index("ix_accidents_year_region", "year", "region_id"), Index("ix_accidents_year", "year"), Index("ix_accidents_region", "region_id"))
    accident_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    hour: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    weekday: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    category: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    accident_type: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    light_condition: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    ist_rad: Mapped[bool] = mapped_column(Boolean, default=False)
    ist_pkw: Mapped[bool] = mapped_column(Boolean, default=False)
    ist_fuss: Mapped[bool] = mapped_column(Boolean, default=False)
    ist_krad: Mapped[bool] = mapped_column(Boolean, default=False)
    ist_gkfz: Mapped[bool] = mapped_column(Boolean, default=False)
    lon: Mapped[float | None] = mapped_column(Double, nullable=True)
    lat: Mapped[float | None] = mapped_column(Double, nullable=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("regions.region_id"), nullable=True)
    import_run_id: Mapped[int] = mapped_column(ForeignKey("import_runs.run_id"), nullable=False)
