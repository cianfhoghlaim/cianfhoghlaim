"""Common utilities and constants for DLT sources."""

from .firecrawl_source import (
    crawl_website,
    create_firecrawl_source,
    get_firecrawl_client,
    map_urls,
    scrape_page,
)
from .incremental import (
    LEVEL_EQUIVALENCES,
    IncrementalCrawlState,
    add_curriculum_metadata,
    compute_content_hash,
    create_incremental_resource,
    get_equivalent_levels,
    make_deduplication_key,
    with_change_detection,
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
