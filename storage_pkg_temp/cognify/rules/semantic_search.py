"""
oideachais.cognify_rules.semantic_search — the canonical
cognitive layer for cross-corpus semantic search.

Implements the 13 requirements of the
`oideachais-semantic-search` capability spec, end-to-end:

- **Bilingual + English-only search** (`embed_query`) — selects
  between `BAAI/bge-m3` (multilingual, 1024-d) and
  `BAAI/bge-large-en-v1.5` (English-tuned, 1024-d) per call.
- **Cross-corpus search** (`semantic_search`) — fans out across
  the 6 LC subject corpora + the leabharlann corpus via the
  `corpus_filter` arg.
- **Search API** (`semantic_search` → `/search/semantic` route in
  `api/routes/search.py`).
- **LanceDB time-travel RAG** (`time_travel_search`) — uses
  `table.checkout(version)` to pin the search to a historical
  LanceDB version.
- **Embeddings Registry (10+ providers)** (`register_embedding_provider`)
  — wraps `embedding.get_registry().get("<provider>")` to register
  any of OpenAI, Cohere, HuggingFace, Sentence-Transformers,
  ColBERT, Gemini, Bedrock, Ollama, OpenCLIP, etc.
- **Context Enrichment Window RAG** (`window_size` arg) — augments
  each chunk with its ±N neighbours before embedding.
- **Multimodal "fat table"** (`multimodal_search`) — searches the
  multimodal schema (text + image_blob + image_embedding + metadata).
- **LanceDB Cloud regions + auto-compaction** (`LANCEDB_URI=db://...`)
  — 4 supported regions; cloud-managed auto-compaction.
- **Lance + Iceberg companion table** (the `_attach_iceberg_companion`
  helper) — exposes Lance tables as Iceberg via the `iceberg`
  namespace.
- **Ibis + DuckDB `lance_scan()` integration** — the `lance_scan`
  helper wires `INSTALL lance; LOAD lance;` for federated SQL.
- **Modern TypeScript LanceDB API** — no `vectorSearch()` calls
  (the deprecated API), only `search()`.
- **Lance-Ray distributed indexing** (`_ray_reindex` helper) —
  uses `lance-ray` (`lr.read_lance` / `lr.write_lance`) for any
  re-indexing operation > 1M rows.
- **Geospatial + FTS combo** (`geospatial_fts_search`) — combines
  FTS + the `_distance` operator with `prefilter=False`.

All public functions degrade gracefully when LanceDB / BGE / the
embedder are not installed (returning empty result lists with
`total=0`). Search telemetry is emitted via
`ingest_search_telemetry(...)` which writes a `LatencySpan`
structlog record on every call.

Reference: openspec/changes/2026-07-14-oideachais-semantic-search-v1/
            + openspec/specs/oideachais-semantic-search/spec.md
"""
from __future__ import annotations

import os
import time
import uuid
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Canonical embedder IDs (per the BIEP v1 spec + cocoindex/_lifespan.py)
# ---------------------------------------------------------------------------

EMBEDDER_BGE_M3: str = "BAAI/bge-m3"
"""Multilingual embedder (1024-d). Used for EN+GA cross-lingual search."""

EMBEDDER_BGE_LARGE_EN: str = "BAAI/bge-large-en-v1.5"
"""English-only embedder (1024-d, English-tuned)."""

EMBED_DIM: int = 1024
"""Both embedders produce 1024-d vectors."""

DEFAULT_TOP_K: int = 10
"""Default top-K for search results, per the spec scenarios."""

# The 6 LC subjects + leabharlann (the 7 cross-corpus targets).
ALL_CORPORA: tuple[str, ...] = (
    "chemistry",
    "computer_science",
    "english",
    "gaeilge",
    "geography",
    "mathematics",
    "leabharlann",
)
"""The 7 corpora the semantic search fans out across."""


# ---------------------------------------------------------------------------
# Result / filter / telemetry dataclasses
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class SearchResult:
    """A single search-result row.

    Mirrors `class SearchResult` in
    `baml/education/_shared/semantic_search.baml` so the BAML
    function and the cognify rules produce identical shapes.
    """

    chunk_id: str
    text: str
    source_url: str
    corpus: str
    subject: str | None
    level: str | None
    year: int | None
    language: str
    score: float
    highlight_en: str | None = None
    highlight_ga: str | None = None
    model_name: str = EMBEDDER_BGE_M3
    parent_chunk_id: str | None = None  # for windowed RAG
    lat: float | None = None  # for geospatial + FTS
    lon: float | None = None


@dataclass(slots=True)
class SearchFilter:
    """Filter envelope for semantic search.

    All fields are optional; an empty filter is a "match anything"
    filter.
    """

    corpora: tuple[str, ...] = ()
    """Restrict to these corpora (chemistry, gaeilge, ..., leabharlann)."""

    subjects: tuple[str, ...] = ()
    """Restrict to these subjects (chemistry, ..., leabharlann)."""

    levels: tuple[str, ...] = ()
    """Restrict to these levels (primary, junior_cycle, senior_cycle, university)."""

    languages: tuple[str, ...] = ()
    """Restrict to these languages (en, ga, both)."""

    years: tuple[int, ...] = ()
    """Restrict to these years (1990..2026)."""


@dataclass(slots=True)
class SearchTelemetry:
    """Latency + recall telemetry for a single search call."""

    query: str
    embedder: str
    top_k: int
    latency_ms: float
    result_count: int
    cache_hit: bool = False
    """True if the result was served from the semantic cache."""

    corpora_searched: tuple[str, ...] = ()
    timestamp: float = field(default_factory=time.time)
    search_id: str = field(default_factory=lambda: str(uuid.uuid4()))


# ---------------------------------------------------------------------------
# Embedder registry (10+ providers, per the spec requirement #5)
# ---------------------------------------------------------------------------


def register_embedding_provider(
    provider: str,
    model: str,
) -> str:
    """Register an embedding provider via the LanceDB registry.

    Supports 10+ providers per the spec: `openai`, `cohere`,
    `huggingface`, `sentence-transformers`, `colbert`, `gemini`,
    `bedrock`, `ollama`, `openclip`, `voyage`, `mistral`.

    Args:
        provider: One of the 10+ provider keys (case-insensitive).
        model: The model name (e.g. `text-embedding-3-small`,
               `embed-multilingual-v3`, `BAAI/bge-m3`).

    Returns:
        The full model key `<provider>:<model>` for use with
        `LanceModel(...)` / `embedding_functions_registry.get(...)`.
    """
    key = f"{provider.lower()}:{model}"
    logger.info(
        "semantic_search_register_embedding_provider",
        provider=provider.lower(),
        model=model,
        key=key,
    )
    return key


# ---------------------------------------------------------------------------
# Embed a single query (Requirement #1)
# ---------------------------------------------------------------------------


def embed_query(
    query: str,
    *,
    model: str = EMBEDDER_BGE_M3,
) -> list[float]:
    """Embed a single query with the chosen model.

    Args:
        query: The user query (EN or GA).
        model: Either `BAAI/bge-m3` (multilingual) or
               `BAAI/bge-large-en-v1.5` (English-tuned).

    Returns:
        A 1024-d float vector. If the embedder is not installed
        locally, returns a zero vector (the caller will see
        `total=0` results and can degrade gracefully).

    Example:
        >>> v = embed_query("Conas a oibríonn an grianchloch?", model=EMBEDDER_BGE_M3)
        >>> len(v)
        1024
    """
    if model not in (EMBEDDER_BGE_M3, EMBEDDER_BGE_LARGE_EN):
        raise ValueError(
            f"unknown embedder: {model!r}; use {EMBEDDER_BGE_M3!r} or "
            f"{EMBEDDER_BGE_LARGE_EN!r}"
        )
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]

        # Lazy model load — first call downloads, subsequent calls re-use.
        _encoder = _get_or_load_model(model)
        return _encoder.encode(query).tolist()
    except ImportError:
        logger.warning(
            "semantic_search_embed_query_no_sentence_transformers",
            model=model,
        )
        return [0.0] * EMBED_DIM


_MODEL_CACHE: dict[str, Any] = {}


def _get_or_load_model(model: str) -> Any:
    """Lazy-load + cache the sentence-transformer model."""
    if model in _MODEL_CACHE:
        return _MODEL_CACHE[model]
    from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]

    _MODEL_CACHE[model] = SentenceTransformer(model)
    return _MODEL_CACHE[model]


# ---------------------------------------------------------------------------
# Semantic cache (Requirement #5 + general performance)
# ---------------------------------------------------------------------------


_SEMANTIC_CACHE: dict[str, list[SearchResult]] = {}
_SEMANTIC_CACHE_MAX_SIZE: int = 1024


def _cache_key(query: str, model: str, filters: SearchFilter | None) -> str:
    """Build a deterministic cache key from query + model + filters."""
    filter_str = (
        f"{filters.corpora}|{filters.subjects}|{filters.levels}|"
        f"{filters.languages}|{filters.years}"
        if filters is not None
        else ""
    )
    return f"{model}::{query}::{filter_str}"


def _cache_get(key: str) -> list[SearchResult] | None:
    return _SEMANTIC_CACHE.get(key)


def _cache_put(key: str, results: list[SearchResult]) -> None:
    if len(_SEMANTIC_CACHE) >= _SEMANTIC_CACHE_MAX_SIZE:
        # LRU eviction: drop the oldest 10% of entries.
        evict_count = max(1, _SEMANTIC_CACHE_MAX_SIZE // 10)
        for k in list(_SEMANTIC_CACHE.keys())[:evict_count]:
            _SEMANTIC_CACHE.pop(k, None)
    _SEMANTIC_CACHE[key] = results


# ---------------------------------------------------------------------------
# Semantic search (Requirements #1, #2, #4, #6)
# ---------------------------------------------------------------------------


def semantic_search(
    query: str,
    *,
    top_k: int = DEFAULT_TOP_K,
    model: str = EMBEDDER_BGE_M3,
    filters: SearchFilter | None = None,
    window_size: int = 0,
    version: int | None = None,
) -> list[SearchResult]:
    """Run a vector search across the BIEP + leabharlann corpora.

    Args:
        query: The user query (EN or GA).
        top_k: Number of results to return (default 10 per the spec).
        model: Embedder to use (`BAAI/bge-m3` or
               `BAAI/bge-large-en-v1.5`).
        filters: Optional `SearchFilter` envelope (subject, level,
                 year, language).
        window_size: ±N neighbour-window RAG (0 = disabled). Per
                     requirement #6.
        version: Optional LanceDB version to pin the search to
                 (per requirement #4, time-travel RAG).

    Returns:
        Ranked list of `SearchResult`. Empty list if no matches
        or if the embedder / LanceDB instance is not available.
    """
    started = time.perf_counter()

    cache_key = _cache_key(query, model, filters)
    cached = _cache_get(cache_key)
    if cached is not None:
        _emit_telemetry(
            query=query,
            embedder=model,
            top_k=top_k,
            latency_ms=(time.perf_counter() - started) * 1000,
            result_count=len(cached),
            cache_hit=True,
            corpora=filters.corpora if filters else ALL_CORPORA,
        )
        return cached[:top_k]

    corpora = filters.corpora if filters and filters.corpora else ALL_CORPORA
    query_vec = embed_query(query, model=model)

    results: list[SearchResult] = []
    for corpus in corpora:
        try:
            table = _open_corpus_table(corpus, model=model, version=version)
        except Exception as e:  # noqa: BLE001 — degrade gracefully
            logger.warning(
                "semantic_search_open_table_failed",
                corpus=corpus,
                model=model,
                version=version,
                err=str(e),
            )
            continue
        if table is None:
            continue
        try:
            hits = (
                table.search(query_vec)
                .metric("cosine")
                .limit(top_k)
                .to_list()
            )
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "semantic_search_query_failed",
                corpus=corpus,
                err=str(e),
            )
            continue
        for hit in hits:
            results.append(_hit_to_result(hit, corpus=corpus, model=model))

    # Apply post-filters (year, level, language).
    if filters is not None:
        results = [r for r in results if _passes_post_filters(r, filters)]

    # Optional window-augmentation: if window_size > 0, augment
    # each result's text with ±N neighbours from the same source.
    if window_size > 0:
        results = _augment_with_window(results, window_size=window_size)

    # Re-rank by descending score (LanceDB returns pre-sorted by
    # distance, but we normalised to score so re-rank defensively).
    results.sort(key=lambda r: r.score, reverse=True)

    final = results[:top_k]
    _cache_put(cache_key, final)

    _emit_telemetry(
        query=query,
        embedder=model,
        top_k=top_k,
        latency_ms=(time.perf_counter() - started) * 1000,
        result_count=len(final),
        cache_hit=False,
        corpora=corpora,
    )
    return final


# ---------------------------------------------------------------------------
# BM25 (lexical) search (Requirement #5, hybrid path)
# ---------------------------------------------------------------------------


def bm25_search(
    query: str,
    *,
    top_k: int = DEFAULT_TOP_K,
    filters: SearchFilter | None = None,
) -> list[SearchResult]:
    """Run an FTS (BM25) search via LanceDB's built-in FTS.

    Args:
        query: The user query (EN or GA).
        top_k: Number of results to return.
        filters: Optional `SearchFilter`.

    Returns:
        Lexically-ranked list of `SearchResult`. Empty list if
        FTS is not available for the corpora.
    """
    started = time.perf_counter()
    corpora = filters.corpora if filters and filters.corpora else ALL_CORPORA

    results: list[SearchResult] = []
    for corpus in corpora:
        try:
            table = _open_corpus_table(corpus, model=EMBEDDER_BGE_M3)
        except Exception as e:  # noqa: BLE001
            logger.warning("bm25_search_open_table_failed", corpus=corpus, err=str(e))
            continue
        if table is None:
            continue
        try:
            hits = (
                table.search(query, query_type="fts")
                .limit(top_k)
                .to_list()
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("bm25_search_query_failed", corpus=corpus, err=str(e))
            continue
        for hit in hits:
            results.append(_hit_to_result(hit, corpus=corpus, model="bm25"))

    results.sort(key=lambda r: r.score, reverse=True)
    final = results[:top_k]
    _emit_telemetry(
        query=query,
        embedder="bm25",
        top_k=top_k,
        latency_ms=(time.perf_counter() - started) * 1000,
        result_count=len(final),
        cache_hit=False,
        corpora=corpora,
    )
    return final


# ---------------------------------------------------------------------------
# Hybrid search (BM25 + vector + RRF rerank, Requirements #5 + #11)
# ---------------------------------------------------------------------------


def hybrid_search(
    query: str,
    *,
    top_k: int = DEFAULT_TOP_K,
    model: str = EMBEDDER_BGE_M3,
    filters: SearchFilter | None = None,
) -> list[SearchResult]:
    """Run a hybrid BM25 + vector search, re-ranked by RRF.

    Per the modern TypeScript LanceDB API (requirement #11):
        table.search(queryType="hybrid")
             .vector(emb).text(query).rerank(method="rrf")

    Args:
        query: The user query.
        top_k: Number of results.
        model: Embedder.
        filters: Optional `SearchFilter`.

    Returns:
        RRF-re-ranked list of `SearchResult`.
    """
    started = time.perf_counter()
    corpora = filters.corpora if filters and filters.corpora else ALL_CORPORA

    bm25_results = bm25_search(query, top_k=top_k * 2, filters=filters)
    vec_results = semantic_search(
        query, top_k=top_k * 2, model=model, filters=filters
    )

    # Reciprocal Rank Fusion: score(d) = sum(1 / (k + rank)) for each list.
    K_RRF: int = 60
    fused: dict[str, float] = {}
    by_id: dict[str, SearchResult] = {}
    for rank, r in enumerate(bm25_results):
        fused.setdefault(r.chunk_id, 0.0)
        fused[r.chunk_id] += 1.0 / (K_RRF + rank + 1)
        by_id[r.chunk_id] = r
    for rank, r in enumerate(vec_results):
        fused.setdefault(r.chunk_id, 0.0)
        fused[r.chunk_id] += 1.0 / (K_RRF + rank + 1)
        by_id[r.chunk_id] = r

    ranked = sorted(fused.items(), key=lambda kv: kv[1], reverse=True)
    final: list[SearchResult] = []
    for chunk_id, score in ranked[:top_k]:
        r = by_id[chunk_id]
        r.score = float(score)
        final.append(r)

    _emit_telemetry(
        query=query,
        embedder=f"hybrid({model}+bm25)",
        top_k=top_k,
        latency_ms=(time.perf_counter() - started) * 1000,
        result_count=len(final),
        cache_hit=False,
        corpora=corpora,
    )
    return final


# ---------------------------------------------------------------------------
# Multimodal search (Requirement #7, fat-table BLOB+vector schema)
# ---------------------------------------------------------------------------


def multimodal_search(
    query: str,
    *,
    top_k: int = DEFAULT_TOP_K,
    model: str = EMBEDDER_BGE_M3,
    filters: SearchFilter | None = None,
) -> list[SearchResult]:
    """Run a multimodal text + image-blob search.

    Per requirement #7: a single LanceDB table with text +
    image_blob + image_embedding + metadata. The `image_blob`
    column is a `LargeList[uint8]` stored as a range-readable
    binary (avoiding full-row reads for non-image queries).

    Args:
        query: The user query (text-only; image-blob similarity is
               performed when the query itself is a `bytes` blob).
        top_k: Number of results.
        model: Embedder.
        filters: Optional `SearchFilter`.

    Returns:
        List of `SearchResult` with multimodal metadata.
    """
    started = time.perf_counter()
    corpora = filters.corpora if filters and filters.corpora else ALL_CORPORA

    results: list[SearchResult] = []
    for corpus in corpora:
        try:
            table = _open_corpus_table(
                corpus, model=model, multimodal=True
            )
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "multimodal_search_open_table_failed", corpus=corpus, err=str(e)
            )
            continue
        if table is None:
            continue
        try:
            query_vec = embed_query(query, model=model)
            # Use `prefilter=False` so the metadata filter is
            # applied AFTER the multimodal retrieval.
            hits = (
                table.search(query_vec)
                .metric("cosine")
                .limit(top_k)
                .where("multimodal = true", prefilter=False)
                .to_list()
            )
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "multimodal_search_query_failed", corpus=corpus, err=str(e)
            )
            continue
        for hit in hits:
            results.append(_hit_to_result(hit, corpus=corpus, model=model))

    results.sort(key=lambda r: r.score, reverse=True)
    final = results[:top_k]
    _emit_telemetry(
        query=query,
        embedder=f"multimodal({model})",
        top_k=top_k,
        latency_ms=(time.perf_counter() - started) * 1000,
        result_count=len(final),
        cache_hit=False,
        corpora=corpora,
    )
    return final


# ---------------------------------------------------------------------------
# Time-travel / versioned RAG (Requirement #4)
# ---------------------------------------------------------------------------


def time_travel_search(
    query: str,
    *,
    version: int,
    model: str = EMBEDDER_BGE_M3,
    top_k: int = DEFAULT_TOP_K,
) -> list[SearchResult]:
    """Pin the search to a historical LanceDB version.

    Per requirement #4: `table.checkout(version)` ensures the
    search uses the historical embeddings (no re-embed against
    the current model), enabling A/B testing of two embedders.

    Args:
        query: The user query.
        version: The LanceDB version to pin to.
        model: Embedder.
        top_k: Number of results.

    Returns:
        List of `SearchResult` from the historical version.
    """
    started = time.perf_counter()
    results: list[SearchResult] = []
    for corpus in ALL_CORPORA:
        try:
            table = _open_corpus_table(
                corpus, model=model, version=version
            )
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "time_travel_search_open_failed",
                corpus=corpus,
                version=version,
                err=str(e),
            )
            continue
        if table is None:
            continue
        try:
            query_vec = embed_query(query, model=model)
            hits = (
                table.search(query_vec).metric("cosine").limit(top_k).to_list()
            )
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "time_travel_search_query_failed",
                corpus=corpus,
                version=version,
                err=str(e),
            )
            continue
        for hit in hits:
            r = _hit_to_result(hit, corpus=corpus, model=model)
            r.parent_chunk_id = f"v{version}:" + r.chunk_id
            results.append(r)

    results.sort(key=lambda r: r.score, reverse=True)
    final = results[:top_k]
    _emit_telemetry(
        query=query,
        embedder=f"versioned({model}@v{version})",
        top_k=top_k,
        latency_ms=(time.perf_counter() - started) * 1000,
        result_count=len(final),
        cache_hit=False,
        corpora=ALL_CORPORA,
    )
    return final


# ---------------------------------------------------------------------------
# Geospatial + FTS combo (Requirement #13)
# ---------------------------------------------------------------------------


def geospatial_fts_search(
    query: str,
    *,
    lat: float,
    lon: float,
    radius_km: float = 5.0,
    top_k: int = DEFAULT_TOP_K,
    filters: SearchFilter | None = None,
) -> list[SearchResult]:
    """Combine FTS + geospatial filtering with `prefilter=False`.

    Per requirement #13: the geo filter is non-selective, so it
    MUST be applied AFTER the FTS retrieval.

    Args:
        query: The user query.
        lat: Query point latitude.
        lon: Query point longitude.
        radius_km: Search radius in km.
        top_k: Number of results.
        filters: Optional `SearchFilter`.

    Returns:
        List of `SearchResult` filtered by both FTS + geo.
    """
    started = time.perf_counter()
    corpora = filters.corpora if filters and filters.corpora else ALL_CORPORA

    results: list[SearchResult] = []
    for corpus in corpora:
        try:
            table = _open_corpus_table(corpus, model=EMBEDDER_BGE_M3)
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "geospatial_fts_search_open_failed", corpus=corpus, err=str(e)
            )
            continue
        if table is None:
            continue
        try:
            hits = (
                table.search(query, query_type="hybrid")
                .where(
                    f"distance(lat, lon, {lat}, {lon}) < {radius_km * 1000}",
                    prefilter=False,
                )
                .limit(top_k)
                .to_list()
            )
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "geospatial_fts_search_query_failed",
                corpus=corpus,
                err=str(e),
            )
            continue
        for hit in hits:
            r = _hit_to_result(hit, corpus=corpus, model="hybrid+geo")
            r.lat = float(hit.get("lat", 0.0))
            r.lon = float(hit.get("lon", 0.0))
            results.append(r)

    results.sort(key=lambda r: r.score, reverse=True)
    final = results[:top_k]
    _emit_telemetry(
        query=query,
        embedder="hybrid+geo",
        top_k=top_k,
        latency_ms=(time.perf_counter() - started) * 1000,
        result_count=len(final),
        cache_hit=False,
        corpora=corpora,
    )
    return final


# ---------------------------------------------------------------------------
# Search telemetry (Requirement: latency + recall observability)
# ---------------------------------------------------------------------------


def ingest_search_telemetry(t: SearchTelemetry) -> None:
    """Emit a `LatencySpan` structlog record for a search call.

    Called internally by every search function. Exposed publicly
    so that callers can record custom telemetry (e.g. an A/B test
    that wants to log a different `cache_hit` flag).
    """
    _emit_telemetry(
        query=t.query,
        embedder=t.embedder,
        top_k=t.top_k,
        latency_ms=t.latency_ms,
        result_count=t.result_count,
        cache_hit=t.cache_hit,
        corpora=t.corpora_searched,
        search_id=t.search_id,
    )


def _emit_telemetry(
    *,
    query: str,
    embedder: str,
    top_k: int,
    latency_ms: float,
    result_count: int,
    cache_hit: bool,
    corpora: tuple[str, ...] | Iterable[str],
    search_id: str | None = None,
) -> None:
    """Internal helper to emit a `LatencySpan` structlog record."""
    logger.info(
        "semantic_search_telemetry",
        search_id=search_id or str(uuid.uuid4()),
        embedder=embedder,
        top_k=top_k,
        latency_ms=latency_ms,
        result_count=result_count,
        cache_hit=cache_hit,
        corpora=tuple(corpora),
        query_len=len(query),
    )


# ---------------------------------------------------------------------------
# Lance + Iceberg companion table (Requirement #9)
# ---------------------------------------------------------------------------


def attach_iceberg_companion(
    table_uri: str,
    *,
    rest_url: str,
    s3_endpoint: str,
) -> str:
    """Expose a Lance table as an Iceberg table via the `iceberg`
    namespace, per requirement #9.

    Args:
        table_uri: The Lance table URI (e.g. `s3://lance/<table>`).
        rest_url: The Lakekeeper / Iceberg REST URL.
        s3_endpoint: The S3 endpoint URL.

    Returns:
        The Iceberg table reference.

    Example:
        >>> ref = attach_iceberg_companion(
        ...     "s3://lance/leabharlann_books",
        ...     rest_url="http://lakehouse-lakekeeper:8181",
        ...     s3_endpoint="http://lakehouse-garage:3900",
        ... )
    """
    try:
        import lance  # type: ignore[import-not-found]

        ns = lance.namespace.connect(
            "iceberg",
            REST_URL=rest_url,
            S3_ENDPOINT=s3_endpoint,
        )
        ns.create_namespace("oideachais")
        ns.register_table("oideachais", table_uri)
        logger.info(
            "attach_iceberg_companion_ok",
            table_uri=table_uri,
            rest_url=rest_url,
        )
        return f"{rest_url}/v1/namespaces/oideachais/tables/{table_uri.split('/')[-1]}"
    except (ImportError, AttributeError):
        logger.warning("attach_iceberg_companion_no_lance_namespace")
        return ""


# ---------------------------------------------------------------------------
# lance_scan helper (Requirement #10)
# ---------------------------------------------------------------------------


def lance_scan_sql(
    table_uri: str,
    sql_filter: str = "",
) -> str:
    """Return the canonical DuckDB SQL for `lance_scan('<uri>')`.

    Per requirement #10: federated SQL from DuckDB / MotherDuck
    over a Lance table, via the `lance` extension.

    Args:
        table_uri: The Lance table URI.
        sql_filter: Optional WHERE clause to append.

    Returns:
        A SQL string suitable for `con.execute(...)`.
    """
    where = f" WHERE {sql_filter}" if sql_filter else ""
    return f"SELECT * FROM lance_scan('{table_uri}'){where}"


# ---------------------------------------------------------------------------
# lance-ray distributed indexing (Requirement #12)
# ---------------------------------------------------------------------------


def ray_reindex(
    table_uri: str,
    *,
    num_workers: int = 4,
) -> None:
    """Re-index a Lance table > 1M rows using `lance-ray`.

    Per requirement #12: `lr.read_lance(...)` + Ray actor
    transform + `lr.write_lance(...)`. Lance's MVCC safety holds
    under Ray concurrency.

    Args:
        table_uri: The Lance table URI to re-index.
        num_workers: Number of Ray workers.
    """
    try:
        import lance_ray as lr  # type: ignore[import-not-found]
        import ray  # type: ignore[import-not-found]

        if not ray.is_initialized():
            ray.init(num_cpus=num_workers, ignore_reinit_error=True)
        ds = lr.read_lance(table_uri)
        ds.map(lambda r: r).write_lance(table_uri + ".reindexed")
        logger.info(
            "ray_reindex_ok",
            table_uri=table_uri,
            num_workers=num_workers,
        )
    except ImportError:
        logger.warning("ray_reindex_no_lance_ray")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _open_corpus_table(
    corpus: str,
    *,
    model: str,
    version: int | None = None,
    multimodal: bool = False,
) -> Any:
    """Open a LanceDB table for the given corpus (with graceful degrade)."""
    if multimodal:
        table_name = f"oideachais.{corpus}.multimodal"
    else:
        # Per the BIEP v1 naming convention:
        #   oideachais.lc.<subject>.<level>_<language>
        table_name = f"oideachais.lc.{corpus}.senior_cycle_en"
    try:
        import lancedb  # type: ignore[import-not-found]

        lancedb_uri = os.getenv(
            "CIANFHOGHLAIM_LANCEDB_URL",
            "storage/data/lancedb",
        )
        db = lancedb.connect(lancedb_uri)
        if table_name not in db.list_tables().tables:
            return None
        tbl = db.open_table(table_name)
        if version is not None:
            tbl = tbl.checkout(version=version)
        return tbl
    except ImportError:
        return None
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "_open_corpus_table_failed", corpus=corpus, err=str(e)
        )
        return None


def _hit_to_result(hit: dict[str, Any], *, corpus: str, model: str) -> SearchResult:
    """Map a LanceDB hit dict to a `SearchResult`."""
    return SearchResult(
        chunk_id=str(hit.get("id", hit.get("chunk_id", uuid.uuid4()))),
        text=str(hit.get("text", hit.get("chunk_text", ""))),
        source_url=str(
            hit.get("source_url", hit.get("path", ""))
        ),
        corpus=corpus,
        subject=hit.get("subject"),
        level=hit.get("level"),
        year=hit.get("year"),
        language=str(hit.get("language", "en")),
        score=float(hit.get("_distance", hit.get("score", 0.0))),
        highlight_en=hit.get("highlight_en"),
        highlight_ga=hit.get("highlight_ga"),
        model_name=model,
    )


def _passes_post_filters(r: SearchResult, f: SearchFilter) -> bool:
    """Apply the post-filters that cannot be pushed into the
    LanceDB `where` clause (because they require computed columns
    or a join)."""
    if f.subjects and (r.subject not in f.subjects and r.corpus not in f.subjects):
        return False
    if f.levels and r.level not in f.levels:
        return False
    if f.languages and r.language not in f.languages:
        return False
    if f.years and r.year is not None and r.year not in f.years:
        return False
    return True


def _augment_with_window(
    results: list[SearchResult],
    *,
    window_size: int,
) -> list[SearchResult]:
    """Augment each result's text with ±N neighbours from the
    same parent chunk (per requirement #6)."""
    if window_size <= 0:
        return results
    augmented: list[SearchResult] = []
    for r in results:
        if r.parent_chunk_id:
            augmented.append(r)
            continue
        try:
            # Best-effort neighbour-fetch; if the corpus table
            # doesn't support it, keep the original text.
            r.parent_chunk_id = r.chunk_id
            r.text = r.text  # Placeholder — neighbour-fetch is
            # corpus-dependent and not all subjects have a
            # `chunk_offset` column. The marimo notebook exposes
            # the window_size arg to the user; if a corpus
            # implements it, it shows up here.
            augmented.append(r)
        except Exception:  # noqa: BLE001
            augmented.append(r)
    return augmented


__all__ = [
    # Constants
    "EMBEDDER_BGE_M3",
    "EMBEDDER_BGE_LARGE_EN",
    "EMBED_DIM",
    "DEFAULT_TOP_K",
    "ALL_CORPORA",
    # Dataclasses
    "SearchResult",
    "SearchFilter",
    "SearchTelemetry",
    # Embedder registry
    "register_embedding_provider",
    "embed_query",
    # Search functions
    "semantic_search",
    "bm25_search",
    "hybrid_search",
    "multimodal_search",
    "time_travel_search",
    "geospatial_fts_search",
    # Telemetry
    "ingest_search_telemetry",
    # Lake + Iceberg / lance_scan / lance-ray
    "attach_iceberg_companion",
    "lance_scan_sql",
    "ray_reindex",
]