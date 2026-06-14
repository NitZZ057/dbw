"""Command-line ETL runner."""
import argparse
import asyncio
import logging
import time
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from etl.sources.genesis_api import GenesisPopulation
from etl.sources.monthly_csv import MonthlyCSV
from etl.sources.rates_csv import RatesCSV
from etl.sources.unfallatlas_csv import UnfallatlasCSV
logger = logging.getLogger(__name__)
async def run(source: str, reset: bool) -> int:
    """Run selected ETL sources and return process status."""
    settings = get_settings()
    logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    if reset:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all); await connection.run_sync(Base.metadata.create_all)
    sources = {"unfallatlas": UnfallatlasCSV(settings.data_dir), "rates": RatesCSV(settings.data_dir), "monthly": MonthlyCSV(settings.data_dir), "genesis": GenesisPopulation(settings.data_dir)}
    selected = list(sources.values()) if source == "all" else [sources[source]]
    failed = False
    try:
        async with SessionLocal() as session:
            for item in selected:
                started = time.monotonic()
                try:
                    result = await item.run(session); logger.info("%s: %s records, %.2fs, %s", item.source_name, result.record_count, time.monotonic() - started, result.status)
                except Exception:
                    failed = True; logger.exception("%s failed after %.2fs", item.source_name, time.monotonic() - started)
    finally:
        await engine.dispose()
    return 1 if failed else 0
def main() -> None:
    """Parse arguments and execute ETL."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["all", "unfallatlas", "rates", "monthly", "genesis"], default="all")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.source, args.reset)))
if __name__ == "__main__":
    main()
