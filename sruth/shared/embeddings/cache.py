"""
Embedding Cache for Performance Optimization.

Caches embeddings to avoid recomputing identical texts.
Useful for:
- Curriculum content that doesn't change
- Repeated queries
- Deduplication workflows
"""

from __future__ import annotations

import hashlib
import json
import logging
import pickle
from pathlib import Path
from typing import Any

from sruth.shared.embeddings.models import EmbeddingConfig

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """
    Cache for embedding vectors.

    Supports both in-memory and disk-based caching.
    """

    def __init__(
        self,
        cache_dir: str | None = None,
        max_size: int = 10_000,
        use_disk: bool = True,
    ):
        """Initialize embedding cache.

        Args:
            cache_dir: Directory for disk cache (None = in-memory only)
            max_size: Maximum number of cached embeddings
            use_disk: Whether to use disk cache
        """
        self.max_size = max_size
        self.use_disk = use_disk
        self._memory_cache: dict[str, dict[str, list[float]]] = {}

        if use_disk and cache_dir:
            self.cache_dir = Path(cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.cache_dir = None

    def _get_key(self, text: str, model: str) -> str:
        """Generate cache key for text/model combination."""
        content = f"{model}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, text: str, model: str) -> list[float] | None:
        """Get cached embedding for text.

        Args:
            text: Text to look up
            model: Model name

        Returns:
            Embedding vector or None if not cached
        """
        key = self._get_key(text, model)

        # Check memory cache first
        if model in self._memory_cache and key in self._memory_cache[model]:
            return self._memory_cache[model][key]

        # Check disk cache
        if self.use_disk and self.cache_dir:
            cache_file = self.cache_dir / f"{key}.pkl"
            if cache_file.exists():
                try:
                    with open(cache_file, "rb") as f:
                        data = pickle.load(f)
                        # Store in memory cache
                        if model not in self._memory_cache:
                            self._memory_cache[model] = {}
                        self._memory_cache[model][key] = data["embedding"]
                        return data["embedding"]
                except Exception as e:
                    logger.warning(f"Failed to load cache entry: {e}")

        return None

    def set(
        self,
        text: str,
        model: str,
        embedding: list[float],
        metadata: dict | None = None,
    ) -> None:
        """Cache embedding for text.

        Args:
            text: Text to cache
            model: Model name
            embedding: Embedding vector
            metadata: Optional metadata to store
        """
        key = self._get_key(text, model)

        # Store in memory cache
        if model not in self._memory_cache:
            self._memory_cache[model] = {}

        # Enforce max size (simple LRU)
        if len(self._memory_cache[model]) >= self.max_size:
            # Remove oldest entry (first key)
            oldest = next(iter(self._memory_cache[model]))
            del self._memory_cache[model][oldest]

        self._memory_cache[model][key] = embedding

        # Store on disk
        if self.use_disk and self.cache_dir:
            cache_file = self.cache_dir / f"{key}.pkl"
            try:
                data = {
                    "text": text,
                    "model": model,
                    "embedding": embedding,
                    "metadata": metadata or {},
                }
                with open(cache_file, "wb") as f:
                    pickle.dump(data, f)
            except Exception as e:
                logger.warning(f"Failed to write cache entry: {e}")

    def get_batch(
        self,
        texts: list[str],
        model: str,
    ) -> dict[str, list[float] | None]:
        """Get cached embeddings for multiple texts.

        Args:
            texts: Texts to look up
            model: Model name

        Returns:
            Dict mapping text to embedding (None if not cached)
        """
        results = {}
        for text in texts:
            results[text] = self.get(text, model)
        return results

    def set_batch(
        self,
        texts: list[str],
        model: str,
        embeddings: list[list[float]],
    ) -> None:
        """Cache embeddings for multiple texts.

        Args:
            texts: Texts to cache
            model: Model name
            embeddings: Embedding vectors
        """
        for text, embedding in zip(texts, embeddings):
            self.set(text, model, embedding)

    def clear(self, model: str | None = None) -> None:
        """Clear cache.

        Args:
            model: Specific model to clear, or None for all
        """
        if model:
            if model in self._memory_cache:
                del self._memory_cache[model]
            if self.use_disk and self.cache_dir:
                # Clear disk cache for model
                for file in self.cache_dir.glob("*.pkl"):
                    try:
                        with open(file, "rb") as f:
                            data = pickle.load(f)
                            if data.get("model") == model:
                                file.unlink()
                    except Exception:
                        pass
        else:
            self._memory_cache.clear()
            if self.use_disk and self.cache_dir:
                for file in self.cache_dir.glob("*.pkl"):
                    file.unlink()

    def stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dict with cache stats
        """
        total_memory = sum(len(cache) for cache in self._memory_cache.values())

        disk_count = 0
        if self.use_disk and self.cache_dir:
            disk_count = len(list(self.cache_dir.glob("*.pkl")))

        return {
            "memory_cached": total_memory,
            "disk_cached": disk_count,
            "models": list(self._memory_cache.keys()),
        }


class DeduplicationCache:
    """
    Specialized cache for deduplication workflows.

    Tracks texts that have been seen and their canonical IDs.
    """

    def __init__(self, cache_dir: str | None = None):
        """Initialize deduplication cache.

        Args:
            cache_dir: Directory for persistent cache
        """
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self._seen: dict[str, str] = {}  # hash -> canonical_id
        self._by_id: dict[str, list[str]] = {}  # id -> list of hashes

        # Load from disk if available
        if self.cache_dir:
            self._load()

    def _get_hash(self, text: str) -> str:
        """Get normalized hash of text."""
        # Normalize whitespace
        normalized = " ".join(text.split())
        return hashlib.sha256(normalized.encode()).hexdigest()

    def get_canonical_id(self, text: str) -> str | None:
        """Get canonical ID for text (if seen before).

        Args:
            text: Text to look up

        Returns:
            Canonical ID or None if not seen
        """
        text_hash = self._get_hash(text)
        return self._seen.get(text_hash)

    def set_canonical_id(self, text: str, canonical_id: str) -> None:
        """Set canonical ID for text.

        Args:
            text: Text to register
            canonical_id: Canonical ID to associate
        """
        text_hash = self._get_hash(text)
        self._seen[text_hash] = canonical_id

        if canonical_id not in self._by_id:
            self._by_id[canonical_id] = []
        self._by_id[canonical_id].append(text_hash)

    def is_duplicate(self, text: str) -> bool:
        """Check if text has been seen before.

        Args:
            text: Text to check

        Returns:
            True if duplicate, False otherwise
        """
        return self._get_hash(text) in self._seen

    def deduplicate_batch(
        self,
        texts: list[str],
    ) -> tuple[list[int], list[str]]:
        """
        Deduplicate a batch of texts.

        Args:
            texts: Texts to deduplicate

        Returns:
            Tuple of (unique_indices, canonical_ids)
        """
        unique_indices = []
        canonical_ids = []
        next_id = 1

        for i, text in enumerate(texts):
            existing_id = self.get_canonical_id(text)
            if existing_id:
                canonical_ids.append(existing_id)
            else:
                new_id = f"doc_{next_id:06d}"
                next_id += 1
                self.set_canonical_id(text, new_id)
                canonical_ids.append(new_id)
                unique_indices.append(i)

        return unique_indices, canonical_ids

    def save(self):
        """Save cache to disk."""
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file = self.cache_dir / "dedup_cache.json"
            try:
                with open(cache_file, "w") as f:
                    json.dump({
                        "seen": self._seen,
                        "by_id": {k: v for k, v in self._by_id.items()},
                    }, f)
            except Exception as e:
                logger.warning(f"Failed to save dedup cache: {e}")

    def _load(self):
        """Load cache from disk."""
        if not self.cache_dir:
            return

        cache_file = self.cache_dir / "dedup_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    self._seen = data.get("seen", {})
                    self._by_id = {k: v for k, v in data.get("by_id", {}).items()}
                logger.info(f"Loaded dedup cache: {len(self._seen)} entries")
            except Exception as e:
                logger.warning(f"Failed to load dedup cache: {e}")

    def clear(self):
        """Clear all cache data."""
        self._seen.clear()
        self._by_id.clear()

        if self.cache_dir:
            cache_file = self.cache_dir / "dedup_cache.json"
            if cache_file.exists():
                cache_file.unlink()
