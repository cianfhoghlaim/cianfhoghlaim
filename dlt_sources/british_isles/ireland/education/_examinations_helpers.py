"""
Shared helpers split from ireland/examinations.py

Phase 3D of openspec change.
"""

import contextlib
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

ALL_JC_SUBJECTS = [
    "mathematics", "english", "gaeilge", "science", "geography", "history",
    "french", "german", "spanish", "business-studies", "home-economics",
    "music", "graphics", "wood-technology", "visual-art", "classics",
    "religious-education",
]

ALL_LCA_SUBJECTS = [
    "english-and-communications",
    "mathematical-applications",
    "information-technology",
]

ALL_LC_SUBJECTS = [
    "mathematics", "english", "gaeilge", "biology", "chemistry", "physics",
    "geography", "history", "french", "german", "spanish", "accounting",
    "business", "economics", "art", "music", "home-economics", "computer-science",
    "agricultural-science", "applied-mathematics", "classical-studies",
    "construction-studies", "design-and-communication-graphics", "engineering",
    "italian", "japanese", "latin", "physical-education", "physics-and-chemistry",
    "politics-and-society", "religious-education", "technology",
]

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
        pages = result.data if hasattr(result, "data") else result.get("data", [])

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

def _get_exam_materials_browser(
    subjects: list[str],
    years: list[int],
    level: str,
    language: str,
    material_types: list[str] | None = None,
) -> Iterator[dict[str, Any]]:
    """
    Get exam materials using browser automation with session reuse.

    Uses scrape_materials_batch which initializes Stagehand once for all
    subjects instead of re-initializing per subject (~30s savings each).

    When USE_LOCAL_SCRAPES=true, skips browser automation entirely
    and yields a stub record indicating the skip.
    """
    # USE_LOCAL_SCRAPES: skip browser automation for testing/offline mode
    if os.environ.get("USE_LOCAL_SCRAPES", "").lower() == "true":
        logger.info("Skipping browser automation (USE_LOCAL_SCRAPES=true)")
        for subject in subjects:
            yield {
                "subject": subject,
                "year": 0,
                "level": level,
                "material_type": "skipped",
                "pdf_url": "",
                "status": "skipped_local_mode",
                "scraped_at": datetime.now(UTC).isoformat(),
            }
        return

    # Strategy: Try Playwright-native first (zero LLM cost, deterministic).
    # Fall back to Stagehand (LLM-driven) if Playwright fails.
    try:
        from sruth_browser.tools.examinations_scraper import (
            scrape_materials_playwright_sync,
        )
    except ImportError:
        scrape_materials_playwright_sync = None

    try:
        from sruth_browser.tools.examinations_scraper import (
            scrape_materials_batch_sync,
        )
    except ImportError:
        scrape_materials_batch_sync = None

    # Try Playwright-native first
    if scrape_materials_playwright_sync is not None:
        try:
            logger.info("Attempting Playwright-native scrape (zero LLM cost)")
            materials = scrape_materials_playwright_sync(
                subjects=subjects,
                years=years,
                level=level,
                language=language,
                material_types=material_types,
            )
            real_materials = [m for m in materials if m.pdf_url and m.content_hash != "error"]
            if real_materials:
                logger.info(f"Playwright-native succeeded: {len(real_materials)} materials")
                for material in materials:
                    record = material.to_dict()
                    if record.get("content_hash") == "error":
                        record["status"] = "error"
                        record["error"] = record.get("title", "unknown error")
                    else:
                        record["status"] = "success"
                    record["scraper"] = "playwright"
                    yield record
                return
            else:
                logger.warning("Playwright-native returned 0 real materials, falling back to Stagehand")
        except Exception as e:
            logger.warning(f"Playwright-native failed: {e}, falling back to Stagehand")

    # Fall back to Stagehand (LLM-driven)
    if scrape_materials_batch_sync is not None:
        try:
            logger.info("Attempting Stagehand LLM scrape")
            materials = scrape_materials_batch_sync(
                subjects=subjects,
                years=years,
                level=level,
                language=language,
                material_types=material_types,
            )

            for material in materials:
                record = material.to_dict()
                if record.get("material_type") == "paper" and record.get("content_hash") == "error":
                    record["status"] = "error"
                    record["error"] = record.get("title", "unknown error")
                else:
                    record["status"] = "success"
                record["scraper"] = "stagehand"
                yield record
            return

        except Exception as e:
            logger.error(f"batch_browser_scrape_failed: {e}")

    # No scraper available
    logger.error("No browser scraper available")
    for subject in subjects:
        yield {
            "subject": subject,
            "year": 0,
            "level": level,
            "material_type": "error",
            "pdf_url": "",
            "status": "no_scraper_available",
            "scraped_at": datetime.now(UTC).isoformat(),
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
        links = result.links if hasattr(result, "links") else result.get("links", [])

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
                    with contextlib.suppress(ValueError):
                        year = int(part.replace("cer_", ""))
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

def junior_cycle_exams_source(
    subjects: list[str] | None = None,
    years: list[int] | None = None,
    language: str = "en",
    material_types: list[str] | None = None,
):
    """DLT source for Junior Cycle exam materials."""
    return sec_examinations_browser_source(
        subjects=subjects,
        years=years,
        level="junior_cycle",
        language=language,
        material_types=material_types,
    )

def leaving_certificate_source(
    subjects: list[str] | None = None,
    years: list[int] | None = None,
    language: str = "en",
    material_types: list[str] | None = None,
):
    """DLT source for Leaving Certificate exam materials."""
    return sec_examinations_browser_source(
        subjects=subjects,
        years=years,
        level="leaving_certificate",
        language=language,
        material_types=material_types,
    )

def mathematics_exams_source(
    years: list[int] | None = None,
    level: str = "leaving_certificate",
    language: str = "en",
    material_types: list[str] | None = None,
):
    """DLT source for Mathematics exam materials only."""
    return sec_examinations_browser_source(
        subjects=["mathematics"],
        years=years,
        level=level,
        language=language,
        material_types=material_types,
    )

def science_subjects_exams_source(
    years: list[int] | None = None,
    language: str = "en",
    material_types: list[str] | None = None,
):
    """DLT source for all science subjects (Biology, Chemistry, Physics)."""
    return sec_examinations_browser_source(
        subjects=["biology", "chemistry", "physics", "agricultural-science"],
        years=years,
        level="leaving_certificate",
        language=language,
        material_types=material_types,
    )
