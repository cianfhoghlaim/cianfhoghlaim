"""
Incremental loading utilities for DLT sources.

Provides utilities for:
- State management across pipeline runs
- Change detection for crawled content
- Deduplication based on content hashes
- Last-modified tracking for efficient re-crawls

DEPRECATION NOTE: `crawl_source` was previously exported from this module
but the canonical home is now `cianfhoghlaim.dlt_sources.common.site_crawler`. The
shim below emits a `DeprecationWarning` and re-exports the new function.
Per the `2026-07-15-pipeline-architecture-clarity-v1` change, this
module's `crawl_source` will be removed in a follow-up change.
"""

from __future__ import annotations
import dlt


import hashlib
import warnings
from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from typing import Any, TypeVar

import dlt_sources
import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Deprecated re-exports (the `site_crawler` primitive is the canonical home).
# ---------------------------------------------------------------------------


def __getattr__(name: str) -> Any:
    """Lazy re-export shim for the deprecated `crawl_source` symbol.

    Emits a `DeprecationWarning` on first access so existing call sites
    can be migrated to `from cianfhoghlaim.dlt_sources.common.site_crawler import
    crawl_site`. The shim adapts the new `crawl_site` (which yields
    `CrawledPage` dataclasses) to the legacy API (which yields `dict`),
    so existing call sites that do `page["nation"] = "en"` keep working.
    """
    if name == "crawl_source":
        warnings.warn(
            "cianfhoghlaim.dlt.common.incremental.crawl_source is deprecated; "
            "use cianfhoghlaim.dlt.common.site_crawler.crawl_site instead. "
            "See openspec/changes/2026-07-15-pipeline-architecture-clarity-v1.",
            DeprecationWarning,
            stacklevel=2,
        )
        from dlt_sources.common.site_crawler import crawl_site

        def _crawl_source_shim(*args: Any, **kwargs: Any) -> Any:
            for page in crawl_site(*args, **kwargs):
                yield page.to_dict()

        return _crawl_source_shim
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def compute_content_hash(content: str | bytes) -> str:
    """
    Compute SHA-256 hash of content for change detection.

    Args:
        content: String or bytes content to hash

    Returns:
        Hex-encoded SHA-256 hash
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def make_deduplication_key(*parts: str) -> str:
    """
    Create a stable deduplication key from multiple parts.

    Args:
        *parts: String parts to combine (e.g., nation, source, url)

    Returns:
        Combined key suitable for primary key use
    """
    return "|".join(str(p) for p in parts if p)


def with_change_detection(
    records: Iterator[dict[str, Any]],
    content_field: str = "markdown",
    hash_field: str = "content_hash",
) -> Iterator[dict[str, Any]]:
    """
    Add content hashing to records for change detection.

    Args:
        records: Iterator of record dictionaries
        content_field: Field containing content to hash
        hash_field: Field name for the computed hash

    Yields:
        Records with added content hash field
    """
    for record in records:
        content = record.get(content_field, "")
        if content:
            record[hash_field] = compute_content_hash(content)
        else:
            record[hash_field] = None
        yield record


class IncrementalCrawlState:
    """
    Manages incremental crawl state for DLT sources.

    Tracks URLs crawled, content hashes, and last crawl times
    to enable efficient incremental updates.
    """

    def __init__(self, source_name: str, nation: str):
        """
        Initialize incremental state tracker.

        Args:
            source_name: Name of the DLT source
            nation: Nation code (e.g., "ireland", "scotland")
        """
        self.source_name = source_name
        self.nation = nation
        self._seen_urls: set[str] = set()
        self._content_hashes: dict[str, str] = {}

    def should_process(self, url: str, content: str | None = None) -> bool:
        """
        Check if a URL should be processed.

        Args:
            url: URL to check
            content: Optional content for hash comparison

        Returns:
            True if the URL should be processed
        """
        if url in self._seen_urls:
            # URL seen in this run - skip
            return False

        self._seen_urls.add(url)

        if content:
            new_hash = compute_content_hash(content)
            old_hash = self._content_hashes.get(url)
            if old_hash and old_hash == new_hash:
                # Content unchanged - skip
                logger.debug(
                    "incremental_skip_unchanged",
                    url=url,
                    source=self.source_name,
                )
                return False
            self._content_hashes[url] = new_hash

        return True

    def mark_processed(self, url: str, content_hash: str | None = None) -> None:
        """
        Mark a URL as processed.

        Args:
            url: URL that was processed
            content_hash: Optional content hash to store
        """
        self._seen_urls.add(url)
        if content_hash:
            self._content_hashes[url] = content_hash


def create_incremental_resource(
    name: str,
    data_generator: Callable[..., Iterator[dict[str, Any]]],
    primary_key: list[str],
    initial_value: datetime | None = None,
    cursor_path: str = "crawled_at",
    nation: str | None = None,
) -> Callable[[], Any]:
    """
    Create a DLT resource with incremental loading support.

    Args:
        name: Resource name
        data_generator: Function that yields records
        primary_key: Fields for primary key
        initial_value: Initial cursor value for first run
        cursor_path: Field containing the cursor value
        nation: Nation identifier for metadata

    Returns:
        DLT resource function
    """
    if initial_value is None:
        initial_value = datetime(2020, 1, 1, tzinfo=UTC)

    @dlt.resource(
        name=name,
        write_disposition="merge",
        primary_key=primary_key,
    )
    def incremental_resource(
        last_crawl: dlt.sources.incremental[datetime] = dlt.sources.incremental(
            cursor_path=cursor_path,
            initial_value=initial_value,
        ),
    ) -> Iterator[dict[str, Any]]:
        """Incremental resource that tracks crawl state."""
        for record in data_generator():
            # Add nation metadata if specified
            if nation and "nation" not in record:
                record["nation"] = nation

            # Add timestamp if not present
            if cursor_path not in record:
                record[cursor_path] = datetime.now(UTC).isoformat()

            yield record

    return incremental_resource


def add_curriculum_metadata(
    records: Iterator[dict[str, Any]],
    nation: str,
    source: str,
    curriculum_level: str | None = None,
    language: str = "en",
) -> Iterator[dict[str, Any]]:
    """
    Add standardized curriculum metadata to records.

    Args:
        records: Iterator of record dictionaries
        nation: Nation code (ireland, england, scotland, wales, northern_ireland)
        source: Source identifier
        curriculum_level: Optional level (primary, secondary, etc.)
        language: Language code (en, ga, cy, gd)

    Yields:
        Records with added metadata
    """
    for record in records:
        record["nation"] = nation
        record["source"] = source
        record["language"] = language
        record["indexed_at"] = datetime.now(UTC).isoformat()

        if curriculum_level:
            record["curriculum_level"] = curriculum_level

        # Compute content hash for change detection
        content = record.get("markdown") or record.get("content", "")
        if content:
            record["content_hash"] = compute_content_hash(content)

        yield record


# Level mapping for cross-nation comparisons
LEVEL_EQUIVALENCES = {
    # Ireland
    "junior_cycle": ["key_stage_3", "national_5", "gcse"],
    "leaving_cert": ["a_level", "higher", "advanced_higher"],
    # England
    "key_stage_3": ["junior_cycle", "national_5"],
    "key_stage_4": ["junior_cycle", "national_5", "gcse"],
    "a_level": ["leaving_cert", "higher", "advanced_higher"],
    # Scotland
    "national_5": ["gcse", "junior_cycle"],
    "higher": ["a_level", "leaving_cert"],
    "advanced_higher": ["a_level", "leaving_cert"],
    # Wales & NI use GCSE/A-Level same as England
    "gcse": ["national_5", "junior_cycle"],
}


def get_equivalent_levels(level: str) -> list[str]:
    """
    Get equivalent education levels across nations.

    Args:
        level: Education level identifier

    Returns:
        List of equivalent levels in other nations
    """
    return LEVEL_EQUIVALENCES.get(level.lower().replace("-", "_").replace(" ", "_"), [])
