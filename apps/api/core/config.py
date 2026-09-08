from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    
    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    @property
    def database_url(self) -> str:
        # Constructs the PostgreSQL connection string automatically
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # Tells Pydantic to read from the local .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Instantiate it once to use across the whole app
settings = Settings()