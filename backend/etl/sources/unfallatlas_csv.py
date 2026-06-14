"""Unfallatlas point CSV source."""
from pathlib import Path
import pandas as pd
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import GERMAN_STATE_AGS
from app.models import Accident, Region, RegionLevel
from etl.base import ETLSource
from etl.transformers.ags import district_ags, municipality_ags, normalize

class UnfallatlasCSV(ETLSource):
    """Load point-level accident CSV files."""
    source_name = "Unfallatlas"
    source_url = "https://unfallatlas.statistikportal.de/"
    filenames = ("accident_per_location_2023.csv", "accident_per_location_2021_in_Schleswig-Holstein.csv")
    def __init__(self, data_dir: str) -> None:
        self.data_dir = Path(data_dir)
    async def extract(self) -> pd.DataFrame:
        """Read both format variants."""
        missing = [name for name in self.filenames if not (self.data_dir / name).exists()]
        if missing:
            raise FileNotFoundError(f"Missing expected files: {', '.join(missing)}")
        frames = [
            pd.read_csv(self.data_dir / self.filenames[0], sep=";", decimal=",", encoding="utf-8-sig", dtype={"ULAND": str, "UREGBEZ": str, "UKREIS": str, "UGEMEINDE": str}, low_memory=False),
            pd.read_csv(self.data_dir / self.filenames[1], sep=";", decimal=".", encoding="utf-8", dtype={"ULAND": str, "UREGBEZ": str, "UKREIS": str, "UGEMEINDE": str}, low_memory=False),
        ]
        self.checksum = self.file_checksum(str(self.data_dir / self.filenames[0]))
        return pd.concat(frames, ignore_index=True)
    async def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map source columns and derive AGS keys."""
        result = df.drop_duplicates("UIDENTSTLAE").copy()
        result["municipality_ags"] = result.apply(lambda r: municipality_ags(r.ULAND, r.UREGBEZ, r.UKREIS, r.UGEMEINDE), axis=1)
        result["district_ags"] = result.apply(lambda r: district_ags(r.ULAND, r.UREGBEZ, r.UKREIS), axis=1)
        result["state_ags"] = result["ULAND"].map(lambda v: normalize(v, 2))
        for column in ("IstRad", "IstPKW", "IstFuss", "IstKrad", "IstGkfz"):
            result[column] = result[column].fillna(0).astype(int).astype(bool)
        return result
    async def load(self, df: pd.DataFrame, session: AsyncSession, run_id: int) -> int:
        """Upsert regions and insert new accidents in batches."""
        for ags in sorted(df["state_ags"].unique()):
            await self._region(session, ags, GERMAN_STATE_AGS.get(ags, ags), RegionLevel.state)
        for ags in sorted(df["district_ags"].unique()):
            await self._region(session, ags, ags, RegionLevel.district)
        for ags in sorted(df["municipality_ags"].unique()):
            await self._region(session, ags, ags, RegionLevel.municipality)
        await session.flush()
        region_ids = dict((await session.execute(select(Region.ags, Region.region_id))).all())
        existing = set((await session.execute(select(Accident.source_id))).scalars())
        records = []
        for row in df.to_dict("records"):
            if str(row["UIDENTSTLAE"]) in existing: continue
            records.append({"source_id": str(row["UIDENTSTLAE"]), "year": int(row["UJAHR"]), "month": int(row["UMONAT"]), "hour": int(row["USTUNDE"]), "weekday": int(row["UWOCHENTAG"]), "category": int(row["UKATEGORIE"]), "accident_type": int(row["UART"]), "light_condition": int(row["ULICHTVERH"]), "ist_rad": row["IstRad"], "ist_pkw": row["IstPKW"], "ist_fuss": row["IstFuss"], "ist_krad": row["IstKrad"], "ist_gkfz": row["IstGkfz"], "lon": None if pd.isna(row["XGCSWGS84"]) else float(row["XGCSWGS84"]), "lat": None if pd.isna(row["YGCSWGS84"]) else float(row["YGCSWGS84"]), "region_id": region_ids.get(row["municipality_ags"], region_ids.get(row["district_ags"])), "import_run_id": run_id})
        for start in range(0, len(records), 5000):
            await session.execute(insert(Accident), records[start:start + 5000])
        return len(records)
    @staticmethod
    async def _region(session: AsyncSession, ags: str, name: str, level: RegionLevel) -> None:
        if not (await session.execute(select(Region.region_id).where(Region.ags == ags))).scalar_one_or_none():
            session.add(Region(ags=ags, name=name, level=level))
