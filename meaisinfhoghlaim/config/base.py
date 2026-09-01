"""
Base Configuration for sruth data pipelines.

Provides FlowSettings base class that all flow-specific settings
should inherit from for consistent configuration across pipelines.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, TypeVar

from pydantic import Field

# Canonical env-var matrix (the CIANFHOGHLAIM_* env vars). The
# FlowSettings class uses pydantic's env_prefix=SRUTH_ for backwards
# compat, but the canonical defaults below read the CIANFHOGHLAIM_*
# vars first and fall back to the SRUTH_ legacy aliases + the
# in-docker defaults.
try:
    from cianfhoghlaim.observability.env_config import (
        FALKORDB_HOST as _CIANFHOGHLAIM_FALKORDB_HOST,
    )
    from cianfhoghlaim.observability.env_config import (
        FALKORDB_PASSWORD as _CIANFHOGHLAIM_FALKORDB_PASSWORD,
    )
    from cianfhoghlaim.observability.env_config import (
        FALKORDB_PORT as _CIANFHOGHLAIM_FALKORDB_PORT,
    )
    from cianfhoghlaim.observability.env_config import (
        resolve_cognee_backend_with_fallback as _resolve_cognee_backend,
    )
except ImportError:  # pragma: no cover
    _CIANFHOGHLAIM_FALKORDB_HOST = "falkordb"
    _CIANFHOGHLAIM_FALKORDB_PORT = 6379
    _CIANFHOGHLAIM_FALKORDB_PASSWORD = None
    _resolve_cognee_backend = lambda: "falkordb"  # type: ignore[assignment]

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


def _resolve_default_llm_model() -> str:
    """Resolve the canonical default LLM model key.

    Resolution chain (in priority order):
    1. ``CIANFHOGHLAIM_LLM_MODEL`` env var (explicit operator override)
    2. ``MODEL_REGISTRY.resolve("text_llm", "default")`` — the unified registry
       (added 2026-08-15 by the ``centralized-model-registry`` openspec change)
    3. The legacy hardcoded fallback ``"claude-sonnet-4-20250514"`` for
       back-compat with deployments that have no MODEL_REGISTRY available.

    This helper is the canonical home for the ``llm_model`` default across
    both the pydantic v1 and pydantic v2 branches of ``FlowSettings``.
    """
    explicit = os.getenv("CIANFHOGHLAIM_LLM_MODEL")
    if explicit:
        return explicit
    try:
        from meaisinfhoghlaim.models.model_registry import MODEL_REGISTRY

        return MODEL_REGISTRY.resolve("text_llm", "default")
    except Exception:  # pragma: no cover - registry not wired
        return "claude-sonnet-4-20250514"


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

        ducklake_uri: str | None = Field(
            default=None,
            description="DuckLake catalog URI (e.g., duckdb:///path/to/catalog.db)",
        )

        # =========================================================================
        # Graph Database Settings
        # =========================================================================
        # Graph Database Settings
        # =========================================================================
        #
        # The Cognee code-side backend selection (falkordb primary +
        # memgraph fallback) is the canonical Cianfhoghlaim default per the
        # agent-observability spec. New code MUST use falkordb; the
        # memgraph defaults below remain for legacy call-sites only.

        memgraph_uri: str = Field(
            default="bolt://memgraph:7687",
            description=(
                "Memgraph Bolt connection URI. Default points at the in-docker "
                "memgraph container (not used by new code; legacy callers only)."
            ),
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
            default_factory=lambda: os.getenv("FALKORDB_HOST") or _CIANFHOGHLAIM_FALKORDB_HOST,
            description="FalkorDB Redis host (default: CIANFHOGHLAIM_FALKORDB_URL host)",
        )

        falkordb_port: int = Field(
            default_factory=lambda: int(os.getenv("FALKORDB_PORT", "0") or "0") or _CIANFHOGHLAIM_FALKORDB_PORT,
            description="FalkorDB Redis port (default: CIANFHOGHLAIM_FALKORDB_URL port)",
        )

        falkordb_password: str | None = Field(
            default_factory=lambda: os.getenv("FALKORDB_PASSWORD") or _CIANFHOGHLAIM_FALKORDB_PASSWORD,
            description="FalkorDB Redis password (default: CIANFHOGHLAIM_FALKORDB_URL password)",
        )

        # Cognee code-side backend selection. Honours
        # CIANFHOGHLAIM_COGNEE_BACKEND with the falkordb → memgraph
        # fallback chain (per dispatch hard-deliverable #2).
        cognee_backend: str = Field(
            default_factory=lambda: _resolve_cognee_backend(),
            description=(
                "Cognee graph backend (falkordb | memgraph | postgres). "
                "Primary = falkordb; fallback = memgraph. Honours "
                "CIANFHOGHLAIM_COGNEE_BACKEND."
            ),
        )

        # =========================================================================
        # Embedding Settings
        # =========================================================================
        #
        # The embedder + dim are env-overridable via the canonical
        # `CIANFHOGHLAIM_EMBED_MODEL` / `CIANFHOGHLAIM_EMBED_DIM` knobs
        # (per the 2026-08-XX centralized-model-registry trilogy). The
        # Pydantic `default_factory` is used because `Field(default=...)`
        # cannot read the env at class-definition time.

        embedding_model: str = Field(
            default_factory=lambda: os.getenv("CIANFHOGHLAIM_EMBED_MODEL", "BAAI/bge-m3"),
            description="Default embedding model (env: CIANFHOGHLAIM_EMBED_MODEL)",
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
            default_factory=lambda: int(os.getenv("CIANFHOGHLAIM_EMBED_DIM", "1024")),
            description="Embedding vector dimensions (env: CIANFHOGHLAIM_EMBED_DIM)",
        )

        # =========================================================================
        # LLM Settings
        # =========================================================================
        #
        # `llm_model` is sourced from `MODEL_REGISTRY.resolve("text_llm", "default")`
        # at instantiation time, so the unified model registry is the single
        # source of truth. The legacy `claude-sonnet-4-20250514` default was
        # hardcoded pre-trilogy; this preserves the env-driven override
        # (CIANFHOGHLAIM_LLM_MODEL) and falls back to the registry.

        llm_model: str = Field(
            default_factory=lambda: _resolve_default_llm_model(),
            description="Default LLM model for extraction (env: CIANFHOGHLAIM_LLM_MODEL; registry: text_llm/default)",
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
            default=False,
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

        s3_bucket: str | None = Field(
            default=None,
            description="S3 bucket for object storage",
        )

        s3_endpoint: str | None = Field(
            default=None,
            description="S3 endpoint URL (for MinIO/Garage)",
        )

        # =========================================================================
        # Methods
        # =========================================================================

        def get_duckdb_path(self, db_name: str) -> Path:
            """Get full path for a named DuckDB database."""
            return self.duckdb_path / f"{db_name}.duckdb"

        def to_dict(self) -> dict[str, Any]:
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

        ducklake_uri: str | None = Field(
            default=None,
            description="DuckLake catalog URI (e.g., duckdb:///path/to/catalog.db)",
        )

        # =========================================================================
        # Graph Database Settings
        # =========================================================================
        # Graph Database Settings
        # =========================================================================
        #
        # The Cognee code-side backend selection (falkordb primary +
        # memgraph fallback) is the canonical Cianfhoghlaim default per the
        # agent-observability spec. New code MUST use falkordb; the
        # memgraph defaults below remain for legacy call-sites only.

        memgraph_uri: str = Field(
            default="bolt://memgraph:7687",
            description=(
                "Memgraph Bolt connection URI. Default points at the in-docker "
                "memgraph container (not used by new code; legacy callers only)."
            ),
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
            default_factory=lambda: os.getenv("FALKORDB_HOST") or _CIANFHOGHLAIM_FALKORDB_HOST,
            description="FalkorDB Redis host (default: CIANFHOGHLAIM_FALKORDB_URL host)",
        )

        falkordb_port: int = Field(
            default_factory=lambda: int(os.getenv("FALKORDB_PORT", "0") or "0") or _CIANFHOGHLAIM_FALKORDB_PORT,
            description="FalkorDB Redis port (default: CIANFHOGHLAIM_FALKORDB_URL port)",
        )

        falkordb_password: str | None = Field(
            default_factory=lambda: os.getenv("FALKORDB_PASSWORD") or _CIANFHOGHLAIM_FALKORDB_PASSWORD,
            description="FalkorDB Redis password (default: CIANFHOGHLAIM_FALKORDB_URL password)",
        )

        # Cognee code-side backend selection. Honours
        # CIANFHOGHLAIM_COGNEE_BACKEND with the falkordb → memgraph
        # fallback chain (per dispatch hard-deliverable #2).
        cognee_backend: str = Field(
            default_factory=lambda: _resolve_cognee_backend(),
            description=(
                "Cognee graph backend (falkordb | memgraph | postgres). "
                "Primary = falkordb; fallback = memgraph. Honours "
                "CIANFHOGHLAIM_COGNEE_BACKEND."
            ),
        )

        # =========================================================================
        # Embedding Settings
        # =========================================================================
        #
        # The embedder + dim are env-overridable via the canonical
        # `CIANFHOGHLAIM_EMBED_MODEL` / `CIANFHOGHLAIM_EMBED_DIM` knobs
        # (per the 2026-08-XX centralized-model-registry trilogy). The
        # Pydantic `default_factory` is used because `Field(default=...)`
        # cannot read the env at class-definition time.

        embedding_model: str = Field(
            default_factory=lambda: os.getenv("CIANFHOGHLAIM_EMBED_MODEL", "BAAI/bge-m3"),
            description="Default embedding model (env: CIANFHOGHLAIM_EMBED_MODEL)",
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
            default_factory=lambda: int(os.getenv("CIANFHOGHLAIM_EMBED_DIM", "1024")),
            description="Embedding vector dimensions (env: CIANFHOGHLAIM_EMBED_DIM)",
        )

        # =========================================================================
        # LLM Settings
        # =========================================================================
        #
        # `llm_model` is sourced from `MODEL_REGISTRY.resolve("text_llm", "default")`
        # at instantiation time, so the unified model registry is the single
        # source of truth. The legacy `claude-sonnet-4-20250514` default was
        # hardcoded pre-trilogy; this preserves the env-driven override
        # (CIANFHOGHLAIM_LLM_MODEL) and falls back to the registry.

        llm_model: str = Field(
            default_factory=lambda: _resolve_default_llm_model(),
            description="Default LLM model for extraction (env: CIANFHOGHLAIM_LLM_MODEL; registry: text_llm/default)",
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
            default=False,
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

        s3_bucket: str | None = Field(
            default=None,
            description="S3 bucket for object storage",
        )

        s3_endpoint: str | None = Field(
            default=None,
            description="S3 endpoint URL (for MinIO/Garage)",
        )

        # =========================================================================
        # Methods
        # =========================================================================

        def get_duckdb_path(self, db_name: str) -> Path:
            """Get full path for a named DuckDB database."""
            return self.duckdb_path / f"{db_name}.duckdb"

        def to_dict(self) -> dict[str, Any]:
            """Convert settings to dictionary, excluding sensitive values."""
            data = self.dict()
            # Mask sensitive fields
            for key in ["memgraph_password", "falkordb_password"]:
                if data.get(key):
                    data[key] = "***"
            return data


# Global settings cache
_settings_cache: dict[str, FlowSettings] = {}


def get_flow_settings(
    settings_class: type[T] = FlowSettings,
    cache_key: str | None = None,
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


# Module-level convenience: ``from meaisinfhoghlaim.config.base import settings``
# returns the default ``FlowSettings()`` instance (the canonical settings
# cache). New code should prefer ``settings`` over instantiating a fresh
# FlowSettings; legacy callers may still call ``get_flow_settings()``.
settings: FlowSettings = get_flow_settings()
