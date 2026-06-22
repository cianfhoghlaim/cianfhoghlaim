"""
Firecrawl integration for crypto documentation scraping.

Provides DLT resources for scraping and crawling cryptocurrency
protocol documentation websites.

Firecrawl handles:
- JavaScript rendering
- Rate limiting
- Markdown conversion
- Sitemap discovery
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Optional

import dlt
from dlt.common.configuration.specs import BaseConfiguration


class FirecrawlConfig(BaseConfiguration):
    """Firecrawl API configuration."""

    api_key: str = dlt.secrets.value
    base_url: str = "https://api.firecrawl.dev/v1"


# Crypto documentation sources to scrape
CRYPTO_DOC_SOURCES = {
    "ethena": {
        "url": "https://docs.ethena.fi",
        "crawl_options": {
            "limit": 100,
            "maxDepth": 3,
            "allowBackwardLinks": False,
        },
        "description": "Ethena protocol documentation",
    },
    "aave": {
        "url": "https://docs.aave.com",
        "crawl_options": {
            "limit": 200,
            "maxDepth": 4,
        },
        "description": "Aave V3 lending protocol docs",
    },
    "pendle": {
        "url": "https://docs.pendle.finance",
        "crawl_options": {
            "limit": 100,
            "maxDepth": 3,
        },
        "description": "Pendle yield tokenization docs",
    },
    "lido": {
        "url": "https://docs.lido.fi",
        "crawl_options": {
            "limit": 150,
            "maxDepth": 3,
        },
        "description": "Lido liquid staking docs",
    },
    "eigenlayer": {
        "url": "https://docs.eigenlayer.xyz",
        "crawl_options": {
            "limit": 100,
            "maxDepth": 3,
        },
        "description": "EigenLayer restaking docs",
    },
    "curve": {
        "url": "https://resources.curve.fi",
        "crawl_options": {
            "limit": 100,
            "maxDepth": 3,
        },
        "description": "Curve Finance docs",
    },
}


def _get_firecrawl_client(api_key: Optional[str] = None):
    """Get Firecrawl client with API key."""
    from firecrawl import FirecrawlApp

    if api_key is None:
        # Try to get from environment or dlt secrets
        import os

        api_key = os.environ.get("FIRECRAWL_API_KEY")

    if not api_key:
        raise ValueError("Firecrawl API key required")

    return FirecrawlApp(api_key=api_key)


@dlt.resource(
    name="firecrawl_pages",
    primary_key=["url", "scraped_at"],
    write_disposition="merge",
)
def firecrawl_scrape(
    urls: list[str],
    api_key: Optional[str] = None,
    formats: Optional[list[str]] = None,
    include_tags: Optional[list[str]] = None,
    exclude_tags: Optional[list[str]] = None,
    wait_for: int = 5000,
) -> Iterator[dict[str, Any]]:
    """
    Scrape individual pages with Firecrawl.

    Args:
        urls: List of URLs to scrape
        api_key: Firecrawl API key
        formats: Output formats (markdown, html, links, etc.)
        include_tags: HTML tags to include
        exclude_tags: HTML tags to exclude
        wait_for: Wait time in ms for JS rendering

    Yields:
        Scraped page records
    """
    app = _get_firecrawl_client(api_key)

    if formats is None:
        formats = ["markdown", "links"]

    scrape_options = {
        "formats": formats,
        "waitFor": wait_for,
    }

    if include_tags:
        scrape_options["includeTags"] = include_tags
    if exclude_tags:
        scrape_options["excludeTags"] = exclude_tags

    for url in urls:
        try:
            result = app.scrape_url(url, params=scrape_options)

            yield {
                "url": url,
                "title": result.get("metadata", {}).get("title"),
                "description": result.get("metadata", {}).get("description"),
                "markdown": result.get("markdown"),
                "html": result.get("html"),
                "links": result.get("links", []),
                "metadata": result.get("metadata", {}),
                "scraped_at": datetime.utcnow(),
                "source": "firecrawl",
            }

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            yield {
                "url": url,
                "error": str(e),
                "scraped_at": datetime.utcnow(),
                "source": "firecrawl",
            }


@dlt.resource(
    name="firecrawl_crawl",
    primary_key=["url", "crawl_id"],
    write_disposition="merge",
)
def firecrawl_crawl(
    start_url: str,
    api_key: Optional[str] = None,
    limit: int = 100,
    max_depth: int = 3,
    include_paths: Optional[list[str]] = None,
    exclude_paths: Optional[list[str]] = None,
    allow_backward_links: bool = False,
    poll_interval: int = 5,
) -> Iterator[dict[str, Any]]:
    """
    Crawl entire site with Firecrawl.

    Args:
        start_url: Starting URL for crawl
        api_key: Firecrawl API key
        limit: Max pages to crawl
        max_depth: Max link depth
        include_paths: URL path patterns to include
        exclude_paths: URL path patterns to exclude
        allow_backward_links: Allow links going up in hierarchy
        poll_interval: Seconds between status polls

    Yields:
        Crawled page records
    """
    import time

    app = _get_firecrawl_client(api_key)

    crawl_params = {
        "limit": limit,
        "maxDepth": max_depth,
        "allowBackwardLinks": allow_backward_links,
        "scrapeOptions": {
            "formats": ["markdown", "links"],
        },
    }

    if include_paths:
        crawl_params["includePaths"] = include_paths
    if exclude_paths:
        crawl_params["excludePaths"] = exclude_paths

    # Start async crawl
    crawl_result = app.async_crawl_url(start_url, params=crawl_params)
    crawl_id = crawl_result.get("id")

    if not crawl_id:
        raise ValueError(f"Failed to start crawl: {crawl_result}")

    print(f"Started crawl {crawl_id} for {start_url}")

    # Poll for completion
    while True:
        status = app.check_crawl_status(crawl_id)

        if status.get("status") == "completed":
            break
        elif status.get("status") == "failed":
            raise Exception(f"Crawl failed: {status.get('error')}")

        progress = status.get("completed", 0)
        total = status.get("total", limit)
        print(f"Crawl progress: {progress}/{total}")

        time.sleep(poll_interval)

    # Get all results
    data = status.get("data", [])

    for page in data:
        yield {
            "crawl_id": crawl_id,
            "url": page.get("metadata", {}).get("sourceURL"),
            "title": page.get("metadata", {}).get("title"),
            "description": page.get("metadata", {}).get("description"),
            "markdown": page.get("markdown"),
            "links": page.get("links", []),
            "metadata": page.get("metadata", {}),
            "start_url": start_url,
            "scraped_at": datetime.utcnow(),
            "source": "firecrawl",
        }


@dlt.resource(
    name="firecrawl_sitemap",
    primary_key="url",
    write_disposition="replace",
)
def firecrawl_map(
    url: str,
    api_key: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 5000,
) -> Iterator[dict[str, Any]]:
    """
    Map site URLs using Firecrawl's map endpoint.

    Fast sitemap discovery without full scraping.

    Args:
        url: Site URL to map
        api_key: Firecrawl API key
        search: Optional search term to filter URLs
        limit: Max URLs to return

    Yields:
        URL mapping records
    """
    app = _get_firecrawl_client(api_key)

    params = {"limit": limit}
    if search:
        params["search"] = search

    result = app.map_url(url, params=params)

    for page_url in result.get("links", []):
        yield {
            "url": page_url,
            "base_url": url,
            "search_term": search,
            "discovered_at": datetime.utcnow(),
        }


@dlt.source(name="crypto_docs")
def scrape_crypto_docs(
    sources: Optional[list[str]] = None,
    api_key: Optional[str] = None,
) -> Iterator[dlt.resource]:
    """
    Scrape crypto protocol documentation.

    Args:
        sources: Source keys from CRYPTO_DOC_SOURCES
        api_key: Firecrawl API key

    Yields:
        DLT resources for each documentation source
    """
    if sources is None:
        sources = list(CRYPTO_DOC_SOURCES.keys())

    for source_key in sources:
        if source_key not in CRYPTO_DOC_SOURCES:
            print(f"Unknown source: {source_key}")
            continue

        source = CRYPTO_DOC_SOURCES[source_key]

        # Create named resource for this source
        @dlt.resource(
            name=f"docs_{source_key}",
            primary_key=["url", "crawl_id"],
            write_disposition="merge",
        )
        def crawl_source(
            url=source["url"],
            options=source.get("crawl_options", {}),
            key=api_key,
        ):
            yield from firecrawl_crawl(
                start_url=url,
                api_key=key,
                limit=options.get("limit", 100),
                max_depth=options.get("maxDepth", 3),
                allow_backward_links=options.get("allowBackwardLinks", False),
            )

        yield crawl_source


def save_to_r2(
    pages: list[dict],
    bucket: str,
    prefix: str = "crypto-docs",
    credentials: Optional[dict] = None,
) -> list[str]:
    """
    Save scraped pages to Cloudflare R2.

    Args:
        pages: Scraped page records
        bucket: R2 bucket name
        prefix: Path prefix in bucket
        credentials: R2 credentials

    Returns:
        List of uploaded keys
    """
    import boto3
    from urllib.parse import urlparse
    import hashlib
    import json

    # Get R2 credentials
    if credentials is None:
        import os

        credentials = {
            "endpoint_url": os.environ.get("R2_ENDPOINT_URL"),
            "aws_access_key_id": os.environ.get("R2_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.environ.get("R2_SECRET_ACCESS_KEY"),
        }

    s3 = boto3.client("s3", **credentials)

    uploaded_keys = []

    for page in pages:
        url = page.get("url", "")
        if not url:
            continue

        # Create key from URL
        parsed = urlparse(url)
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        path = parsed.path.strip("/").replace("/", "_") or "index"
        key = f"{prefix}/{parsed.netloc}/{path}_{url_hash}.json"

        # Upload page data
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(page, default=str),
            ContentType="application/json",
        )

        uploaded_keys.append(key)

    return uploaded_keys


def run_firecrawl_pipeline(
    sources: Optional[list[str]] = None,
    api_key: Optional[str] = None,
    destination_type: str = "duckdb",
    upload_to_r2: bool = False,
    r2_bucket: Optional[str] = None,
):
    """
    Run Firecrawl documentation pipeline.

    Args:
        sources: Documentation sources to crawl
        api_key: Firecrawl API key
        destination_type: DLT destination type
        upload_to_r2: Whether to upload to R2
        r2_bucket: R2 bucket name
    """
    from pipelines.shared.duckdb_destination import create_pipeline

    if sources is None:
        sources = ["ethena", "aave", "pendle"]

    pipeline, metadata = create_pipeline(
        pipeline_name="crypto_docs",
        destination_type=destination_type,
    )

    # Run crawl for each source
    all_pages = []

    for source_key in sources:
        if source_key not in CRYPTO_DOC_SOURCES:
            continue

        source = CRYPTO_DOC_SOURCES[source_key]
        options = source.get("crawl_options", {})

        print(f"Crawling {source_key}: {source['url']}")

        crawl_resource = firecrawl_crawl(
            start_url=source["url"],
            api_key=api_key,
            limit=options.get("limit", 100),
            max_depth=options.get("maxDepth", 3),
        )

        # Run pipeline
        load_info = pipeline.run(crawl_resource)
        print(f"Loaded {source_key}: {load_info}")

        # Collect pages for R2 upload
        if upload_to_r2:
            all_pages.extend(list(crawl_resource))

    # Upload to R2 if requested
    if upload_to_r2 and r2_bucket and all_pages:
        keys = save_to_r2(all_pages, r2_bucket)
        print(f"Uploaded {len(keys)} documents to R2")

    return pipeline


if __name__ == "__main__":
    # Test with single source
    run_firecrawl_pipeline(
        sources=["ethena"],
        destination_type="duckdb",
    )
