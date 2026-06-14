"""Regional accident-rate CSV source."""
from pathlib import Path
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Indicator, IndicatorValue, Region, RegionLevel
from etl.base import ETLSource
from etl.transformers.ags import normalize
class RatesCSV(ETLSource):
    """Load district accident rates."""
    source_name = "Regionalstatistik accident rates"
    source_url = "https://www.regionalstatistik.de/"
    def __init__(self, data_dir: str) -> None: self.path = Path(data_dir) / "accident_per_10000_per_city.csv"
    async def extract(self) -> pd.DataFrame:
        """Read the rates CSV."""
        if not self.path.exists(): raise FileNotFoundError(f"Missing expected file: {self.path.name}")
        self.checksum = self.file_checksum(str(self.path))
        return pd.read_csv(self.path, sep=";", encoding="latin-1", skiprows=2)
    async def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize AGS and values."""
        result = df.rename(columns=lambda c: c.strip().lower()).copy()
        result["schluessel"] = result["schluessel"].map(lambda v: normalize(v, 5))
        result["wert"] = result["wert"].astype(str).str.replace(",", ".", regex=False).astype(float)
        return result
    async def load(self, df: pd.DataFrame, session: AsyncSession, run_id: int) -> int:
        """Upsert district rate indicator values."""
        indicator = (await session.execute(select(Indicator).where(Indicator.code == "UNFALL_10000_EW"))).scalar_one_or_none()
        if not indicator:
            indicator = Indicator(code="UNFALL_10000_EW", name="Straßenverkehrsunfälle je 10.000 EW", unit="per 10,000 inhabitants", source_system="Regionalstatistik"); session.add(indicator); await session.flush()
        count = 0
        for row in df.to_dict("records"):
            region = (await session.execute(select(Region).where(Region.ags == row["schluessel"]))).scalar_one_or_none()
            if not region:
                region = Region(ags=row["schluessel"], name=row["regionaleinheit"], level=RegionLevel.district); session.add(region); await session.flush()
            value = await session.get(IndicatorValue, (region.region_id, indicator.indicator_id, 0))
            if value: value.value = row["wert"]
            else: session.add(IndicatorValue(region_id=region.region_id, indicator_id=indicator.indicator_id, year=0, value=row["wert"]))
            count += 1
        return count
