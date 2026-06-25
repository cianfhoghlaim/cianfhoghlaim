"""
Croílár Shared Utilities — cross-cutting helpers for the personal portfolio.

This package contains shared utilities for the croilar subproject,
including path resolution, configuration, database access, embeddings,
MCP gateway, agent orchestration, and observability.

The optional `sruth.shared` re-export is performed lazily so that the
croilar subproject can be imported standalone (e.g. for tests, the web
frontend, or deployment to Cloudflare Workers) without the sister
sruth monorepo package being installed.
"""

from __future__ import annotations

# Optional re-export from sruth.shared (sister monorepo) — only when present.
# Aleyum historically depended on sruth.shared; that import was made the
# canonical source of SerialDatabaseExecutor, CircuitBreaker, RateLimiter,
# retry_with_backoff, etc. Croílár keeps the same surface so that any
# `from _shared import ...` call continues to work, but degrades gracefully
# if sruth is not installed.
try:
    from sruth.shared import (
        CircuitBreaker,
        RateLimiter,
        SerialDatabaseExecutor,
        get_executor,
        retry_with_backoff,
        run_serial,
    )

    _SRUTH_AVAILABLE = True
except ImportError:  # pragma: no cover — sruth is an optional sister package
    CircuitBreaker = None  # type: ignore[assignment]
    RateLimiter = None  # type: ignore[assignment]
    SerialDatabaseExecutor = None  # type: ignore[assignment]
    get_executor = None  # type: ignore[assignment]
    retry_with_backoff = None  # type: ignore[assignment]
    run_serial = None  # type: ignore[assignment]
    _SRUTH_AVAILABLE = False


# Aleyum/Croílár-specific exports
# (populated as modules are implemented — see _shared/{agents,observability,...})
# from .mcp import MCPGateway
# from .agents import AgentRouter, select_framework
# from .observability import AleyumTracer


# Stream registry — domain-driven replacement for the legacy persona model.
from .streams import (
    DEFAULT_SOURCES_PATH,
    Stream,
    StreamModel,
    StreamSource,
    StreamSourceModel,
    StreamSourceType,
    StreamsFile,
    get_stream,
    iter_asset_keys,
    list_streams,
    load_streams_from_mapping,
    load_streams_from_yaml,
    reset_cache,
)


__all__ = [
    # Re-exported from sruth.shared when available
    "SerialDatabaseExecutor",
    "get_executor",
    "run_serial",
    "CircuitBreaker",
    "RateLimiter",
    "retry_with_backoff",
    # Stream registry
    "Stream",
    "StreamSource",
    "StreamSourceType",
    "StreamModel",
    "StreamSourceModel",
    "StreamsFile",
    "DEFAULT_SOURCES_PATH",
    "get_stream",
    "list_streams",
    "load_streams_from_mapping",
    "load_streams_from_yaml",
    "reset_cache",
    "iter_asset_keys",
    # Capability flag
    "_SRUTH_AVAILABLE",
]
