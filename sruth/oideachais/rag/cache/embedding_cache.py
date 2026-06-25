"""
Embedding Cache.

Caches embeddings with similarity-based lookup for near-duplicate queries.
"""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingEntry:
    """A cached embedding with text."""

    text_hash: str
    text: str
    embedding: np.ndarray
    created_at: datetime
    expires_at: datetime
    hit_count: int = 0

    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


class EmbeddingCache:
    """
    Cache embeddings with similarity-based retrieval.

    Features:
    - Exact match lookup by text hash
    - Similarity-based lookup for near-duplicates
    - TTL expiration
    - Memory-efficient numpy storage
    """

    def __init__(
        self,
        ttl_seconds: int = 604800,  # 7 days
        max_size: int = 100000,
        similarity_threshold: float = 0.95,
    ):
        """
        Initialize embedding cache.

        Args:
            ttl_seconds: Time-to-live for cache entries
            max_size: Maximum number of embeddings to store
            similarity_threshold: Minimum cosine similarity for similar lookup
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.similarity_threshold = similarity_threshold

        self._cache: dict[str, EmbeddingEntry] = {}
        self._embedding_matrix: np.ndarray | None = None
        self._keys_order: list[str] = []
        self._stats = {"hits": 0, "misses": 0, "similar_hits": 0}

    def _text_hash(self, text: str) -> str:
        """Generate hash for text."""
        normalized = text.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:32]

    def _rebuild_matrix(self) -> None:
        """Rebuild the embedding matrix for similarity search."""
        if not self._cache:
            self._embedding_matrix = None
            self._keys_order = []
            return

        self._keys_order = list(self._cache.keys())
        embeddings = [self._cache[k].embedding for k in self._keys_order]
        self._embedding_matrix = np.vstack(embeddings)

        # Normalize for cosine similarity
        norms = np.linalg.norm(self._embedding_matrix, axis=1, keepdims=True)
        self._embedding_matrix = self._embedding_matrix / np.clip(norms, 1e-10, None)

    async def get(self, text: str) -> np.ndarray | None:
        """
        Get cached embedding by exact text match.

        Args:
            text: Text to look up

        Returns:
            Cached embedding or None
        """
        text_hash = self._text_hash(text)

        if text_hash not in self._cache:
            self._stats["misses"] += 1
            return None

        entry = self._cache[text_hash]

        if entry.is_expired:
            del self._cache[text_hash]
            self._stats["misses"] += 1
            return None

        entry.hit_count += 1
        self._stats["hits"] += 1
        return entry.embedding

    async def get_similar(
        self,
        embedding: np.ndarray,
    ) -> tuple[str, np.ndarray, float] | None:
        """
        Find similar cached embedding using cosine similarity.

        Args:
            embedding: Query embedding

        Returns:
            Tuple of (text, embedding, similarity) or None
        """
        if self._embedding_matrix is None or len(self._keys_order) == 0:
            return None

        # Normalize query
        query_norm = embedding / np.clip(np.linalg.norm(embedding), 1e-10, None)

        # Compute similarities
        similarities = np.dot(self._embedding_matrix, query_norm)
        max_idx = np.argmax(similarities)
        max_sim = similarities[max_idx]

        if max_sim >= self.similarity_threshold:
            key = self._keys_order[max_idx]
            entry = self._cache[key]

            if not entry.is_expired:
                entry.hit_count += 1
                self._stats["similar_hits"] += 1
                logger.debug(f"Similar embedding found (sim={max_sim:.3f})")
                return (entry.text, entry.embedding, float(max_sim))

        return None

    async def set(
        self,
        text: str,
        embedding: np.ndarray,
        ttl_override: int | None = None,
    ) -> None:
        """
        Cache an embedding.

        Args:
            text: Source text
            embedding: Embedding vector
            ttl_override: Optional TTL override
        """
        text_hash = self._text_hash(text)
        ttl = ttl_override or self.ttl_seconds

        # Evict if at capacity
        if len(self._cache) >= self.max_size:
            await self._evict_lru()

        now = datetime.now()
        self._cache[text_hash] = EmbeddingEntry(
            text_hash=text_hash,
            text=text,
            embedding=embedding.astype(np.float32),
            created_at=now,
            expires_at=now + timedelta(seconds=ttl),
        )

        # Rebuild matrix periodically
        if len(self._cache) % 100 == 0:
            self._rebuild_matrix()

    async def set_batch(
        self,
        texts: list[str],
        embeddings: np.ndarray,
        ttl_override: int | None = None,
    ) -> None:
        """
        Cache multiple embeddings efficiently.

        Args:
            texts: List of source texts
            embeddings: Embedding matrix (n_texts x dim)
            ttl_override: Optional TTL override
        """
        ttl = ttl_override or self.ttl_seconds
        now = datetime.now()
        expires_at = now + timedelta(seconds=ttl)

        for i, text in enumerate(texts):
            text_hash = self._text_hash(text)

            # Skip if already cached
            if text_hash in self._cache:
                continue

            # Evict if needed
            if len(self._cache) >= self.max_size:
                await self._evict_lru()

            self._cache[text_hash] = EmbeddingEntry(
                text_hash=text_hash,
                text=text,
                embedding=embeddings[i].astype(np.float32),
                created_at=now,
                expires_at=expires_at,
            )

        # Rebuild matrix after batch insert
        self._rebuild_matrix()

    async def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return

        # Find entry with lowest hit count and oldest creation
        min_key = min(
            self._cache.keys(),
            key=lambda k: (self._cache[k].hit_count, self._cache[k].created_at),
        )
        del self._cache[min_key]

    async def cleanup_expired(self) -> int:
        """Remove expired entries."""
        expired_keys = [
            key for key, entry in self._cache.items() if entry.is_expired
        ]
        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            self._rebuild_matrix()

        return len(expired_keys)

    def get_stats(self) -> dict[str, any]:
        """Get cache statistics."""
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0

        return {
            "exact_hits": self._stats["hits"],
            "similar_hits": self._stats["similar_hits"],
            "misses": self._stats["misses"],
            "hit_rate": hit_rate,
            "size": len(self._cache),
            "max_size": self.max_size,
            "similarity_threshold": self.similarity_threshold,
        }
