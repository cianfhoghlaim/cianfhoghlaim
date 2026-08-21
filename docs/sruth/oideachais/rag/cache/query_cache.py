"""
Query Cache.

Caches full query results with TTL and LRU eviction.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional
from collections import OrderedDict

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """A cached query result."""

    key: str
    value: Any
    created_at: datetime
    expires_at: datetime
    hit_count: int = 0

    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


class QueryCache:
    """
    LRU cache for query results with TTL.

    Features:
    - TTL-based expiration
    - LRU eviction when max_size reached
    - Async-compatible interface
    """

    def __init__(
        self,
        ttl_seconds: int = 3600,
        max_size: int = 10000,
    ):
        """
        Initialize query cache.

        Args:
            ttl_seconds: Time-to-live for cache entries
            max_size: Maximum number of entries
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = {"hits": 0, "misses": 0, "evictions": 0}

    def _generate_key(
        self,
        query: str,
        mode: str,
        params: dict[str, Any],
    ) -> str:
        """Generate cache key from query and params."""
        # Normalize params for consistent hashing
        key_data = {
            "query": query.lower().strip(),
            "mode": mode,
            "params": {k: v for k, v in sorted(params.items()) if v is not None},
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()[:32]

    async def get(
        self,
        query: str,
        mode: str,
        params: dict[str, Any],
    ) -> Optional[Any]:
        """
        Get cached query result.

        Args:
            query: Query text
            mode: Query mode
            params: Query parameters

        Returns:
            Cached result or None
        """
        key = self._generate_key(query, mode, params)

        if key not in self._cache:
            self._stats["misses"] += 1
            return None

        entry = self._cache[key]

        # Check expiration
        if entry.is_expired:
            del self._cache[key]
            self._stats["misses"] += 1
            return None

        # Move to end (LRU)
        self._cache.move_to_end(key)
        entry.hit_count += 1
        self._stats["hits"] += 1

        logger.debug(f"Cache hit for query: {query[:50]}...")
        return entry.value

    async def set(
        self,
        query: str,
        mode: str,
        params: dict[str, Any],
        value: Any,
        ttl_override: Optional[int] = None,
    ) -> None:
        """
        Cache a query result.

        Args:
            query: Query text
            mode: Query mode
            params: Query parameters
            value: Result to cache
            ttl_override: Optional TTL override
        """
        key = self._generate_key(query, mode, params)
        ttl = ttl_override or self.ttl_seconds

        # Evict if at capacity
        while len(self._cache) >= self.max_size:
            # Remove oldest (first) item
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._stats["evictions"] += 1

        now = datetime.now()
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl),
        )

        self._cache[key] = entry
        self._cache.move_to_end(key)

    async def invalidate(
        self,
        query: Optional[str] = None,
        mode: Optional[str] = None,
    ) -> int:
        """
        Invalidate cache entries.

        Args:
            query: Optional query to invalidate
            mode: Optional mode to invalidate

        Returns:
            Number of entries invalidated
        """
        if query is None and mode is None:
            count = len(self._cache)
            self._cache.clear()
            return count

        # Find matching keys
        keys_to_remove = []
        for key, entry in self._cache.items():
            # Simple pattern matching on cached data
            should_remove = False
            if query and query.lower() in str(entry.value).lower():
                should_remove = True
            if mode and mode in key:
                should_remove = True
            if should_remove:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._cache[key]

        return len(keys_to_remove)

    async def cleanup_expired(self) -> int:
        """Remove expired entries."""
        expired_keys = [key for key, entry in self._cache.items() if entry.is_expired]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0

        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "hit_rate": hit_rate,
            "size": len(self._cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
        }
