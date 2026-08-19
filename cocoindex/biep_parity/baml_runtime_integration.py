"""baml_runtime_integration — the canonical runtime integration between
BAML extraction + CocoIndex search.

Per the 2026-11-25-mega-3c-marimo-and-integration-v1 change (Phase 5).

The runtime module exposes the 3 canonical helpers that tie together:

1. The 4-stage BAML extraction (lc_extract_chunk, jc_extract_chunk,
   alevel_extract_chunk, gcse_extract_chunk) from
   `cocoindex/biep_parity/4_stage_extraction.py`.
2. The CocoIndex search closures (get_search from
   `cocoindex/_shared/cocoindex_query_api.py`).
3. Runtime metrics (call counts, latencies) for the extraction layer.

All 3 helpers are no-ops when the optional dependencies (BAML,
lancedb) are not installed.

Usage:

    from cocoindex.biep_parity.baml_runtime_integration import (
        get_search_closure_for_stage,
        run_stage_extraction,
        get_extraction_metrics,
    )

    # Search a stage-specific CocoIndex App
    search = get_search_closure_for_stage("lc", "mathematics")
    results = search("Chemical equilibrium", top_k=5)

    # Extract a chunk via the canonical 4-stage dispatch
    result = await run_stage_extraction("lc", chunk_text, "mathematics")

    # Inspect runtime metrics
    metrics = get_extraction_metrics("lc")
"""
from __future__ import annotations

import importlib.util
import logging
import sys
import time
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)


REPO_ROOT = Path(__file__).resolve().parents[2]


# Lazy imports
try:
    from baml_client.baml_client import b  # noqa: F401
    _HAS_BAML = True
except ImportError:
    _HAS_BAML = False
    b = None  # type: ignore


# ============================================================================
# Runtime metrics (call counts + latencies per stage)
# ============================================================================


# In-memory metrics dict: stage → {"call_count": int, "total_latency_ms": float}
_METRICS: dict[str, dict[str, float]] = {}


def _record_metric(stage: str, latency_ms: float) -> None:
    """Record a single extraction metric for the given stage."""
    if stage not in _METRICS:
        _METRICS[stage] = {"call_count": 0, "total_latency_ms": 0.0}
    _METRICS[stage]["call_count"] += 1
    _METRICS[stage]["total_latency_ms"] += latency_ms


# ============================================================================
# Module loaders (use spec_from_file_location for resilience)
# ============================================================================


def _load_module_via_spec(name: str, rel_path: str) -> Any | None:
    """Load a module via importlib.util.spec_from_file_location."""
    try:
        path = REPO_ROOT / rel_path
        if not path.exists():
            return None
        spec = importlib.util.spec_from_file_location(name, str(path))
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.debug("baml_runtime_integration: failed to load %s: %s", name, e)
        return None


def _get_4_stage_extraction() -> Any | None:
    """Load the 4-stage extraction module."""
    return _load_module_via_spec(
        "cocoindex.biep_parity.4_stage_extraction",
        "cocoindex/biep_parity/4_stage_extraction.py",
    )


def _get_cocoindex_query_api() -> Any | None:
    """Load the cocoindex query API module."""
    return _load_module_via_spec(
        "cocoindex._shared.cocoindex_query_api",
        "cocoindex/_shared/cocoindex_query_api.py",
    )


# ============================================================================
# The 3 canonical helpers
# ============================================================================


def get_search_closure_for_stage(
    stage: str,
    subject: str,
    *,
    embedder: str = "BAAI/bge-m3",
    top_k: int = 5,
) -> Callable[..., list[dict[str, Any]]] | None:
    """Get a search() closure for a specific stage + subject.

    The stage determines the BIEP CocoIndex App namespace:
    - "lc" → ireland_lc_<subject>_embedding
    - "jc" → ireland_jc_<subject>_embedding
    - "alevel" → ireland_lc_<subject>_embedding (fallback)
    - "gcse" → ireland_lc_<subject>_embedding (fallback)

    Args:
        stage: One of "lc", "jc", "alevel", "gcse".
        subject: The subject slug (mathematics, chemistry, etc.).
        embedder: The embedder name (default: BAAI/bge-m3).
        top_k: Default top_k for the search.

    Returns:
        A callable search() closure, or None if the query API is
        not importable.
    """
    query_api = _get_cocoindex_query_api()
    if query_api is None:
        return None

    get_search = getattr(query_api, "get_search", None)
    if get_search is None or not callable(get_search):
        return None

    # Stage → App namespace mapping
    stage_app_prefix = {
        "lc": "ireland_lc",
        "jc": "ireland_jc",
        "alevel": "ireland_lc",  # fallback to LC
        "gcse": "ireland_lc",  # fallback to LC
    }
    prefix = stage_app_prefix.get(stage.lower(), "ireland_lc")
    app_name = f"{prefix}_{subject}_embedding"

    try:
        return get_search(app_name, embedder=embedder, top_k=top_k)
    except Exception as e:
        logger.debug(
            "baml_runtime_integration: get_search failed for %s: %s",
            app_name, e,
        )
        return None


async def run_stage_extraction(
    stage: str,
    chunk_text: str,
    subject: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Dispatch a chunk to the canonical 4-stage extraction function.

    Args:
        stage: One of "lc", "jc", "alevel", "gcse".
        chunk_text: The chunk of text to extract from.
        subject: The subject slug.
        **kwargs: Extra kwargs forwarded to the stage-specific
            extract_chunk function (ncca_lo_code, filename, board, etc.).

    Returns:
        A dict containing the extraction result or an error message.

    Records runtime metrics (call count + latency) for the stage.
    """
    start = time.time()
    stage_key = stage.lower()

    extraction = _get_4_stage_extraction()
    if extraction is None:
        _record_metric(stage_key, 0.0)
        return {"error": "4_stage_extraction not importable"}

    extract_chunk_fn = getattr(extraction, "extract_chunk", None)
    if extract_chunk_fn is None or not callable(extract_chunk_fn):
        _record_metric(stage_key, 0.0)
        return {"error": "extract_chunk not available"}

    try:
        result = await extract_chunk_fn(stage, chunk_text, subject, **kwargs)
    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        _record_metric(stage_key, latency_ms)
        return {"error": str(e), "stage": stage_key, "subject": subject}

    latency_ms = (time.time() - start) * 1000
    _record_metric(stage_key, latency_ms)
    return result


def get_extraction_metrics(stage: str | None = None) -> dict[str, Any]:
    """Return the runtime metrics for the extraction layer.

    Args:
        stage: Optional stage filter. If None, returns metrics for
            all 4 stages.

    Returns:
        A dict mapping stage → {"call_count": int, "total_latency_ms": float,
        "avg_latency_ms": float}.
    """
    if stage is not None:
        stage_key = stage.lower()
        if stage_key not in _METRICS:
            return {"stage": stage_key, "call_count": 0, "total_latency_ms": 0.0, "avg_latency_ms": 0.0}
        m = _METRICS[stage_key]
        avg = m["total_latency_ms"] / m["call_count"] if m["call_count"] > 0 else 0.0
        return {
            "stage": stage_key,
            "call_count": int(m["call_count"]),
            "total_latency_ms": float(m["total_latency_ms"]),
            "avg_latency_ms": float(avg),
        }

    # Return all stages
    result = {}
    for s in ["lc", "jc", "alevel", "gcse"]:
        m = _METRICS.get(s, {"call_count": 0, "total_latency_ms": 0.0})
        avg = m["total_latency_ms"] / m["call_count"] if m["call_count"] > 0 else 0.0
        result[s] = {
            "call_count": int(m["call_count"]),
            "total_latency_ms": float(m["total_latency_ms"]),
            "avg_latency_ms": float(avg),
        }
    return result


def reset_extraction_metrics() -> None:
    """Reset all runtime metrics (useful for tests)."""
    _METRICS.clear()


__all__ = [
    "get_search_closure_for_stage",
    "run_stage_extraction",
    "get_extraction_metrics",
    "reset_extraction_metrics",
]
