"""Ingest service configuration from environment."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class IngestSettings(BaseSettings):
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

    # Qdrant
    QDRANT_HOST: str = "phx-qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "phx_chunks"

    # Ollama
    OLLAMA_HOST: str = "phx-ollama"
    OLLAMA_PORT: int = 11434
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    EMBEDDING_DIM: int = 768

    # Ingest
    TENANT_ID: str = "default"
    INGEST_DATA_ROOT: str = "/customer_data"
    SOURCES_CONFIG_PATH: str = "/app/config/sources.yaml"
    INGEST_SCHEDULE_SECONDS: int = 3600
    LOG_LEVEL: str = "INFO"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def ollama_base_url(self) -> str:
        return f"http://{self.OLLAMA_HOST}:{self.OLLAMA_PORT}"


settings = IngestSettings()
