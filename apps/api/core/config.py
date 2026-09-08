from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AURA API"
    app_version: str = "0.1.0"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "aura"
    postgres_user: str = "aura"
    postgres_password: str = "aura_dev_password"

    redis_host: str = "localhost"
    redis_port: int = 6379

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()