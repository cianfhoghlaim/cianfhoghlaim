"""
Base Subject Source - Foundation for per-subject DLT resources.

Provides the BaseSubjectSource class that handles:
- Subject-specific URL resolution
- Firecrawl crawling with rate limiting
- PDF URL extraction from pages
- Bilingual support (EN/GA)
- Content hashing for deduplication

Usage:
    from cianfhoghlaim.dlt.british_isles.ie.subjects.base import (
        create_subject_source,
        crawl_subject,
        extract_pdfs_from_subject,
    )

    # Create DLT resources for a subject
    pages, pdfs = create_subject_source("mathematics", "senior_cycle", "en")
"""

from __future__ import annotations

import hashlib
import os
import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urljoin, urlparse

import dlt
import structlog

from ..curriculum_registry import SubjectRegistry, URLResolver

logger = structlog.get_logger(__name__)


# Document type patterns for classification
DOCUMENT_TYPE_PATTERNS: dict[str, list[str]] = {
    "specification": ["specification", "spec"],
    "syllabus": ["syllabus"],
    "guidelines": ["guideline", "guidelines", "guide"],
    "assessment": ["assessment", "marking", "scheme"],
    "brief": ["brief", "overview"],
    "sample": ["sample", "example"],
    "report": ["report", "examiner"],
    "circular": ["circular", "cl_"],
}


@dataclass
class CrawledPage:
    """A crawled curriculum page."""

    url: str
    title: str | None
    content: str | None
    content_hash: str
    cycle: str
    subject: str
    language: str
    source: str
    document_type: str
    crawled_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)
    links: list[str] = field(default_factory=list)
    status: str = "success"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for DLT."""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "content_hash": self.content_hash,
            "cycle": self.cycle,
            "subject": self.subject,
            "language": self.language,
            "source": self.source,
            "document_type": self.document_type,
            "crawled_at": self.crawled_at.isoformat(),
            "metadata": self.metadata,
            "status": self.status,
            "error": self.error,
        }


@dataclass
class PDFResource:
    """A PDF resource discovered from a curriculum page."""

    url: str
    cycle: str
    subject: str
    language: str
    source: str
    document_type: str
    discovered_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    source_page_url: str | None = None
    title: str | None = None
    year: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for DLT."""
        return {
            "url": self.url,
            "cycle": self.cycle,
            "subject": self.subject,
            "language": self.language,
            "source": self.source,
            "document_type": self.document_type,
            "discovered_at": self.discovered_at.isoformat(),
            "source_page_url": self.source_page_url,
            "title": self.title,
            "year": self.year,
        }


def compute_content_hash(content: str | None) -> str:
    """Compute SHA-256 hash of content for deduplication."""
    if not content:
        return hashlib.sha256(b"").hexdigest()
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def classify_document_type(url: str, title: str | None = None) -> str:
    """Classify document type from URL and title."""
    text = f"{url} {title or ''}".lower()

    for doc_type, patterns in DOCUMENT_TYPE_PATTERNS.items():
        if any(p in text for p in patterns):
            return doc_type

    return "document"


def extract_year_from_url(url: str) -> int | None:
    """Extract year from URL if present."""
    # Match 4-digit years between 1990-2030
    match = re.search(r"(19[9]\d|20[0-3]\d)", url)
    if match:
        return int(match.group(1))
    return None


def is_pdf_url(url: str) -> bool:
    """Check if URL points to a PDF file."""
    parsed = urlparse(url.lower())
    return (
        parsed.path.endswith(".pdf")
        or ".pdf" in parsed.path
        or "getmedia" in parsed.path  # curriculumonline.ie pattern
    )


def extract_pdf_urls(links: list[Any], base_url: str) -> list[str]:
    """Extract PDF URLs from a list of links."""
    pdf_urls = []

    for link in links:
        # Handle both string and dict formats
        if isinstance(link, str):
            url = link
        elif isinstance(link, dict):
            url = link.get("url") or link.get("href", "")
        else:
            continue

        if not url:
            continue

        # Make absolute URL
        if not url.startswith("http"):
            url = urljoin(base_url, url)

        if is_pdf_url(url):
            pdf_urls.append(url)

    return list(set(pdf_urls))  # Deduplicate


def _crawl_with_firecrawl(
    source_name: str,
    base_url: str,
    include_paths: list[str],
    exclude_paths: list[str] | None = None,
    max_pages: int = 50,
    max_depth: int = 3,
) -> Iterator[dict[str, Any]]:
    """Crawl using Firecrawl API."""
    try:
        from firecrawl import FirecrawlApp
    except ImportError:
        logger.warning("firecrawl_not_installed", source=source_name)
        yield {
            "url": base_url,
            "status": "firecrawl_not_installed",
            "source": source_name,
            "crawled_at": datetime.now(UTC).isoformat(),
        }
        return

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        logger.warning("firecrawl_api_key_missing", source=source_name)
        yield {
            "url": base_url,
            "status": "no_api_key",
            "source": source_name,
            "crawled_at": datetime.now(UTC).isoformat(),
        }
        return

    app = FirecrawlApp(api_key=api_key)

    try:
        logger.info(
            "crawl_started",
            source=source_name,
            base_url=base_url,
            include_paths=include_paths[:3],
            max_pages=max_pages,
        )

        # Use new firecrawl-py v2 API with keyword arguments
        from firecrawl.v2.types import ScrapeOptions

        scrape_opts = ScrapeOptions(formats=["markdown", "links"])

        result = app.crawl(
            base_url,
            limit=max_pages,
            max_discovery_depth=max_depth,
            include_paths=include_paths,
            exclude_paths=exclude_paths,
            scrape_options=scrape_opts,
            poll_interval=5,
        )

        page_count = 0
        # Handle both CrawlJob object and dict response
        pages = result.data if hasattr(result, "data") else result.get("data", [])

        for page in pages:
            page_count += 1
            # Convert Document to dict if needed
            if hasattr(page, "model_dump"):
                yield page.model_dump()
            elif hasattr(page, "dict"):
                yield page.dict()
            else:
                yield page

        logger.info(
            "crawl_completed",
            source=source_name,
            page_count=page_count,
        )

    except Exception as e:
        logger.error(
            "crawl_failed",
            source=source_name,
            error=str(e),
            error_type=type(e).__name__,
        )
        yield {
            "url": base_url,
            "error": str(e),
            "status": "error",
            "source": source_name,
            "crawled_at": datetime.now(UTC).isoformat(),
        }


def crawl_subject(
    subject: str,
    cycle: str,
    language: str = "en",
    sources: list[str] | None = None,
    max_pages: int = 50,
) -> Iterator[CrawledPage]:
    """
    Crawl curriculum pages for a specific subject.

    Args:
        subject: Subject slug (e.g., "mathematics")
        cycle: Education cycle (junior_cycle, senior_cycle)
        language: Language code ("en" or "ga")
        sources: Optional list of sources (default: curriculumonline, ncca)
        max_pages: Maximum pages per source

    Yields:
        CrawledPage objects
    """
    registry = SubjectRegistry.from_default()
    resolver = URLResolver(registry)

    if sources is None:
        sources = ["curriculumonline", "ncca"]

    subject_config = registry.get_subject(subject)
    if not subject_config:
        logger.warning("subject_not_found", subject=subject)
        return

    if cycle not in subject_config.cycles:
        logger.warning(
            "subject_not_in_cycle",
            subject=subject,
            cycle=cycle,
            available_cycles=subject_config.cycles,
        )
        return

    # Get crawl configs
    crawl_configs = resolver.resolve_urls(cycle, subject, language)

    for source_name in sources:
        if source_name not in crawl_configs:
            continue

        config = crawl_configs[source_name]

        for raw_page in _crawl_with_firecrawl(
            source_name=source_name,
            base_url=config.base_url,
            include_paths=config.include_paths,
            exclude_paths=config.exclude_paths,
            max_pages=max_pages,
        ):
            # Handle error pages
            if raw_page.get("status") in ("error", "no_api_key", "firecrawl_not_installed"):
                yield CrawledPage(
                    url=raw_page.get("url", config.base_url),
                    title=None,
                    content=None,
                    content_hash="",
                    cycle=cycle,
                    subject=subject,
                    language=language,
                    source=source_name,
                    document_type="error",
                    status=raw_page.get("status", "error"),
                    error=raw_page.get("error"),
                )
                continue

            # Extract content
            url = raw_page.get("metadata", {}).get("url") or raw_page.get("url", "")
            title = raw_page.get("metadata", {}).get("title")
            content = raw_page.get("markdown", "")
            links = raw_page.get("links", [])

            yield CrawledPage(
                url=url,
                title=title,
                content=content,
                content_hash=compute_content_hash(content),
                cycle=cycle,
                subject=subject,
                language=language,
                source=source_name,
                document_type=classify_document_type(url, title),
                metadata=raw_page.get("metadata", {}),
                links=links if isinstance(links, list) else [],
            )


def extract_pdfs_from_subject(
    subject: str,
    cycle: str,
    language: str = "en",
    sources: list[str] | None = None,
    max_pages: int = 50,
) -> Iterator[PDFResource]:
    """
    Extract PDF URLs from curriculum pages for a specific subject.

    Args:
        subject: Subject slug (e.g., "mathematics")
        cycle: Education cycle (junior_cycle, senior_cycle)
        language: Language code ("en" or "ga")
        sources: Optional list of sources
        max_pages: Maximum pages per source

    Yields:
        PDFResource objects
    """
    seen_urls: set[str] = set()

    for page in crawl_subject(subject, cycle, language, sources, max_pages):
        if page.status != "success":
            continue

        # Get base URL for relative link resolution
        base_url = page.url

        # Extract PDF URLs from links
        pdf_urls = extract_pdf_urls(page.links, base_url)

        # Also check content for PDF links
        if page.content:
            # Simple regex for PDF links in markdown
            content_pdfs = re.findall(r'\[([^\]]*)\]\(([^)]*\.pdf[^)]*)\)', page.content, re.IGNORECASE)
            for _title, pdf_url in content_pdfs:
                if not pdf_url.startswith("http"):
                    pdf_url = urljoin(base_url, pdf_url)
                pdf_urls.append(pdf_url)

        for pdf_url in pdf_urls:
            if pdf_url in seen_urls:
                continue
            seen_urls.add(pdf_url)

            yield PDFResource(
                url=pdf_url,
                cycle=cycle,
                subject=subject,
                language=language,
                source=page.source,
                document_type=classify_document_type(pdf_url),
                source_page_url=page.url,
                year=extract_year_from_url(pdf_url),
            )


def create_subject_source(
    subject: str,
    cycle: str,
    language: str = "en",
    sources: list[str] | None = None,
    max_pages: int = 50,
):
    """
    Create DLT source with pages and PDFs resources for a subject.

    Args:
        subject: Subject slug
        cycle: Education cycle
        language: Language code
        sources: Optional list of sources
        max_pages: Max pages per source

    Returns:
        Tuple of (pages_resource, pdfs_resource)
    """
    subject_clean = subject.replace("-", "_")

    @dlt.resource(
        name=f"{subject_clean}_pages",
        write_disposition="merge",
        primary_key=["url"],
        columns={
            "url": {"data_type": "text"},
            "title": {"data_type": "text"},
            "content": {"data_type": "text"},
            "content_hash": {"data_type": "text"},
            "cycle": {"data_type": "text"},
            "subject": {"data_type": "text"},
            "language": {"data_type": "text"},
            "source": {"data_type": "text"},
            "document_type": {"data_type": "text"},
            "crawled_at": {"data_type": "timestamp"},
            "metadata": {"data_type": "complex"},
            "status": {"data_type": "text"},
            "error": {"data_type": "text"},
        },
    )
    def pages_resource() -> Iterator[dict[str, Any]]:
        """Crawled pages for {subject}."""
        for page in crawl_subject(subject, cycle, language, sources, max_pages):
            yield page.to_dict()

    @dlt.resource(
        name=f"{subject_clean}_pdfs",
        write_disposition="merge",
        primary_key=["url"],
        columns={
            "url": {"data_type": "text"},
            "cycle": {"data_type": "text"},
            "subject": {"data_type": "text"},
            "language": {"data_type": "text"},
            "source": {"data_type": "text"},
            "document_type": {"data_type": "text"},
            "discovered_at": {"data_type": "timestamp"},
            "source_page_url": {"data_type": "text"},
            "title": {"data_type": "text"},
            "year": {"data_type": "bigint"},
        },
    )
    def pdfs_resource() -> Iterator[dict[str, Any]]:
        """PDF URLs for {subject}."""
        for pdf in extract_pdfs_from_subject(subject, cycle, language, sources, max_pages):
            yield pdf.to_dict()

    return pages_resource, pdfs_resource


def create_all_subject_resources(
    cycle: str,
    language: str = "en",
    subjects: list[str] | None = None,
    sources: list[str] | None = None,
    max_pages_per_subject: int = 30,
) -> list[dlt.resource]:
    """
    Create DLT resources for all subjects in a cycle.

    Args:
        cycle: Education cycle
        language: Language code
        subjects: Optional list of subjects (default: all in cycle)
        sources: Optional list of sources
        max_pages_per_subject: Max pages per subject

    Returns:
        List of DLT resources
    """
    registry = SubjectRegistry.from_default()

    if subjects is None:
        subjects = [s.slug for s in registry.get_subjects_for_cycle(cycle)]

    resources = []
    for subject in subjects:
        pages_res, pdfs_res = create_subject_source(
            subject=subject,
            cycle=cycle,
            language=language,
            sources=sources,
            max_pages=max_pages_per_subject,
        )
        resources.extend([pages_res, pdfs_res])

    logger.info(
        "subject_resources_created",
        cycle=cycle,
        language=language,
        subject_count=len(subjects),
        resource_count=len(resources),
    )

    return resources
