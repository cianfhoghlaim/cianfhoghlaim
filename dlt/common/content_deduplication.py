"""
Content Deduplication - Cross-source content deduplication for curriculum data.

Provides:
- Content hash-based deduplication across sources
- Source provenance tracking
- Canonical URL resolution
- Incremental state management

Usage:
    from cianfhoghlaim.dlt.common.content_deduplication import (
        ContentDeduplicator,
        DeduplicationResult,
    )

    deduplicator = ContentDeduplicator()

    # Check if content is duplicate
    result = deduplicator.process_page(normalized_page)
    if result.is_new:
        yield result.page.to_dict()
    else:
        yield result.to_provenance_record()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import structlog
from cianfhoghlaim.dlt.common.source_adapters import NormalizedPage

logger = structlog.get_logger(__name__)


@dataclass
class SourceProvenance:
    """Tracks that a source provided specific content."""

    content_hash: str
    source: str
    url: str
    discovered_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for DLT resource output."""
        return {
            "content_hash": self.content_hash,
            "source": self.source,
            "source_url": self.url,
            "discovered_at": self.discovered_at.isoformat(),
        }


@dataclass
class DeduplicationResult:
    """Result of deduplication check for a page."""

    page: NormalizedPage
    is_new: bool
    existing_sources: list[str] = field(default_factory=list)
    canonical_url: str | None = None

    def to_provenance_record(self) -> dict[str, Any]:
        """
        Create a provenance record for duplicate content.

        Used when content already exists from another source.
        """
        return {
            "content_hash": self.page.content_hash,
            "source": self.page.source,
            "source_url": self.page.url,
            "canonical_url": self.canonical_url,
            "discovered_at": self.page.crawled_at.isoformat(),
            "is_duplicate": True,
        }


class ContentDeduplicator:
    """
    Deduplicates content across curriculum sources.

    Uses content hashing to identify duplicate content from different sources
    (e.g., same Mathematics specification appearing on both curriculumonline.ie
    and ncca.ie).

    Tracks provenance to know which sources provide which content.
    """

    def __init__(self):
        """Initialize the deduplicator."""
        # In-memory cache: content_hash -> (canonical_url, sources)
        self._content_cache: dict[str, tuple[str, set[str]]] = {}

        # Track all seen URLs to avoid re-processing
        self._seen_urls: set[str] = set()

        # Statistics
        self._stats = {
            "total_processed": 0,
            "new_content": 0,
            "duplicates": 0,
            "by_source": {},
        }

    def process_page(self, page: NormalizedPage) -> DeduplicationResult:
        """
        Process a page and determine if it's new or duplicate content.

        Args:
            page: Normalized page to process

        Returns:
            DeduplicationResult indicating if content is new
        """
        self._stats["total_processed"] += 1
        source_stats = self._stats["by_source"].setdefault(page.source, {"new": 0, "duplicate": 0})

        # Skip if we've seen this exact URL
        if page.url in self._seen_urls:
            return DeduplicationResult(
                page=page,
                is_new=False,
                existing_sources=[page.source],
                canonical_url=page.url,
            )

        self._seen_urls.add(page.url)

        # Check if we've seen this content hash before
        if page.content_hash in self._content_cache:
            canonical_url, existing_sources = self._content_cache[page.content_hash]

            # Add this source to the set
            existing_sources.add(page.source)

            self._stats["duplicates"] += 1
            source_stats["duplicate"] += 1

            logger.debug(
                "content_duplicate_found",
                url=page.url,
                source=page.source,
                content_hash=page.content_hash[:16],
                canonical_url=canonical_url,
                existing_sources=list(existing_sources),
            )

            return DeduplicationResult(
                page=page,
                is_new=False,
                existing_sources=list(existing_sources),
                canonical_url=canonical_url,
            )

        # New content - store in cache
        self._content_cache[page.content_hash] = (page.url, {page.source})

        self._stats["new_content"] += 1
        source_stats["new"] += 1

        logger.debug(
            "new_content_found",
            url=page.url,
            source=page.source,
            content_hash=page.content_hash[:16],
        )

        return DeduplicationResult(
            page=page,
            is_new=True,
        )

    def is_duplicate(self, content_hash: str) -> bool:
        """Check if a content hash has been seen before."""
        return content_hash in self._content_cache

    def get_canonical_url(self, content_hash: str) -> str | None:
        """Get the canonical (first-seen) URL for a content hash."""
        if content_hash in self._content_cache:
            return self._content_cache[content_hash][0]
        return None

    def get_sources_for_content(self, content_hash: str) -> list[str]:
        """Get all sources that have provided this content."""
        if content_hash in self._content_cache:
            return list(self._content_cache[content_hash][1])
        return []

    def mark_seen(self, content_hash: str, url: str, source: str) -> None:
        """Manually mark content as seen."""
        if content_hash not in self._content_cache:
            self._content_cache[content_hash] = (url, {source})
        else:
            self._content_cache[content_hash][1].add(source)
        self._seen_urls.add(url)

    def get_stats(self) -> dict[str, Any]:
        """Get deduplication statistics."""
        return {
            **self._stats,
            "unique_content_count": len(self._content_cache),
            "unique_urls_count": len(self._seen_urls),
        }

    def reset(self) -> None:
        """Reset the deduplicator state."""
        self._content_cache.clear()
        self._seen_urls.clear()
        self._stats = {
            "total_processed": 0,
            "new_content": 0,
            "duplicates": 0,
            "by_source": {},
        }


class PersistentDeduplicator:
    """
    Deduplicator that can load/save state from database.

    Extends ContentDeduplicator with persistence capabilities for
    incremental crawling across multiple runs.
    """

    def __init__(self, deduplicator: ContentDeduplicator | None = None):
        """Initialize with optional existing deduplicator."""
        self._deduplicator = deduplicator or ContentDeduplicator()

    def load_from_database(
        self,
        conn: Any,
        cycle: str | None = None,
        subject: str | None = None,
    ) -> int:
        """
        Load existing content hashes from database.

        Args:
            conn: DuckDB connection
            cycle: Optional cycle filter
            subject: Optional subject filter

        Returns:
            Number of hashes loaded
        """
        try:
            # Build query with optional filters
            query = "SELECT content_hash, url, source FROM education.curriculum_pages WHERE 1=1"
            params = []

            if cycle:
                query += " AND cycle = ?"
                params.append(cycle)

            if subject:
                query += " AND subject = ?"
                params.append(subject)

            result = conn.execute(query, params).fetchall()

            loaded_count = 0
            for content_hash, url, source in result:
                self._deduplicator.mark_seen(content_hash, url, source)
                loaded_count += 1

            logger.info(
                "deduplicator_state_loaded",
                loaded_count=loaded_count,
                cycle=cycle,
                subject=subject,
            )

            return loaded_count

        except Exception as e:
            logger.warning(
                "deduplicator_load_failed",
                error=str(e),
                cycle=cycle,
                subject=subject,
            )
            return 0

    def process_page(self, page: NormalizedPage) -> DeduplicationResult:
        """Process a page using the internal deduplicator."""
        return self._deduplicator.process_page(page)

    def get_stats(self) -> dict[str, Any]:
        """Get statistics from the internal deduplicator."""
        return self._deduplicator.get_stats()


def deduplicate_pages(
    pages: list[NormalizedPage],
) -> tuple[list[NormalizedPage], list[SourceProvenance]]:
    """
    Convenience function to deduplicate a batch of pages.

    Args:
        pages: List of normalized pages

    Returns:
        Tuple of (unique pages, provenance records for duplicates)
    """
    deduplicator = ContentDeduplicator()
    unique_pages = []
    provenance_records = []

    for page in pages:
        result = deduplicator.process_page(page)

        if result.is_new:
            unique_pages.append(page)
        else:
            provenance_records.append(
                SourceProvenance(
                    content_hash=page.content_hash,
                    source=page.source,
                    url=page.url,
                    discovered_at=page.crawled_at,
                )
            )

    logger.info(
        "batch_deduplication_complete",
        total_pages=len(pages),
        unique_pages=len(unique_pages),
        duplicates=len(provenance_records),
    )

    return unique_pages, provenance_records
