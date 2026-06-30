"""
Shared helpers split from uk/wales/curriculum_for_wales.py

Phase 3D of openspec change.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

from ...common.firecrawl_source import crawl_website, scrape_page
from ...common.incremental import compute_content_hash

AOLE_AREAS = [
    "expressive_arts",
    "health_wellbeing",
    "humanities",
    "languages_literacy_communication",
    "mathematics_numeracy",
    "science_technology",
]

HWB_URLS = {
    "curriculum": "https://hwb.gov.wales/curriculum-for-wales/",
    "what_matters": "https://hwb.gov.wales/curriculum-for-wales/designing-your-curriculum/developing-a-vision-for-curriculum-design/",
    "aole": "https://hwb.gov.wales/curriculum-for-wales/areas-of-learning-and-experience/",
    "cross_curricular": "https://hwb.gov.wales/curriculum-for-wales/cross-curricular-skills/",
    "assessment": "https://hwb.gov.wales/curriculum-for-wales/assessment/",
    "welsh_language": "https://hwb.gov.wales/curriculum-for-wales/designing-your-curriculum/welsh-language/",
}

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
    else:
        urls_to_crawl = [
            ("gcse", WJEC_URLS["gcse"]),
            ("a_level", WJEC_URLS["a_level"]),
        ]

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
