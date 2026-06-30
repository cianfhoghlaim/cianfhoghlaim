"""
DLT source for ncca.ie (National Council for Curriculum and Assessment).

Crawls and extracts:
- Curriculum frameworks and publications
- Guidelines for teachers
- Research reports
- Early childhood, primary, and post-primary content

Usage:
    from cianfhoghlaim.dlt.british_isles.ie.education.ncca import ncca_source

    # Full crawl (all cycles, subjects, languages)
    pipeline = dlt.pipeline(pipeline_name="ncca", destination="duckdb")
    pipeline.run(ncca_source())

    # Partitioned crawl (specific cycle/subject/language)
    pipeline.run(ncca_source(
        cycle="junior_cycle",
        subject="mathematics",
        language="en",
    ))
"""

import os
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt
from observability.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# Path Mappings for Firecrawl URL Filtering
# ============================================================================

# Cycle path mappings (English and Irish versions)
CYCLE_PATH_MAPPING: dict[str, dict[str, str]] = {
    "early_childhood": {"en": "early-childhood", "ga": "an-luath-oige"},
    "primary": {"en": "primary", "ga": "bunscoil"},
    "junior_cycle": {"en": "junior-cycle", "ga": "an-tsraith-shoisearach"},
    "senior_cycle": {"en": "senior-cycle", "ga": "an-tsraith-shinsearach"},
}

# Subject path mappings (common subjects with Irish translations)
# Note: NCCA uses different URL structures per subject - these are search keywords
SUBJECT_PATH_MAPPING: dict[str, dict[str, list[str]]] = {
    # Core subjects
    "english": {"en": ["english"], "ga": ["bearla"]},
    "irish": {"en": ["irish", "gaeilge"], "ga": ["gaeilge"]},
    "mathematics": {"en": ["mathematics", "maths"], "ga": ["matamaitic"]},
    # STEM
    "science": {"en": ["science"], "ga": ["eolaiocht"]},
    "technology": {"en": ["technology"], "ga": ["teicneolaiocht"]},
    "engineering": {"en": ["engineering"], "ga": ["innealtóireacht"]},
    # Humanities
    "history": {"en": ["history"], "ga": ["stair"]},
    "geography": {"en": ["geography"], "ga": ["tíreolaíocht"]},
    "religious_education": {"en": ["religious-education", "religion"], "ga": ["oideachas-reiligiúnach"]},
    # Languages
    "french": {"en": ["french"], "ga": ["fraincis"]},
    "german": {"en": ["german"], "ga": ["gearmáinis"]},
    "spanish": {"en": ["spanish"], "ga": ["spáinnis"]},
    # Arts
    "art": {"en": ["art", "visual-art"], "ga": ["ealaín"]},
    "music": {"en": ["music"], "ga": ["ceol"]},
    "drama": {"en": ["drama"], "ga": ["drámaíocht"]},
    # Wellbeing
    "pe": {"en": ["physical-education", "pe"], "ga": ["corpoideachas"]},
    "sphe": {"en": ["sphe", "social-personal"], "ga": ["osps"]},
    "cspe": {"en": ["cspe", "civic"], "ga": ["osgp"]},
    "wellbeing": {"en": ["wellbeing"], "ga": ["folláine"]},
    # Business & Economics
    "business": {"en": ["business"], "ga": ["gnó"]},
    "economics": {"en": ["economics"], "ga": ["eacnamaíocht"]},
    "home_economics": {"en": ["home-economics"], "ga": ["eacnamaíocht-bhaile"]},
    # Applied
    "applied_technology": {"en": ["applied-technology"], "ga": ["teicneolaíocht-fheidhmeach"]},
    "graphics": {"en": ["graphics", "technical-graphics"], "ga": ["grafaic"]},
    "wood_technology": {"en": ["wood-technology"], "ga": ["teicneolaíocht-adhmaid"]},
    "metalwork": {"en": ["metalwork"], "ga": ["miotalóireacht"]},
}

# Valid values for validation
VALID_CYCLES = list(CYCLE_PATH_MAPPING.keys())
VALID_SUBJECTS = list(SUBJECT_PATH_MAPPING.keys())
VALID_LANGUAGES = ["en", "ga"]


def _get_include_paths(
    language: str,
    cycle: str | None = None,
    subject: str | None = None,
) -> list[str]:
    """
    Generate Firecrawl include paths based on cycle/subject/language filters.

    Args:
        language: "en" or "ga"
        cycle: Optional cycle filter (primary, junior_cycle, senior_cycle, early_childhood)
        subject: Optional subject filter (mathematics, irish, english, etc.)

    Returns:
        List of URL path patterns for Firecrawl to include
    """
    lang_prefix = "/ga" if language == "ga" else "/en"
    paths = []

    # Get cycle paths
    if cycle:
        if cycle not in CYCLE_PATH_MAPPING:
            logger.warning("invalid_cycle", cycle=cycle, valid=VALID_CYCLES)
            return []
        cycle_path = CYCLE_PATH_MAPPING[cycle][language]
        paths.append(f"{lang_prefix}/{cycle_path}/")
    else:
        # Include all cycles for this language
        for cycle_info in CYCLE_PATH_MAPPING.values():
            paths.append(f"{lang_prefix}/{cycle_info[language]}/")

    # If subject is specified, filter paths to include subject keywords
    if subject:
        if subject not in SUBJECT_PATH_MAPPING:
            logger.warning("invalid_subject", subject=subject, valid=VALID_SUBJECTS)
            return paths  # Return cycle paths without subject filter

        subject_keywords = SUBJECT_PATH_MAPPING[subject][language]
        # Create paths that include both cycle and subject
        # NCCA URLs often have subject in the path like /en/junior-cycle/mathematics/
        subject_paths = []
        for base_path in paths:
            for keyword in subject_keywords:
                subject_paths.append(f"{base_path}*{keyword}*")
        return subject_paths

    return paths


def _crawl_ncca(
    language: str = "en",
    cycle: str | None = None,
    subject: str | None = None,
    max_pages: int = 100,
) -> Iterator[dict[str, Any]]:
    """
    Crawl ncca.ie using Firecrawl.

    Args:
        language: "en" for English, "ga" for Irish
        cycle: Filter by cycle (early_childhood, primary, junior_cycle, senior_cycle)
        subject: Filter by subject (mathematics, irish, english, etc.)
        max_pages: Maximum pages to crawl

    Yields:
        Dict with crawled page data
    """
    try:
        from firecrawl import FirecrawlApp
    except ImportError:
        yield {
            "url": "https://ncca.ie",
            "status": "firecrawl_not_installed",
            "language": language,
            "cycle": cycle,
            "subject": subject,
            "source": "ncca",
            "crawled_at": datetime.now(UTC).isoformat(),
        }
        return

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        yield {
            "url": "https://ncca.ie",
            "status": "no_api_key",
            "language": language,
            "cycle": cycle,
            "subject": subject,
            "source": "ncca",
            "crawled_at": datetime.now(UTC).isoformat(),
        }
        return

    app = FirecrawlApp(api_key=api_key)

    # Build include paths based on language, cycle, and subject
    include_paths = _get_include_paths(language, cycle, subject)


    try:
        logger.info(
            "ncca_crawl_started",
            language=language,
            cycle=cycle,
            subject=subject,
            max_pages=max_pages,
            include_paths=include_paths,
        )

        result = app.crawl(
            url="https://ncca.ie",
            limit=max_pages,
            max_discovery_depth=3,
            include_paths=include_paths,
            scrape_options={
                "formats": ["markdown", "links"],
            },
            poll_interval=5,
        )

        page_count = 0
        for page in getattr(result, "data", []):
            metadata = getattr(page, "metadata", {}) if hasattr(page, "metadata") else page.get("metadata", {})
            page_count += 1
            yield {
                "url": getattr(metadata, "sourceURL", "") if hasattr(metadata, "sourceURL") else metadata.get("sourceURL", ""),
                "title": getattr(metadata, "title", "") if hasattr(metadata, "title") else metadata.get("title", ""),
                "description": getattr(metadata, "description", "") if hasattr(metadata, "description") else metadata.get("description", ""),
                "markdown": getattr(page, "markdown", "") if hasattr(page, "markdown") else page.get("markdown", ""),
                "links": getattr(page, "links", []) if hasattr(page, "links") else page.get("links", []),
                "language": language,
                "cycle": cycle,
                "subject": subject,
                "source": "ncca",
                "crawled_at": datetime.now(UTC).isoformat(),
                "status": "success",
            }

        logger.info(
            "ncca_crawl_completed",
            language=language,
            cycle=cycle,
            subject=subject,
            page_count=page_count,
        )

    except ConnectionError as e:
        logger.error(
            "ncca_crawl_connection_error",
            language=language,
            cycle=cycle,
            subject=subject,
            error=str(e),
        )
        yield {
            "url": "https://ncca.ie",
            "error": f"Connection error: {e}",
            "language": language,
            "cycle": cycle,
            "subject": subject,
            "source": "ncca",
            "crawled_at": datetime.now(UTC).isoformat(),
            "status": "connection_error",
        }
    except TimeoutError as e:
        logger.error(
            "ncca_crawl_timeout",
            language=language,
            cycle=cycle,
            subject=subject,
            error=str(e),
        )
        yield {
            "url": "https://ncca.ie",
            "error": f"Timeout: {e}",
            "language": language,
            "cycle": cycle,
            "subject": subject,
            "source": "ncca",
            "crawled_at": datetime.now(UTC).isoformat(),
            "status": "timeout",
        }
    except ValueError as e:
        logger.error(
            "ncca_crawl_value_error",
            language=language,
            cycle=cycle,
            subject=subject,
            error=str(e),
        )
        yield {
            "url": "https://ncca.ie",
            "error": f"Invalid response: {e}",
            "language": language,
            "cycle": cycle,
            "subject": subject,
            "source": "ncca",
            "crawled_at": datetime.now(UTC).isoformat(),
            "status": "parse_error",
        }
    except RuntimeError as e:
        # Firecrawl-specific errors
        logger.error(
            "ncca_crawl_runtime_error",
            language=language,
            cycle=cycle,
            subject=subject,
            error=str(e),
            error_type=type(e).__name__,
        )
        yield {
            "url": "https://ncca.ie",
            "error": str(e),
            "language": language,
            "cycle": cycle,
            "subject": subject,
            "source": "ncca",
            "crawled_at": datetime.now(UTC).isoformat(),
            "status": "error",
        }


@dlt.source(name="ncca")
def ncca_source(
    language: str = "en",
    cycle: str | None = None,
    subject: str | None = None,
    max_pages: int = 100,
):
    """
    DLT source for ncca.ie content.

    Supports partitioned crawling by cycle, subject, and language for
    targeted curriculum data extraction.

    Args:
        language: "en" for English, "ga" for Irish
        cycle: Optional filter (early_childhood, primary, junior_cycle, senior_cycle)
        subject: Optional filter (mathematics, irish, english, science, etc.)
        max_pages: Maximum pages to crawl per partition

    Returns:
        DLT source with ncca_pages resource

    Examples:
        # Full crawl (all content)
        pipeline.run(ncca_source())

        # Targeted crawl (Junior Cycle Mathematics in English)
        pipeline.run(ncca_source(
            cycle="junior_cycle",
            subject="mathematics",
            language="en",
        ))

        # All subjects for Senior Cycle in Irish
        pipeline.run(ncca_source(
            cycle="senior_cycle",
            language="ga",
        ))
    """

    @dlt.resource(
        name="ncca_pages",
        write_disposition="merge",
        primary_key=["url"],
        columns={
            "url": {"data_type": "text"},
            "title": {"data_type": "text"},
            "description": {"data_type": "text"},
            "markdown": {"data_type": "text"},
            "links": {"data_type": "complex"},
            "language": {"data_type": "text"},
            "cycle": {"data_type": "text"},
            "subject": {"data_type": "text"},
            "source": {"data_type": "text"},
            "crawled_at": {"data_type": "timestamp"},
            "status": {"data_type": "text"},
        },
    )
    def ncca_pages():
        """Crawled NCCA pages with cycle/subject metadata."""
        yield from _crawl_ncca(language, cycle, subject, max_pages)

    return ncca_pages


# Backward compatibility alias (deprecated)
def ncca_source_legacy(
    language: str = "en",
    section: str | None = None,
    max_pages: int = 100,
):
    """
    Legacy source function - use ncca_source(cycle=...) instead.

    Deprecated: Use cycle parameter instead of section.
    """
    logger.warning(
        "ncca_source_legacy_deprecated",
        message="Use ncca_source(cycle=...) instead of section parameter",
    )
    return ncca_source(language=language, cycle=section, max_pages=max_pages)
