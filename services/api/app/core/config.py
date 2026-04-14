"""
Application configuration loaded from environment variables.
All secrets must be provided via environment — never hardcoded.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Postgres
    POSTGRES_HOST: str = "phx-postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "phx"
    POSTGRES_USER: str = "phx"
    POSTGRES_PASSWORD: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 8

    # Qdrant
    QDRANT_HOST: str = "phx-qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "phx_chunks"

    # Ollama
    OLLAMA_HOST: str = "phx-ollama"
    OLLAMA_PORT: int = 11434
    OLLAMA_LLM_MODEL: str = "llama3.2"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    EMBEDDING_DIM: int = 768

    # Application
    TENANT_ID: str = "default"
    LOG_LEVEL: str = "INFO"

    # CORS origins — restrict to internal addresses
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://phx-ui:80"]

    # RAG config (can be overridden by app.yaml)
    RAG_TOP_K: int = 8
    RAG_MIN_SCORE: float = 0.30
    RAG_STRICT_MODE: bool = True
    RAG_MAX_CONTEXT_TOKENS: int = 3000

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def ollama_base_url(self) -> str:
        return f"http://{self.OLLAMA_HOST}:{self.OLLAMA_PORT}"

    @property
    def qdrant_url(self) -> str:
        return f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"


settings = Settings()
