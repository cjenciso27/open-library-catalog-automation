from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
ENV_PREFIX = "LIBRARY_"
LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        env_prefix=ENV_PREFIX,
        extra="ignore",
    )

    api_base_url: str = "https://openlibrary.org"
    user_agent: str = "OpenLibraryCatalogAutomation/1.0 (student project)"
    request_timeout: float = Field(default=15.0, gt=0)
    max_retries: int = Field(default=3, ge=0, le=10)
    backoff_factor: float = Field(default=0.5, ge=0)
    max_concurrency: int = Field(default=5, ge=1, le=20)
    page_size: int = Field(default=20, ge=1, le=100)
    db_path: Path = BASE_DIR / "data" / "library.db"
    cache_ttl_hours: float = Field(default=24, gt=0)
    output_dir: Path = BASE_DIR / "data" / "outputs"
    log_dir: Path = BASE_DIR / "logs"
    log_level: str = "INFO"

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        level = value.strip().upper()
        if level not in LOG_LEVELS:
            raise ValueError(f"log_level must be one of {sorted(LOG_LEVELS)}")
        return level

    @field_validator("api_base_url")
    @classmethod
    def validate_base_url(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("api_base_url must start with http:// or https://")
        return value.rstrip("/")

    @field_validator("db_path", "output_dir", "log_dir")
    @classmethod
    def resolve_path(cls, value: Path) -> Path:
        return value if value.is_absolute() else BASE_DIR / value

    @staticmethod
    def env_key(field_name: str) -> str:
        return f"{ENV_PREFIX}{field_name.upper()}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reload_settings() -> Settings:
    get_settings.cache_clear()
    return get_settings()
