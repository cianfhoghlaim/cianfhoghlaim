"""Common utilities and constants for DLT sources."""

from .firecrawl_source import (
    create_firecrawl_source,
    crawl_website,
    scrape_page,
    map_urls,
    get_firecrawl_client,
)

from .incremental import (
    compute_content_hash,
    make_deduplication_key,
    with_change_detection,
    IncrementalCrawlState,
    create_incremental_resource,
    add_curriculum_metadata,
    get_equivalent_levels,
    LEVEL_EQUIVALENCES,
)

__all__ = [
    # Firecrawl utilities
    "create_firecrawl_source",
    "crawl_website",
    "scrape_page",
    "map_urls",
    "get_firecrawl_client",
    # Incremental loading utilities
    "compute_content_hash",
    "make_deduplication_key",
    "with_change_detection",
    "IncrementalCrawlState",
    "create_incremental_resource",
    "add_curriculum_metadata",
    "get_equivalent_levels",
    "LEVEL_EQUIVALENCES",
]
