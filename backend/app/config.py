# Environment configuration
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server (with defaults so they don’t break validation)
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "production"

    # Database
    DATABASE_URL: str
    REDIS_URL: str

    # API Keys
    VOYAGE_API_KEY: str
    ANTHROPIC_API_KEY: str

    # Slack Integration
    SLACK_CLIENT_ID: str = ""
    SLACK_CLIENT_SECRET: str = ""

    # JWT Authentication
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # File Upload
    UPLOAD_DIR: str = "./uploads"

    # Document Processing
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # Vector Search
    EMBEDDING_DIMENSION: int = 1024
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.3

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Singleton instance
settings = Settings()