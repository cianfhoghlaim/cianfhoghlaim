"""
Canonical env-var matrix for the Cianfhoghlaim code-side callers.

This module is the single source of truth for the
``CIANFHOGHLAIM_*`` env-var matrix introduced by openspec change
``2026-07-02-align-cianfhoghlaim-env-with-stacks``. Every code-side
caller (Dagster resources, BAML clients, DLT destinations, CocoIndex
flows, Langfuse / Logfire / MLflow clients, Cognee memory) MUST
import from here rather than re-declaring the env-var defaults
locally.

The 5-group host model (``infrastructure-stacks`` spec) places every
service on either ``bunchloch`` (workload), ``cax41-hetzner``
(storage), or ``arm1-oci`` (control plane). The defaults below are
the in-docker DNS names (so the same code works inside any
container on the cianfhoghlaim docker network); on-host override
via the same env vars (e.g. ``CIANFHOGHLAIM_LANGFUSE_URL=http://127.0.0.1:3001``
when running ``dagster dev`` from the MacBook).

Env-var matrix (7 vars total):

  CIANFHOGHLAIM_LITELLM_URL     — LiteLLM OpenAI-compatible gateway
  CIANFHOGHLAIM_LANGFUSE_URL    — Langfuse v3 trace ingestion
  CIANFHOGHLAIM_MLFLOW_URL      — MLflow v3 tracking server
  CIANFHOGHLAIM_FALKORDB_URL    — FalkorDB graph (Redis-compatible)
  CIANFHOGHLAIM_LANCEDB_URL     — lakehouse-lance-namespace REST
  CIANFHOGHLAIM_LOGFIRE_TOKEN   — Pydantic Logfire SaaS token (empty=local OTLP)
  CIANFHOGHLAIM_COGNEE_BACKEND  — Cognee graph backend: falkordb|memgraph|postgres

Legacy aliases (kept for backwards compatibility with operators
who already set the non-prefixed names):

  LITELLM_BASE_URL              — alias for CIANFHOGHLAIM_LITELLM_URL
  LANGFUSE_HOST                 — alias for CIANFHOGHLAIM_LANGFUSE_URL
  MLFLOW_TRACKING_URI           — alias for CIANFHOGHLAIM_MLFLOW_URL
  FALKORDB_HOST + FALKORDB_PORT — alias for CIANFHOGHLAIM_FALKORDB_URL
  LANCEDB_URI                   — alias for CIANFHOGHLAIM_LANCEDB_URL
  LOGFIRE_TOKEN                 — alias for CIANFHOGHLAIM_LOGFIRE_TOKEN

The Cognee backend selection (``falkordb`` primary + ``memgraph``
fallback) honours the ``agent-observability`` spec which removed
Memgraph + Neo4j from the production stack lineup. Operators MAY
still target Memgraph by setting ``CIANFHOGHLAIM_COGNEE_BACKEND=memgraph``
for legacy reasons; new code MUST use ``falkordb``.

When the new ``CIANFHOGHLAIM_*`` var is unset, the legacy alias is
checked, and finally the in-docker DNS default is used. The
precedence is therefore: ``CIANFHOGHLAIM_*`` > legacy alias > in-docker default.
"""
from __future__ import annotations

import os
from typing import Final

# ============================================================================
# Helpers (defined first so the module-level constants below can use them)
# ============================================================================


def _compose_redis_url_from_parts() -> str | None:
    """Build a redis:// URL from FALKORDB_HOST + FALKORDB_PORT (+ optional
    FALKORDB_PASSWORD) if the legacy aliases are set. Returns None if
    FALKORDB_HOST is unset (the typical case for new operators)."""
    host = os.getenv("FALKORDB_HOST")
    if not host:
        return None
    port = os.getenv("FALKORDB_PORT", "6379")
    password = os.getenv("FALKORDB_PASSWORD")
    if password:
        return f"redis://:{password}@{host}:{port}"
    return f"redis://{host}:{port}"


_VALID_COGNEE_BACKENDS: Final[tuple[str, ...]] = ("falkordb", "memgraph", "postgres")
COGNEE_BACKEND_PRIMARY: Final[str] = "falkordb"
COGNEE_BACKEND_FALLBACK: Final[str] = "memgraph"


def _resolve_cognee_backend() -> str:
    """Resolve the Cognee backend with fallback semantics.

    Precedence: CIANFHOGHLAIM_COGNEE_BACKEND > COGNEE_BACKEND (legacy) >
    in-docker default (falkordb). If the primary is unreachable at
    runtime, callers SHOULD fall back to memgraph (per the dispatch's
    hard-deliverable #2 wording).
    """
    raw = (
        os.getenv("CIANFHOGHLAIM_COGNEE_BACKEND")
        or os.getenv("COGNEE_BACKEND")
        or COGNEE_BACKEND_PRIMARY
    )
    backend = raw.strip().lower()
    if backend not in _VALID_COGNEE_BACKENDS:
        # Silent fallback to primary for unknown values
        return COGNEE_BACKEND_PRIMARY
    return backend


# ============================================================================
# 1. LITELLM — OpenAI-compatible LLM gateway (chokepoint)
# ============================================================================
# Deployed: bonneagar/stacks/litellm, container litellm, port 4000.
# In docker: http://litellm:4000/v1
# On host:   http://127.0.0.1:4000/v1 (per the litellm compose port map)
LITELLM_URL: Final[str] = (
    os.getenv("CIANFHOGHLAIM_LITELLM_URL")
    or os.getenv("LITELLM_BASE_URL")
    or "http://litellm:4000/v1"
)

# ============================================================================
# 2. LANGFUSE — v3 LLM trace ingestion (web service)
# ============================================================================
# Deployed: bonneagar/stacks/langfuse, container langfuse-web, port 3000.
# In docker: http://langfuse:3000 (container port 3000)
# On host:   http://127.0.0.1:3001 (port-shifted via LANGFUSE_PORT to avoid
#            OrbStack collision on bunchloch)
LANGFUSE_URL: Final[str] = (
    os.getenv("CIANFHOGHLAIM_LANGFUSE_URL")
    or os.getenv("LANGFUSE_HOST")
    or "http://langfuse:3000"
)

# ============================================================================
# 3. MLFLOW — v3 experiment tracking + model registry
# ============================================================================
# Deployed: bonneagar/stacks/mlflow, container mlflow, port 5000.
# In docker: http://mlflow:5000
# On host:   http://127.0.0.1:5000 (default MLFLOW_PORT=5000)
MLFLOW_URL: Final[str] = (
    os.getenv("CIANFHOGHLAIM_MLFLOW_URL")
    or os.getenv("MLFLOW_TRACKING_URI")
    or "http://mlflow:5000"
)

# ============================================================================
# 4. FALKORDB — graph cache (Redis-compatible)
# ============================================================================
# Deployed: bonneagar/stacks/falkordb, container falkordb, port 6379.
# In docker: redis://falkordb:6379 (container port 6379)
# On host:   redis://127.0.0.1:6379 (FALKORDB_PORT=6379 default in compose;
#            operators MAY port-shift to 6380 to avoid dragonfly collision)
FALKORDB_URL: Final[str] = (
    os.getenv("CIANFHOGHLAIM_FALKORDB_URL")
    or _compose_redis_url_from_parts()
    or "redis://falkordb:6379"
)


# Convenience accessors for the (host, port, password) split (FalkorDB
# clients need them separately, not as a URL).
FALKORDB_HOST: Final[str] = os.getenv("FALKORDB_HOST", "falkordb")
FALKORDB_PORT: Final[int] = int(os.getenv("FALKORDB_PORT", "6379"))
FALKORDB_PASSWORD: Final[str | None] = os.getenv("FALKORDB_PASSWORD") or None

# ============================================================================
# 5. LANCEDB — lakehouse-lance-namespace REST (the canonical vector store)
# ============================================================================
# Deployed: bonneagar/stacks/lakehouse, container lakehouse-lance-namespace,
# port 8182.
# In docker: rest://lakehouse-lance-namespace:8182
# On host:   rest://127.0.0.1:8182 (LANCE_NAMESPACE_PORT=8182 default)
LANCEDB_URL: Final[str] = (
    os.getenv("CIANFHOGHLAIM_LANCEDB_URL")
    or os.getenv("LANCEDB_URI")
    or "rest://lakehouse-lance-namespace:8182"
)

# ============================================================================
# 6. LOGFIRE — Pydantic Logfire SaaS token (empty = local OTLP collector)
# ============================================================================
# Deployed: bonneagar/stacks/logfire, container logfire-otel, ports 4317/4318.
# LOGFIRE_TOKEN is sourced from Infisical (dev-baile/cianfhoghlaim/logfire-token)
# via the Locket sidecar at container runtime. Empty in dev = spans go to the
# local OTel collector only (the lakehouse `logfire` stack).
LOGFIRE_TOKEN: Final[str] = (
    os.getenv("CIANFHOGHLAIM_LOGFIRE_TOKEN")
    or os.getenv("LOGFIRE_TOKEN")
    or ""
)

# ============================================================================
# 7. COGNEE BACKEND — primary + fallback graph selection
# ============================================================================
# Deployed: bonneagar/stacks/cognee, container cianfhoghlaim-cognee, port 8000.
# The Cognee service supports multiple graph backends:
#   falkordb  (Redis-compatible; the KCG default per agent-observability spec)
#   memgraph  (Bolt-compatible; legacy fallback; deprecated for new code)
#   postgres  (USE_UNIFIED_PROVIDER=pghybrid; the actual deployed setting)
#
# Per the dispatch's hard-deliverable #2 + the canonical agent-memory-systems
# spec, the Cognee code-side default is falkordb (primary) with memgraph as
# the legacy fallback. New code MUST use falkordb.
COGNEE_BACKEND: Final[str] = _resolve_cognee_backend()


def resolve_cognee_backend_with_fallback(raise_on_error: bool = False) -> str:
    """Return the Cognee backend to use at runtime, applying the
    falkordb → memgraph fallback chain.

    Args:
        raise_on_error: If True, raise a RuntimeError listing the
            exhausted backends instead of silently falling back.
            Defaults to False (silent fallback, the KCG convention).

    Returns:
        One of "falkordb" (preferred) or "memgraph" (fallback). The
        "postgres" value is intentionally NOT in the fallback chain —
        it represents the actual deployed cognee stack's internal
        unified-provider setting, not a Cognee-client-side backend
        choice.
    """
    backend = COGNEE_BACKEND
    if backend == "postgres":
        # The cognee stack itself uses pghybrid; the code-side caller
        # only cares about the graph backend it talks to directly.
        return COGNEE_BACKEND_PRIMARY
    if backend in ("falkordb", "memgraph"):
        return backend
    # Unknown — apply the explicit fallback chain
    if raise_on_error:
        raise RuntimeError(
            f"Unknown Cognee backend: {backend!r}. "
            f"Valid options: {', '.join(_VALID_COGNEE_BACKENDS)}"
        )
    return COGNEE_BACKEND_FALLBACK


# ============================================================================
# 8. The 7-row env-var matrix (the canonical contract)
# ============================================================================
ENV_VAR_MATRIX: Final[dict[str, dict[str, str]]] = {
    "CIANFHOGHLAIM_LITELLM_URL": {
        "default": "http://litellm:4000/v1",
        "legacy_alias": "LITELLM_BASE_URL",
        "stack": "litellm",
        "host": "bunchloch",
        "purpose": "OpenAI-compatible LLM gateway (chokepoint)",
    },
    "CIANFHOGHLAIM_LANGFUSE_URL": {
        "default": "http://langfuse:3000",
        "legacy_alias": "LANGFUSE_HOST",
        "stack": "langfuse",
        "host": "bunchloch",
        "purpose": "LLM trace ingestion (web service)",
    },
    "CIANFHOGHLAIM_MLFLOW_URL": {
        "default": "http://mlflow:5000",
        "legacy_alias": "MLFLOW_TRACKING_URI",
        "stack": "mlflow",
        "host": "bunchloch",
        "purpose": "Experiment tracking + model registry",
    },
    "CIANFHOGHLAIM_FALKORDB_URL": {
        "default": "redis://falkordb:6379",
        "legacy_alias": "FALKORDB_HOST + FALKORDB_PORT",
        "stack": "falkordb",
        "host": "bunchloch",
        "purpose": "Graph cache (Redis-compatible)",
    },
    "CIANFHOGHLAIM_LANCEDB_URL": {
        "default": "rest://lakehouse-lance-namespace:8182",
        "legacy_alias": "LANCEDB_URI",
        "stack": "lakehouse",
        "host": "cax41-hetzner",
        "purpose": "Lance table REST namespace (vector store)",
    },
    "CIANFHOGHLAIM_LOGFIRE_TOKEN": {
        "default": "(empty in dev, from Infisical via Locket in prod)",
        "legacy_alias": "LOGFIRE_TOKEN",
        "stack": "logfire",
        "host": "bunchloch",
        "purpose": "Pydantic Logfire SaaS token; empty = local OTLP",
    },
    "CIANFHOGHLAIM_COGNEE_BACKEND": {
        "default": "falkordb (fallback: memgraph)",
        "legacy_alias": "COGNEE_BACKEND",
        "stack": "cognee",
        "host": "bunchloch",
        "purpose": "Cognee graph backend (falkordb|memgraph|postgres)",
    },
}


__all__ = [
    "LITELLM_URL",
    "LANGFUSE_URL",
    "MLFLOW_URL",
    "FALKORDB_URL",
    "FALKORDB_HOST",
    "FALKORDB_PORT",
    "FALKORDB_PASSWORD",
    "LANCEDB_URL",
    "LOGFIRE_TOKEN",
    "COGNEE_BACKEND",
    "COGNEE_BACKEND_PRIMARY",
    "COGNEE_BACKEND_FALLBACK",
    "resolve_cognee_backend_with_fallback",
    "ENV_VAR_MATRIX",
]
