from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"

    database_url: str = ""

    qdrant_url: str = ""
    qdrant_api_key: str = ""

    redis_url: str = ""

    llm_provider: str = "local"
    llm_api_key: str = ""

    embedding_provider: str = "local"

    jwt_secret: str = ""


settings = Settings()
