"""ETL source abstraction."""
from abc import ABC, abstractmethod
import hashlib
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import LICENSE
from app.models import ImportRun

class ETLSource(ABC):
    """Extract, transform, and load source contract."""
    source_name: str
    source_url: str
    license: str = LICENSE
    checksum: str = ""
    @abstractmethod
    async def extract(self) -> pd.DataFrame:
        """Extract source records."""
    @abstractmethod
    async def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize source records."""
    @abstractmethod
    async def load(self, df: pd.DataFrame, session: AsyncSession, run_id: int) -> int:
        """Load normalized records."""
    async def run(self, session: AsyncSession) -> ImportRun:
        """Run the source and persist provenance."""
        run = ImportRun(source_name=self.source_name, source_url=self.source_url, license=self.license, record_count=0, checksum=self.checksum, status="running")
        session.add(run)
        await session.flush()
        try:
            frame = await self.transform(await self.extract())
            run.checksum = self.checksum
            run.record_count = await self.load(frame, session, run.run_id)
            run.status = "success"
        except Exception as exc:
            run.status = "failed"
            run.error_message = str(exc)
            raise
        finally:
            await session.commit()
        return run
    @staticmethod
    def file_checksum(path: str) -> str:
        """Calculate a SHA-256 file checksum."""
        digest = hashlib.sha256()
        with open(path, "rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
