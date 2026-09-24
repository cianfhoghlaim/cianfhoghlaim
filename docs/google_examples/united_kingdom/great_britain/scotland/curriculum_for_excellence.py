"""
DLT source for Scotland's Curriculum for Excellence (CfE).

Crawls and extracts from:
- education.gov.scot - Curriculum for Excellence documentation
- SQA (sqa.org.uk) - Qualifications and course specifications

Includes:
- CfE Benchmarks
- Experiences and Outcomes (Es+Os)
- SQA National Qualifications (National 5, Higher, Advanced Higher)
- Gaelic Medium Education resources

Usage:
    from sruth.oideachais.dlt_sources.uk.scotland.curriculum_for_excellence import (
        curriculum_for_excellence_source,
        sqa_qualifications_source,
    )

    pipeline = dlt.pipeline(
        pipeline_name="scotland_curriculum",
        destination="duckdb",
    )
    pipeline.run(curriculum_for_excellence_source())
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt

from ...common.firecrawl_source import crawl_website, scrape_page
from ...common.incremental import compute_content_hash

# Education Scotland CfE URLs
CFE_URLS = {
    "benchmarks": "https://education.gov.scot/improvement/learning-resources/curriculum-for-excellence-benchmarks/",
    "experiences_outcomes": "https://education.gov.scot/curriculum-for-excellence/",
    "early_level": "https://education.gov.scot/curriculum-for-excellence/curriculum-areas/",
    "broad_general_education": "https://education.gov.scot/curriculum-for-excellence/broad-general-education/",
    "senior_phase": "https://education.gov.scot/curriculum-for-excellence/senior-phase/",
    "gaelic_medium": "https://education.gov.scot/improvement/learning-resources/foghlam-tron-ghaidhlig/",
    "resources": "https://education.gov.scot/improvement/learning-resources/",
}

# SQA Qualification URLs
SQA_URLS = {
    "national_5": "https://www.sqa.org.uk/sqa/45600.html",
    "higher": "https://www.sqa.org.uk/sqa/45601.html",
    "advanced_higher": "https://www.sqa.org.uk/sqa/45602.html",
    "skills_for_work": "https://www.sqa.org.uk/sqa/45693.html",
    "course_specs": "https://www.sqa.org.uk/sqa/48454.html",
    "subject_pages": "https://www.sqa.org.uk/sqa/48460.html",
}

# CfE Curriculum Areas
CFE_CURRICULUM_AREAS = [
    "expressive_arts",
    "health_wellbeing",
    "languages",
    "mathematics",
    "religious_moral_education",
    "sciences",
    "social_studies",
    "technologies",
]


def _crawl_education_gov_scot(
    section: str | None = None,
    include_gaelic: bool = True,
    max_pages: int = 300,
) -> Iterator[dict[str, Any]]:
    """
    Crawl Education Scotland CfE resources.

    Args:
        section: Specific section to crawl (benchmarks, experiences_outcomes, etc.)
        include_gaelic: Whether to include Gaelic medium resources
        max_pages: Maximum pages to crawl

    Yields:
        Crawled page data with CfE metadata
    """
    # Determine base URLs to crawl
    urls_to_crawl = []
    if section and section in CFE_URLS:
        urls_to_crawl.append(CFE_URLS[section])
    else:
        # Crawl main CfE sections
        urls_to_crawl.extend([
            CFE_URLS["benchmarks"],
            CFE_URLS["experiences_outcomes"],
            CFE_URLS["broad_general_education"],
            CFE_URLS["senior_phase"],
        ])

    if include_gaelic:
        urls_to_crawl.append(CFE_URLS["gaelic_medium"])

    include_paths = [
        "/curriculum-for-excellence/*",
        "/improvement/learning-resources/*",
        "/scottish-attainment-challenge/*",
    ]

    exclude_paths = [
        "/media/*",
        "/parentzone/*",
        "/accessibility/*",
    ]

    for base_url in urls_to_crawl:
        for page in crawl_website(
            base_url=base_url,
            include_paths=include_paths,
            exclude_paths=exclude_paths,
            max_pages=max_pages // len(urls_to_crawl),
            max_depth=4,
        ):
            # Determine curriculum level from URL
            url = page.get("url", "")
            level = "broad_general_education"
            if "senior-phase" in url:
                level = "senior_phase"
            elif "early-level" in url:
                level = "early_level"
            elif "benchmark" in url.lower():
                level = "benchmarks"

            # Detect Gaelic content
            language = "en"
            if "gaidhlig" in url.lower() or "foghlam-tron" in url:
                language = "gd"

            page["nation"] = "scotland"
            page["source"] = "education_gov_scot"
            page["curriculum_framework"] = "curriculum_for_excellence"
            page["curriculum_level"] = level
            page["language"] = language
            page["indexed_at"] = datetime.now(UTC).isoformat()

            # Add content hash for change detection
            content = page.get("markdown", "")
            if content:
                page["content_hash"] = compute_content_hash(content)

            yield page


def _crawl_sqa_qualifications(
    qualification_level: str | None = None,
    subjects: list[str] | None = None,
    max_pages: int = 200,
) -> Iterator[dict[str, Any]]:
    """
    Crawl SQA qualification specifications.

    Args:
        qualification_level: Specific level (national_5, higher, advanced_higher)
        subjects: Optional list of subjects to filter
        max_pages: Maximum pages to crawl

    Yields:
        Crawled SQA specification pages
    """
    urls_to_crawl = []
    if qualification_level and qualification_level in SQA_URLS:
        urls_to_crawl.append((qualification_level, SQA_URLS[qualification_level]))
    else:
        for level in ["national_5", "higher", "advanced_higher"]:
            urls_to_crawl.append((level, SQA_URLS[level]))

    include_paths = [
        "/sqa/files/*",
        "/sqa/*",
    ]

    exclude_paths = [
        "/media/*",
        "/results/*",
        "/appeals/*",
    ]

    for level, base_url in urls_to_crawl:
        for page in crawl_website(
            base_url=base_url,
            include_paths=include_paths,
            exclude_paths=exclude_paths,
            max_pages=max_pages // len(urls_to_crawl),
            max_depth=3,
        ):
            url = page.get("url", "")

            # Try to extract subject from URL or title
            subject = None
            title = page.get("title", "")
            for subj in ["mathematics", "english", "physics", "chemistry", "biology", "history", "geography", "computing", "gaidhlig"]:
                if subj in url.lower() or subj in title.lower():
                    subject = subj
                    break

            # Detect Gaelic content
            language = "en"
            if "gaidhlig" in url.lower() or "gaidhlig" in title.lower():
                language = "gd"
                subject = "gaidhlig"

            page["nation"] = "scotland"
            page["source"] = "sqa"
            page["qualification_level"] = level
            page["curriculum_framework"] = "sqa_national_qualifications"
            page["subject"] = subject
            page["language"] = language
            page["indexed_at"] = datetime.now(UTC).isoformat()

            # Add content hash
            content = page.get("markdown", "")
            if content:
                page["content_hash"] = compute_content_hash(content)

            yield page


def _extract_sqa_pdf_links(qualification_level: str) -> Iterator[dict[str, Any]]:
    """
    Extract PDF specification links from SQA pages.

    SQA publishes course specifications as PDF documents.
    """
    if qualification_level not in SQA_URLS:
        return

    page = scrape_page(SQA_URLS[qualification_level])
    links = page.get("links", [])

    for link in links:
        if not link:
            continue

        lower_link = link.lower()
        if ".pdf" in lower_link and ("course" in lower_link or "spec" in lower_link):
            yield {
                "url": link if link.startswith("http") else f"https://www.sqa.org.uk{link}",
                "file_type": "pdf",
                "qualification_level": qualification_level,
                "source_page": SQA_URLS[qualification_level],
                "nation": "scotland",
                "source": "sqa",
                "discovered_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="scotland_cfe")
def curriculum_for_excellence_source(
    section: str | None = None,
    include_gaelic: bool = True,
    max_pages: int = 300,
):
    """
    DLT source for Scotland's Curriculum for Excellence.

    Args:
        section: Specific CfE section (benchmarks, experiences_outcomes, etc.)
        include_gaelic: Include Gaelic Medium Education resources
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with CfE pages resource
    """

    @dlt.resource(
        name="cfe_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def cfe_pages():
        """Crawled Curriculum for Excellence pages."""
        yield from _crawl_education_gov_scot(section, include_gaelic, max_pages)

    return cfe_pages


@dlt.source(name="scotland_sqa")
def sqa_qualifications_source(
    qualification_level: str | None = None,
    include_pdf_links: bool = True,
    max_pages: int = 200,
):
    """
    DLT source for SQA National Qualifications.

    Args:
        qualification_level: national_5, higher, or advanced_higher
        include_pdf_links: Extract PDF specification links
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with SQA pages and optionally PDF links
    """

    @dlt.resource(
        name="sqa_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def sqa_pages():
        """Crawled SQA qualification pages."""
        yield from _crawl_sqa_qualifications(qualification_level, None, max_pages)

    @dlt.resource(
        name="sqa_pdf_links",
        write_disposition="merge",
        primary_key=["url"],
    )
    def sqa_pdf_links():
        """SQA PDF specification links."""
        if include_pdf_links:
            for level in ["national_5", "higher", "advanced_higher"]:
                if qualification_level is None or qualification_level == level:
                    yield from _extract_sqa_pdf_links(level)

    return sqa_pages, sqa_pdf_links


@dlt.source(name="scotland_gaelic_curriculum")
def gaelic_curriculum_source(max_pages: int = 100):
    """
    DLT source specifically for Gaelic Medium Education resources.

    Focuses on:
    - Foghlam tron Ghàidhlig resources
    - Stòrlann materials
    - SQA Gàidhlig qualifications

    Args:
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with Gaelic education resources
    """

    @dlt.resource(
        name="gaelic_cfe_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def gaelic_cfe_pages():
        """Gaelic Medium CfE resources."""
        for page in crawl_website(
            base_url=CFE_URLS["gaelic_medium"],
            max_pages=max_pages,
            max_depth=3,
        ):
            page["nation"] = "scotland"
            page["source"] = "education_gov_scot"
            page["language"] = "gd"
            page["curriculum_framework"] = "foghlam_tron_ghaidhlig"
            page["indexed_at"] = datetime.now(UTC).isoformat()
            yield page

    return gaelic_cfe_pages
