"""
DLT source for protocol documentation using Firecrawl.

Provides access to:
- Protocol documentation pages (preconfigured)
- User-provided arbitrary URLs (dynamic scraping)
- Whitepapers and technical specs
- Audit reports with PDF download
- API documentation

Enhanced with:
- Garage S3 storage for PDFs
- DuckLake integration for metadata
"""

import hashlib
import os
import re
from datetime import datetime, timezone
from typing import Any, Iterator

import dlt

try:
    from firecrawl import FirecrawlApp
except ImportError:
    FirecrawlApp = None


def _get_client() -> "FirecrawlApp":
    """Get Firecrawl client."""
    if FirecrawlApp is None:
        raise ImportError("firecrawl-py is required. Install with: pip install firecrawl-py")

    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable is required")

    return FirecrawlApp(api_key=api_key)


def _scrape_url(url: str, include_raw_html: bool = False) -> dict[str, Any]:
    """Scrape a single URL."""
    try:
        client = _get_client()

        formats = ["markdown", "links"]
        if include_raw_html:
            formats.append("rawHtml")

        result = client.scrape_url(
            url,
            params={
                "formats": formats,
                "onlyMainContent": True,
                "removeBase64Images": True,
            },
        )

        return {
            "url": url,
            "title": result.get("metadata", {}).get("title"),
            "description": result.get("metadata", {}).get("description"),
            "language": result.get("metadata", {}).get("language"),
            "markdown": result.get("markdown"),
            "links": result.get("links", []),
            "raw_html": result.get("rawHtml") if include_raw_html else None,
            "og_title": result.get("metadata", {}).get("ogTitle"),
            "og_description": result.get("metadata", {}).get("ogDescription"),
            "og_image": result.get("metadata", {}).get("ogImage"),
            "status_code": result.get("metadata", {}).get("statusCode"),
            "status": "success",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "status": "error",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }


def _crawl_site(
    url: str,
    max_depth: int = 2,
    limit: int = 50,
    include_paths: list[str] | None = None,
    exclude_paths: list[str] | None = None,
) -> Iterator[dict[str, Any]]:
    """Crawl an entire site."""
    try:
        client = _get_client()

        params = {
            "limit": limit,
            "maxDepth": max_depth,
            "scrapeOptions": {
                "formats": ["markdown", "links"],
                "onlyMainContent": True,
                "removeBase64Images": True,
            },
        }

        if include_paths:
            params["includePaths"] = include_paths
        if exclude_paths:
            params["excludePaths"] = exclude_paths

        crawl_result = client.crawl_url(url, params=params, poll_interval=5)

        for page in crawl_result.get("data", []):
            yield {
                "source_url": url,
                "url": page.get("metadata", {}).get("sourceURL"),
                "title": page.get("metadata", {}).get("title"),
                "description": page.get("metadata", {}).get("description"),
                "language": page.get("metadata", {}).get("language"),
                "markdown": page.get("markdown"),
                "links": page.get("links", []),
                "og_title": page.get("metadata", {}).get("ogTitle"),
                "og_description": page.get("metadata", {}).get("ogDescription"),
                "status_code": page.get("metadata", {}).get("statusCode"),
                "status": "success",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

    except Exception as e:
        yield {
            "source_url": url,
            "error": str(e),
            "status": "error",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }


def _map_site(url: str, limit: int = 100) -> Iterator[dict[str, Any]]:
    """Map all URLs on a site without scraping content."""
    try:
        client = _get_client()

        result = client.map_url(url, params={"limit": limit})

        for page_url in result.get("links", []):
            yield {
                "source_url": url,
                "url": page_url,
                "status": "success",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

    except Exception as e:
        yield {
            "source_url": url,
            "error": str(e),
            "status": "error",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }


# Common protocol documentation URLs
PROTOCOL_DOCS = {
    "uniswap": {
        "docs_url": "https://docs.uniswap.org",
        "include_paths": ["/concepts", "/contracts", "/sdk"],
    },
    "aave": {
        "docs_url": "https://docs.aave.com",
        "include_paths": ["/developers", "/faq"],
    },
    "compound": {
        "docs_url": "https://docs.compound.finance",
        "include_paths": [],
    },
    "maker": {
        "docs_url": "https://docs.makerdao.com",
        "include_paths": [],
    },
    "curve": {
        "docs_url": "https://resources.curve.fi",
        "include_paths": [],
    },
    "lido": {
        "docs_url": "https://docs.lido.fi",
        "include_paths": [],
    },
    "eigenlayer": {
        "docs_url": "https://docs.eigenlayer.xyz",
        "include_paths": [],
    },
    "arbitrum": {
        "docs_url": "https://docs.arbitrum.io",
        "include_paths": ["/for-devs"],
    },
    "optimism": {
        "docs_url": "https://docs.optimism.io",
        "include_paths": ["/builders"],
    },
}


@dlt.source(name="protocol_docs")
def protocol_docs_source(
    protocols: list[str] | None = None,
    custom_urls: list[dict[str, Any]] | None = None,
    max_depth: int = 2,
    page_limit: int = 50,
    scrape_mode: str = "crawl",
):
    """
    DLT source for protocol documentation.

    Args:
        protocols: List of protocol names to fetch docs for (uses predefined URLs)
        custom_urls: Custom URLs with optional include_paths
        max_depth: Maximum crawl depth
        page_limit: Maximum pages to crawl per site
        scrape_mode: "crawl" for full content, "map" for URL discovery only

    Returns:
        DLT source with documentation content
    """
    protocols = protocols or list(PROTOCOL_DOCS.keys())
    custom_urls = custom_urls or []

    @dlt.resource(
        name="documentation",
        write_disposition="merge",
        primary_key=["url"],
    )
    def documentation():
        """Protocol documentation content."""
        # Process predefined protocols
        for protocol_name in protocols:
            if protocol_name not in PROTOCOL_DOCS:
                continue

            config = PROTOCOL_DOCS[protocol_name]
            docs_url = config["docs_url"]
            include_paths = config.get("include_paths", [])

            if scrape_mode == "crawl":
                for page in _crawl_site(
                    docs_url,
                    max_depth=max_depth,
                    limit=page_limit,
                    include_paths=include_paths if include_paths else None,
                ):
                    page["protocol"] = protocol_name
                    yield page
            else:
                for page in _map_site(docs_url, limit=page_limit):
                    page["protocol"] = protocol_name
                    yield page

        # Process custom URLs
        for custom in custom_urls:
            url = custom.get("url")
            if not url:
                continue

            include_paths = custom.get("include_paths", [])
            protocol = custom.get("name", url)

            if scrape_mode == "crawl":
                for page in _crawl_site(
                    url,
                    max_depth=max_depth,
                    limit=page_limit,
                    include_paths=include_paths if include_paths else None,
                ):
                    page["protocol"] = protocol
                    yield page
            else:
                for page in _map_site(url, limit=page_limit):
                    page["protocol"] = protocol
                    yield page

    @dlt.resource(
        name="single_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def single_pages(urls: list[str] | None = None):
        """Single page scrapes (whitepapers, specific docs)."""
        urls = urls or []
        for url in urls:
            yield _scrape_url(url)

    return documentation, single_pages


@dlt.source(name="audit_reports")
def audit_reports_source(urls: list[str]):
    """
    DLT source for audit reports.

    Args:
        urls: List of audit report URLs (PDFs, web pages)

    Returns:
        DLT source with audit report content
    """

    @dlt.resource(
        name="audits",
        write_disposition="merge",
        primary_key=["url"],
    )
    def audits():
        """Audit report content."""
        for url in urls:
            result = _scrape_url(url, include_raw_html=True)
            result["document_type"] = "audit"
            yield result

    return audits


# =========================================================================
# PDF Extraction Helpers
# =========================================================================

PDF_URL_PATTERN = re.compile(r'https?://[^\s<>"\']+\.pdf(?:\?[^\s<>"\']*)?', re.IGNORECASE)


def _extract_pdf_links(content: str, links: list[str]) -> list[str]:
    """Extract PDF links from content and link list."""
    pdf_links = set()

    # From explicit links
    for link in links:
        if link and ".pdf" in link.lower():
            pdf_links.add(link)

    # From content (regex)
    if content:
        matches = PDF_URL_PATTERN.findall(content)
        pdf_links.update(matches)

    return list(pdf_links)


def _download_pdfs_to_garage(pdf_urls: list[str], protocol: str | None = None) -> list[dict]:
    """Download PDFs and store in Garage S3."""
    try:
        from crypteolas.storage.garage_client import get_garage_client
    except ImportError:
        return []

    results = []
    garage = get_garage_client()

    for pdf_url in pdf_urls:
        try:
            stored = garage.download_and_store_pdf(pdf_url, protocol=protocol)
            if stored:
                results.append({
                    "url": pdf_url,
                    "s3_key": stored.key,
                    "s3_bucket": stored.bucket,
                    "size": stored.size,
                    "etag": stored.etag,
                })
        except Exception as e:
            results.append({
                "url": pdf_url,
                "error": str(e),
            })

    return results


# =========================================================================
# User-Provided URL Source
# =========================================================================

@dlt.source(name="user_urls")
def user_urls_source(
    urls: list[str] | None = None,
    user_id: str | None = None,
    download_pdfs: bool = True,
    max_depth: int = 1,
    page_limit: int = 20,
):
    """
    DLT source for user-provided arbitrary URLs.

    Args:
        urls: List of URLs to scrape
        user_id: ID of user who requested the scrape
        download_pdfs: Whether to download and store PDFs
        max_depth: Maximum crawl depth for each URL
        page_limit: Maximum pages per URL

    Returns:
        DLT source with scraped content and PDF references
    """
    urls = urls or []

    @dlt.resource(
        name="user_documents",
        write_disposition="merge",
        primary_key=["url"],
    )
    def user_documents():
        """User-provided URL content."""
        for url in urls:
            # Single page scrape for depth=0, crawl otherwise
            if max_depth == 0:
                result = _scrape_url(url)
                result["source_type"] = "user_url"
                result["requested_by"] = user_id

                # Extract and optionally download PDFs
                pdf_links = _extract_pdf_links(
                    result.get("markdown", ""),
                    result.get("links", []),
                )
                result["pdf_links"] = pdf_links

                if download_pdfs and pdf_links:
                    result["pdf_downloads"] = _download_pdfs_to_garage(pdf_links)

                yield result
            else:
                # Crawl the site
                for page in _crawl_site(url, max_depth=max_depth, limit=page_limit):
                    page["source_type"] = "user_url"
                    page["requested_by"] = user_id

                    # Extract PDFs
                    pdf_links = _extract_pdf_links(
                        page.get("markdown", ""),
                        page.get("links", []),
                    )
                    page["pdf_links"] = pdf_links

                    if download_pdfs and pdf_links:
                        page["pdf_downloads"] = _download_pdfs_to_garage(pdf_links)

                    yield page

    @dlt.resource(
        name="pdf_downloads",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pdf_downloads(pdf_urls: list[str] | None = None):
        """Explicit PDF downloads."""
        pdf_urls = pdf_urls or []
        for pdf_url in pdf_urls:
            try:
                from crypteolas.storage.garage_client import get_garage_client

                garage = get_garage_client()
                stored = garage.download_and_store_pdf(pdf_url)

                yield {
                    "url": pdf_url,
                    "source_type": "user_url",
                    "requested_by": user_id,
                    "s3_key": stored.key if stored else None,
                    "s3_bucket": stored.bucket if stored else None,
                    "size": stored.size if stored else None,
                    "status": "success" if stored else "failed",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }
            except Exception as e:
                yield {
                    "url": pdf_url,
                    "source_type": "user_url",
                    "requested_by": user_id,
                    "error": str(e),
                    "status": "error",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

    return user_documents, pdf_downloads


# =========================================================================
# GitHub Documentation Source
# =========================================================================

@dlt.source(name="github_docs")
def github_docs_source(
    repos: list[dict[str, str]] | None = None,
):
    """
    DLT source for GitHub repository documentation.

    Args:
        repos: List of repos with owner/name, e.g., [{"owner": "uniswap", "repo": "v3-core"}]

    Returns:
        DLT source with README and docs/ content
    """
    repos = repos or []

    @dlt.resource(
        name="github_readme",
        write_disposition="merge",
        primary_key=["repo_url"],
    )
    def github_readme():
        """Repository README files."""
        for repo in repos:
            owner = repo.get("owner")
            name = repo.get("repo")
            if not owner or not name:
                continue

            readme_url = f"https://raw.githubusercontent.com/{owner}/{name}/main/README.md"
            alt_url = f"https://raw.githubusercontent.com/{owner}/{name}/master/README.md"

            result = _scrape_url(readme_url)
            if result.get("status") == "error":
                result = _scrape_url(alt_url)

            result["source_type"] = "github"
            result["repo_url"] = f"https://github.com/{owner}/{name}"
            result["repo_owner"] = owner
            result["repo_name"] = name
            result["file_type"] = "readme"

            yield result

    @dlt.resource(
        name="github_docs_folder",
        write_disposition="merge",
        primary_key=["url"],
    )
    def github_docs_folder():
        """Repository docs/ folder content."""
        for repo in repos:
            owner = repo.get("owner")
            name = repo.get("repo")
            if not owner or not name:
                continue

            # Scrape GitHub Pages if available
            pages_url = f"https://{owner}.github.io/{name}"
            for page in _crawl_site(pages_url, max_depth=2, limit=30):
                page["source_type"] = "github"
                page["repo_url"] = f"https://github.com/{owner}/{name}"
                page["repo_owner"] = owner
                page["repo_name"] = name
                page["file_type"] = "docs"
                yield page

    return github_readme, github_docs_folder


# =========================================================================
# Combined Documentation Source
# =========================================================================

@dlt.source(name="all_documentation")
def all_documentation_source(
    protocols: list[str] | None = None,
    user_urls: list[str] | None = None,
    github_repos: list[dict[str, str]] | None = None,
    user_id: str | None = None,
    download_pdfs: bool = True,
    max_depth: int = 2,
    page_limit: int = 50,
):
    """
    Combined DLT source for all documentation types.

    Aggregates:
    - Protocol documentation (preconfigured)
    - User-provided URLs (dynamic)
    - GitHub repository docs

    Args:
        protocols: Protocol names to scrape
        user_urls: User-provided URLs
        github_repos: GitHub repos to scrape
        user_id: User ID for tracking
        download_pdfs: Whether to download PDFs
        max_depth: Crawl depth
        page_limit: Max pages per source

    Returns:
        Unified DLT source
    """
    protocols = protocols or []
    user_urls = user_urls or []
    github_repos = github_repos or []

    @dlt.resource(
        name="unified_docs",
        write_disposition="merge",
        primary_key=["url"],
    )
    def unified_docs():
        """All documentation unified."""
        # Protocol docs
        for protocol_name in protocols:
            if protocol_name not in PROTOCOL_DOCS:
                continue

            config = PROTOCOL_DOCS[protocol_name]
            for page in _crawl_site(
                config["docs_url"],
                max_depth=max_depth,
                limit=page_limit,
                include_paths=config.get("include_paths"),
            ):
                page["protocol"] = protocol_name
                page["source_type"] = "protocol_docs"
                yield page

        # User URLs
        for url in user_urls:
            result = _scrape_url(url)
            result["source_type"] = "user_url"
            result["requested_by"] = user_id

            pdf_links = _extract_pdf_links(
                result.get("markdown", ""),
                result.get("links", []),
            )
            result["pdf_links"] = pdf_links

            if download_pdfs and pdf_links:
                result["pdf_downloads"] = _download_pdfs_to_garage(pdf_links)

            yield result

        # GitHub repos
        for repo in github_repos:
            owner = repo.get("owner")
            name = repo.get("repo")
            if not owner or not name:
                continue

            readme_url = f"https://raw.githubusercontent.com/{owner}/{name}/main/README.md"
            result = _scrape_url(readme_url)
            result["source_type"] = "github"
            result["repo_url"] = f"https://github.com/{owner}/{name}"
            yield result

    return unified_docs
