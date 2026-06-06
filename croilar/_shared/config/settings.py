"""
Configuration settings for Aleyum.

Uses Pydantic Settings for environment variable loading and validation.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class AleyumSettings(BaseSettings):
    """
    Aleyum configuration settings.

    All settings can be overridden via environment variables with ALEYUM_ prefix.
    """

    model_config = SettingsConfigDict(
        env_prefix="ALEYUM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database settings
    lancedb_uri: str = "~/.lancedb/aleyum"
    duckdb_path: str = "~/.duckdb/aleyum.db"

    # LiteLLM MCP Gateway
    litellm_base_url: str = "http://litellm:4000"
    litellm_api_key: Optional[str] = None

    # Embedding settings
    embedding_model: str = "BAAI/bge-m3"
    embedding_batch_size: int = 256

    # Browser agent settings
    browser_backend: str = "stagehand"  # stagehand, crawl4ai, skyvern, cdp
    browserbase_api_key: Optional[str] = None
    browserbase_project_id: Optional[str] = None

    # Agent framework settings
    default_agent_framework: str = "adk"  # adk or agno
    agent_complexity_threshold: float = 0.5

    # Observability
    datadog_enabled: bool = False
    datadog_api_key: Optional[str] = None
    langfuse_enabled: bool = False
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    logfire_enabled: bool = False
    logfire_token: Optional[str] = None


@lru_cache
def get_settings() -> AleyumSettings:
    """Get cached settings instance."""
    return AleyumSettings()
