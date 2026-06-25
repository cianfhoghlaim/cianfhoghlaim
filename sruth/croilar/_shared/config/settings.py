"""Configuration settings for the Croílár Stream registry.

Per round 11 of the multi-quadrant refactor plan
(the `croilar-aleyum-to-streams-cleanup-v1` openspec change),
the legacy `AleyumSettings` class + the `ALEYUM_` env prefix have
been fully retired. The canonical `StreamSettings` class is the
only API.

- Loads stream definitions from `croilar/config/sources.yaml`
- Exposes a typed `streams: dict[str, Stream]` field
- Env prefix is `STREAMS_`
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from sruth.croilar._shared.streams import (
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

    embedding_model: str = "BAAI/bge-m3"
    embedding_batch_size: int = 256

    browser_backend: str = "stagehand"  # stagehand, crawl4ai, skyvern, cdp
    browserbase_api_key: Optional[str] = None
    browserbase_project_id: Optional[str] = None

    default_agent_framework: str = "adk"  # adk or agno
    agent_complexity_threshold: float = 0.5

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


@lru_cache
def get_settings() -> StreamSettings:
    """Get cached settings instance."""
    return StreamSettings()


__all__ = ["StreamSettings", "get_settings"]
