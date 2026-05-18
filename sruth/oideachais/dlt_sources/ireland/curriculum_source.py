"""
Unified Curriculum Source - Subject-centric DLT source for Irish curriculum data.

Merges content from curriculumonline.ie, ncca.ie, and examinations.ie into
a unified, deduplicated data source organized by (cycle, subject, language).

Key Features:
- Subject-centric data model (cycle → subject → language → source)
- Cross-source deduplication via content hashing
- Source provenance tracking
- Efficient incremental updates

Usage:
    from oideachais.dlt_sources.ireland.curriculum_source import (
        curriculum_source,
    )

    # Crawl all sources for Junior Cycle Mathematics in English
    pipeline = dlt.pipeline(pipeline_name="curriculum", destination="duckdb")
    pipeline.run(curriculum_source(
        cycle="junior_cycle",
        subject="mathematics",
        language="en",
    ))

    # Crawl entire cycle (all subjects, all sources)
    pipeline.run(curriculum_source(
        cycle="junior_cycle",
        language="en",
    ))
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from typing import Any

import dlt
import structlog
from oideachais.dlt_sources.ireland.content_deduplication import (
    ContentDeduplicator,
)
from oideachais.dlt_sources.ireland.curriculum_registry import (
    SubjectRegistry,
    URLResolver,
)
from oideachais.dlt_sources.ireland.source_adapters import (
    get_all_adapters,
)

logger = structlog.get_logger(__name__)


def _crawl_source(
    source_name: str,
    base_url: str,
    include_paths: list[str] | None = None,
    exclude_paths: list[str] | None = None,
    max_pages: int = 50,
    max_depth: int = 3,
) -> Iterator[dict[str, Any]]:
    """
    Crawl a curriculum source using Firecrawl.

    Args:
        source_name: Name of the source for logging
        base_url: Base URL to crawl
        include_paths: URL patterns to include
        exclude_paths: URL patterns to exclude
        max_pages: Maximum pages to crawl
        max_depth: Maximum crawl depth

    Yields:
        Raw page dictionaries from Firecrawl
    """
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

    # Build scrape options for the new Firecrawl v2 API
    try:
        from firecrawl.v2.types import ScrapeOptions
        scrape_opts = ScrapeOptions(formats=["markdown", "links"])
    except ImportError:
        scrape_opts = None

    try:
        # Handle None or empty include_paths
        paths_to_log = include_paths[:3] if include_paths else []
        logger.info(
            "crawl_started",
            source=source_name,
            base_url=base_url,
            include_paths=paths_to_log,
            max_pages=max_pages,
        )

        # Build crawl kwargs - only include paths if non-empty
        crawl_kwargs = {
            "url": base_url,
            "limit": max_pages,
            "max_discovery_depth": max_depth,
            "scrape_options": scrape_opts,
            "poll_interval": 5,
        }
        # Only add include_paths if it's a non-empty list (Firecrawl treats '*' as invalid regex)
        if include_paths:
            crawl_kwargs["include_paths"] = include_paths
        if exclude_paths:
            crawl_kwargs["exclude_paths"] = exclude_paths

        # Use new Firecrawl v2 API: crawl() with direct parameters
        result = app.crawl(**crawl_kwargs)

        page_count = 0
        # Result is a CrawlJob object with .data attribute
        pages = result.data if hasattr(result, 'data') else result.get("data", [])
        for page in pages:
            page_count += 1
            # Convert Document object to dict if needed
            if hasattr(page, 'model_dump'):
                yield page.model_dump()
            elif hasattr(page, 'dict'):
                yield page.dict()
            else:
                yield page

        logger.info(
            "crawl_completed",
            source=source_name,
            page_count=page_count,
        )

    except (RuntimeError, ConnectionError, TimeoutError, ValueError) as e:
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


# ============================================================================
# Parallel URL Scraping (for known subject URLs)
# ============================================================================

# Cycle path mappings for URL generation
CYCLE_PATH_MAPPING = {
    "early_childhood": {"en": "early-childhood", "ga": "an-luath-oige"},
    "primary": {"en": "primary", "ga": "bunscoil"},
    "junior_cycle": {"en": "junior-cycle", "ga": "an-tsraith-shoisearach"},
    "senior_cycle": {"en": "senior-cycle", "ga": "an-tsraith-shinsearach"},
}

# NCCA Irish path mappings for cycles
NCCA_CYCLE_GA = {
    "early_childhood": "an-luath-oige",
    "primary": "bunscoil",
    "junior_cycle": "an-tsraith-shoisearach",
    "senior_cycle": "an-tsraith-shinsearach",
}


def build_subject_urls(
    cycle: str,
    subject: str,
    registry: SubjectRegistry | None = None,
    language: str | None = None,
) -> list[dict[str, str]]:
    """
    Build all 4 URLs for a subject (2 sites × 2 languages).
    Optionally filter by language.

    Args:
        cycle: Education cycle (junior_cycle, senior_cycle, etc.)
        subject: Subject slug (chemistry, mathematics, etc.)
        registry: Optional SubjectRegistry for subject name lookups
        language: Optional language code ("en" or "ga") to filter results

    Returns:
        List of URL dicts with site, language, and URL
    """
    if registry is None:
        registry = SubjectRegistry.from_default()

    cycle_en = CYCLE_PATH_MAPPING.get(cycle, {}).get("en", cycle.replace("_", "-"))
    cycle_ga = NCCA_CYCLE_GA.get(cycle, cycle.replace("_", "-"))

    # Get subject config for Irish name (if available)
    subject_config = registry.get_subject(subject)
    subject_ga = subject  # Default to English slug

    if subject_config and "ga" in subject_config.name:
        # Use Irish name from registry if available
        subject_ga = subject_config.name.get("ga", subject)
        # Convert to URL-safe slug
        subject_ga = subject_ga.lower().replace(" ", "-")

    urls = [
        # Curriculum Online - English
        {
            "site": "curriculumonline",
            "language": "en",
            "url": f"https://www.curriculumonline.ie/{cycle_en}/{cycle_en}-subjects/{subject}/",
        },
        # Curriculum Online - Irish
        {
            "site": "curriculumonline",
            "language": "ga",
            "url": f"https://www.curriculumonline.ie/ga-ie/{cycle_en}/{cycle_en}-subjects/{subject}/",
        },
        # NCCA - English
        {
            "site": "ncca",
            "language": "en",
            "url": f"https://ncca.ie/en/{cycle_en}/curriculum-developments/{subject}/",
        },
        # NCCA - Irish
        {
            "site": "ncca",
            "language": "ga",
            "url": f"https://ncca.ie/ga/{cycle_ga}/forbairtí-curaclaim/{subject_ga}/",
        },
    ]

    if language:
        urls = [u for u in urls if u["language"] == language]

    return urls


def _scrape_single_url(
    url_config: dict[str, str],
    cycle: str,
    subject: str,
    max_pages: int = 50,
    max_depth: int = 3,
) -> list[dict[str, Any]]:
    """
    Scrape a single URL and return normalized pages.

    Args:
        url_config: Dict with site, language, url
        cycle: Education cycle
        subject: Subject slug
        max_pages: Max pages to crawl
        max_depth: Max crawl depth

    Returns:
        List of page dicts
    """
    site = url_config["site"]
    language = url_config["language"]
    url = url_config["url"]

    logger.info(
        "scraping_url",
        site=site,
        language=language,
        url=url,
    )

    pages = []
    for page in _crawl_source(
        source_name=site,
        base_url=url,
        include_paths=None,  # Crawl all pages from base URL (no path filter)
        max_pages=max_pages,
        max_depth=max_depth,
    ):
        # Add metadata
        page["cycle"] = cycle
        page["subject"] = subject
        page["language"] = language
        page["source"] = site
        pages.append(page)

    return pages


def parallel_scrape_subject(
    cycle: str,
    subject: str,
    registry: SubjectRegistry | None = None,
    language: str | None = None,
    max_workers: int = 2,
    max_pages_per_url: int = 50,
    max_depth: int = 3,
) -> Iterator[dict[str, Any]]:
    """
    Scrape all URLs for a subject in parallel.

    Scrapes URLs concurrently:
    - curriculumonline.ie (en)
    - curriculumonline.ie (ga)
    - ncca.ie (en)
    - ncca.ie (ga)
    
    If language is provided, only that language's URLs are scraped.

    Args:
        cycle: Education cycle
        subject: Subject slug
        registry: Optional SubjectRegistry
        language: Optional language code ("en" or "ga")
        max_workers: Max concurrent scrapes (default 2 to prevent rate limits)
        max_pages_per_url: Max pages per URL
        max_depth: Max crawl depth

    Yields:
        Normalized page dicts
    """
    if registry is None:
        registry = SubjectRegistry.from_default()

    urls = build_subject_urls(cycle, subject, registry, language=language)

    logger.info(
        "parallel_scrape_started",
        cycle=cycle,
        subject=subject,
        url_count=len(urls),
    )

    # Scrape all URLs in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _scrape_single_url,
                url_config,
                cycle,
                subject,
                max_pages_per_url,
                max_depth,
            ): url_config
            for url_config in urls
        }

        for future in as_completed(futures):
            url_config = futures[future]
            try:
                pages = future.result()
                logger.info(
                    "url_scrape_completed",
                    site=url_config["site"],
                    language=url_config["language"],
                    page_count=len(pages),
                )
                yield from pages
            except Exception as e:
                logger.error(
                    "url_scrape_failed",
                    site=url_config["site"],
                    language=url_config["language"],
                    error=str(e),
                )
                # Yield error record
                yield {
                    "url": url_config["url"],
                    "error": str(e),
                    "status": "error",
                    "source": url_config["site"],
                    "language": url_config["language"],
                    "cycle": cycle,
                    "subject": subject,
                    "crawled_at": datetime.now(UTC).isoformat(),
                }

    logger.info(
        "parallel_scrape_completed",
        cycle=cycle,
        subject=subject,
    )


def _crawl_subjects(
    subjects: list[str],
    cycle: str,
    language: str,
    sources: list[str],
    registry: SubjectRegistry,
    resolver: URLResolver,
    deduplicator: ContentDeduplicator,
    max_pages_per_subject: int = 50,
) -> Iterator[dict[str, Any]]:
    """
    Crawl multiple subjects across sources with deduplication.

    Args:
        subjects: List of subject slugs to crawl
        cycle: Education cycle
        language: Language code
        sources: List of source names to include
        registry: Subject registry
        resolver: URL resolver
        deduplicator: Content deduplicator
        max_pages_per_subject: Max pages per subject per source

    Yields:
        Normalized page dictionaries
    """
    adapters = get_all_adapters()

    for subject in subjects:
        subject_config = registry.get_subject(subject)
        if not subject_config:
            logger.warning("subject_not_found", subject=subject)
            continue

        if cycle not in subject_config.cycles:
            logger.debug(
                "subject_not_in_cycle",
                subject=subject,
                cycle=cycle,
            )
            continue

        # Get crawl configs for this subject
        crawl_configs = resolver.resolve_urls(cycle, subject, language)

        for source_name in sources:
            if source_name not in crawl_configs:
                continue

            config = crawl_configs[source_name]
            adapter = adapters.get(source_name)
            if not adapter:
                continue

            # Crawl the source
            for raw_page in _crawl_source(
                source_name=source_name,
                base_url=config.base_url,
                include_paths=config.include_paths,
                exclude_paths=config.exclude_paths,
                max_pages=max_pages_per_subject,
            ):
                # Handle error pages
                if raw_page.get("status") in ("error", "no_api_key", "firecrawl_not_installed"):
                    raw_page["cycle"] = cycle
                    raw_page["subject"] = subject
                    raw_page["language"] = language
                    yield raw_page
                    continue

                # Normalize the page
                normalized = adapter.normalize_page(
                    raw_page,
                    cycle=cycle,
                    subject=subject,
                    language=language,
                )

                # Check for duplicates
                result = deduplicator.process_page(normalized)

                if result.is_new:
                    yield normalized.to_dict()
                else:
                    # Yield provenance record instead
                    yield result.to_provenance_record()


@dlt.source(name="ireland_curriculum")
def curriculum_source(
    cycle: str,
    subject: str | None = None,
    language: str = "en",
    sources: list[str] | None = None,
    max_pages_per_subject: int = 50,
    deduplicate: bool = True,
):
    """
    Unified DLT source for Irish curriculum data.

    Subject-centric: crawls all specified sources for a (cycle, subject, language)
    combination, deduplicating content across sources.

    Args:
        cycle: Education cycle (early_childhood, primary, junior_cycle, senior_cycle)
        subject: Optional subject slug. If None, crawls all subjects for the cycle.
        language: Language code ("en" or "ga")
        sources: Optional list of sources. Default: all sources.
        max_pages_per_subject: Max pages to crawl per subject per source
        deduplicate: Whether to deduplicate content across sources

    Returns:
        DLT source with curriculum_pages, curriculum_pdfs, and source_provenance

    Examples:
        # Single subject
        curriculum_source(
            cycle="junior_cycle",
            subject="mathematics",
            language="en",
        )

        # All subjects in a cycle
        curriculum_source(
            cycle="senior_cycle",
            language="ga",
        )

        # Specific sources only
        curriculum_source(
            cycle="junior_cycle",
            subject="irish",
            sources=["ncca", "curriculumonline"],
        )
    """
    # Initialize components
    registry = SubjectRegistry.from_default()
    resolver = URLResolver(registry)
    deduplicator = ContentDeduplicator() if deduplicate else None

    # Default to all sources
    if sources is None:
        sources = ["curriculumonline", "ncca", "examinations"]

    # Determine subjects to crawl
    if subject:
        subjects = [subject]
    else:
        subjects = [s.slug for s in registry.get_subjects_for_cycle(cycle)]

    logger.info(
        "curriculum_source_initialized",
        cycle=cycle,
        subject=subject,
        language=language,
        sources=sources,
        subject_count=len(subjects),
    )

    @dlt.resource(
        name="curriculum_pages",
        write_disposition="merge",
        primary_key=["content_hash"],
        columns={
            "url": {"data_type": "text"},
            "title": {"data_type": "text"},
            "content": {"data_type": "text"},
            "content_hash": {"data_type": "text"},
            "cycle": {"data_type": "text"},
            "subject": {"data_type": "text"},
            "language": {"data_type": "text"},
            "source": {"data_type": "text"},
            "crawled_at": {"data_type": "timestamp"},
            "metadata": {"data_type": "complex"},
        },
    )
    def curriculum_pages() -> Iterator[dict[str, Any]]:
        """Crawled and deduplicated curriculum pages."""
        nonlocal deduplicator
        if deduplicator is None:
            deduplicator = ContentDeduplicator()

        for page_data in _crawl_subjects(
            subjects=subjects,
            cycle=cycle,
            language=language,
            sources=sources,
            registry=registry,
            resolver=resolver,
            deduplicator=deduplicator,
            max_pages_per_subject=max_pages_per_subject,
        ):
            # Filter out provenance records (they go to source_provenance)
            if not page_data.get("is_duplicate"):
                yield page_data

    @dlt.resource(
        name="source_provenance",
        write_disposition="merge",
        primary_key=["content_hash", "source"],
        columns={
            "content_hash": {"data_type": "text"},
            "source": {"data_type": "text"},
            "source_url": {"data_type": "text"},
            "canonical_url": {"data_type": "text"},
            "discovered_at": {"data_type": "timestamp"},
            "is_duplicate": {"data_type": "bool"},
        },
    )
    def source_provenance() -> Iterator[dict[str, Any]]:
        """Track which sources provide which content."""
        nonlocal deduplicator
        if deduplicator is None:
            deduplicator = ContentDeduplicator()

        for page_data in _crawl_subjects(
            subjects=subjects,
            cycle=cycle,
            language=language,
            sources=sources,
            registry=registry,
            resolver=resolver,
            deduplicator=deduplicator,
            max_pages_per_subject=max_pages_per_subject,
        ):
            # Only yield provenance records (duplicates)
            if page_data.get("is_duplicate"):
                yield page_data

    @dlt.resource(
        name="curriculum_pdfs",
        write_disposition="merge",
        primary_key=["url"],
        columns={
            "url": {"data_type": "text"},
            "cycle": {"data_type": "text"},
            "subject": {"data_type": "text"},
            "language": {"data_type": "text"},
            "source": {"data_type": "text"},
            "pdf_type": {"data_type": "text"},
            "discovered_at": {"data_type": "timestamp"},
        },
    )
    def curriculum_pdfs() -> Iterator[dict[str, Any]]:
        """Discovered PDF URLs from crawled pages."""
        # Extract PDF URLs from crawled page links
        seen_pdfs: set[str] = set()

        for page_data in _crawl_subjects(
            subjects=subjects,
            cycle=cycle,
            language=language,
            sources=sources,
            registry=registry,
            resolver=resolver,
            deduplicator=ContentDeduplicator(),  # Fresh deduplicator
            max_pages_per_subject=max_pages_per_subject,
        ):
            # Extract PDF links from metadata
            metadata = page_data.get("metadata", {})
            links = metadata.get("links", [])

            for link in links:
                if isinstance(link, str) and ".pdf" in link.lower():
                    if link in seen_pdfs:
                        continue
                    seen_pdfs.add(link)

                    yield {
                        "url": link,
                        "cycle": cycle,
                        "subject": page_data.get("subject"),
                        "language": language,
                        "source": page_data.get("source"),
                        "pdf_type": _classify_pdf(link),
                        "discovered_at": datetime.now(UTC).isoformat(),
                    }

    return curriculum_pages, source_provenance, curriculum_pdfs


def _classify_pdf(url: str) -> str:
    """Classify a PDF by its URL."""
    url_lower = url.lower()

    if "specification" in url_lower or "spec" in url_lower:
        return "specification"
    elif "syllabus" in url_lower:
        return "syllabus"
    elif "marking" in url_lower or "scheme" in url_lower:
        return "marking_scheme"
    elif "examiner" in url_lower or "cer_" in url_lower:
        return "examiner_report"
    elif "circular" in url_lower:
        return "circular"
    elif "guideline" in url_lower:
        return "guidelines"
    elif "brief" in url_lower:
        return "brief"
    else:
        return "document"


# Convenience functions for common use cases


def crawl_cycle(
    cycle: str,
    language: str = "en",
    sources: list[str] | None = None,
    max_pages_per_subject: int = 30,
):
    """
    Convenience function to crawl an entire education cycle.

    Args:
        cycle: Education cycle
        language: Language code
        sources: Optional list of sources
        max_pages_per_subject: Max pages per subject

    Returns:
        DLT source for the cycle
    """
    return curriculum_source(
        cycle=cycle,
        subject=None,  # All subjects
        language=language,
        sources=sources,
        max_pages_per_subject=max_pages_per_subject,
    )


def crawl_subject(
    subject: str,
    language: str = "en",
    sources: list[str] | None = None,
    max_pages: int = 100,
):
    """
    Convenience function to crawl a single subject across all its cycles.

    Args:
        subject: Subject slug
        language: Language code
        sources: Optional list of sources
        max_pages: Max pages per cycle

    Returns:
        Generator of DLT sources for each cycle
    """
    registry = SubjectRegistry.from_default()
    subject_config = registry.get_subject(subject)

    if not subject_config:
        logger.warning("subject_not_found", subject=subject)
        return

    for cycle in subject_config.cycles:
        yield curriculum_source(
            cycle=cycle,
            subject=subject,
            language=language,
            sources=sources,
            max_pages_per_subject=max_pages,
        )
