"""Application configuration from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load settings from .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Elasticsearch (use URL + API key, or Cloud ID + API key)
    elasticsearch_url: str = ""
    elasticsearch_cloud_id: str = ""
    elasticsearch_api_key: str = ""

    # Elastic Agent Builder (Phase 5)
    kibana_url: str = ""
    kibana_api_key: str = ""
    agent_id: str = "context-engine-agent"

    # Spec Generation LLM (Phase 6) - optional; fallback to Kibana converse
    spec_inference_id: str = ""

    # Auth
    jwt_secret_key: str = "change-this-to-a-random-64-char-string"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440

    # Backend
    backend_cors_origins: str = "http://localhost:3000,http://localhost:5173"
    api_v1_prefix: str = "/api/v1"


def get_settings() -> Settings:
    """Return application settings singleton."""
    return Settings()
