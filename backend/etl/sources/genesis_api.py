"""GENESIS district population source."""
import io
import logging
from pathlib import Path
import httpx
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential
from app.models import Indicator, IndicatorValue, Region
from etl.base import ETLSource
from etl.transformers.ags import normalize
logger = logging.getLogger(__name__)
BASE_URL = "https://genesis.destatis.de/genesisWS/rest/2020/data/tablefile"
class GenesisPopulation(ETLSource):
    """Fetch population by district, with an offline fallback."""
    source_name = "GENESIS population"
    source_url = BASE_URL
    def __init__(self, data_dir: str, year: int = 2023) -> None:
        self.year = year
        self.fallback = Path(__file__).parents[1] / "data" / "fallback_population.csv"
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4), reraise=True)
    async def _request(self) -> str:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(BASE_URL, params={"username": "GUEST", "password": "GUEST", "name": "12411-0015", "area": "all", "compress": "false", "transpose": "false", "startyear": self.year, "endyear": self.year, "format": "csv"})
            response.raise_for_status()
            return response.text
    async def extract(self) -> pd.DataFrame:
        """Fetch GENESIS or read fallback data."""
        try:
            text = await self._request()
            lines = text.splitlines()
            start = next(i for i, line in enumerate(lines) if "Kreiskennziffer" in line or "AGS" in line)
            return pd.read_csv(io.StringIO("\n".join(lines[start:])), sep=";")
        except Exception as exc:
            logger.warning("GENESIS unavailable; using fallback: %s", exc)
            return pd.read_csv(self.fallback)
    async def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize AGS and population columns."""
        result = df.copy()
        ags_col = next(c for c in result.columns if "AGS" in c or "Kreiskennziffer" in c)
        pop_col = next(c for c in result.columns if "population" in c.lower() or "insgesamt" in c.lower() or "Bevölkerung" in c)
        return pd.DataFrame({"ags": result[ags_col].map(lambda v: normalize(v, 5)), "population": pd.to_numeric(result[pop_col], errors="coerce")}).dropna()
    async def load(self, df: pd.DataFrame, session: AsyncSession, run_id: int) -> int:
        """Update region population and population indicators."""
        indicator = (await session.execute(select(Indicator).where(Indicator.code == "BEV_GESAMT"))).scalar_one_or_none()
        if not indicator:
            indicator = Indicator(code="BEV_GESAMT", name="Bevölkerung insgesamt", unit="Personen", source_system="GENESIS Destatis"); session.add(indicator); await session.flush()
        count = 0
        for row in df.to_dict("records"):
            region = (await session.execute(select(Region).where(Region.ags == row["ags"]))).scalar_one_or_none()
            if not region: continue
            region.population = int(row["population"])
            value = await session.get(IndicatorValue, (region.region_id, indicator.indicator_id, self.year))
            if value: value.value = float(row["population"])
            else: session.add(IndicatorValue(region_id=region.region_id, indicator_id=indicator.indicator_id, year=self.year, value=float(row["population"])))
            count += 1
        return count
