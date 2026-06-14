"""Environment-driven application configuration."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

GERMAN_STATE_AGS: dict[str, str] = {
    "01": "Schleswig-Holstein", "02": "Hamburg", "03": "Niedersachsen", "04": "Bremen",
    "05": "Nordrhein-Westfalen", "06": "Hessen", "07": "Rheinland-Pfalz",
    "08": "Baden-Württemberg", "09": "Bayern", "10": "Saarland", "11": "Berlin",
    "12": "Brandenburg", "13": "Mecklenburg-Vorpommern", "14": "Sachsen",
    "15": "Sachsen-Anhalt", "16": "Thüringen",
}
LICENSE = "Datenlizenz Deutschland – Namensnennung – Version 2.0"

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    database_url: str = "postgresql+asyncpg://unfallatlas:unfallatlas@db:5432/unfallatlas"
    data_dir: str = "/app/data"
    log_level: str = "INFO"
    api_cache_ttl: int = 300
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
