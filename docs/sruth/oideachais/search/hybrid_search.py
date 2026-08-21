"""
Hybrid Search Engine.

Configurable hybrid search combining semantic (vector) and keyword search
with adjustable weighting based on genizah_search patterns.
"""

from __future__ import annotations

import asyncio
import logging
import math
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class SearchFilters:
    """Filters for search queries."""

    subject: Optional[str] = None
    level: Optional[str] = None
    source_type: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    strand: Optional[str] = None
    has_irish: Optional[bool] = None


@dataclass
class SearchResult:
    """A single search result."""

    doc_id: str
    title: str
    content: str
    score: float

    # Metadata
    subject: Optional[str] = None
    level: Optional[str] = None
    source_type: Optional[str] = None

    # Score breakdown
    semantic_score: Optional[float] = None
    keyword_score: Optional[float] = None

    # Highlight snippets
    highlights: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "content": self.content[:500],  # Truncate for response
            "score": self.score,
            "subject": self.subject,
            "level": self.level,
            "source_type": self.source_type,
            "semantic_score": self.semantic_score,
            "keyword_score": self.keyword_score,
            "highlights": self.highlights,
        }


@dataclass
class HybridSearchResult:
    """Result of a hybrid search query."""

    results: list[SearchResult]
    total: int
    page: int
    page_size: int
    total_pages: int

    # Search parameters
    query: str
    weights: dict[str, float]
    filters: Optional[SearchFilters] = None

    # Performance metrics
    semantic_time_ms: float = 0.0
    keyword_time_ms: float = 0.0
    total_time_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "results": [r.to_dict() for r in self.results],
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
            "query": self.query,
            "weights": self.weights,
            "performance": {
                "semantic_time_ms": self.semantic_time_ms,
                "keyword_time_ms": self.keyword_time_ms,
                "total_time_ms": self.total_time_ms,
            },
        }


class HybridSearchEngine:
    """
    Configurable hybrid search engine.

    Combines:
    - Semantic search via vector store (LanceDB/Qdrant)
    - Keyword search via text store (Elasticsearch)

    With configurable weighting and score normalization.
    """

    def __init__(
        self,
        vector_store: Any = None,
        text_store: Any = None,
        default_semantic_weight: float = 0.7,
        default_keyword_weight: float = 0.3,
    ):
        """
        Initialize hybrid search engine.

        Args:
            vector_store: Vector database client
            text_store: Text search client (Elasticsearch)
            default_semantic_weight: Default weight for semantic search
            default_keyword_weight: Default weight for keyword search
        """
        self.vector_store = vector_store
        self.text_store = text_store
        self.default_semantic_weight = default_semantic_weight
        self.default_keyword_weight = default_keyword_weight

    async def search(
        self,
        query: str,
        semantic_weight: Optional[float] = None,
        keyword_weight: Optional[float] = None,
        filters: Optional[SearchFilters] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> HybridSearchResult:
        """
        Execute hybrid search with configurable weighting.

        Args:
            query: Search query
            semantic_weight: Weight for semantic search (0-1)
            keyword_weight: Weight for keyword search (0-1)
            filters: Optional search filters
            page: Page number (1-indexed)
            page_size: Results per page

        Returns:
            HybridSearchResult with combined results
        """
        import time

        start_time = time.time()

        # Use defaults if not specified
        sem_weight = semantic_weight or self.default_semantic_weight
        kw_weight = keyword_weight or self.default_keyword_weight

        # Normalize weights
        total_weight = sem_weight + kw_weight
        if total_weight > 0:
            sem_weight = sem_weight / total_weight
            kw_weight = kw_weight / total_weight

        # Fetch more results than needed for combining
        fetch_size = page_size * 3

        # Run searches in parallel
        semantic_task = self._semantic_search(query, fetch_size, filters)
        keyword_task = self._keyword_search(query, fetch_size, filters)

        (semantic_results, semantic_time), (keyword_results, keyword_time) = await asyncio.gather(
            self._timed(semantic_task),
            self._timed(keyword_task),
        )

        # Combine results with RRF (Reciprocal Rank Fusion)
        combined = self._combine_results(
            semantic_results,
            keyword_results,
            sem_weight,
            kw_weight,
        )

        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        paged_results = combined[start:end]

        total_time = (time.time() - start_time) * 1000

        return HybridSearchResult(
            results=paged_results,
            total=len(combined),
            page=page,
            page_size=page_size,
            total_pages=math.ceil(len(combined) / page_size),
            query=query,
            weights={"semantic": sem_weight, "keyword": kw_weight},
            filters=filters,
            semantic_time_ms=semantic_time,
            keyword_time_ms=keyword_time,
            total_time_ms=total_time,
        )

    async def _timed(self, coro) -> tuple[Any, float]:
        """Execute coroutine and return result with timing."""
        import time

        start = time.time()
        result = await coro
        elapsed = (time.time() - start) * 1000
        return result, elapsed

    async def _semantic_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[SearchFilters],
    ) -> list[SearchResult]:
        """Execute semantic search via vector store."""
        if not self.vector_store:
            return []

        try:
            # Build filter dict
            filter_dict = {}
            if filters:
                if filters.subject:
                    filter_dict["subject"] = filters.subject
                if filters.level:
                    filter_dict["level"] = filters.level
                if filters.source_type:
                    filter_dict["source_type"] = filters.source_type

            results = await self.vector_store.search(
                query,
                top_k=top_k,
                filters=filter_dict if filter_dict else None,
            )

            return [
                SearchResult(
                    doc_id=r.get("id", ""),
                    title=r.get("title", ""),
                    content=r.get("content", ""),
                    score=r.get("score", 0.0),
                    subject=r.get("subject"),
                    level=r.get("level"),
                    source_type=r.get("source_type"),
                    semantic_score=r.get("score", 0.0),
                )
                for r in results
            ]

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    async def _keyword_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[SearchFilters],
    ) -> list[SearchResult]:
        """Execute keyword search via text store."""
        if not self.text_store:
            return []

        try:
            results = await self.text_store.search(
                query,
                size=top_k,
                filters=filters,
            )

            return [
                SearchResult(
                    doc_id=r.get("id", ""),
                    title=r.get("title", ""),
                    content=r.get("content", ""),
                    score=r.get("score", 0.0),
                    subject=r.get("subject"),
                    level=r.get("level"),
                    source_type=r.get("source_type"),
                    keyword_score=r.get("score", 0.0),
                    highlights=r.get("highlights", []),
                )
                for r in results
            ]

        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []

    def _combine_results(
        self,
        semantic_results: list[SearchResult],
        keyword_results: list[SearchResult],
        semantic_weight: float,
        keyword_weight: float,
    ) -> list[SearchResult]:
        """
        Combine results using weighted Reciprocal Rank Fusion.

        RRF score = weight * 1/(k + rank)
        where k is a constant (60 by default)
        """
        k = 60  # RRF constant

        # Build score maps
        combined_scores: dict[str, float] = {}
        doc_map: dict[str, SearchResult] = {}

        # Process semantic results
        for rank, result in enumerate(semantic_results, 1):
            rrf_score = semantic_weight * (1 / (k + rank))
            combined_scores[result.doc_id] = combined_scores.get(result.doc_id, 0) + rrf_score
            doc_map[result.doc_id] = result

        # Process keyword results
        for rank, result in enumerate(keyword_results, 1):
            rrf_score = keyword_weight * (1 / (k + rank))
            combined_scores[result.doc_id] = combined_scores.get(result.doc_id, 0) + rrf_score

            # Merge data if we already have this doc
            if result.doc_id in doc_map:
                existing = doc_map[result.doc_id]
                existing.keyword_score = result.keyword_score
                existing.highlights = result.highlights
            else:
                doc_map[result.doc_id] = result

        # Create final sorted list
        sorted_ids = sorted(
            combined_scores.keys(),
            key=lambda x: combined_scores[x],
            reverse=True,
        )

        return [
            SearchResult(
                doc_id=doc_id,
                title=doc_map[doc_id].title,
                content=doc_map[doc_id].content,
                score=combined_scores[doc_id],
                subject=doc_map[doc_id].subject,
                level=doc_map[doc_id].level,
                source_type=doc_map[doc_id].source_type,
                semantic_score=doc_map[doc_id].semantic_score,
                keyword_score=doc_map[doc_id].keyword_score,
                highlights=doc_map[doc_id].highlights,
            )
            for doc_id in sorted_ids
        ]

    async def adjust_weights(
        self,
        query: str,
    ) -> tuple[float, float]:
        """
        Dynamically adjust weights based on query characteristics.

        Returns:
            Tuple of (semantic_weight, keyword_weight)
        """
        # Heuristics for weight adjustment
        query_lower = query.lower()

        # Exact phrase queries favor keyword search
        if '"' in query:
            return 0.3, 0.7

        # Learning outcome codes favor keyword search
        import re

        if re.search(r"[A-Z]{2,3}_[A-Z]{2,4}_[A-Z]_\d+", query):
            return 0.4, 0.6

        # Question words favor semantic search
        question_words = ["what", "why", "how", "explain", "describe"]
        if any(word in query_lower for word in question_words):
            return 0.8, 0.2

        # Short queries (1-2 words) favor keyword
        if len(query.split()) <= 2:
            return 0.4, 0.6

        # Default balanced weights
        return self.default_semantic_weight, self.default_keyword_weight
