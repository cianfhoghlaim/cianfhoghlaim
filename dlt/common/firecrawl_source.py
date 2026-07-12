"""
Shared Firecrawl utilities for web scraping across nations.

Provides a consistent interface for crawling and scraping
educational websites using Firecrawl or self-hosted browser stack.

The adapter pattern allows seamless fallback:
1. Self-hosted browser stack (via sruth-browser client) - $0 cost
2. Firecrawl API - paid fallback

Set BROWSER_API_URL to use the self-hosted browser stack.
"""

import asyncio
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)


# Client type flag for determining which backend is active
_active_client_type: str | None = None


def get_browser_client():
    """Get BrowserClient if sruth-browser is available and BROWSER_API_URL is set."""
    browser_url = os.getenv("BROWSER_API_URL")
    if not browser_url:
        return None

    try:
        from bonneagar.stacks.browser.sruth_browser import BrowserClient

        return BrowserClient(base_url=browser_url)
    except ImportError:
        logger.debug("sruth_browser_not_installed")
        return None


def get_firecrawl_client():
    """Get Firecrawl client, handling import gracefully."""
    try:
        from firecrawl import FirecrawlApp

        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            return None
        return FirecrawlApp(api_key=api_key)
    except ImportError:
        return None


def get_scraper_client():
    """Get the best available scraper client.

    Priority:
    1. BrowserClient (self-hosted, $0)
    2. FirecrawlApp (paid API)

    Returns:
        Tuple of (client, client_type) where client_type is 'browser' or 'firecrawl'
    """
    global _active_client_type

    # Try browser client first (self-hosted, free)
    browser = get_browser_client()
    if browser:
        _active_client_type = "browser"
        return browser, "browser"

    # Fall back to Firecrawl
    firecrawl = get_firecrawl_client()
    if firecrawl:
        _active_client_type = "firecrawl"
        return firecrawl, "firecrawl"

    _active_client_type = None
    return None, None


def scrape_page(url: str, formats: list[str] | None = None) -> dict[str, Any]:
    """
    Scrape a single page using BrowserClient (preferred) or Firecrawl (fallback).

    Args:
        url: URL to scrape
        formats: Output formats (default: ["markdown", "links"])

    Returns:
        Scraped page data with metadata
    """
    formats = formats or ["markdown", "links"]
    client, client_type = get_scraper_client()

    if not client:
        return {
            "url": url,
            "status": "client_unavailable",
            "scraped_at": datetime.now(UTC).isoformat(),
        }

    try:
        if client_type == "browser":
            # Use BrowserClient (async)
            from bonneagar.stacks.browser.sruth_browser import ExtractionFormat

            format_map = {
                "markdown": ExtractionFormat.MARKDOWN,
                "html": ExtractionFormat.HTML,
                "links": ExtractionFormat.LINKS,
                "json": ExtractionFormat.JSON,
            }
            extraction_formats = [format_map.get(f, ExtractionFormat.MARKDOWN) for f in formats]

            async def _scrape():
                async with client:
                    return await client.scrape(url, formats=extraction_formats)

            result = asyncio.run(_scrape())

            return {
                "url": result.url,
                "title": result.metadata.get("title") if result.metadata else None,
                "description": result.metadata.get("description") if result.metadata else None,
                "markdown": result.content.get("markdown"),
                "html": result.content.get("html"),
                "links": result.content.get("links", []),
                "language": result.metadata.get("language") if result.metadata else None,
                "status": "success",
                "backend": client_type,
                "scraped_at": datetime.now(UTC).isoformat(),
            }
        else:
            # Use Firecrawl (sync)
            result = client.scrape_url(url, params={"formats": formats})
            metadata = result.get("metadata", {})

            return {
                "url": metadata.get("sourceURL", url),
                "title": metadata.get("title"),
                "description": metadata.get("description"),
                "markdown": result.get("markdown"),
                "html": result.get("html"),
                "links": result.get("links", []),
                "language": metadata.get("language"),
                "status": "success",
                "backend": client_type,
                "scraped_at": datetime.now(UTC).isoformat(),
            }
    except (RuntimeError, ConnectionError, TimeoutError, ValueError) as e:
        logger.warning("scrape_failed", url=url, backend=client_type, error=str(e))
        return {
            "url": url,
            "error": str(e),
            "status": "error",
            "backend": client_type,
            "scraped_at": datetime.now(UTC).isoformat(),
        }


def crawl_website(
    base_url: str,
    include_paths: list[str] | None = None,
    exclude_paths: list[str] | None = None,
    max_pages: int = 100,
    max_depth: int = 3,
    formats: list[str] | None = None,
) -> Iterator[dict[str, Any]]:
    """
    Crawl a website using BrowserClient (preferred) or Firecrawl (fallback).

    Args:
        base_url: Starting URL for crawl
        include_paths: URL paths to include (glob patterns)
        exclude_paths: URL paths to exclude (glob patterns)
        max_pages: Maximum pages to crawl
        max_depth: Maximum crawl depth
        formats: Output formats (default: ["markdown", "links"])

    Yields:
        Crawled page data
    """
    formats = formats or ["markdown", "links"]
    client, client_type = get_scraper_client()

    if not client:
        yield {
            "url": base_url,
            "status": "client_unavailable",
            "crawled_at": datetime.now(UTC).isoformat(),
        }
        return

    try:
        if client_type == "browser":
            # Use BrowserClient: discover URLs then batch scrape
            from bonneagar.stacks.browser.sruth_browser import ExtractionFormat

            format_map = {
                "markdown": ExtractionFormat.MARKDOWN,
                "html": ExtractionFormat.HTML,
                "links": ExtractionFormat.LINKS,
                "json": ExtractionFormat.JSON,
            }
            extraction_formats = [format_map.get(f, ExtractionFormat.MARKDOWN) for f in formats]

            async def _crawl():
                async with client:
                    # Discover URLs first
                    urls = await client.discover_site(base_url, max_urls=max_pages)

                    # Filter URLs by include/exclude paths
                    filtered_urls = []
                    for url in urls:
                        # Check include paths
                        if include_paths:
                            matches_include = any(p in url for p in include_paths)
                            if not matches_include:
                                continue

                        # Check exclude paths
                        if exclude_paths:
                            matches_exclude = any(p in url for p in exclude_paths)
                            if matches_exclude:
                                continue

                        filtered_urls.append(url)

                    # Batch scrape filtered URLs
                    results = await client.batch_scrape(
                        filtered_urls[:max_pages],
                        formats=extraction_formats,
                    )
                    return results

            results = asyncio.run(_crawl())

            for result in results:
                yield {
                    "url": result.url,
                    "title": result.metadata.get("title") if result.metadata else None,
                    "description": result.metadata.get("description") if result.metadata else None,
                    "markdown": result.content.get("markdown"),
                    "links": result.content.get("links", []),
                    "language": result.metadata.get("language") if result.metadata else None,
                    "status": "success",
                    "backend": client_type,
                    "crawled_at": datetime.now(UTC).isoformat(),
                }
        else:
            # Use Firecrawl (sync)
            crawl_config = {
                "limit": max_pages,
                "maxDepth": max_depth,
                "scrapeOptions": {"formats": formats},
            }

            if include_paths:
                crawl_config["includePaths"] = include_paths
            if exclude_paths:
                crawl_config["excludePaths"] = exclude_paths

            result = client.crawl_url(base_url, params=crawl_config, poll_interval=5)

            for page in result.get("data", []):
                metadata = page.get("metadata", {})
                yield {
                    "url": metadata.get("sourceURL"),
                    "title": metadata.get("title"),
                    "description": metadata.get("description"),
                    "markdown": page.get("markdown"),
                    "links": page.get("links", []),
                    "language": metadata.get("language"),
                    "status": "success",
                    "backend": client_type,
                    "crawled_at": datetime.now(UTC).isoformat(),
                }
    except (RuntimeError, ConnectionError, TimeoutError, ValueError) as e:
        logger.warning("crawl_failed", url=base_url, backend=client_type, error=str(e))
        yield {
            "url": base_url,
            "error": str(e),
            "status": "error",
            "backend": client_type,
            "crawled_at": datetime.now(UTC).isoformat(),
        }


def map_urls(
    base_url: str,
    search: str | None = None,
    max_urls: int = 1000,
) -> Iterator[str]:
    """
    Map all URLs on a website using BrowserClient (preferred) or Firecrawl (fallback).

    Args:
        base_url: Website to map
        search: Optional search filter
        max_urls: Maximum URLs to return

    Yields:
        Discovered URLs
    """
    client, client_type = get_scraper_client()

    if not client:
        return

    try:
        if client_type == "browser":
            # Use BrowserClient (async)
            async def _map():
                async with client:
                    urls = await client.discover_site(base_url, max_urls=max_urls)
                    # Filter by search term if provided
                    if search:
                        urls = [u for u in urls if search.lower() in u.lower()]
                    return urls

            urls = asyncio.run(_map())
            yield from urls
        else:
            # Use Firecrawl (sync)
            params = {"limit": max_urls}
            if search:
                params["search"] = search

            result = client.map_url(base_url, params=params)
            yield from result.get("links", [])
    except (RuntimeError, ConnectionError, TimeoutError, ValueError) as e:
        logger.warning("map_failed", url=base_url, backend=client_type, error=str(e))
        return


def create_firecrawl_source(
    source_name: str,
    base_url: str,
    include_paths: list[str] | None = None,
    exclude_paths: list[str] | None = None,
    max_pages: int = 100,
    max_depth: int = 3,
    resource_name: str = "pages",
):
    """
    Create a DLT source from Firecrawl configuration.

    Args:
        source_name: Name for the DLT source
        base_url: Starting URL for crawl
        include_paths: URL paths to include
        exclude_paths: URL paths to exclude
        max_pages: Maximum pages to crawl
        max_depth: Maximum crawl depth
        resource_name: Name for the pages resource

    Returns:
        DLT source function
    """

    @dlt.source(name=source_name)
    def firecrawl_source():
        @dlt.resource(
            name=resource_name,
            write_disposition="merge",
            primary_key=["url"],
        )
        def pages():
            yield from crawl_website(
                base_url=base_url,
                include_paths=include_paths,
                exclude_paths=exclude_paths,
                max_pages=max_pages,
                max_depth=max_depth,
            )

        return pages

    return firecrawl_source
