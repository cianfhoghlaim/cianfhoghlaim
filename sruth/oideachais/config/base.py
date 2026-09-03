"""
Base Configuration for sruth data pipelines.

Provides FlowSettings base class that all flow-specific settings
should inherit from for consistent configuration across pipelines.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar

from pydantic import Field

# Handle pydantic v1 vs v2 settings
_PYDANTIC_V2 = False
SettingsConfigDict = None

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    _PYDANTIC_V2 = True
except ImportError:
    # Fallback for pydantic v1 or missing pydantic-settings
    try:
        from pydantic import BaseSettings  # type: ignore
    except ImportError:
        # Minimal fallback
        from pydantic import BaseModel as BaseSettings  # type: ignore

T = TypeVar("T", bound="FlowSettings")


if _PYDANTIC_V2:
    class FlowSettings(BaseSettings):
        """
        Base settings for all sruth data flows (pydantic v2).

        All flow-specific settings should inherit from this class to ensure
        consistent configuration patterns across the codebase.
        """

        model_config = SettingsConfigDict(
            env_prefix="SRUTH_",
            extra="ignore",
            env_file=".env",
            env_file_encoding="utf-8",
        )

        # =========================================================================
        # Database Settings
        # =========================================================================

        duckdb_path: Path = Field(
            default=Path.home() / ".sruth" / "duckdb",
            description="Base path for DuckDB databases",
        )

        lancedb_uri: str = Field(
            default=str(Path.home() / ".sruth" / "lancedb"),
            description="LanceDB connection URI",
        )

        ducklake_uri: Optional[str] = Field(
            default=None,
            description="DuckLake catalog URI (e.g., duckdb:///path/to/catalog.db)",
        )

        # =========================================================================
        # Graph Database Settings
        # =========================================================================

        memgraph_uri: str = Field(
            default="bolt://localhost:7687",
            description="Memgraph Bolt connection URI",
        )

        memgraph_username: str = Field(
            default="",
            description="Memgraph username (optional)",
        )

        memgraph_password: str = Field(
            default="",
            description="Memgraph password (optional)",
        )

        falkordb_host: str = Field(
            default="localhost",
            description="FalkorDB Redis host",
        )

        falkordb_port: int = Field(
            default=6379,
            description="FalkorDB Redis port",
        )

        falkordb_password: Optional[str] = Field(
            default=None,
            description="FalkorDB Redis password",
        )

        # =========================================================================
        # Embedding Settings
        # =========================================================================

        embedding_model: str = Field(
            default="BAAI/bge-m3",
            description="Default embedding model",
        )

        embedding_batch_size: int = Field(
            default=256,
            description="Batch size for embedding operations",
        )

        embedding_min_batch: int = Field(
            default=100,
            description="Minimum batch size before warning (100x performance diff)",
        )

        embedding_dimensions: int = Field(
            default=1024,
            description="Embedding vector dimensions",
        )

        # =========================================================================
        # LLM Settings
        # =========================================================================

        llm_model: str = Field(
            default="claude-sonnet-4-20250514",
            description="Default LLM model for extraction",
        )

        llm_temperature: float = Field(
            default=0.0,
            description="LLM temperature for structured extraction",
        )

        llm_max_tokens: int = Field(
            default=4096,
            description="Maximum tokens for LLM responses",
        )

        # =========================================================================
        # Observability Settings
        # =========================================================================

        datadog_enabled: bool = Field(
            default=True,
            description="Enable Datadog LLMObs tracing",
        )

        langfuse_enabled: bool = Field(
            default=True,
            description="Enable Langfuse tracing",
        )

        logfire_enabled: bool = Field(
            default=False,
            description="Enable Logfire tracing",
        )

        # =========================================================================
        # Storage Settings
        # =========================================================================

        s3_bucket: Optional[str] = Field(
            default=None,
            description="S3 bucket for object storage",
        )

        s3_endpoint: Optional[str] = Field(
            default=None,
            description="S3 endpoint URL (for MinIO/Garage)",
        )

        # =========================================================================
        # Methods
        # =========================================================================

        def get_duckdb_path(self, db_name: str) -> Path:
            """Get full path for a named DuckDB database."""
            return self.duckdb_path / f"{db_name}.duckdb"

        def to_dict(self) -> Dict[str, Any]:
            """Convert settings to dictionary, excluding sensitive values."""
            data = self.model_dump()
            # Mask sensitive fields
            for key in ["memgraph_password", "falkordb_password"]:
                if data.get(key):
                    data[key] = "***"
            return data

else:
    # Pydantic v1 fallback
    class FlowSettings(BaseSettings):  # type: ignore
        """
        Base settings for all sruth data flows (pydantic v1).

        All flow-specific settings should inherit from this class to ensure
        consistent configuration patterns across the codebase.
        """

        class Config:
            env_prefix = "SRUTH_"
            extra = "ignore"
            env_file = ".env"
            env_file_encoding = "utf-8"

        # =========================================================================
        # Database Settings
        # =========================================================================

        duckdb_path: Path = Field(
            default=Path.home() / ".sruth" / "duckdb",
            description="Base path for DuckDB databases",
        )

        lancedb_uri: str = Field(
            default=str(Path.home() / ".sruth" / "lancedb"),
            description="LanceDB connection URI",
        )

        ducklake_uri: Optional[str] = Field(
            default=None,
            description="DuckLake catalog URI (e.g., duckdb:///path/to/catalog.db)",
        )

        # =========================================================================
        # Graph Database Settings
        # =========================================================================

        memgraph_uri: str = Field(
            default="bolt://localhost:7687",
            description="Memgraph Bolt connection URI",
        )

        memgraph_username: str = Field(
            default="",
            description="Memgraph username (optional)",
        )

        memgraph_password: str = Field(
            default="",
            description="Memgraph password (optional)",
        )

        falkordb_host: str = Field(
            default="localhost",
            description="FalkorDB Redis host",
        )

        falkordb_port: int = Field(
            default=6379,
            description="FalkorDB Redis port",
        )

        falkordb_password: Optional[str] = Field(
            default=None,
            description="FalkorDB Redis password",
        )

        # =========================================================================
        # Embedding Settings
        # =========================================================================

        embedding_model: str = Field(
            default="BAAI/bge-m3",
            description="Default embedding model",
        )

        embedding_batch_size: int = Field(
            default=256,
            description="Batch size for embedding operations",
        )

        embedding_min_batch: int = Field(
            default=100,
            description="Minimum batch size before warning (100x performance diff)",
        )

        embedding_dimensions: int = Field(
            default=1024,
            description="Embedding vector dimensions",
        )

        # =========================================================================
        # LLM Settings
        # =========================================================================

        llm_model: str = Field(
            default="claude-sonnet-4-20250514",
            description="Default LLM model for extraction",
        )

        llm_temperature: float = Field(
            default=0.0,
            description="LLM temperature for structured extraction",
        )

        llm_max_tokens: int = Field(
            default=4096,
            description="Maximum tokens for LLM responses",
        )

        # =========================================================================
        # Observability Settings
        # =========================================================================

        datadog_enabled: bool = Field(
            default=True,
            description="Enable Datadog LLMObs tracing",
        )

        langfuse_enabled: bool = Field(
            default=True,
            description="Enable Langfuse tracing",
        )

        logfire_enabled: bool = Field(
            default=False,
            description="Enable Logfire tracing",
        )

        # =========================================================================
        # Storage Settings
        # =========================================================================

        s3_bucket: Optional[str] = Field(
            default=None,
            description="S3 bucket for object storage",
        )

        s3_endpoint: Optional[str] = Field(
            default=None,
            description="S3 endpoint URL (for MinIO/Garage)",
        )

        # =========================================================================
        # Methods
        # =========================================================================

        def get_duckdb_path(self, db_name: str) -> Path:
            """Get full path for a named DuckDB database."""
            return self.duckdb_path / f"{db_name}.duckdb"

        def to_dict(self) -> Dict[str, Any]:
            """Convert settings to dictionary, excluding sensitive values."""
            data = self.dict()
            # Mask sensitive fields
            for key in ["memgraph_password", "falkordb_password"]:
                if data.get(key):
                    data[key] = "***"
            return data


# Global settings cache
_settings_cache: Dict[str, FlowSettings] = {}


def get_flow_settings(
    settings_class: Type[T] = FlowSettings,
    cache_key: Optional[str] = None,
) -> T:
    """
    Get or create flow settings instance.

    Args:
        settings_class: Settings class to instantiate
        cache_key: Optional cache key (defaults to class name)

    Returns:
        Settings instance
    """
    key = cache_key or settings_class.__name__

    if key not in _settings_cache:
        _settings_cache[key] = settings_class()

    return _settings_cache[key]  # type: ignore
