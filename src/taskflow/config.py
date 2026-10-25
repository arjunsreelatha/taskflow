"""Application settings, loaded from environment variables prefixed TASKFLOW_."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TASKFLOW_", env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://taskflow:taskflow@localhost:5432/taskflow"
    default_max_attempts: int = 3
    default_timeout_seconds: int = 300


@lru_cache
def get_settings() -> Settings:
    return Settings()