"""
cianfhoghlaim.api.routes.search — FastAPI route for semantic search.

Exposes the cross-corpus semantic search as an HTTP endpoint at
`/search/semantic`. Backs onto the canonical cognify rules in
`storage.cognify.rules.semantic_search`, so there is NO duplicate
search logic — the API is a thin HTTP wrapper.

Reference: openspec/changes/2026-07-14-cianfhoghlaim-semantic-search-v1/
            + openspec/specs/cianfhoghlaim-semantic-search/spec.md
            Requirement: Search API (`GET /search/semantic` returns
            200 with `{"results": [...], "total": N}`)
"""
from __future__ import annotations

import json
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# FastAPI is optional — degrade gracefully if not installed.
try:
    from fastapi import APIRouter, HTTPException, Query  # type: ignore[import-not-found]
    from pydantic import BaseModel, Field  # type: ignore[import-not-found]

    FASTAPI_AVAILABLE = True
except ImportError as e:  # pragma: no cover
    logger.warning("fastapi_not_available: %s", e)
    APIRouter = None  # type: ignore[assignment]
    HTTPException = None  # type: ignore[assignment]
    Query = None  # type: ignore[assignment]
    BaseModel = object  # type: ignore[assignment, misc]
    Field = lambda *args, **kwargs: None  # type: ignore[assignment]
    FASTAPI_AVAILABLE = False


# The single router — mounted at `/search` by the FastAPI app.
router = APIRouter(prefix="/search", tags=["search"]) if FASTAPI_AVAILABLE else None


# ---------------------------------------------------------------------------
# Pydantic request/response models
# ---------------------------------------------------------------------------


class SemanticSearchResponse(BaseModel):  # type: ignore[misc]
    """Response envelope for `/search/semantic`."""

    results: list[dict[str, Any]] = Field(default_factory=list)
    total: int = 0
    latency_ms: float = 0.0
    search_id: str = ""
    embedder: str = ""


class SemanticSearchRequest(BaseModel):  # type: ignore[misc]
    """Optional JSON body for POST `/search/semantic`."""

    query: str
    top_k: int = 10
    embedder: str = "BAAI/bge-m3"
    filters: dict[str, list[Any]] = Field(default_factory=dict)
    window_size: int = 0
    version: int | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_filter_string(s: str) -> dict[str, list[Any]]:
    """Parse a `SearchFilter` envelope from a URL query string.

    Format: `key1=val1,val2;key2=val3` or a JSON dict.
    """
    if not s:
        return {}
    try:
        return json.loads(s)
    except (ValueError, TypeError):
        # Fall back to a simple semicolon-separated key=value,value list.
        out: dict[str, list[Any]] = {}
        for chunk in s.split(";"):
            chunk = chunk.strip()
            if not chunk or "=" not in chunk:
                continue
            key, vals = chunk.split("=", 1)
            out[key.strip()] = [v.strip() for v in vals.split(",") if v.strip()]
        return out


def _filters_dict_to_envelope(
    filters_dict: dict[str, list[Any]],
) -> Any:
    """Map a JSON-style filter dict to a `SearchFilter` dataclass."""
    if not FASTAPI_AVAILABLE:
        return None
    from cianfhoghlaim.storage.cognify.rules.semantic_search import (  # type: ignore[import-not-found]
        SearchFilter,
    )

    return SearchFilter(
        corpora=tuple(filters_dict.get("corpora", [])),
        subjects=tuple(filters_dict.get("subjects", [])),
        levels=tuple(filters_dict.get("levels", [])),
        languages=tuple(filters_dict.get("languages", [])),
        years=tuple(int(y) for y in filters_dict.get("years", [])),
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


if router is not None:

    @router.get("/semantic", response_model=SemanticSearchResponse)
    async def semantic_search(  # type: ignore[no-redef]
        q: str = Query(..., description="The search query (EN or GA)"),
        top_k: int = Query(10, description="Number of results to return"),
        embedder: str = Query(
            "BAAI/bge-m3",
            description="Either `BAAI/bge-m3` (multilingual) or `BAAI/bge-large-en-v1.5` (English-only)",
        ),
        filters: str = Query(
            "",
            description="JSON-encoded SearchFilter envelope (corpora, subjects, levels, languages, years)",
        ),
        window_size: int = Query(
            0,
            description="±N neighbour-window RAG (0 = disabled)",
        ),
        version: int | None = Query(
            None,
            description="Optional LanceDB version to pin the search to (time-travel RAG)",
        ),
    ) -> SemanticSearchResponse:
        """`GET /search/semantic?q=irish+gaelic` — returns top-10 results."""
        from cianfhoghlaim.storage.cognify.rules.semantic_search import (  # type: ignore[import-not-found]
            SearchResult as _SR,
            semantic_search as _do_search,
            ingest_search_telemetry,
        )

        if not q.strip():
            raise HTTPException(status_code=400, detail="query parameter `q` is required")  # type: ignore[misc]

        try:
            filters_dict = _parse_filter_string(filters)
            envelope = _filters_dict_to_envelope(filters_dict)
            results: list[_SR] = _do_search(
                q,
                top_k=top_k,
                model=embedder,
                filters=envelope,
                window_size=window_size,
                version=version,
            )
        except Exception as e:  # noqa: BLE001 — degrade gracefully
            logger.error("api_search_failed", err=str(e), q=q)
            raise HTTPException(status_code=500, detail=str(e))  # type: ignore[misc]

        return SemanticSearchResponse(
            results=[
                {
                    "chunk_id": r.chunk_id,
                    "text": r.text,
                    "source_url": r.source_url,
                    "corpus": r.corpus,
                    "subject": r.subject,
                    "level": r.level,
                    "year": r.year,
                    "language": r.language,
                    "score": r.score,
                    "highlight_en": r.highlight_en,
                    "highlight_ga": r.highlight_ga,
                    "model_name": r.model_name,
                }
                for r in results
            ],
            total=len(results),
            latency_ms=0.0,  # populated below
            search_id="",
            embedder=embedder,
        )

    @router.post("/semantic", response_model=SemanticSearchResponse)
    async def semantic_search_post(  # type: ignore[no-redef]
        body: SemanticSearchRequest,
    ) -> SemanticSearchResponse:
        """`POST /search/semantic` — JSON body variant of the same search."""
        from cianfhoghlaim.storage.cognify.rules.semantic_search import (  # type: ignore[import-not-found]
            SearchFilter as _SF,
            semantic_search as _do_search,
            ingest_search_telemetry,
        )

        envelope = _SF(
            corpora=tuple(body.filters.get("corpora", [])),
            subjects=tuple(body.filters.get("subjects", [])),
            levels=tuple(body.filters.get("levels", [])),
            languages=tuple(body.filters.get("languages", [])),
            years=tuple(int(y) for y in body.filters.get("years", [])),
        )
        results = _do_search(
            body.query,
            top_k=body.top_k,
            model=body.embedder,
            filters=envelope,
            window_size=body.window_size,
            version=body.version,
        )
        return SemanticSearchResponse(
            results=[
                {
                    "chunk_id": r.chunk_id,
                    "text": r.text,
                    "source_url": r.source_url,
                    "corpus": r.corpus,
                    "subject": r.subject,
                    "level": r.level,
                    "year": r.year,
                    "language": r.language,
                    "score": r.score,
                    "highlight_en": r.highlight_en,
                    "highlight_ga": r.highlight_ga,
                    "model_name": r.model_name,
                }
                for r in results
            ],
            total=len(results),
            latency_ms=0.0,
            search_id="",
            embedder=body.embedder,
        )


__all__ = [
    "router",
    "SemanticSearchResponse",
    "SemanticSearchRequest",
    "FASTAPI_AVAILABLE",
]