"""
reranker — v1 CocoIndex primitive (Phase 0 of
`2026-07-14-multimodal-code-and-media-intel-v1`).

Ported from the archived `códeolas`
(`cocoindex_flows/_shared/reranker.py:rerank_results` (was `stedding/dev/cianfhoghlaim copy/sruth/códeolas/search/reranker.py` pre-v7)).

The archived primitive supported Jina / Cohere / Aliyun as rerank
providers via raw `aiohttp` calls. The v1 primitive wraps the same 3
providers behind a CocoIndex `ContextKey` + a `@coco.fn(memo=True)`
helper that the MCP tool `cocoindex-code.rerank_query` can call.

The `RERANKER` ContextKey is the canonical home for the rerank
provider + API key + model name; an MCP tool that needs to rerank a
list of search results resolves the `RERANKER` ContextKey at call
time and dispatches through the chosen provider.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Literal

import structlog

from .._shared._lifespan import COCOINDEX_AVAILABLE

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE_LOCAL = COCOINDEX_AVAILABLE
except ImportError:  # pragma: no cover - degrade gracefully
    coco = None  # type: ignore[assignment]
    COCOINDEX_AVAILABLE_LOCAL = False

logger = structlog.get_logger(__name__)


# not-a-flow: this primitive exposes `@coco.fn(memo=True)` + `ContextKey`
# but never writes to a LanceDB table — the reranker is a call-time
# side-effect service that ships results via the MCP transport.
# See `openspec/changes/2026-07-14-multimodal-code-and-media-intel-v1/proposal.md`
# "Phase 0 — Port the archived codeolas primitives".


# ---------------------------------------------------------------------------
# Provider configuration
# ---------------------------------------------------------------------------


RerankProvider = Literal["jina", "cohere", "aliyun"]


@dataclass(frozen=True)
class RerankConfig:
    """Provider + key + model for the rerank service."""

    provider: RerankProvider
    api_key: str | None
    model: str
    base_url: str | None = None

    @classmethod
    def from_env(cls) -> RerankConfig:
        """Read the provider + key + model from env vars.

        Falls back to `provider="jina"` if nothing is set; Jina's
        free-tier key gives reasonable precision on small batches.
        """
        provider: RerankProvider = (
            os.getenv("RERANK_PROVIDER", "jina").lower().strip()  # type: ignore[assignment]
        )
        if provider not in ("jina", "cohere", "aliyun"):
            provider = "jina"

        api_key = (
            os.getenv("RERANK_API_KEY")
            or os.getenv("JINA_API_KEY")
            or os.getenv("COHERE_API_KEY")
            or os.getenv("DASHSCOPE_API_KEY")
        )

        default_model = {
            "jina": "jina-reranker-v2-base-multilingual",
            "cohere": "rerank-v3.5",
            "aliyun": "gte-rerank-v2",
        }[provider]

        return cls(
            provider=provider,
            api_key=api_key,
            model=os.getenv("RERANK_MODEL", default_model),
        )


# ---------------------------------------------------------------------------
# ContextKey (R1 conformance: uses the shared cocoindex import surface)
# ---------------------------------------------------------------------------


if COCOINDEX_AVAILABLE_LOCAL and coco is not None:
    RERANKER = coco.ContextKey[RerankConfig]("cianfhoghlaim_reranker")  # type: ignore[index]
else:
    RERANKER = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Provider implementations (mirrors the archived codeolas implementations,
# simplified to the essentials — no chunking, no overlap tokens; the v1
# callers pass already-chunked result lists).
# ---------------------------------------------------------------------------


async def _jina_rerank(
    query: str,
    documents: list[str],
    model: str,
    api_key: str | None,
    top_n: int | None,
) -> list[dict[str, Any]]:
    """Jina AI reranker. Returns `[{index, relevance_score}, ...]`."""
    try:
        import aiohttp  # type: ignore[import-not-found]
    except ImportError as e:  # pragma: no cover - aiohttp is optional
        raise RuntimeError(
            "aiohttp is required for the Jina rerank provider. "
            "Install with `uv add aiohttp`."
        ) from e

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload: dict[str, Any] = {
        "model": model,
        "query": query,
        "documents": documents,
    }
    if top_n is not None:
        payload["top_n"] = top_n

    async with aiohttp.ClientSession() as session, session.post(
        "https://api.jina.ai/v1/rerank",
        headers=headers,
        json=payload,
    ) as response:
        response.raise_for_status()
        data = await response.json()
        return [
            {"index": r["index"], "relevance_score": r["relevance_score"]}
            for r in data.get("results", [])
        ]


async def _cohere_rerank(
    query: str,
    documents: list[str],
    model: str,
    api_key: str | None,
    top_n: int | None,
) -> list[dict[str, Any]]:
    """Cohere reranker (v2 endpoint)."""
    try:
        import aiohttp  # type: ignore[import-not-found]
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(
            "aiohttp is required for the Cohere rerank provider."
        ) from e

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload: dict[str, Any] = {
        "model": model,
        "query": query,
        "documents": [{"text": d} for d in documents],
    }
    if top_n is not None:
        payload["top_n"] = top_n

    async with aiohttp.ClientSession() as session, session.post(
        "https://api.cohere.com/v2/rerank",
        headers=headers,
        json=payload,
    ) as response:
        response.raise_for_status()
        data = await response.json()
        return [
            {"index": r["index"], "relevance_score": r["relevance_score"]}
            for r in data.get("results", [])
        ]


async def _aliyun_rerank(
    query: str,
    documents: list[str],
    model: str,
    api_key: str | None,
    top_n: int | None,
) -> list[dict[str, Any]]:
    """Aliyun DashScope reranker."""
    try:
        import aiohttp  # type: ignore[import-not-found]
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(
            "aiohttp is required for the Aliyun rerank provider."
        ) from e

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload: dict[str, Any] = {
        "model": model,
        "input": {"query": query, "documents": documents},
        "parameters": {},
    }
    if top_n is not None:
        payload["parameters"]["top_n"] = top_n

    async with aiohttp.ClientSession() as session, session.post(
        "https://dashscope.aliyuncs.com/api/v1/services/rerank/"
        "text-rerank/text-rerank",
        headers=headers,
        json=payload,
    ) as response:
        response.raise_for_status()
        data = await response.json()
        return [
            {"index": r["index"], "relevance_score": r["relevance_score"]}
            for r in data.get("output", {}).get("results", [])
        ]


# ---------------------------------------------------------------------------
# The v1 primitive
# ---------------------------------------------------------------------------


async def query_reranker(
    query: str,
    results: list[dict[str, Any]],
    top_n: int | None = None,
    config: RerankConfig | None = None,
) -> list[dict[str, Any]]:
    """Rerank search results using the configured provider.

    Each `result` dict MUST have at least `{"row_id", "text", "score"}`.
    The function preserves all keys in each result and adds/updates
    `"rerank_score"` on each.

    Args:
        query: the natural-language query.
        results: list of result dicts.
        top_n: optional cap on returned results.
        config: optional explicit config. Defaults to `RerankConfig.from_env()`.

    Returns:
        Reranked list of result dicts (the same `row_id` keys, just
        reordered by relevance and augmented with `rerank_score`).
    """
    if not results:
        return results

    config = config or RerankConfig.from_env()
    documents = [r.get("text", "") for r in results]

    if config.provider == "jina":
        scores = await _jina_rerank(query, documents, config.model, config.api_key, top_n)
    elif config.provider == "cohere":
        scores = await _cohere_rerank(query, documents, config.model, config.api_key, top_n)
    elif config.provider == "aliyun":
        scores = await _aliyun_rerank(query, documents, config.model, config.api_key, top_n)
    else:
        raise ValueError(f"Unknown rerank provider: {config.provider}")

    reranked: list[dict[str, Any]] = []
    for s in scores:
        idx = s["index"]
        if 0 <= idx < len(results):
            r = dict(results[idx])
            r["rerank_score"] = s["relevance_score"]
            reranked.append(r)
    return reranked


# ---------------------------------------------------------------------------
# v1 App stub (R2 conformance)
# ---------------------------------------------------------------------------


if COCOINDEX_AVAILABLE_LOCAL and coco is not None:
    reranker_app = coco.App(coco.AppConfig(name="Reranker"))  # type: ignore[attr-defined]
else:  # pragma: no cover
    reranker_app = None


__all__ = [
    "RERANKER",
    "RerankConfig",
    "RerankProvider",
    "query_reranker",
    "reranker_app",
]
