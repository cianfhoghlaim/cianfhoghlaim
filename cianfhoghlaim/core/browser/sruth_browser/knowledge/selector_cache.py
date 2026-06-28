"""CSS selector cache for frequently accessed elements."""

from datetime import datetime
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


class CachedSelector(BaseModel):
    """A cached CSS selector with metadata."""

    description: str
    selector: str
    domain: str
    page_pattern: str | None = None  # Regex for matching pages

    # Metrics
    use_count: int = 0
    success_count: int = 0
    failure_count: int = 0

    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: datetime = Field(default_factory=datetime.utcnow)
    last_verified: datetime | None = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0

    @property
    def is_reliable(self) -> bool:
        """Check if selector is reliable enough to use."""
        return self.success_rate >= 0.8 and self.use_count >= 3


class SelectorCache:
    """Cache for CSS selectors learned from interactions.

    Stagehand can observe elements and provide selectors.
    This cache stores successful selectors for reuse.
    """

    def __init__(self, max_selectors_per_domain: int = 100):
        self.max_per_domain = max_selectors_per_domain
        self._cache: dict[str, list[CachedSelector]] = {}

    def add(
        self,
        domain: str,
        description: str,
        selector: str,
        page_pattern: str | None = None,
    ) -> CachedSelector:
        """Add a selector to the cache."""
        if domain not in self._cache:
            self._cache[domain] = []

        # Check for existing
        for cached in self._cache[domain]:
            if cached.description == description and cached.selector == selector:
                return cached

        # Create new
        cached = CachedSelector(
            description=description,
            selector=selector,
            domain=domain,
            page_pattern=page_pattern,
        )

        self._cache[domain].append(cached)

        # Prune if too many
        if len(self._cache[domain]) > self.max_per_domain:
            self._prune_domain(domain)

        return cached

    def get(
        self,
        domain: str,
        description: str,
        page_url: str | None = None,
    ) -> CachedSelector | None:
        """Get a cached selector by description."""
        if domain not in self._cache:
            return None

        import re

        for cached in self._cache[domain]:
            if cached.description.lower() == description.lower():
                # Check page pattern if specified
                if cached.page_pattern and page_url:
                    if not re.search(cached.page_pattern, page_url):
                        continue
                return cached

        return None

    def find_similar(
        self,
        domain: str,
        description: str,
        threshold: float = 0.7,
    ) -> list[CachedSelector]:
        """Find selectors with similar descriptions."""
        if domain not in self._cache:
            return []

        # Simple word overlap similarity
        desc_words = set(description.lower().split())

        similar = []
        for cached in self._cache[domain]:
            cached_words = set(cached.description.lower().split())
            overlap = len(desc_words & cached_words)
            total = len(desc_words | cached_words)
            similarity = overlap / total if total > 0 else 0

            if similarity >= threshold:
                similar.append(cached)

        return sorted(similar, key=lambda x: x.success_rate, reverse=True)

    def record_use(
        self,
        domain: str,
        description: str,
        success: bool,
    ) -> None:
        """Record selector usage result."""
        cached = self.get(domain, description)
        if not cached:
            return

        cached.use_count += 1
        cached.last_used = datetime.utcnow()

        if success:
            cached.success_count += 1
            cached.last_verified = datetime.utcnow()
        else:
            cached.failure_count += 1

    def get_reliable_selectors(
        self,
        domain: str,
    ) -> list[CachedSelector]:
        """Get all reliable selectors for a domain."""
        if domain not in self._cache:
            return []

        return [s for s in self._cache[domain] if s.is_reliable]

    def _prune_domain(self, domain: str) -> None:
        """Remove least useful selectors from a domain."""
        selectors = self._cache[domain]

        # Sort by usefulness (success rate * use count)
        selectors.sort(
            key=lambda s: s.success_rate * s.use_count,
            reverse=True,
        )

        # Keep top selectors
        self._cache[domain] = selectors[:self.max_per_domain]

    def export(self) -> dict[str, Any]:
        """Export cache data."""
        return {
            domain: [s.model_dump() for s in selectors]
            for domain, selectors in self._cache.items()
        }

    def import_data(self, data: dict[str, Any]) -> None:
        """Import cache data."""
        for domain, selectors in data.items():
            self._cache[domain] = [CachedSelector(**s) for s in selectors]


# Global instance
_cache: SelectorCache | None = None


def get_selector_cache() -> SelectorCache:
    """Get the global selector cache instance."""
    global _cache
    if _cache is None:
        _cache = SelectorCache()
    return _cache
