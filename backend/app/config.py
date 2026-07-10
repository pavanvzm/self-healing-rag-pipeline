"""Application configuration managed via Pydantic Settings."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    app_name: str = "Self-Healing RAG Pipeline"
    debug: bool = False

    # Database (PostgreSQL)
    database_url: str = "postgresql+asyncpg://raguser:ragpass@localhost:5432/ragdb"
    database_url_sync: str = "postgresql+psycopg2://raguser:ragpass@localhost:5432/ragdb"

    # Vector DB (Qdrant)
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "documents"

    # Redis (for caching/queue)
    redis_url: str = "redis://localhost:6379/0"

    # LLM Provider (openai / anthropic / mock)
    llm_provider: str = "mock"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-haiku-20240307"

    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # Pipeline defaults
    default_top_k: int = 4
    relevance_threshold: float = 0.6
    max_healing_attempts: int = 3
    max_regeneration_attempts: int = 2
    generation_confidence_threshold: float = 0.8
    enable_web_search_fallback: bool = False

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
