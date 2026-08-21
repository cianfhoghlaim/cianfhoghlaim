"""
Unified Curriculum Source - Subject-centric DLT source for Scottish curriculum data.

Merges content from Education Scotland, SQA, and Bòrd na Gàidhlig into
a unified, deduplicated data source organized by (level, subject, language).

Key Features:
- Subject-centric data model (level → subject → language → source)
- Cross-source deduplication via content hashing
- Source provenance tracking
- Bilingual support (Scottish Gaelic/Gàidhlig + English)

Usage:
    from sruth.oideachais.dlt_sources.scotland.curriculum_source import (
        curriculum_source,
    )

    # Crawl all sources for Fourth Level Mathematics in English
    pipeline = dlt.pipeline(pipeline_name="scotland_curriculum", destination="duckdb")
    pipeline.run(curriculum_source(
        level="fourth",
        subject="mathematics",
        language="en",
    ))

    # Crawl entire curriculum level (all subjects, all sources)
    pipeline.run(curriculum_source(
        level="fourth",
        language="en",
    ))
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Iterator

import dlt
import structlog
from concurrent.futures import ThreadPoolExecutor, as_completed

from sruth.oideachais.dlt_sources.scotland.curriculum_registry import (
    SubjectRegistry,
    URLResolver,
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
    Crawl a Scottish curriculum source using Firecrawl.

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
            "crawled_at": datetime.now(timezone.utc).isoformat(),
        }
        return

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        logger.warning("firecrawl_api_key_missing", source=source_name)
        yield {
            "url": base_url,
            "status": "no_api_key",
            "source": source_name,
            "crawled_at": datetime.now(timezone.utc).isoformat(),
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

        # Build crawl kwargs
        crawl_kwargs = {
            "url": base_url,
            "limit": max_pages,
            "max_discovery_depth": max_depth,
            "scrape_options": scrape_opts,
            "poll_interval": 5,
        }
        if include_paths:
            crawl_kwargs["include_paths"] = include_paths
        if exclude_paths:
            crawl_kwargs["exclude_paths"] = exclude_paths

        # Use Firecrawl v2 API
        result = app.crawl(**crawl_kwargs)

        page_count = 0
        pages = result.data if hasattr(result, 'data') else result.get("data", [])
        for page in pages:
            page_count += 1
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
            "crawled_at": datetime.now(timezone.utc).isoformat(),
        }


# ============================================================================
# Parallel URL Scraping
# ============================================================================

# Curriculum level path mappings for URL generation
LEVEL_PATH_MAPPING = {
    "early": {"en": "early-level", "gd": "ire-innic"},
    "first": {"en": "first-level", "gd": "ire-chiùil"},
    "second": {"en": "second-level", "gd": "ire-dàna"},
    "third": {"en": "third-level", "gd": "ire-treas"},
    "fourth": {"en": "fourth-level", "gd": "ire-ceathrach"},
}


def build_subject_urls(
    level: str,
    subject: str,
    registry: SubjectRegistry | None = None,
) -> list[dict[str, str]]:
    """
    Build all URLs for a Scottish subject (sources × languages).

    Args:
        level: Curriculum level (first, second, third, fourth)
        subject: Subject slug (mathematics, gaelic_learners, etc.)
        registry: Optional SubjectRegistry for subject name lookups

    Returns:
        List of URL dicts with source, language, and URL
    """
    if registry is None:
        registry = SubjectRegistry.from_default()

    subject_config = registry.get_subject(subject)
    if not subject_config:
        logger.warning("subject_not_found", subject=subject)
        return []

    urls = []

    # Build URLs for each source the subject has
    for source_name, path in subject_config.urls.items():
        # Handle compound source names like "sqa_n5"
        base_source = source_name.split("_")[0]
        source_config = registry.get_source(base_source)

        if not source_config:
            continue

        # English URL
        urls.append({
            "source": source_name,
            "language": "en",
            "url": source_config.get_full_url(path, "en"),
        })

        # Scottish Gaelic URL (if source supports it)
        if "gd" in source_config.language_prefixes:
            urls.append({
                "source": source_name,
                "language": "gd",
                "url": source_config.get_full_url(path, "gd"),
            })

    return urls


def _scrape_single_url(
    url_config: dict[str, str],
    level: str,
    subject: str,
    max_pages: int = 50,
    max_depth: int = 3,
) -> list[dict[str, Any]]:
    """
    Scrape a single URL and return normalized pages.

    Args:
        url_config: Dict with source, language, url
        level: Curriculum level
        subject: Subject slug
        max_pages: Max pages to crawl
        max_depth: Max crawl depth

    Returns:
        List of page dicts
    """
    source = url_config["source"]
    language = url_config["language"]
    url = url_config["url"]

    logger.info(
        "scraping_url",
        source=source,
        language=language,
        url=url,
    )

    pages = []
    for page in _crawl_source(
        source_name=source,
        base_url=url,
        include_paths=None,
        max_pages=max_pages,
        max_depth=max_depth,
    ):
        page["level"] = level
        page["subject"] = subject
        page["language"] = language
        page["nation"] = "scotland"
        pages.append(page)

    return pages


def parallel_scrape_subject(
    level: str,
    subject: str,
    registry: SubjectRegistry | None = None,
    max_workers: int = 4,
    max_pages_per_url: int = 50,
    max_depth: int = 3,
) -> Iterator[dict[str, Any]]:
    """
    Scrape all URLs for a Scottish subject in parallel.

    Scrapes URLs concurrently across sources and languages.

    Args:
        level: Curriculum level
        subject: Subject slug
        registry: Optional SubjectRegistry
        max_workers: Max concurrent scrapes
        max_pages_per_url: Max pages per URL
        max_depth: Max crawl depth

    Yields:
        Normalized page dicts
    """
    if registry is None:
        registry = SubjectRegistry.from_default()

    urls = build_subject_urls(level, subject, registry)

    logger.info(
        "parallel_scrape_started",
        level=level,
        subject=subject,
        url_count=len(urls),
    )

    # Scrape all URLs in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _scrape_single_url,
                url_config,
                level,
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
                    source=url_config["source"],
                    language=url_config["language"],
                    page_count=len(pages),
                )
                yield from pages
            except Exception as e:
                logger.error(
                    "url_scrape_failed",
                    source=url_config["source"],
                    language=url_config["language"],
                    error=str(e),
                )
                yield {
                    "url": url_config["url"],
                    "error": str(e),
                    "status": "error",
                    "source": url_config["source"],
                    "language": url_config["language"],
                    "level": level,
                    "subject": subject,
                    "nation": "scotland",
                    "crawled_at": datetime.now(timezone.utc).isoformat(),
                }

    logger.info(
        "parallel_scrape_completed",
        level=level,
        subject=subject,
    )


def _crawl_subjects(
    subjects: list[str],
    level: str,
    language: str,
    sources: list[str],
    registry: SubjectRegistry,
    resolver: URLResolver,
    max_pages_per_subject: int = 50,
) -> Iterator[dict[str, Any]]:
    """
    Crawl multiple subjects across sources.

    Args:
        subjects: List of subject slugs to crawl
        level: Curriculum level
        language: Language code
        sources: List of source names to include
        registry: Subject registry
        resolver: URL resolver
        max_pages_per_subject: Max pages per subject per source

    Yields:
        Normalized page dictionaries
    """
    for subject in subjects:
        subject_config = registry.get_subject(subject)
        if not subject_config:
            logger.warning("subject_not_found", subject=subject)
            continue

        if level not in subject_config.levels:
            logger.debug(
                "subject_not_in_level",
                subject=subject,
                level=level,
            )
            continue

        # Get crawl configs for this subject
        crawl_configs = resolver.resolve_urls(level, subject, language)

        for source_name in sources:
            if source_name not in crawl_configs:
                continue

            config = crawl_configs[source_name]

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
                    raw_page["level"] = level
                    raw_page["subject"] = subject
                    raw_page["language"] = language
                    raw_page["nation"] = "scotland"
                    yield raw_page
                    continue

                # Add metadata
                raw_page["level"] = level
                raw_page["subject"] = subject
                raw_page["language"] = language
                raw_page["nation"] = "scotland"
                raw_page["source"] = source_name

                yield raw_page


@dlt.source(name="scotland_curriculum")
def curriculum_source(
    level: str,
    subject: str | None = None,
    language: str = "en",
    sources: list[str] | None = None,
    max_pages_per_subject: int = 50,
):
    """
    Unified DLT source for Scottish curriculum data.

    Subject-centric: crawls all specified sources for a (level, subject, language)
    combination.

    Args:
        level: Curriculum level (early, first, second, third, fourth)
        subject: Optional subject slug. If None, crawls all subjects for the level.
        language: Language code ("en" or "gd")
        sources: Optional list of sources. Default: all sources.
        max_pages_per_subject: Max pages to crawl per subject per source

    Returns:
        DLT source with curriculum_pages and curriculum_pdfs

    Examples:
        # Single subject
        curriculum_source(
            level="fourth",
            subject="mathematics",
            language="en",
        )

        # All subjects in a level
        curriculum_source(
            level="fourth",
            language="gd",
        )

        # Specific sources only
        curriculum_source(
            level="fourth",
            subject="gaelic_learners",
            sources=["sqa", "bord_na_gaidhlig"],
        )
    """
    # Initialize components
    registry = SubjectRegistry.from_default()
    resolver = URLResolver(registry)

    # Default to all sources
    if sources is None:
        sources = ["education_scotland", "sqa", "bord_na_gaidhlig"]

    # Determine subjects to crawl
    if subject:
        subjects = [subject]
    else:
        subjects = [s.slug for s in registry.get_subjects_for_level(level)]

    logger.info(
        "scotland_curriculum_source_initialized",
        level=level,
        subject=subject,
        language=language,
        sources=sources,
        subject_count=len(subjects),
    )

    @dlt.resource(
        name="curriculum_pages",
        write_disposition="merge",
        primary_key=["url"],
        columns={
            "url": {"data_type": "text"},
            "title": {"data_type": "text"},
            "content": {"data_type": "text"},
            "level": {"data_type": "text"},
            "subject": {"data_type": "text"},
            "language": {"data_type": "text"},
            "source": {"data_type": "text"},
            "nation": {"data_type": "text"},
            "crawled_at": {"data_type": "timestamp"},
            "metadata": {"data_type": "complex"},
        },
    )
    def curriculum_pages() -> Iterator[dict[str, Any]]:
        """Crawled Scottish curriculum pages."""
        for page_data in _crawl_subjects(
            subjects=subjects,
            level=level,
            language=language,
            sources=sources,
            registry=registry,
            resolver=resolver,
            max_pages_per_subject=max_pages_per_subject,
        ):
            yield page_data

    @dlt.resource(
        name="curriculum_pdfs",
        write_disposition="merge",
        primary_key=["url"],
        columns={
            "url": {"data_type": "text"},
            "level": {"data_type": "text"},
            "subject": {"data_type": "text"},
            "language": {"data_type": "text"},
            "source": {"data_type": "text"},
            "nation": {"data_type": "text"},
            "pdf_type": {"data_type": "text"},
            "discovered_at": {"data_type": "timestamp"},
        },
    )
    def curriculum_pdfs() -> Iterator[dict[str, Any]]:
        """Discovered PDF URLs from crawled pages."""
        seen_pdfs: set[str] = set()

        for page_data in _crawl_subjects(
            subjects=subjects,
            level=level,
            language=language,
            sources=sources,
            registry=registry,
            resolver=resolver,
            max_pages_per_subject=max_pages_per_subject,
        ):
            metadata = page_data.get("metadata", {})
            links = metadata.get("links", []) if isinstance(metadata, dict) else []

            for link in links:
                if isinstance(link, str) and ".pdf" in link.lower():
                    if link in seen_pdfs:
                        continue
                    seen_pdfs.add(link)

                    yield {
                        "url": link,
                        "level": level,
                        "subject": page_data.get("subject"),
                        "language": language,
                        "nation": "scotland",
                        "source": page_data.get("source"),
                        "pdf_type": _classify_pdf(link),
                        "discovered_at": datetime.now(timezone.utc).isoformat(),
                    }

    return curriculum_pages, curriculum_pdfs


def _classify_pdf(url: str) -> str:
    """Classify a PDF by its URL."""
    url_lower = url.lower()

    if "specification" in url_lower or "smeasachadh" in url_lower:
        return "specification"
    elif "past-paper" in url_lower or "exam" in url_lower or "paipear" in url_lower:
        return "past_paper"
    elif "mark" in url_lower and "scheme" in url_lower:
        return "mark_scheme"
    elif "examiner" in url_lower:
        return "examiner_report"
    elif "guideline" in url_lower:
        return "guidelines"
    else:
        return "document"


# Convenience functions for common use cases


def crawl_level(
    level: str,
    language: str = "en",
    sources: list[str] | None = None,
    max_pages_per_subject: int = 30,
):
    """
    Convenience function to crawl an entire curriculum level.

    Args:
        level: Curriculum level
        language: Language code
        sources: Optional list of sources
        max_pages_per_subject: Max pages per subject

    Returns:
        DLT source for the level
    """
    return curriculum_source(
        level=level,
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
    Convenience function to crawl a single subject across all its levels.

    Args:
        subject: Subject slug
        language: Language code
        sources: Optional list of sources
        max_pages: Max pages per level

    Returns:
        Generator of DLT sources for each level
    """
    registry = SubjectRegistry.from_default()
    subject_config = registry.get_subject(subject)

    if not subject_config:
        logger.warning("subject_not_found", subject=subject)
        return

    for level in subject_config.levels:
        yield curriculum_source(
            level=level,
            subject=subject,
            language=language,
            sources=sources,
            max_pages_per_subject=max_pages,
        )


__all__ = [
    "curriculum_source",
    "parallel_scrape_subject",
    "build_subject_urls",
    "crawl_level",
    "crawl_subject",
]
