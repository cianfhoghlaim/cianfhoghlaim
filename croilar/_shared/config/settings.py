"""Configuration settings for the Croílár Stream registry.

The legacy `AleyumSettings` class is replaced by `StreamSettings`, which:

- Loads stream definitions from `croilar/config/sources.yaml`
- Exposes a typed `streams: dict[str, Stream]` field
- Env prefix is `STREAMS_` (was `ALEYUM_`)

Backwards-compat: a deprecated `AleyumSettings` alias is kept temporarily
and will be removed in a follow-up change.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from croilar._shared.streams import (
    DEFAULT_SOURCES_PATH,
    Stream,
    list_streams,
)


class StreamSettings(BaseSettings):
    """Stream-driven configuration for Croílár.

    All settings can be overridden via environment variables with `STREAMS_` prefix.
    """

    model_config = SettingsConfigDict(
        env_prefix="STREAMS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    sources_yaml_path: Path = Field(default=DEFAULT_SOURCES_PATH)
    r2_bucket: str = "cianfhoghlaim-public"
    lancedb_uri: str = "~/.lancedb/croilar"
    duckdb_root: str = "~/.duckdb/croilar"
    default_agent_port: int = 7774

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

    def streams(self) -> list[Stream]:
        """Load the Stream registry from `sources_yaml_path`."""
        return list_streams(self.sources_yaml_path)

    def stream(self, stream_id: str) -> Stream:
        """Look up a single Stream by id."""
        for s in self.streams():
            if s.id == stream_id:
                return s
        raise KeyError(
            f"stream {stream_id!r} not registered; "
            f"available: {[s.id for s in self.streams()]}"
        )


# Deprecated alias — kept temporarily for downstream imports.
# Remove in a follow-up change once all callers migrate.
AleyumSettings = StreamSettings


@lru_cache
def get_settings() -> StreamSettings:
    """Get cached settings instance."""
    return StreamSettings()


__all__ = ["StreamSettings", "AleyumSettings", "get_settings"]
