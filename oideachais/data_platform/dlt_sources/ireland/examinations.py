"""
DLT source for examinations.ie (State Examinations Commission).

Crawls and extracts:
- Chief Examiner Reports (200+ PDFs)
- Exam material archives
- Marking schemes
- Statistics and circulars
"""

import os
from collections.abc import Iterator
from datetime import UTC, datetime
from logging import basicConfig, getLogger
from typing import Any

import dlt
import logfire

logfire.configure(send_to_logfire='if-token-present')
basicConfig(handlers=[logfire.LogfireLoggingHandler()])

logger = getLogger(__name__)


def _crawl_examinations(
    content_type: str | None = None,
    max_pages: int = 100,
) -> Iterator[dict[str, Any]]:
    """Crawl examinations.ie using Firecrawl."""
    try:
        from firecrawl import FirecrawlApp
    except ImportError:
        yield {
            "url": "https://www.examinations.ie",
            "status": "firecrawl_not_installed",
            "source": "examinations",
            "crawled_at": datetime.now(UTC).isoformat(),
        }
        return

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        yield {
            "url": "https://www.examinations.ie",
            "status": "no_api_key",
            "source": "examinations",
            "crawled_at": datetime.now(UTC).isoformat(),
        }
        return

    app = FirecrawlApp(api_key=api_key)

    # Build include paths based on content type
    include_paths = []
    content_type_paths = {
        "examiner_reports": ["/archive/examiners_reports/"],
        "exam_materials": ["/exammaterialarchive/"],
        "statistics": ["/statistics/"],
        "circulars": ["/schools/circulars/"],
    }

    if content_type and content_type in content_type_paths:
        include_paths = content_type_paths[content_type]
    else:
        # Include all content types
        for paths in content_type_paths.values():
            include_paths.extend(paths)

    try:
        from firecrawl.v2.types import ScrapeOptions

        scrape_opts = ScrapeOptions(formats=["markdown", "links"])

        result = app.crawl(
            "https://www.examinations.ie",
            limit=max_pages,
            max_discovery_depth=3,
            include_paths=include_paths,
            scrape_options=scrape_opts,
            poll_interval=5,
        )

        # Handle both CrawlJob object and dict response
        if hasattr(result, "data"):
            pages = result.data
        else:
            pages = result.get("data", [])

        for page in pages:
            # Convert Document to dict if needed
            if hasattr(page, "model_dump"):
                page = page.model_dump()
            elif hasattr(page, "dict"):
                page = page.dict()

            metadata = page.get("metadata", {})
            yield {
                "url": metadata.get("url") or metadata.get("sourceURL"),
                "title": metadata.get("title"),
                "description": metadata.get("description"),
                "markdown": page.get("markdown"),
                "links": page.get("links", []),
                "content_type": content_type,
                "source": "examinations",
                "crawled_at": datetime.now(UTC).isoformat(),
                "status": "success",
            }
    except (RuntimeError, ConnectionError, TimeoutError, ValueError) as e:
        logger.error("examinations_crawl_failed", error=str(e))
        yield {
            "url": "https://www.examinations.ie",
            "error": str(e),
            "source": "examinations",
            "crawled_at": datetime.now(UTC).isoformat(),
            "status": "error",
        }


def _map_examiner_reports(max_urls: int = 500) -> Iterator[dict[str, Any]]:
    """Map examiner report PDF URLs from examinations.ie."""
    try:
        from firecrawl import FirecrawlApp
    except ImportError:
        return

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        return

    app = FirecrawlApp(api_key=api_key)

    try:
        result = app.map(
            "https://www.examinations.ie",
            search="examiners_reports",
            limit=max_urls,
        )

        # Handle both MapResult object and dict response
        if hasattr(result, "links"):
            links = result.links
        else:
            links = result.get("links", [])

        for link in links:
            # Handle both string and LinkResult objects
            if isinstance(link, str):
                url = link
            elif hasattr(link, "url"):
                url = link.url
            elif hasattr(link, "href"):
                url = link.href
            else:
                continue

            if not url or ".pdf" not in url.lower():
                continue

            # Extract subject and year from URL if possible
            subject = None
            year = None

            # URLs like: /archive/examiners_reports/cer_2023/LC_English.pdf
            parts = url.split("/")
            for part in parts:
                if part.startswith("cer_"):
                    try:
                        year = int(part.replace("cer_", ""))
                    except ValueError:
                        pass
                if ".pdf" in part:
                    subject = part.replace(".pdf", "").replace("_", " ")

            yield {
                "url": url,
                "content_type": "examiner_report_pdf",
                "subject": subject,
                "year": year,
                "source": "examinations",
                "discovered_at": datetime.now(UTC).isoformat(),
            }
    except (RuntimeError, ConnectionError, TimeoutError, ValueError) as e:
        logger.warning("examiner_reports_map_failed", error=str(e))


@dlt.source(name="examinations")
def examinations_source(
    content_type: str | None = None,
    max_pages: int = 100,
    include_report_pdfs: bool = True,
):
    """
    DLT source for examinations.ie content (Firecrawl-based).

    Args:
        content_type: Optional filter (examiner_reports, exam_materials, statistics, circulars)
        max_pages: Maximum pages to crawl
        include_report_pdfs: Whether to include examiner report PDF discovery

    Returns:
        DLT source with examinations_pages and optionally report_pdfs resources
    """

    @dlt.resource(
        name="examinations_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def examinations_pages():
        """Crawled SEC pages."""
        yield from _crawl_examinations(content_type, max_pages)

    @dlt.resource(
        name="examiner_report_pdfs",
        write_disposition="merge",
        primary_key=["url"],
    )
    def examiner_report_pdfs():
        """Discovered examiner report PDF URLs."""
        if include_report_pdfs:
            yield from _map_examiner_reports()

    return examinations_pages, examiner_report_pdfs


# Browser-based exam material sources (for dropdown interaction)

# All SEC subjects
ALL_LC_SUBJECTS = [
    "mathematics", "english", "gaeilge", "biology", "chemistry", "physics",
    "geography", "history", "french", "german", "spanish", "accounting",
    "business", "economics", "art", "music", "home-economics", "computer-science",
    "agricultural-science", "applied-mathematics", "classical-studies",
    "construction-studies", "design-and-communication-graphics", "engineering",
    "italian", "japanese", "latin", "physical-education", "physics-and-chemistry",
    "politics-and-society", "religious-education", "technology",
]

ALL_JC_SUBJECTS = [
    "mathematics", "english", "gaeilge", "science", "geography", "history",
    "french", "german", "spanish", "business-studies", "home-economics",
    "music", "graphics", "wood-technology", "visual-art", "classics",
    "religious-education",
]


def _get_exam_materials_browser(
    subjects: list[str],
    years: list[int],
    level: str,
    language: str,
) -> Iterator[dict[str, Any]]:
    """
    Get exam materials using browser automation.

    This is a synchronous wrapper that runs the async scraper.
    """
    try:
        from sruth_browser.tools.examinations_scraper import (
            scrape_exam_materials_sync,
        )
    except ImportError:
        logger.warning("browser_tools_not_available")
        yield {
            "subject": "all",
            "year": 0,
            "level": level,
            "material_type": "error",
            "pdf_url": "",
            "status": "browser_tools_not_available",
            "scraped_at": datetime.now(UTC).isoformat(),
        }
        return

    for subject in subjects:
        try:
            materials = scrape_exam_materials_sync(
                subject=subject,
                years=years,
                level=level,
                language=language,
            )

            for material in materials:
                yield material.to_dict()

        except Exception as e:
            logger.error(
                "browser_scrape_failed",
                subject=subject,
                error=str(e),
            )
            yield {
                "subject": subject,
                "year": 0,
                "level": level,
                "material_type": "error",
                "pdf_url": "",
                "status": "error",
                "error": str(e),
                "scraped_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="sec_examinations_browser")
def sec_examinations_browser_source(
    subjects: list[str] | None = None,
    years: list[int] | None = None,
    level: str = "leaving_certificate",
    language: str = "en",
):
    """
    DLT source for SEC exam materials using browser automation.

    Uses Stagehand browser automation to interact with dropdowns on examinations.ie
    and download exam papers, marking schemes, and examiner reports.

    Args:
        subjects: List of subject slugs (default: all LC subjects)
        years: List of years (default: 2020-2024)
        level: Exam level (leaving_certificate, junior_cycle)
        language: Language code (en, ga)

    Returns:
        DLT resources for exam papers, marking schemes, and reports

    Examples:
        # All Leaving Certificate subjects, recent years
        pipeline.run(sec_examinations_browser_source(years=[2023, 2024]))

        # Mathematics only, full archive
        pipeline.run(sec_examinations_browser_source(
            subjects=["mathematics"],
            years=list(range(1999, 2025)),
        ))
    """
    if subjects is None:
        subjects = ALL_LC_SUBJECTS if level == "leaving_certificate" else ALL_JC_SUBJECTS

    if years is None:
        years = list(range(2020, 2025))

    logger.info(
        "sec_examinations_browser_source_initialized",
        subject_count=len(subjects),
        year_count=len(years),
        level=level,
        language=language,
    )

    @dlt.resource(
        name="exam_papers",
        write_disposition="merge",
        primary_key=["pdf_url"],
        columns={
            "subject": {"data_type": "text"},
            "year": {"data_type": "bigint"},
            "level": {"data_type": "text"},
            "material_type": {"data_type": "text"},
            "pdf_url": {"data_type": "text"},
            "title": {"data_type": "text"},
            "paper_number": {"data_type": "bigint"},
            "exam_level": {"data_type": "text"},
            "language": {"data_type": "text"},
            "content_hash": {"data_type": "text"},
            "scraped_at": {"data_type": "timestamp"},
        },
    )
    def exam_papers() -> Iterator[dict[str, Any]]:
        """Past examination papers."""
        for material in _get_exam_materials_browser(subjects, years, level, language):
            if material.get("material_type") == "paper":
                yield material

    @dlt.resource(
        name="marking_schemes",
        write_disposition="merge",
        primary_key=["pdf_url"],
    )
    def marking_schemes() -> Iterator[dict[str, Any]]:
        """Marking schemes for examination papers."""
        for material in _get_exam_materials_browser(subjects, years, level, language):
            if material.get("material_type") == "marking_scheme":
                yield material

    @dlt.resource(
        name="examiner_reports",
        write_disposition="append",
        primary_key=["pdf_url"],
    )
    def examiner_reports() -> Iterator[dict[str, Any]]:
        """Chief Examiner Reports."""
        for material in _get_exam_materials_browser(subjects, years, level, language):
            if material.get("material_type") == "examiner_report":
                yield material

    @dlt.resource(
        name="all_exam_materials",
        write_disposition="merge",
        primary_key=["pdf_url"],
    )
    def all_exam_materials() -> Iterator[dict[str, Any]]:
        """All exam materials (papers, schemes, reports)."""
        yield from _get_exam_materials_browser(subjects, years, level, language)

    return exam_papers, marking_schemes, examiner_reports, all_exam_materials


# Convenience functions


def leaving_certificate_source(
    subjects: list[str] | None = None,
    years: list[int] | None = None,
    language: str = "en",
):
    """DLT source for Leaving Certificate exam materials."""
    return sec_examinations_browser_source(
        subjects=subjects,
        years=years,
        level="leaving_certificate",
        language=language,
    )


def junior_cycle_exams_source(
    subjects: list[str] | None = None,
    years: list[int] | None = None,
    language: str = "en",
):
    """DLT source for Junior Cycle exam materials."""
    return sec_examinations_browser_source(
        subjects=subjects,
        years=years,
        level="junior_cycle",
        language=language,
    )


def mathematics_exams_source(
    years: list[int] | None = None,
    level: str = "leaving_certificate",
    language: str = "en",
):
    """DLT source for Mathematics exam materials only."""
    return sec_examinations_browser_source(
        subjects=["mathematics"],
        years=years,
        level=level,
        language=language,
    )


def science_subjects_exams_source(
    years: list[int] | None = None,
    language: str = "en",
):
    """DLT source for all science subjects (Biology, Chemistry, Physics)."""
    return sec_examinations_browser_source(
        subjects=["biology", "chemistry", "physics", "agricultural-science"],
        years=years,
        level="leaving_certificate",
        language=language,
    )
