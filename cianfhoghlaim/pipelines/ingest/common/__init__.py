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
    "LEVEL_EQUIVALENCES",
    "IncrementalCrawlState",
    "add_curriculum_metadata",
    # Incremental loading utilities
    "compute_content_hash",
    "crawl_website",
    # Firecrawl utilities
    "create_firecrawl_source",
    "create_incremental_resource",
    "get_equivalent_levels",
    "get_firecrawl_client",
    "make_deduplication_key",
    "map_urls",
    "scrape_page",
    "with_change_detection",
]
