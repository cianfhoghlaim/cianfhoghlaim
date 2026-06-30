"""
Shared helpers split from uk/northern_ireland/ccea_curriculum.py

Phase 3D of openspec change.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

from cianfhoghlaim.dlt.common.firecrawl_source import crawl_website, scrape_page
from cianfhoghlaim.dlt.common.incremental import compute_content_hash

CCEA_QUAL_URLS = {
    "gcse": "https://ccea.org.uk/qualifications/gcse",
    "a_level": "https://ccea.org.uk/qualifications/gce-a-level",
    "as_level": "https://ccea.org.uk/qualifications/gce-as-level",
    "entry_level": "https://ccea.org.uk/qualifications/entry-level",
    "essential_skills": "https://ccea.org.uk/qualifications/essential-skills",
}

NI_AREAS_OF_LEARNING = [
    "language_literacy",
    "mathematics_numeracy",
    "the_arts",
    "world_around_us",
    "personal_development_mutual_understanding",
    "physical_education",
    "religious_education",
]

NI_CURRICULUM_URLS = {
    "foundation": "https://ccea.org.uk/curriculum/foundation-stage",
    "key_stage_1": "https://ccea.org.uk/curriculum/key-stage-1",
    "key_stage_2": "https://ccea.org.uk/curriculum/key-stage-2",
    "key_stage_3": "https://ccea.org.uk/curriculum/key-stage-3",
    "key_stage_4": "https://ccea.org.uk/curriculum/key-stage-4",
    "cross_curricular": "https://ccea.org.uk/curriculum/cross-curricular-skills",
    "irish_medium": "https://ccea.org.uk/curriculum/irish-medium",
}

def _crawl_ccea_qualifications(
    qualification_level: str | None = None,
    max_pages: int = 150,
) -> Iterator[dict[str, Any]]:
    """
    Crawl CCEA qualification specifications.

    Args:
        qualification_level: "gcse", "a_level", or "as_level"
        max_pages: Maximum pages to crawl

    Yields:
        Crawled specification pages
    """
    urls_to_crawl = []

    if qualification_level and qualification_level in CCEA_QUAL_URLS:
        urls_to_crawl.append((qualification_level, CCEA_QUAL_URLS[qualification_level]))
    else:
        for level in ["gcse", "a_level", "as_level"]:
            urls_to_crawl.append((level, CCEA_QUAL_URLS[level]))

    include_paths = [
        "/qualifications/*",
        "/specifications/*",
        "/past-papers/*",
    ]

    for level, base_url in urls_to_crawl:
        for page in crawl_website(
            base_url=base_url,
            include_paths=include_paths,
            max_pages=max_pages // len(urls_to_crawl),
            max_depth=3,
        ):
            url = page.get("url", "")
            title = page.get("title", "")

            # Try to extract subject
            subject = None
            # CCEA offers Irish as a subject (unique to NI among UK nations)
            for subj in ["mathematics", "english", "irish", "physics", "chemistry", "biology",
                         "history", "geography", "technology", "home-economics"]:
                if subj in url.lower() or subj in title.lower():
                    subject = subj.replace("-", "_")
                    break

            # Detect Irish subject content
            language = "en"
            if subject == "irish" or "gaeilge" in url.lower():
                language = "ga"

            page["nation"] = "northern_ireland"
            page["source"] = "ccea"
            page["qualification_level"] = level
            page["curriculum_framework"] = "ccea_qualifications"
            page["subject"] = subject
            page["language"] = language
            page["indexed_at"] = datetime.now(UTC).isoformat()

            # Add content hash
            content = page.get("markdown", "")
            if content:
                page["content_hash"] = compute_content_hash(content)

            yield page

def _crawl_ni_curriculum(
    key_stage: str | None = None,
    include_irish_medium: bool = True,
    max_pages: int = 200,
) -> Iterator[dict[str, Any]]:
    """
    Crawl CCEA Northern Ireland Curriculum resources.

    Args:
        key_stage: Specific key stage to crawl (foundation, key_stage_1, etc.)
        include_irish_medium: Include Irish-medium education resources
        max_pages: Maximum pages to crawl

    Yields:
        Crawled curriculum pages with metadata
    """
    urls_to_crawl = []

    if key_stage and key_stage in NI_CURRICULUM_URLS:
        urls_to_crawl.append((key_stage, NI_CURRICULUM_URLS[key_stage]))
    else:
        # Crawl all key stages
        for stage in ["foundation", "key_stage_1", "key_stage_2", "key_stage_3", "key_stage_4"]:
            urls_to_crawl.append((stage, NI_CURRICULUM_URLS[stage]))

    if include_irish_medium and (key_stage is None or key_stage == "irish_medium"):
        urls_to_crawl.append(("irish_medium", NI_CURRICULUM_URLS["irish_medium"]))

    include_paths = [
        "/curriculum/*",
        "/learning-resources/*",
        "/support/*",
    ]

    exclude_paths = [
        "/news/*",
        "/events/*",
        "/about/*",
    ]

    for stage, base_url in urls_to_crawl:
        for page in crawl_website(
            base_url=base_url,
            include_paths=include_paths,
            exclude_paths=exclude_paths,
            max_pages=max_pages // len(urls_to_crawl),
            max_depth=4,
        ):
            url = page.get("url", "")

            # Detect Irish-medium content
            language = "en"
            is_irish_medium = False
            if "irish-medium" in url.lower() or "gaeilge" in url.lower():
                language = "ga"
                is_irish_medium = True

            # Try to detect Area of Learning
            area_of_learning = None
            for area in NI_AREAS_OF_LEARNING:
                if area.replace("_", "-") in url.lower():
                    area_of_learning = area
                    break

            page["nation"] = "northern_ireland"
            page["source"] = "ccea"
            page["curriculum_framework"] = "ni_curriculum"
            page["key_stage"] = stage
            page["area_of_learning"] = area_of_learning
            page["language"] = language
            page["is_irish_medium"] = is_irish_medium
            page["indexed_at"] = datetime.now(UTC).isoformat()

            # Add content hash
            content = page.get("markdown", "")
            if content:
                page["content_hash"] = compute_content_hash(content)

            yield page

def _extract_ccea_pdf_links(qualification_level: str) -> Iterator[dict[str, Any]]:
    """
    Extract PDF specification links from CCEA pages.
    """
    if qualification_level not in CCEA_QUAL_URLS:
        return

    page = scrape_page(CCEA_QUAL_URLS[qualification_level])
    links = page.get("links", [])

    for link in links:
        if not link:
            continue

        lower_link = link.lower()
        if ".pdf" in lower_link and ("spec" in lower_link or "support" in lower_link):
            yield {
                "url": link if link.startswith("http") else f"https://ccea.org.uk{link}",
                "file_type": "pdf",
                "qualification_level": qualification_level,
                "source_page": CCEA_QUAL_URLS[qualification_level],
                "nation": "northern_ireland",
                "source": "ccea",
                "discovered_at": datetime.now(UTC).isoformat(),
            }
