"""
DLT source for Wales' Curriculum for Wales and WJEC qualifications.

Crawls and extracts from:
- hwb.gov.wales - Curriculum for Wales (Cwricwlwm i Gymru)
- gov.wales - Welsh Government education resources
- wjec.co.uk / cbac.co.uk - WJEC/CBAC qualifications (bilingual)
- qualifications.wales - Qualifications Wales oversight body

Includes:
- Areas of Learning and Experience (AoLE)
- Statements of What Matters
- WJEC GCSE and A-Level specifications
- Welsh-medium and bilingual resources

Usage:
    from oideachais.dlt_sources.uk.wales.curriculum_for_wales import (
        curriculum_for_wales_source,
        wjec_qualifications_source,
    )

    pipeline = dlt.pipeline(
        pipeline_name="wales_curriculum",
        destination="duckdb",
    )
    pipeline.run(curriculum_for_wales_source())
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt

from ...common.firecrawl_source import crawl_website, scrape_page
from ...common.incremental import compute_content_hash

# Hwb (Welsh Government digital learning) URLs
HWB_URLS = {
    "curriculum": "https://hwb.gov.wales/curriculum-for-wales/",
    "what_matters": "https://hwb.gov.wales/curriculum-for-wales/designing-your-curriculum/developing-a-vision-for-curriculum-design/",
    "aole": "https://hwb.gov.wales/curriculum-for-wales/areas-of-learning-and-experience/",
    "cross_curricular": "https://hwb.gov.wales/curriculum-for-wales/cross-curricular-skills/",
    "assessment": "https://hwb.gov.wales/curriculum-for-wales/assessment/",
    "welsh_language": "https://hwb.gov.wales/curriculum-for-wales/designing-your-curriculum/welsh-language/",
}

# Areas of Learning and Experience
AOLE_AREAS = [
    "expressive_arts",
    "health_wellbeing",
    "humanities",
    "languages_literacy_communication",
    "mathematics_numeracy",
    "science_technology",
]

# WJEC/CBAC URLs (bilingual exam board)
WJEC_URLS = {
    "gcse": "https://www.wjec.co.uk/qualifications/gcse/",
    "a_level": "https://www.wjec.co.uk/qualifications/a-level/",
    "vocational": "https://www.wjec.co.uk/qualifications/vocational-qualifications/",
    "welsh_baccalaureate": "https://www.wjec.co.uk/qualifications/welsh-baccalaureate/",
    # Welsh language version (CBAC)
    "cbac_tgau": "https://www.cbac.co.uk/cymwysterau/tgau/",
    "cbac_safon_uwch": "https://www.cbac.co.uk/cymwysterau/safon-uwch/",
}


def _crawl_hwb_curriculum(
    aole: str | None = None,
    language: str = "en",
    max_pages: int = 200,
) -> Iterator[dict[str, Any]]:
    """
    Crawl Hwb Curriculum for Wales resources.

    Args:
        aole: Specific Area of Learning and Experience to crawl
        language: "en" for English, "cy" for Welsh
        max_pages: Maximum pages to crawl

    Yields:
        Crawled curriculum pages with metadata
    """
    # Hwb supports language switching via URL or cookies
    # Most content is available in both English and Welsh
    urls_to_crawl = [
        HWB_URLS["curriculum"],
        HWB_URLS["aole"],
        HWB_URLS["what_matters"],
    ]

    if language == "cy":
        # Welsh language URLs use /cy/ prefix
        urls_to_crawl = [url.replace("hwb.gov.wales/", "hwb.gov.wales/cy/") for url in urls_to_crawl]

    include_paths = [
        "/curriculum-for-wales/*",
        "/cwricwlwm-i-gymru/*",  # Welsh language path
        "/resources/*",
        "/adnoddau/*",  # Welsh for "resources"
    ]

    exclude_paths = [
        "/api/*",
        "/search/*",
        "/login/*",
    ]

    for base_url in urls_to_crawl:
        for page in crawl_website(
            base_url=base_url,
            include_paths=include_paths,
            exclude_paths=exclude_paths,
            max_pages=max_pages // len(urls_to_crawl),
            max_depth=4,
        ):
            url = page.get("url", "")

            # Detect language from URL
            detected_lang = "cy" if "/cy/" in url or "/cwricwlwm" in url else "en"

            # Determine AoLE from URL
            detected_aole = None
            for area in AOLE_AREAS:
                if area.replace("_", "-") in url.lower():
                    detected_aole = area
                    break

            # Detect What Matters statements
            is_what_matters = "what-matters" in url or "yr-hyn-sy'n-bwysig" in url

            page["nation"] = "wales"
            page["source"] = "hwb"
            page["curriculum_framework"] = "curriculum_for_wales"
            page["language"] = detected_lang
            page["aole"] = detected_aole or aole
            page["is_what_matters"] = is_what_matters
            page["indexed_at"] = datetime.now(UTC).isoformat()

            # Add content hash
            content = page.get("markdown", "")
            if content:
                page["content_hash"] = compute_content_hash(content)

            yield page


def _crawl_wjec_qualifications(
    qualification_level: str | None = None,
    language: str = "en",
    max_pages: int = 150,
) -> Iterator[dict[str, Any]]:
    """
    Crawl WJEC/CBAC qualification specifications.

    Args:
        qualification_level: "gcse" or "a_level"
        language: "en" for English (WJEC), "cy" for Welsh (CBAC)
        max_pages: Maximum pages to crawl

    Yields:
        Crawled specification pages
    """
    if language == "cy":
        # Use CBAC (Welsh language) URLs
        urls_to_crawl = [
            ("tgau", WJEC_URLS["cbac_tgau"]),
            ("safon_uwch", WJEC_URLS["cbac_safon_uwch"]),
        ]
        base_domain = "https://www.cbac.co.uk"
    else:
        urls_to_crawl = [
            ("gcse", WJEC_URLS["gcse"]),
            ("a_level", WJEC_URLS["a_level"]),
        ]
        base_domain = "https://www.wjec.co.uk"

    if qualification_level:
        urls_to_crawl = [(level, url) for level, url in urls_to_crawl if level == qualification_level]

    include_paths = [
        "/qualifications/*",
        "/cymwysterau/*",  # Welsh
        "/specifications/*",
        "/manyleb/*",  # Welsh for "specifications"
    ]

    for level, base_url in urls_to_crawl:
        for page in crawl_website(
            base_url=base_url,
            include_paths=include_paths,
            max_pages=max_pages // len(urls_to_crawl),
            max_depth=3,
        ):
            url = page.get("url", "")

            # Map Welsh level names to English equivalents
            normalized_level = level
            if level == "tgau":
                normalized_level = "gcse"
            elif level == "safon_uwch":
                normalized_level = "a_level"

            # Try to extract subject from URL
            subject = None
            title = page.get("title", "")
            for subj in ["mathematics", "mathemateg", "english", "saesneg", "welsh", "cymraeg",
                         "biology", "bioleg", "chemistry", "cemeg", "physics", "ffiseg",
                         "history", "hanes", "geography", "daearyddiaeth"]:
                if subj in url.lower() or subj in title.lower():
                    # Normalize Welsh subject names to English
                    subject_map = {
                        "mathemateg": "mathematics",
                        "saesneg": "english",
                        "cymraeg": "welsh",
                        "bioleg": "biology",
                        "cemeg": "chemistry",
                        "ffiseg": "physics",
                        "hanes": "history",
                        "daearyddiaeth": "geography",
                    }
                    subject = subject_map.get(subj, subj)
                    break

            # Detect language
            detected_lang = "cy" if "cbac.co.uk" in url or any(w in url.lower() for w in ["cymraeg", "tgau", "safon"]) else "en"

            page["nation"] = "wales"
            page["source"] = "wjec" if detected_lang == "en" else "cbac"
            page["qualification_level"] = normalized_level
            page["curriculum_framework"] = "wjec_qualifications"
            page["subject"] = subject
            page["language"] = detected_lang
            page["indexed_at"] = datetime.now(UTC).isoformat()

            # Add content hash
            content = page.get("markdown", "")
            if content:
                page["content_hash"] = compute_content_hash(content)

            yield page


def _extract_wjec_pdf_links(qualification_level: str, language: str = "en") -> Iterator[dict[str, Any]]:
    """
    Extract PDF specification links from WJEC pages.
    """
    if language == "cy":
        url_map = {"gcse": WJEC_URLS["cbac_tgau"], "a_level": WJEC_URLS["cbac_safon_uwch"]}
    else:
        url_map = {"gcse": WJEC_URLS["gcse"], "a_level": WJEC_URLS["a_level"]}

    if qualification_level not in url_map:
        return

    page = scrape_page(url_map[qualification_level])
    links = page.get("links", [])

    for link in links:
        if not link:
            continue

        lower_link = link.lower()
        if ".pdf" in lower_link and ("spec" in lower_link or "manyleb" in lower_link):
            base_domain = "https://www.cbac.co.uk" if language == "cy" else "https://www.wjec.co.uk"
            yield {
                "url": link if link.startswith("http") else f"{base_domain}{link}",
                "file_type": "pdf",
                "qualification_level": qualification_level,
                "source_page": url_map[qualification_level],
                "nation": "wales",
                "source": "cbac" if language == "cy" else "wjec",
                "language": language,
                "discovered_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="wales_curriculum")
def curriculum_for_wales_source(
    aole: str | None = None,
    languages: list[str] | None = None,
    max_pages: int = 200,
):
    """
    DLT source for Wales' Curriculum for Wales.

    Args:
        aole: Specific Area of Learning and Experience
        languages: Languages to crawl ["en", "cy"], defaults to both
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with Hwb curriculum pages
    """
    languages = languages or ["en", "cy"]

    @dlt.resource(
        name="curriculum_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def curriculum_pages():
        """Crawled Curriculum for Wales pages."""
        for lang in languages:
            yield from _crawl_hwb_curriculum(aole, lang, max_pages // len(languages))

    return curriculum_pages


@dlt.source(name="wales_wjec")
def wjec_qualifications_source(
    qualification_level: str | None = None,
    languages: list[str] | None = None,
    include_pdf_links: bool = True,
    max_pages: int = 150,
):
    """
    DLT source for WJEC/CBAC qualifications.

    Args:
        qualification_level: "gcse" or "a_level"
        languages: ["en"] for WJEC, ["cy"] for CBAC, or both
        include_pdf_links: Extract PDF specification links
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with WJEC pages and optionally PDF links
    """
    languages = languages or ["en", "cy"]

    @dlt.resource(
        name="wjec_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def wjec_pages():
        """Crawled WJEC/CBAC qualification pages."""
        for lang in languages:
            yield from _crawl_wjec_qualifications(qualification_level, lang, max_pages // len(languages))

    @dlt.resource(
        name="wjec_pdf_links",
        write_disposition="merge",
        primary_key=["url"],
    )
    def wjec_pdf_links():
        """WJEC/CBAC PDF specification links."""
        if include_pdf_links:
            for level in ["gcse", "a_level"]:
                if qualification_level is None or qualification_level == level:
                    for lang in languages:
                        yield from _extract_wjec_pdf_links(level, lang)

    return wjec_pages, wjec_pdf_links


@dlt.source(name="wales_welsh_medium")
def welsh_medium_source(max_pages: int = 100):
    """
    DLT source specifically for Welsh-medium education resources.

    Focuses on:
    - Cymraeg (Welsh language) as a subject
    - Resources through the medium of Welsh
    - Bilingual education materials

    Args:
        max_pages: Maximum pages to crawl

    Returns:
        DLT source with Welsh-medium resources
    """

    @dlt.resource(
        name="welsh_medium_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def welsh_medium_pages():
        """Welsh-medium curriculum resources."""
        # Crawl Welsh language section of Hwb
        for page in crawl_website(
            base_url=HWB_URLS["welsh_language"],
            max_pages=max_pages,
            max_depth=3,
        ):
            page["nation"] = "wales"
            page["source"] = "hwb"
            page["language"] = "cy"
            page["curriculum_framework"] = "curriculum_for_wales"
            page["is_welsh_medium"] = True
            page["indexed_at"] = datetime.now(UTC).isoformat()
            yield page

    return welsh_medium_pages
