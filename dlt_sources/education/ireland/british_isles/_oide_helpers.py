"""
Shared helpers split from ireland/oide.py

Phase 3D of openspec change.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

from dlt.common import firecrawl_source
from dlt_sources.common.incremental import compute_content_hash

crawl_website, scrape_page = firecrawl_source.crawl_website, firecrawl_source.scrape_page

OIDE_SUBJECTS = {
    # Primary
    "primary_mathematics": "https://oide.ie/primary/mathematics/",
    "primary_english": "https://oide.ie/primary/english/",
    "primary_irish": "https://oide.ie/primary/gaeilge/",
    "primary_science": "https://oide.ie/primary/science/",
    "primary_sese": "https://oide.ie/primary/sese/",
    # Post-Primary Junior Cycle
    "jc_english": "https://oide.ie/post-primary/junior-cycle/english/",
    "jc_mathematics": "https://oide.ie/post-primary/junior-cycle/mathematics/",
    "jc_irish": "https://oide.ie/post-primary/junior-cycle/gaeilge/",
    "jc_science": "https://oide.ie/post-primary/junior-cycle/science/",
    "jc_history": "https://oide.ie/post-primary/junior-cycle/history/",
    "jc_geography": "https://oide.ie/post-primary/junior-cycle/geography/",
    # Post-Primary Senior Cycle
    "lc_english": "https://oide.ie/post-primary/senior-cycle/english/",
    "lc_mathematics": "https://oide.ie/post-primary/senior-cycle/mathematics/",
    "lc_irish": "https://oide.ie/post-primary/senior-cycle/gaeilge/",
    "lc_physics": "https://oide.ie/post-primary/senior-cycle/physics/",
    "lc_chemistry": "https://oide.ie/post-primary/senior-cycle/chemistry/",
    "lc_biology": "https://oide.ie/post-primary/senior-cycle/biology/",
}

OIDE_URLS = {
    "home": "https://oide.ie/",
    "primary": "https://oide.ie/primary/",
    "post_primary": "https://oide.ie/post-primary/",
    "digital_technologies": "https://oide.ie/digital-technologies/",
    "leadership": "https://oide.ie/leadership/",
    "wellbeing": "https://oide.ie/wellbeing/",
    "stem": "https://oide.ie/stem/",
    "languages": "https://oide.ie/languages/",
    "irish": "https://oide.ie/gaeilge/",  # Irish-medium resources
}

def _crawl_oide_section(
    section: str | None = None,
    language: str = "en",
    max_pages: int = 150,
) -> Iterator[dict[str, Any]]:
    """
    Crawl Oide.ie CPD resources.

    Args:
        section: Specific section to crawl (primary, post_primary, etc.)
        language: "en" for English, "ga" for Irish
        max_pages: Maximum pages to crawl

    Yields:
        Crawled CPD resource pages with metadata
    """
    urls_to_crawl = []

    if section and section in OIDE_URLS:
        urls_to_crawl.append((section, OIDE_URLS[section]))
    else:
        # Crawl main sections
        for sec in ["primary", "post_primary", "digital_technologies", "stem", "languages"]:
            if sec in OIDE_URLS:
                urls_to_crawl.append((sec, OIDE_URLS[sec]))

    # Always include Irish-medium if requested or section is irish
    if language == "ga" or section == "irish":
        if ("irish", OIDE_URLS["irish"]) not in urls_to_crawl:
            urls_to_crawl.append(("irish", OIDE_URLS["irish"]))

    include_paths = [
        "/primary/*",
        "/post-primary/*",
        "/digital-technologies/*",
        "/stem/*",
        "/languages/*",
        "/gaeilge/*",
        "/resources/*",
    ]

    exclude_paths = [
        "/events/*",
        "/news/*",
        "/contact/*",
        "/about/*",
    ]

    for sec, base_url in urls_to_crawl:
        for page in crawl_website(
            base_url=base_url,
            include_paths=include_paths,
            exclude_paths=exclude_paths,
            max_pages=max_pages // len(urls_to_crawl),
            max_depth=4,
        ):
            url = page.get("url", "")

            # Determine curriculum level
            level = None
            if "primary" in url and "post-primary" not in url:
                level = "primary"
            elif "junior-cycle" in url:
                level = "junior_cycle"
            elif "senior-cycle" in url:
                level = "leaving_cert"
            elif "post-primary" in url:
                level = "post_primary"

            # Detect Irish-medium content
            detected_lang = "ga" if "gaeilge" in url.lower() else "en"

            # Try to detect subject
            subject = None
            title = page.get("title", "")
            for subj in ["mathematics", "matamaitic", "english", "bearla", "irish", "gaeilge",
                         "science", "eolaiocht", "history", "stair", "geography", "tiriocht",
                         "physics", "fisic", "chemistry", "ceimice", "biology", "bitheolaiocht"]:
                if subj in url.lower() or subj in title.lower():
                    # Normalize Irish subject names
                    subject_map = {
                        "matamaitic": "mathematics",
                        "bearla": "english",
                        "gaeilge": "irish",
                        "eolaiocht": "science",
                        "stair": "history",
                        "tiriocht": "geography",
                        "fisic": "physics",
                        "ceimice": "chemistry",
                        "bitheolaiocht": "biology",
                    }
                    subject = subject_map.get(subj, subj)
                    break

            page["nation"] = "ireland"
            page["source"] = "oide"
            page["resource_type"] = "cpd"
            page["curriculum_level"] = level
            page["subject"] = subject
            page["section"] = sec
            page["language"] = detected_lang
            page["indexed_at"] = datetime.now(UTC).isoformat()

            # Add content hash
            content = page.get("markdown", "")
            if content:
                page["content_hash"] = compute_content_hash(content)

            yield page

def _crawl_oide_subject(
    subject_key: str,
    max_pages: int = 50,
) -> Iterator[dict[str, Any]]:
    """
    Crawl a specific Oide.ie subject page.

    Args:
        subject_key: Key from OIDE_SUBJECTS dict
        max_pages: Maximum pages to crawl

    Yields:
        Subject-specific CPD resources
    """
    if subject_key not in OIDE_SUBJECTS:
        return

    base_url = OIDE_SUBJECTS[subject_key]

    # Parse subject and level from key
    parts = subject_key.split("_")
    level = parts[0]  # primary, jc, or lc
    subject = "_".join(parts[1:])

    level_map = {"primary": "primary", "jc": "junior_cycle", "lc": "leaving_cert"}
    curriculum_level = level_map.get(level, level)

    for page in crawl_website(
        base_url=base_url,
        max_pages=max_pages,
        max_depth=3,
    ):
        url = page.get("url", "")

        # Detect language
        language = "ga" if "gaeilge" in url.lower() or subject == "irish" else "en"

        page["nation"] = "ireland"
        page["source"] = "oide"
        page["resource_type"] = "cpd"
        page["curriculum_level"] = curriculum_level
        page["subject"] = subject
        page["language"] = language
        page["indexed_at"] = datetime.now(UTC).isoformat()

        # Add content hash
        content = page.get("markdown", "")
        if content:
            page["content_hash"] = compute_content_hash(content)

        yield page

def _extract_oide_resource_links(section: str) -> Iterator[dict[str, Any]]:
    """
    Extract downloadable resource links from Oide pages.

    Many CPD resources are available as PDFs, PPTs, etc.
    """
    if section not in OIDE_URLS:
        return

    page = scrape_page(OIDE_URLS[section])
    links = page.get("links", [])

    for link in links:
        if not link:
            continue

        lower_link = link.lower()
        # Look for downloadable resources
        if any(ext in lower_link for ext in [".pdf", ".pptx", ".ppt", ".docx", ".doc", ".xlsx"]):
            file_type = "pdf"
            if ".ppt" in lower_link:
                file_type = "presentation"
            elif ".doc" in lower_link:
                file_type = "document"
            elif ".xls" in lower_link:
                file_type = "spreadsheet"

            yield {
                "url": link if link.startswith("http") else f"https://oide.ie{link}",
                "file_type": file_type,
                "section": section,
                "source_page": OIDE_URLS[section],
                "nation": "ireland",
                "source": "oide",
                "resource_type": "cpd_download",
                "discovered_at": datetime.now(UTC).isoformat(),
            }
