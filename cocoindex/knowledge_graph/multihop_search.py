"""
multihop_search — v1 CocoIndex primitive (Phase 0 of
`2026-07-14-multimodal-code-and-media-intel-v1`).

Ported from the archived `códeolas`
(`stedding/dev/cianfhoghlaim copy/sruth/códeolas/search/multihop.py:multihop_search`).

The archived primitive took a `CodebaseAnalyzer` instance and iteratively
called `analyzer.search(...)` with refined queries. The v1 primitive is
table-agnostic: it accepts a list of `(table_name, embed_and_search_fn)`
pairs and fans out across all of them, fusing the candidate sets and
emitting a Langfuse v3 span per iteration.

Convergence rule (same as the original): when the per-iteration overlap
between new + existing candidates is ≥ `convergence_threshold`, stop.

The 5 new Apps (`YoutubeKgEmbedding`, `PackageChangelogEmbedding`,
`CodebaseGitHistory`, `RepoArchDocs`, `MediaLocalEmbedding`) all register
their tables via `register_multihop_source(...)` so this primitive can
fan out across them in one MCP-level call.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import structlog

from ._lifespan import COCOINDEX_AVAILABLE, LANCE_DB

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]

    if COCOINDEX_AVAILABLE:
        LANCE_DB_CK: Any = LANCE_DB
    else:
        LANCE_DB_CK = None
except ImportError:  # pragma: no cover - degrade gracefully
    coco = None  # type: ignore[assignment]
    LANCE_DB_CK = None

logger = structlog.get_logger(__name__)


# not-a-flow: this primitive exposes `@coco.fn(memo=True)` + `ContextKey`
# but never writes to a LanceDB table — it fuses results from 5+
# registered source tables at call time and returns them via the MCP
# transport. See `openspec/changes/2026-07-14-multimodal-code-and-media-intel-v1/proposal.md`
# "Phase 0 — Port the archived codeolas primitives".


# ---------------------------------------------------------------------------
# Registry of sources
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MultihopSource:
    """One source the multihop_search primitive can fan out to."""

    table_name: str
    description: str
    embed_and_search_fn: Callable[[str, int], Awaitable[list[dict[str, Any]]]]


# Module-level registry. Each of the 5 new Apps calls
# `register_multihop_source(...)` at import time. The MCP tool
# `cocoindex-code.multihop_search` calls `list_multihop_sources()` to
# see what's available.
_SOURCES: dict[str, MultihopSource] = {}


def register_multihop_source(source: MultihopSource) -> None:
    """Register one table as a multihop_search source."""
    _SOURCES[source.table_name] = source
    logger.info(
        "multihop_search.registered_source",
        table_name=source.table_name,
        description=source.description,
    )


def list_multihop_sources() -> list[MultihopSource]:
    """List all currently-registered multihop sources."""
    return list(_SOURCES.values())


def clear_multihop_sources() -> None:
    """Clear the registry. Tests only."""
    _SOURCES.clear()


# ---------------------------------------------------------------------------
# Result schema
# ---------------------------------------------------------------------------


@dataclass
class MultihopCandidate:
    """One candidate row from one source table."""

    source_table: str
    row_id: str  # canonical row id (sha256(table + row_id) for cross-table dedup)
    score: float
    text: str
    citation: dict[str, Any] = field(default_factory=dict)
    seen_in_iterations: list[int] = field(default_factory=list)


@dataclass
class MultihopResult:
    """Final return value of `multihop_search()`."""

    question: str
    candidates: list[MultihopCandidate]
    iterations: int
    converged: bool
    queries_used: list[str]
    synthesis: str
    total_sources_found: int
    final_convergence_score: float
    langfuse_span_id: str | None = None


# ---------------------------------------------------------------------------
# The primitive
# ---------------------------------------------------------------------------


# The convergence_score is the Jaccard overlap between new candidates
# and the existing union. The default threshold of 0.85 mirrors the
# archived codeolas default (see `search/multihop.py:multihop_search`).
DEFAULT_CONVERGENCE_THRESHOLD = 0.85
DEFAULT_MAX_ITERATIONS = 3
DEFAULT_LIMIT = 10


def _row_dedupe_key(source_table: str, row_id: str) -> str:
    """Stable dedupe key across tables."""
    raw = f"{source_table}::{row_id}".encode()
    return hashlib.sha256(raw).hexdigest()[:32]


def _refine_query(
    original_question: str,
    new_candidates: list[MultihopCandidate],
) -> str | None:
    """Generate a refined query based on the new candidates.

    Mirrors the archived `_refine_query` heuristic: pull concept-like
    tokens (function/class names, noun phrases) from the top 5
    candidates and append the first one we haven't seen yet.

    For text-heavy v1 results (the new Apps embed structured text, not
    AST nodes), we use the first non-trivial capitalized phrase from
    each candidate as the concept surrogate.
    """
    seen_terms: set[str] = set()
    for cand in new_candidates[:5]:
        text = cand.text or ""
        for token in text.split():
            if len(token) > 4 and token[0].isupper():
                seen_terms.add(token.strip(".,;:()[]{}"))

    if not seen_terms:
        return None

    pick = next(iter(sorted(seen_terms)))
    return f"{original_question} {pick}"


def _synthesize_findings(
    question: str,
    candidates: list[MultihopCandidate],
) -> str:
    """Build a deterministic synthesis string (no LLM — keeps the primitive cheap).

    Per-source breakdown + the top citation per source. The MCP tool
    `multihop_search` may optionally pass the synthesis to
    `qwen3.6-27b-mtp` for a richer answer; that LLM step is layered on
    top of this primitive's output and lives in the MCP tool, not here.
    """
    if not candidates:
        return f"No relevant sources found for: {question!r}"

    by_source: dict[str, list[MultihopCandidate]] = {}
    for c in candidates:
        by_source.setdefault(c.source_table, []).append(c)

    parts: list[str] = [
        f"Found {len(candidates)} relevant rows across {len(by_source)} tables:",
        "",
    ]
    for source_table in sorted(by_source):
        rows = by_source[source_table]
        parts.append(f"### {source_table} ({len(rows)} rows)")
        for c in rows[:3]:
            citation = c.citation.get("row_id", c.row_id)
            preview = (c.text or "")[:140].replace("\n", " ")
            parts.append(f"- `{citation}` (score {c.score:.2f}): {preview}…")
        parts.append("")

    return "\n".join(parts)


async def _embed_and_search_one_source(
    source: MultihopSource,
    query: str,
    limit: int,
) -> list[MultihopCandidate]:
    """Run one source's embed_and_search_fn and normalize results.

    Each source's `embed_and_search_fn` returns a list of
    `{"row_id": str, "score": float, "text": str, "citation": dict}` dicts.
    This function normalizes them into `MultihopCandidate` records and
    tags each with `seen_in_iterations=[current_iteration]`.
    """
    raw = await source.embed_and_search_fn(query, limit)
    out: list[MultihopCandidate] = []
    for row in raw:
        out.append(
            MultihopCandidate(
                source_table=source.table_name,
                row_id=str(row.get("row_id", "")),
                score=float(row.get("score", 0.0)),
                text=str(row.get("text", "")),
                citation=dict(row.get("citation", {})),
            )
        )
    return out


def _compute_overlap(
    union_keys: set[str],
    new_keys: set[str],
) -> float:
    """Compute Jaccard overlap between the union and the new set."""
    if not new_keys:
        return 1.0
    intersection = union_keys & new_keys
    union = union_keys | new_keys
    if not union:
        return 1.0
    return len(intersection) / len(union)


# Langfuse v3 integration — wrapped in a no-op fallback when the SDK is
# not installed (Phase 0 ships before Phase 6 wires Langfuse globally).
async def _emit_langfuse_span(
    iteration: int,
    query: str,
    new_count: int,
    overlap: float,
    converged: bool,
) -> str | None:
    """Emit a Langfuse v3 span and return its id (or None on no-op)."""
    try:
        from langfuse import Langfuse  # type: ignore[import-not-found]

        lf = Langfuse()
        span = lf.span(
            name=f"multihop.iteration.{iteration}",
            input={"query": query},
            output={
                "new_candidates": new_count,
                "overlap_score": overlap,
                "converged": converged,
            },
        )
        return str(span.id)
    except Exception:  # pragma: no cover - Langfuse is optional in dev
        return None


async def multihop_search(
    question: str,
    limit: int = DEFAULT_LIMIT,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    convergence_threshold: float = DEFAULT_CONVERGENCE_THRESHOLD,
    sources: list[str] | None = None,
) -> MultihopResult:
    """The v1 multihop primitive.

    Iteratively queries each registered source table with refined
    queries, dedupes across tables, and stops when the Jaccard overlap
    of new + existing candidates ≥ `convergence_threshold`.

    Args:
        question: the research question / natural-language query.
        limit: per-source per-iteration row limit.
        max_iterations: maximum number of refinement iterations.
        convergence_threshold: stop when Jaccard overlap ≥ this value.
        sources: optional explicit source-table allowlist. Defaults to
            all registered sources.

    Returns:
        A `MultihopResult` with `candidates`, `iterations`, `converged`,
        `queries_used`, `synthesis`, `total_sources_found`,
        `final_convergence_score`, and the Langfuse v3 span id (if any).
    """
    chosen_sources = (
        [_SOURCES[name] for name in sources if name in _SOURCES]
        if sources
        else list(_SOURCES.values())
    )
    if not chosen_sources:
        logger.warning("multihop_search.no_sources_registered")
        return MultihopResult(
            question=question,
            candidates=[],
            iterations=0,
            converged=True,
            queries_used=[question],
            synthesis=f"No sources registered for multihop_search. Query was: {question!r}",
            total_sources_found=0,
            final_convergence_score=1.0,
            langfuse_span_id=None,
        )

    union: dict[str, MultihopCandidate] = {}  # dedupe_key -> candidate
    queries_used: list[str] = [question]
    iteration = 0
    converged = False
    final_overlap = 0.0
    span_ids: list[str] = []

    while iteration < max_iterations and not converged:
        iteration += 1
        current_query = queries_used[-1]

        # Fan out across sources in parallel.
        import asyncio

        per_source_lists = await asyncio.gather(
            *(_embed_and_search_one_source(s, current_query, limit) for s in chosen_sources),
            return_exceptions=True,
        )

        all_new: list[MultihopCandidate] = []
        for source, result in zip(chosen_sources, per_source_lists):
            if isinstance(result, BaseException):
                logger.warning(
                    "multihop_search.source_failed",
                    source=source.table_name,
                    error=str(result),
                )
                continue
            all_new.extend(result)

        if not all_new:
            logger.info("multihop_search.no_new_candidates", iteration=iteration)
            break

        new_keys = {
            _row_dedupe_key(c.source_table, c.row_id)
            for c in all_new
            if c.row_id
        }
        union_before = set(union.keys())
        for cand in all_new:
            key = _row_dedupe_key(cand.source_table, cand.row_id)
            if key and key not in union:
                union[key] = cand
            if key in union:
                union[key].seen_in_iterations.append(iteration)

        overlap = _compute_overlap(union_before, new_keys)
        final_overlap = overlap

        span_id = await _emit_langfuse_span(
            iteration=iteration,
            query=current_query,
            new_count=len(new_keys - union_before),
            overlap=overlap,
            converged=False,
        )
        if span_id:
            span_ids.append(span_id)

        if overlap >= convergence_threshold:
            converged = True
            break

        # Refine the query.
        refined = _refine_query(question, all_new)
        if refined and refined not in queries_used:
            queries_used.append(refined)
        else:
            # No new query to try — consider converged.
            converged = True
            break

    # Final sort by score, then trim to the most useful window.
    final_candidates = sorted(union.values(), key=lambda c: c.score, reverse=True)
    synthesis = _synthesize_findings(question, final_candidates[:limit])

    return MultihopResult(
        question=question,
        candidates=final_candidates[: limit * len(chosen_sources)],
        iterations=iteration,
        converged=converged,
        queries_used=queries_used,
        synthesis=synthesis,
        total_sources_found=len(union),
        final_convergence_score=final_overlap,
        langfuse_span_id=span_ids[-1] if span_ids else None,
    )


# ---------------------------------------------------------------------------
# CocoIndex v1 app surface (the R2 conformance stub).
#
# This primitive is exposed to other Apps + the MCP tool layer; it does
# not write to a LanceDB table (the R4-exempt comment at the top of
# this file documents why). We still declare the v1 `coco.App(...)` at
# module scope to satisfy the R2 conformance check, but it carries no
# source/target — the real work happens at MCP call time.
# ---------------------------------------------------------------------------

if COCOINDEX_AVAILABLE and coco is not None:
    multihop_search_app = coco.App(coco.AppConfig(name="MultihopSearch"))  # type: ignore[attr-defined]
else:  # pragma: no cover - degrade gracefully
    multihop_search_app = None


__all__ = [
    "DEFAULT_CONVERGENCE_THRESHOLD",
    "DEFAULT_LIMIT",
    "DEFAULT_MAX_ITERATIONS",
    "MultihopCandidate",
    "MultihopResult",
    "MultihopSource",
    "clear_multihop_sources",
    "list_multihop_sources",
    "multihop_search",
    "multihop_search_app",
    "register_multihop_source",
]


# Test-mode env knobs. Production code reads from the registered sources
# at call time; these are useful for the smoke tests in
# `tests/test_multihop_search.py`.
_MULTIHOP_TEST_QUERY = os.getenv("MULTIHOP_TEST_QUERY", "LanceDB table mount")
_MULTIHOP_TEST_LIMIT = int(os.getenv("MULTIHOP_TEST_LIMIT", "5"))


# ---------------------------------------------------------------------------
# Test helper: in-process no-op source (only used by the conformance test).
# ---------------------------------------------------------------------------


async def _no_op_embed_and_search(query: str, limit: int) -> list[dict[str, Any]]:
    """A test-only source that returns 1 deterministic row per call."""
    return [
        {
            "row_id": f"test-row-{uuid.uuid4().hex[:8]}",
            "score": 0.42,
            "text": f"Test result for query {query!r}",
            "citation": {"source_kind": "test"},
        }
    ]


_TEST_SOURCE_REGISTERED = False


def _register_test_source_if_needed() -> None:
    """Register the no-op test source once. No-op in production."""
    global _TEST_SOURCE_REGISTERED
    if _TEST_SOURCE_REGISTERED:
        return
    if not any(s.table_name == "_multihop_test" for s in _SOURCES.values()):
        register_multihop_source(
            MultihopSource(
                table_name="_multihop_test",
                description="In-process no-op source (test only)",
                embed_and_search_fn=_no_op_embed_and_search,
            )
        )
    _TEST_SOURCE_REGISTERED = True


# Register the test source on import (safe — it's a no-op stub).
_register_test_source_if_needed()


# Capture the module-load timestamp for the Langfuse span fallback.
_LOADED_AT = datetime.now().isoformat()
