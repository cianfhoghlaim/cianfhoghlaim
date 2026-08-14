"""Memory router — routes agent queries to the right polyglot backend.

Per the `2026-08-14-firecrawl-corpus-and-portals` change. The
router takes a natural-language query + an optional intent hint,
then selects the right backend:

- **Temporal** ("What was the Dagster API in version 1.10?") →
  `Graphiti` (bi-temporal knowledge graph)
- **Vector** ("What's the relevant chunk for this code query?") →
  `LanceDB` (HNSW)
- **Graph** ("How does BAML ExtractCurriculumSyllabus relate to
  CocoIndex _lifespan.py?") → `Cognee` (cross-doc graph)
- **Hybrid** (default) → all 3 backends, merged + RRF-ranked
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# Intent patterns (simple regex-based heuristics)
TEMPORAL_PATTERNS = [
    r"\b(in|since|after|before|during|by|v\d+(\.\d+)*)\b",
    r"\b(version|release|changelog|deprecated|removed|added)\b",
    r"\b(history|previously|earlier|originally)\b",
    r"\b(timeline|when|did|was)\b",
]
GRAPH_PATTERNS = [
    r"\b(how does|relate|relationship|relationship between|connection)\b",
    r"\b(depends on|uses|imports|inherits|extends)\b",
    r"\b(compare|comparison|versus|vs\.?)\b",
]
VECTOR_PATTERNS = [
    r"\b(what is|what's|find|search|relevant)\b",
    r"\b(example|snippet|code|function|method)\b",
]


@dataclass(frozen=True)
class MemoryRouterResult:
    """The merged result of a polyglot memory query."""

    query: str
    intent: str  # "temporal" | "vector" | "graph" | "hybrid"
    graphiti_hits: list[Any] = field(default_factory=list)
    lancedb_hits: list[Any] = field(default_factory=list)
    cognee_hits: list[Any] = field(default_factory=list)
    merged: list[dict[str, Any]] = field(default_factory=list)


def _detect_intent(query: str) -> str:
    """Detect the intent from the query string."""
    q = query.lower()
    temporal_score = sum(1 for p in TEMPORAL_PATTERNS if re.search(p, q))
    graph_score = sum(1 for p in GRAPH_PATTERNS if re.search(p, q))
    vector_score = sum(1 for p in VECTOR_PATTERNS if re.search(p, q))

    scores = {
        "temporal": temporal_score,
        "graph": graph_score,
        "vector": vector_score,
    }
    intent = max(scores, key=scores.get)
    if scores[intent] == 0:
        return "hybrid"
    # If 2 backends tie, prefer hybrid
    top_score = scores[intent]
    if sum(1 for s in scores.values() if s == top_score) > 1:
        return "hybrid"
    return intent


def _embed_query(query: str) -> list[float]:
    """Embed a query using the shared BGE-M3 embedder (1024-d)."""
    try:
        from cianfhoghlaim.cocoindex._lifespan import embed as lifespan_embed

        return lifespan_embed(query)
    except ImportError:  # pragma: no cover
        return [0.0] * 1024


class MemoryRouter:
    """The polyglot memory router.

    Pick the right backend per intent, then merge + RRF-rank the
    results. The router is the canonical surface for every agent
    query against the agent reference corpus.
    """

    def __init__(
        self,
        graphiti: Any | None = None,
        lancedb: Any | None = None,
        cognee: Any | None = None,
    ) -> None:
        # Lazy import to keep module import-safe in CI
        from .cognee_store import CogneeMemoryStore
        from .graphiti_store import GraphitiMemoryStore
        from .lancedb_store import LanceDBMemoryStore

        self.graphiti = graphiti or GraphitiMemoryStore()
        self.lancedb = lancedb or LanceDBMemoryStore()
        self.cognee = cognee or CogneeMemoryStore()

    def route(self, query: str, *, k: int = 5) -> MemoryRouterResult:
        """Route a query to the right backend(s) + merge.

        Args:
            query: The natural-language query.
            k: The number of hits per backend (default 5).

        Returns:
            The merged `MemoryRouterResult`.
        """
        intent = _detect_intent(query)
        logger.info("memory_router.intent: %s (query=%s)", intent, query[:80])

        graphiti_hits: list[Any] = []
        lancedb_hits: list[Any] = []
        cognee_hits: list[Any] = []

        if intent in ("temporal", "hybrid"):
            graphiti_hits = self.graphiti.search(query, k=k)
        if intent in ("vector", "hybrid"):
            lancedb_hits = self.lancedb.search(query, k=k)
        if intent in ("graph", "hybrid"):
            cognee_hits = self.cognee.search(query, k=k)

        # Merge via Reciprocal Rank Fusion (RRF) — the canonical
        # ranking algorithm for hybrid search.
        merged = self._rrf_merge(
            graphiti_hits=graphiti_hits,
            lancedb_hits=lancedb_hits,
            cognee_hits=cognee_hits,
        )

        return MemoryRouterResult(
            query=query,
            intent=intent,
            graphiti_hits=graphiti_hits,
            lancedb_hits=lancedb_hits,
            cognee_hits=cognee_hits,
            merged=merged,
        )

    def _rrf_merge(
        self,
        *,
        graphiti_hits: list[Any],
        lancedb_hits: list[Any],
        cognee_hits: list[Any],
        k_rrf: int = 60,
    ) -> list[dict[str, Any]]:
        """Reciprocal Rank Fusion across the 3 backends.

        RRF score = sum(1 / (k_rrf + rank)) for each list that contains
        the same entity (matched by URL + entity name).
        """
        scores: dict[str, float] = {}
        sources: dict[str, list[str]] = {}

        def _add(hits: list[Any], backend_name: str) -> None:
            for rank, hit in enumerate(hits):
                # The entity key is the URL + the chunk/entity name
                if hasattr(hit, "url"):
                    key = f"{hit.url}|{getattr(hit, 'name', getattr(hit, 'chunk_text', ''))[:80]}"
                else:
                    key = str(rank)
                scores[key] = scores.get(key, 0.0) + 1.0 / (k_rrf + rank + 1)
                sources.setdefault(key, []).append(backend_name)

        _add(graphiti_hits, "graphiti")
        _add(lancedb_hits, "lancedb")
        _add(cognee_hits, "cognee")

        # Sort by score descending
        return [
            {"key": k, "score": v, "sources": sources.get(k, [])}
            for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True)
        ]


__all__ = ["MemoryRouter", "MemoryRouterResult", "_embed_query", "_detect_intent"]