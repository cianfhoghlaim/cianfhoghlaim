"""
Web scraping modules for crypto documentation and research.

Uses Firecrawl for reliable scraping with JavaScript rendering.
"""

from pipelines.scrapers.firecrawl_source import (
    firecrawl_scrape,
    firecrawl_crawl,
    firecrawl_map,
    scrape_crypto_docs,
)

__all__ = [
    "firecrawl_scrape",
    "firecrawl_crawl",
    "firecrawl_map",
    "scrape_crypto_docs",
]
