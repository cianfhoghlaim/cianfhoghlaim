"""
Unified Curriculum Source - Subject-centric DLT source for Isle of Man curriculum data.

Merges content from DESC, Culture Vannin, Learn Manx, and Manx Music into
a unified, deduplicated data source organized by (key_stage, subject, language).

Key Features:
- Subject-centric data model (key_stage → subject → language → source)
- Cross-source deduplication via content hashing
- Source provenance tracking
- Bilingual support (Manx/Gaelg + English)

Usage:
    from sruth.oideachais.dlt_sources.isle_of_man.curriculum_source import (
        curriculum_source,
    )

    # Crawl all sources for Secondary Manx in English
    pipeline = dlt.pipeline(pipeline_name="isle_of_man_curriculum", destination="duckdb")
    pipeline.run(curriculum_source(
        key_stage="secondary",
        subject="manx",
        language="en",
    ))

    # Crawl entire key stage (all subjects, all sources)
    pipeline.run(curriculum_source(
        key_stage="secondary",
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

from sruth.oideachais.dlt_sources.isle_of_man.curriculum_registry import (
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
    Crawl an Isle of Man curriculum source using Firecrawl.

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

# Key stage path mappings for URL generation
KEY_STAGE_PATH_MAPPING = {
    "foundation": {"en": "foundation-stage", "gv": "bun-toshee"},
    "primary": {"en": "primary", "gv": "bun-scoill"},
    "secondary": {"en": "secondary", "gv": "yn-scoill"},
    "higher": {"en": "higher-education", "gv": "ynsagh"},
}


def build_subject_urls(
    key_stage: str,
    subject: str,
    registry: SubjectRegistry | None = None,
) -> list[dict[str, str]]:
    """
    Build all URLs for an Isle of Man subject (sources × languages).

    Args:
        key_stage: Education key stage (foundation, primary, secondary, higher)
        subject: Subject slug (manx, mathematics, etc.)
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
        source = registry.get_source(source_name)

        if not source:
            continue

        # English URL
        urls.append({
            "source": source_name,
            "language": "en",
            "url": source.get_full_url(path, "en"),
        })

        # Manx URL (limited Manx content available)
        if "gv" in source.language_prefixes:
            urls.append({
                "source": source_name,
                "language": "gv",
                "url": source.get_full_url(path, "gv"),
            })

    return urls


def _scrape_single_url(
    url_config: dict[str, str],
    key_stage: str,
    subject: str,
    max_pages: int = 50,
    max_depth: int = 3,
) -> list[dict[str, Any]]:
    """
    Scrape a single URL and return normalized pages.

    Args:
        url_config: Dict with source, language, url
        key_stage: Education key stage
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
        page["key_stage"] = key_stage
        page["subject"] = subject
        page["language"] = language
        page["nation"] = "isle_of_man"
        pages.append(page)

    return pages


def parallel_scrape_subject(
    key_stage: str,
    subject: str,
    registry: SubjectRegistry | None = None,
    max_workers: int = 4,
    max_pages_per_url: int = 50,
    max_depth: int = 3,
) -> Iterator[dict[str, Any]]:
    """
    Scrape all URLs for an Isle of Man subject in parallel.

    Scrapes URLs concurrently across sources and languages.

    Args:
        key_stage: Education key stage
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

    urls = build_subject_urls(key_stage, subject, registry)

    logger.info(
        "parallel_scrape_started",
        key_stage=key_stage,
        subject=subject,
        url_count=len(urls),
    )

    # Scrape all URLs in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _scrape_single_url,
                url_config,
                key_stage,
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
                    "key_stage": key_stage,
                    "subject": subject,
                    "nation": "isle_of_man",
                    "crawled_at": datetime.now(timezone.utc).isoformat(),
                }

    logger.info(
        "parallel_scrape_completed",
        key_stage=key_stage,
        subject=subject,
    )


def _crawl_subjects(
    subjects: list[str],
    key_stage: str,
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
        key_stage: Education key stage
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

        if key_stage not in subject_config.key_stages:
            logger.debug(
                "subject_not_in_key_stage",
                subject=subject,
                key_stage=key_stage,
            )
            continue

        # Get crawl configs for this subject
        crawl_configs = resolver.resolve_urls(key_stage, subject, language)

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
                    raw_page["key_stage"] = key_stage
                    raw_page["subject"] = subject
                    raw_page["language"] = language
                    raw_page["nation"] = "isle_of_man"
                    yield raw_page
                    continue

                # Add metadata
                raw_page["key_stage"] = key_stage
                raw_page["subject"] = subject
                raw_page["language"] = language
                raw_page["nation"] = "isle_of_man"
                raw_page["source"] = source_name

                yield raw_page


@dlt.source(name="isle_of_man_curriculum")
def curriculum_source(
    key_stage: str,
    subject: str | None = None,
    language: str = "en",
    sources: list[str] | None = None,
    max_pages_per_subject: int = 50,
):
    """
    Unified DLT source for Isle of Man curriculum data.

    Subject-centric: crawls all specified sources for a (key_stage, subject, language)
    combination.

    Args:
        key_stage: Education key stage (foundation, primary, secondary, higher)
        subject: Optional subject slug. If None, crawls all subjects for the key stage.
        language: Language code ("en" or "gv")
        sources: Optional list of sources. Default: all sources.
        max_pages_per_subject: Max pages to crawl per subject per source

    Returns:
        DLT source with curriculum_pages and curriculum_pdfs

    Examples:
        # Single subject
        curriculum_source(
            key_stage="secondary",
            subject="manx",
            language="en",
        )

        # All subjects in a key stage
        curriculum_source(
            key_stage="secondary",
            language="gv",
        )

        # Specific sources only
        curriculum_source(
            key_stage="secondary",
            subject="manx",
            sources=["learn_manx", "culture_vannin"],
        )
    """
    # Initialize components
    registry = SubjectRegistry.from_default()
    resolver = URLResolver(registry)

    # Default to all sources
    if sources is None:
        sources = ["desc", "culture_vannin", "learn_manx", "manx_music"]

    # Determine subjects to crawl
    if subject:
        subjects = [subject]
    else:
        subjects = [s.slug for s in registry.get_subjects_for_key_stage(key_stage)]

    logger.info(
        "isle_of_man_curriculum_source_initialized",
        key_stage=key_stage,
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
            "key_stage": {"data_type": "text"},
            "subject": {"data_type": "text"},
            "language": {"data_type": "text"},
            "source": {"data_type": "text"},
            "nation": {"data_type": "text"},
            "crawled_at": {"data_type": "timestamp"},
            "metadata": {"data_type": "complex"},
        },
    )
    def curriculum_pages() -> Iterator[dict[str, Any]]:
        """Crawled Isle of Man curriculum pages."""
        for page_data in _crawl_subjects(
            subjects=subjects,
            key_stage=key_stage,
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
            "key_stage": {"data_type": "text"},
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
            key_stage=key_stage,
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
                        "key_stage": key_stage,
                        "subject": page_data.get("subject"),
                        "language": language,
                        "nation": "isle_of_man",
                        "source": page_data.get("source"),
                        "pdf_type": _classify_pdf(link),
                        "discovered_at": datetime.now(timezone.utc).isoformat(),
                    }

    return curriculum_pages, curriculum_pdfs


def _classify_pdf(url: str) -> str:
    """Classify a PDF by its URL."""
    url_lower = url.lower()

    if "specification" in url_lower:
        return "specification"
    elif "past-paper" in url_lower or "exam" in url_lower:
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


def crawl_key_stage(
    key_stage: str,
    language: str = "en",
    sources: list[str] | None = None,
    max_pages_per_subject: int = 30,
):
    """
    Convenience function to crawl an entire key stage.

    Args:
        key_stage: Education key stage
        language: Language code
        sources: Optional list of sources
        max_pages_per_subject: Max pages per subject

    Returns:
        DLT source for the key stage
    """
    return curriculum_source(
        key_stage=key_stage,
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
    Convenience function to crawl a single subject across all its key stages.

    Args:
        subject: Subject slug
        language: Language code
        sources: Optional list of sources
        max_pages: Max pages per key stage

    Returns:
        Generator of DLT sources for each key stage
    """
    registry = SubjectRegistry.from_default()
    subject_config = registry.get_subject(subject)

    if not subject_config:
        logger.warning("subject_not_found", subject=subject)
        return

    for key_stage in subject_config.key_stages:
        yield curriculum_source(
            key_stage=key_stage,
            subject=subject,
            language=language,
            sources=sources,
            max_pages_per_subject=max_pages,
        )


__all__ = [
    "curriculum_source",
    "parallel_scrape_subject",
    "build_subject_urls",
    "crawl_key_stage",
    "crawl_subject",
]
