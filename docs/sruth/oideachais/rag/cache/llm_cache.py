"""
LLM Response Cache.

Caches LLM API responses for repeated queries to reduce latency and cost.
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
class LLMCacheEntry:
    """A cached LLM response."""

    key: str
    prompt_hash: str
    response: dict[str, Any]
    model: str
    created_at: datetime
    expires_at: datetime
    tokens_saved: int = 0
    hit_count: int = 0

    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


class LLMCache:
    """
    Cache for LLM API responses.

    Features:
    - Caches by prompt + model combination
    - Tracks tokens saved
    - TTL-based expiration
    - Cost estimation
    """

    def __init__(
        self,
        ttl_seconds: int = 86400,  # 24 hours
        max_size: int = 5000,
    ):
        """
        Initialize LLM cache.

        Args:
            ttl_seconds: Time-to-live for cache entries
            max_size: Maximum number of entries
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: OrderedDict[str, LLMCacheEntry] = OrderedDict()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "tokens_saved": 0,
            "requests_saved": 0,
        }

    def _generate_key(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.0,
        **kwargs,
    ) -> str:
        """Generate cache key from request parameters."""
        # Only cache deterministic requests (temperature = 0)
        if temperature > 0:
            return ""

        key_data = {
            "messages": messages,
            "model": model,
            # Include other deterministic params
            "max_tokens": kwargs.get("max_tokens"),
            "response_format": kwargs.get("response_format"),
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()[:32]

    def _estimate_tokens(self, messages: list[dict[str, str]]) -> int:
        """Estimate token count for messages."""
        # Simple estimation: ~4 chars per token
        total_chars = sum(len(m.get("content", "")) for m in messages)
        return total_chars // 4

    async def get(
        self,
        messages: list[dict[str, str]],
        model: str,
        **kwargs,
    ) -> Optional[dict[str, Any]]:
        """
        Get cached LLM response.

        Args:
            messages: Chat messages
            model: Model name
            **kwargs: Additional parameters

        Returns:
            Cached response or None
        """
        key = self._generate_key(messages, model, **kwargs)

        if not key or key not in self._cache:
            self._stats["misses"] += 1
            return None

        entry = self._cache[key]

        if entry.is_expired:
            del self._cache[key]
            self._stats["misses"] += 1
            return None

        # Update stats
        self._cache.move_to_end(key)
        entry.hit_count += 1
        self._stats["hits"] += 1
        self._stats["tokens_saved"] += entry.tokens_saved
        self._stats["requests_saved"] += 1

        logger.debug(f"LLM cache hit for model {model}")
        return entry.response

    async def set(
        self,
        messages: list[dict[str, str]],
        model: str,
        response: dict[str, Any],
        **kwargs,
    ) -> None:
        """
        Cache an LLM response.

        Args:
            messages: Chat messages
            model: Model name
            response: API response
            **kwargs: Additional parameters
        """
        key = self._generate_key(messages, model, **kwargs)

        if not key:  # Non-deterministic request
            return

        # Evict if at capacity
        while len(self._cache) >= self.max_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        now = datetime.now()
        tokens = self._estimate_tokens(messages)

        # Add response tokens
        if "usage" in response:
            tokens += response["usage"].get("completion_tokens", 0)

        entry = LLMCacheEntry(
            key=key,
            prompt_hash=hashlib.sha256(json.dumps(messages).encode()).hexdigest()[:16],
            response=response,
            model=model,
            created_at=now,
            expires_at=now + timedelta(seconds=self.ttl_seconds),
            tokens_saved=tokens,
        )

        self._cache[key] = entry
        self._cache.move_to_end(key)

    async def invalidate_model(self, model: str) -> int:
        """Invalidate all entries for a specific model."""
        keys_to_remove = [key for key, entry in self._cache.items() if entry.model == model]
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

        # Estimate cost savings (rough estimate)
        # Assuming $0.01 per 1K tokens for input/output average
        cost_saved = self._stats["tokens_saved"] * 0.00001

        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "hit_rate": hit_rate,
            "tokens_saved": self._stats["tokens_saved"],
            "requests_saved": self._stats["requests_saved"],
            "estimated_cost_saved_usd": round(cost_saved, 2),
            "size": len(self._cache),
            "max_size": self.max_size,
        }

    def get_cache_summary(self) -> dict[str, Any]:
        """Get summary of cached entries by model."""
        by_model: dict[str, int] = {}
        for entry in self._cache.values():
            by_model[entry.model] = by_model.get(entry.model, 0) + 1

        return {
            "total_entries": len(self._cache),
            "by_model": by_model,
            "stats": self.get_stats(),
        }
