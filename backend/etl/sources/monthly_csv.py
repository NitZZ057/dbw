"""GENESIS monthly accident CSV source."""
import re
from pathlib import Path
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Indicator, IndicatorValue, Region, RegionLevel
from etl.base import ETLSource
MONTHS = {"Januar": 1, "Februar": 2, "März": 3, "April": 4, "Mai": 5, "Juni": 6, "Juli": 7, "August": 8, "September": 9, "Oktober": 10, "November": 11, "Dezember": 12}
class MonthlyCSV(ETLSource):
    """Load monthly Germany-wide accident indicators."""
    source_name = "GENESIS monthly accidents"
    source_url = "https://www-genesis.destatis.de/"
    def __init__(self, data_dir: str) -> None: self.path = Path(data_dir) / "accidents_with_persons_per_month.csv"
    async def extract(self) -> pd.DataFrame:
        """Read monthly wide-format CSV."""
        if not self.path.exists(): raise FileNotFoundError(f"Missing expected file: {self.path.name}")
        self.checksum = self.file_checksum(str(self.path))
        with self.path.open(encoding="utf-8") as source:
            lines = [next(source).rstrip("\n").split(";") for _ in range(8)]
        years = lines[6][5:]
        months = lines[7][5:]
        current_year = ""
        periods: list[str] = []
        for year, month in zip(years, months):
            current_year = year or current_year
            periods.append(f"{month} {current_year}")
        names = ["accident_type", "location", "severity", "measure", "unit", *periods]
        return pd.read_csv(self.path, sep=";", encoding="utf-8", skiprows=8, header=None, names=names)
    async def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Forward-fill dimensions and melt month columns."""
        result = df.copy()
        result[["accident_type", "location", "severity"]] = result[["accident_type", "location", "severity"]].ffill()
        result = result[(result["measure"] == "Unfälle mit Personenschaden") & (result["unit"] == "Anzahl")]
        melted = result.melt(id_vars=["accident_type", "location", "severity", "measure", "unit"], var_name="period", value_name="value")
        melted = melted[~melted["value"].isin(["..."]) & melted["value"].notna()].copy()
        def period(value: str) -> tuple[int, int]:
            match = re.search(r"(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember).*?(\d{4})", str(value))
            return (MONTHS[match.group(1)], int(match.group(2))) if match else (0, 0)
        melted[["month", "year"]] = melted["period"].map(period).apply(pd.Series)
        melted = melted[melted["year"] > 0]
        melted["value"] = pd.to_numeric(melted["value"], errors="coerce")
        return melted.dropna(subset=["value"])
    async def load(self, df: pd.DataFrame, session: AsyncSession, run_id: int) -> int:
        """Store one annualized indicator per dimension combination."""
        region = (await session.execute(select(Region).where(Region.ags == "DG"))).scalar_one_or_none()
        if not region:
            region = Region(ags="DG", name="Deutschland", level=RegionLevel.state); session.add(region); await session.flush()
        count = 0
        for dimensions, group in df.groupby(["accident_type", "location", "severity"]):
            code = "MONAT_" + str(abs(hash(dimensions)))[:12]
            indicator = (await session.execute(select(Indicator).where(Indicator.code == code))).scalar_one_or_none()
            if not indicator:
                indicator = Indicator(code=code, name=" / ".join(map(str, dimensions)), unit="Anzahl", source_system="GENESIS Destatis"); session.add(indicator); await session.flush()
            for year, annual in group.groupby("year")["value"].sum().items():
                value = await session.get(IndicatorValue, (region.region_id, indicator.indicator_id, int(year)))
                if value: value.value = float(annual)
                else: session.add(IndicatorValue(region_id=region.region_id, indicator_id=indicator.indicator_id, year=int(year), value=float(annual)))
                count += 1
        return count
