"""
Curriculum Cache Manager.

Unified manager for multi-level caching with curriculum-specific optimizations.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Optional

import numpy as np

from .query_cache import QueryCache
from .embedding_cache import EmbeddingCache
from .llm_cache import LLMCache

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Configuration for curriculum cache manager."""

    # Query cache
    query_ttl: int = 3600  # 1 hour
    query_max_size: int = 10000

    # Embedding cache
    embedding_ttl: int = 604800  # 7 days
    embedding_max_size: int = 100000
    embedding_similarity_threshold: float = 0.95

    # LLM cache
    llm_ttl: int = 86400  # 24 hours
    llm_max_size: int = 5000

    # Curriculum-specific caches (longer TTLs)
    curriculum_code_ttl: int = 2592000  # 30 days
    prerequisite_chain_ttl: int = 2592000  # 30 days
    learning_outcome_ttl: int = 31536000  # 1 year


class CurriculumCacheManager:
    """
    Multi-level cache manager for curriculum RAG.

    Provides unified interface for:
    - Query result caching
    - Embedding caching with similarity lookup
    - LLM response caching
    - Curriculum-specific long-term caching
    """

    def __init__(self, config: Optional[CacheConfig] = None):
        """
        Initialize cache manager.

        Args:
            config: Cache configuration
        """
        self.config = config or CacheConfig()

        # Initialize caches
        self.query_cache = QueryCache(
            ttl_seconds=self.config.query_ttl,
            max_size=self.config.query_max_size,
        )
        self.embedding_cache = EmbeddingCache(
            ttl_seconds=self.config.embedding_ttl,
            max_size=self.config.embedding_max_size,
            similarity_threshold=self.config.embedding_similarity_threshold,
        )
        self.llm_cache = LLMCache(
            ttl_seconds=self.config.llm_ttl,
            max_size=self.config.llm_max_size,
        )

        # Curriculum-specific caches (reuse QueryCache with different TTLs)
        self.curriculum_code_cache = QueryCache(
            ttl_seconds=self.config.curriculum_code_ttl,
            max_size=50000,
        )
        self.prerequisite_cache = QueryCache(
            ttl_seconds=self.config.prerequisite_chain_ttl,
            max_size=10000,
        )
        self.learning_outcome_cache = QueryCache(
            ttl_seconds=self.config.learning_outcome_ttl,
            max_size=50000,
        )

    # =========================================================================
    # Query Cache Operations
    # =========================================================================

    async def get_query(
        self,
        query: str,
        mode: str,
        params: dict[str, Any],
    ) -> Optional[Any]:
        """Get cached query result."""
        return await self.query_cache.get(query, mode, params)

    async def set_query(
        self,
        query: str,
        mode: str,
        params: dict[str, Any],
        result: Any,
    ) -> None:
        """Cache query result."""
        await self.query_cache.set(query, mode, params, result)

    async def get_or_compute_query(
        self,
        query: str,
        mode: str,
        params: dict[str, Any],
        compute_fn: Callable,
    ) -> Any:
        """Get cached result or compute and cache."""
        cached = await self.get_query(query, mode, params)
        if cached is not None:
            return cached

        result = await compute_fn()
        await self.set_query(query, mode, params, result)
        return result

    # =========================================================================
    # Embedding Cache Operations
    # =========================================================================

    async def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get cached embedding by exact match."""
        return await self.embedding_cache.get(text)

    async def get_similar_embedding(
        self,
        embedding: np.ndarray,
    ) -> Optional[tuple[str, np.ndarray, float]]:
        """Find similar cached embedding."""
        return await self.embedding_cache.get_similar(embedding)

    async def set_embedding(
        self,
        text: str,
        embedding: np.ndarray,
    ) -> None:
        """Cache embedding."""
        await self.embedding_cache.set(text, embedding)

    async def set_embeddings_batch(
        self,
        texts: list[str],
        embeddings: np.ndarray,
    ) -> None:
        """Cache batch of embeddings."""
        await self.embedding_cache.set_batch(texts, embeddings)

    # =========================================================================
    # LLM Cache Operations
    # =========================================================================

    async def get_llm_response(
        self,
        messages: list[dict[str, str]],
        model: str,
        **kwargs,
    ) -> Optional[dict[str, Any]]:
        """Get cached LLM response."""
        return await self.llm_cache.get(messages, model, **kwargs)

    async def set_llm_response(
        self,
        messages: list[dict[str, str]],
        model: str,
        response: dict[str, Any],
        **kwargs,
    ) -> None:
        """Cache LLM response."""
        await self.llm_cache.set(messages, model, response, **kwargs)

    # =========================================================================
    # Curriculum-Specific Cache Operations
    # =========================================================================

    async def get_curriculum_code(self, code: str) -> Optional[dict[str, Any]]:
        """Get cached curriculum code data (e.g., TG_MAT_G_1.1)."""
        return await self.curriculum_code_cache.get(code, "curriculum_code", {})

    async def set_curriculum_code(
        self,
        code: str,
        data: dict[str, Any],
    ) -> None:
        """Cache curriculum code data."""
        await self.curriculum_code_cache.set(code, "curriculum_code", {}, data)

    async def get_prerequisite_chain(
        self,
        concept_id: str,
    ) -> Optional[list[dict[str, Any]]]:
        """Get cached prerequisite chain."""
        return await self.prerequisite_cache.get(
            concept_id, "prerequisite", {}
        )

    async def set_prerequisite_chain(
        self,
        concept_id: str,
        chain: list[dict[str, Any]],
    ) -> None:
        """Cache prerequisite chain."""
        await self.prerequisite_cache.set(
            concept_id, "prerequisite", {}, chain
        )

    async def get_learning_outcome(
        self,
        lo_code: str,
    ) -> Optional[dict[str, Any]]:
        """Get cached learning outcome data."""
        return await self.learning_outcome_cache.get(
            lo_code, "learning_outcome", {}
        )

    async def set_learning_outcome(
        self,
        lo_code: str,
        data: dict[str, Any],
    ) -> None:
        """Cache learning outcome data."""
        await self.learning_outcome_cache.set(
            lo_code, "learning_outcome", {}, data
        )

    # =========================================================================
    # Maintenance Operations
    # =========================================================================

    async def cleanup_all(self) -> dict[str, int]:
        """Clean up expired entries from all caches."""
        results = {
            "query": await self.query_cache.cleanup_expired(),
            "embedding": await self.embedding_cache.cleanup_expired(),
            "llm": await self.llm_cache.cleanup_expired(),
            "curriculum_code": await self.curriculum_code_cache.cleanup_expired(),
            "prerequisite": await self.prerequisite_cache.cleanup_expired(),
            "learning_outcome": await self.learning_outcome_cache.cleanup_expired(),
        }
        logger.info(f"Cache cleanup: {results}")
        return results

    async def invalidate_all(self) -> None:
        """Invalidate all caches."""
        await self.query_cache.invalidate()
        self.embedding_cache._cache.clear()
        self.embedding_cache._rebuild_matrix()
        await self.llm_cache.cleanup_expired()  # Just expire, not full clear
        await self.curriculum_code_cache.invalidate()
        await self.prerequisite_cache.invalidate()
        await self.learning_outcome_cache.invalidate()
        logger.info("All caches invalidated")

    def get_all_stats(self) -> dict[str, Any]:
        """Get statistics from all caches."""
        return {
            "query_cache": self.query_cache.get_stats(),
            "embedding_cache": self.embedding_cache.get_stats(),
            "llm_cache": self.llm_cache.get_stats(),
            "curriculum_code_cache": self.curriculum_code_cache.get_stats(),
            "prerequisite_cache": self.prerequisite_cache.get_stats(),
            "learning_outcome_cache": self.learning_outcome_cache.get_stats(),
        }

    def get_memory_usage(self) -> dict[str, int]:
        """Estimate memory usage of caches."""
        import sys

        return {
            "query_cache_entries": len(self.query_cache._cache),
            "embedding_cache_entries": len(self.embedding_cache._cache),
            "llm_cache_entries": len(self.llm_cache._cache),
            "curriculum_code_entries": len(self.curriculum_code_cache._cache),
            "prerequisite_entries": len(self.prerequisite_cache._cache),
            "learning_outcome_entries": len(self.learning_outcome_cache._cache),
        }
