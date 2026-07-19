"""
Shared helpers split from uk/england/national_curriculum.py

Phase 3D of openspec change.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

from dlt_sources.common.firecrawl_source import crawl_website, scrape_page
from dlt_sources.common.incremental import compute_content_hash

EXAM_BOARD_URLS = {
    "aqa": {
        "gcse": "https://www.aqa.org.uk/subjects/gcse",
        "a_level": "https://www.aqa.org.uk/subjects/a-level",
        "specifications": "https://www.aqa.org.uk/find-past-papers-and-mark-schemes",
    },
    "edexcel": {
        "gcse": "https://qualifications.pearson.com/en/qualifications/edexcel-gcses.html",
        "a_level": "https://qualifications.pearson.com/en/qualifications/edexcel-a-levels.html",
        "international": "https://qualifications.pearson.com/en/qualifications/edexcel-international-gcses.html",
    },
    "ocr": {
        "gcse": "https://www.ocr.org.uk/qualifications/gcse/",
        "a_level": "https://www.ocr.org.uk/qualifications/as-and-a-level/",
        "cambridge_nationals": "https://www.ocr.org.uk/qualifications/cambridge-nationals/",
    },
}

GOV_UK_CURRICULUM_URLS = {
    "overview": "https://www.gov.uk/national-curriculum",
    "key_stage_1": "https://www.gov.uk/government/collections/national-curriculum-key-stage-1-and-2",
    "key_stage_2": "https://www.gov.uk/government/collections/national-curriculum-key-stage-1-and-2",
    "key_stage_3": "https://www.gov.uk/government/collections/national-curriculum-key-stage-3-and-4",
    "key_stage_4": "https://www.gov.uk/government/collections/national-curriculum-key-stage-3-and-4",
    "subject_content": "https://www.gov.uk/government/collections/gcse-subject-content",
    "a_level_content": "https://www.gov.uk/government/collections/gce-as-and-a-level-subject-content",
}

NC_SUBJECTS = [
    "english",
    "mathematics",
    "science",
    "art_design",
    "citizenship",
    "computing",
    "design_technology",
    "geography",
    "history",
    "languages",
    "music",
    "physical_education",
]

def _crawl_exam_board(
    board: str,
    qualification_level: str | None = None,
    max_pages: int = 100,
) -> Iterator[dict[str, Any]]:
    """
    Crawl an exam board's qualification pages.

    Args:
        board: "aqa", "edexcel", or "ocr"
        qualification_level: "gcse" or "a_level"
        max_pages: Maximum pages to crawl

    Yields:
        Crawled specification pages
    """
    if board not in EXAM_BOARD_URLS:
        return

    board_urls = EXAM_BOARD_URLS[board]
    urls_to_crawl = []

    if qualification_level and qualification_level in board_urls:
        urls_to_crawl.append((qualification_level, board_urls[qualification_level]))
    else:
        for level in ["gcse", "a_level"]:
            if level in board_urls:
                urls_to_crawl.append((level, board_urls[level]))

    include_paths = [
        "/subjects/*",
        "/qualifications/*",
        "/specifications/*",
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
            for subj in ["mathematics", "maths", "english", "physics", "chemistry", "biology",
                         "history", "geography", "computer-science", "economics", "psychology"]:
                if subj in url.lower() or subj in title.lower():
                    # Normalize "maths" to "mathematics"
                    subject = "mathematics" if subj == "maths" else subj.replace("-", "_")
                    break

            page["nation"] = "england"
            page["source"] = board
            page["qualification_level"] = level
            page["curriculum_framework"] = f"{board}_qualifications"
            page["subject"] = subject
            page["language"] = "en"
            page["indexed_at"] = datetime.now(UTC).isoformat()

            # Add content hash
            content = page.get("markdown", "")
            if content:
                page["content_hash"] = compute_content_hash(content)

            yield page

def _crawl_gov_uk_curriculum(
    key_stage: str | None = None,
    max_pages: int = 200,
) -> Iterator[dict[str, Any]]:
    """
    Crawl gov.uk National Curriculum resources.

    Args:
        key_stage: Specific key stage to crawl (key_stage_1, key_stage_2, etc.)
        max_pages: Maximum pages to crawl

    Yields:
        Crawled curriculum pages with metadata
    """
    urls_to_crawl = []

    if key_stage and key_stage in GOV_UK_CURRICULUM_URLS:
        urls_to_crawl.append((key_stage, GOV_UK_CURRICULUM_URLS[key_stage]))
    else:
        urls_to_crawl.extend([
            ("overview", GOV_UK_CURRICULUM_URLS["overview"]),
            ("key_stage_1_2", GOV_UK_CURRICULUM_URLS["key_stage_1"]),
            ("key_stage_3_4", GOV_UK_CURRICULUM_URLS["key_stage_3"]),
            ("gcse_content", GOV_UK_CURRICULUM_URLS["subject_content"]),
            ("a_level_content", GOV_UK_CURRICULUM_URLS["a_level_content"]),
        ])

    include_paths = [
        "/national-curriculum*",
        "/government/publications/*curriculum*",
        "/government/collections/*curriculum*",
        "/government/collections/*gcse*",
        "/government/collections/*a-level*",
    ]

    exclude_paths = [
        "/government/consultations/*",
        "/government/news/*",
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

            # Determine key stage from URL
            detected_stage = stage
            if "key-stage-1" in url or "ks1" in url.lower():
                detected_stage = "key_stage_1"
            elif "key-stage-2" in url or "ks2" in url.lower():
                detected_stage = "key_stage_2"
            elif "key-stage-3" in url or "ks3" in url.lower():
                detected_stage = "key_stage_3"
            elif "key-stage-4" in url or "ks4" in url.lower():
                detected_stage = "key_stage_4"

            # Detect subject from URL
            subject = None
            title = page.get("title", "")
            for subj in NC_SUBJECTS:
                subj_pattern = subj.replace("_", "-")
                if subj_pattern in url.lower() or subj in title.lower():
                    subject = subj
                    break

            page["nation"] = "england"
            page["source"] = "gov_uk"
            page["curriculum_framework"] = "national_curriculum"
            page["key_stage"] = detected_stage
            page["subject"] = subject
            page["language"] = "en"
            page["indexed_at"] = datetime.now(UTC).isoformat()

            # Add content hash
            content = page.get("markdown", "")
            if content:
                page["content_hash"] = compute_content_hash(content)

            yield page

def _extract_exam_board_pdf_links(board: str, qualification_level: str) -> Iterator[dict[str, Any]]:
    """
    Extract PDF specification links from exam board pages.
    """
    if board not in EXAM_BOARD_URLS:
        return

    board_urls = EXAM_BOARD_URLS[board]
    if qualification_level not in board_urls:
        return

    page = scrape_page(board_urls[qualification_level])
    links = page.get("links", [])

    base_domains = {
        "aqa": "https://www.aqa.org.uk",
        "edexcel": "https://qualifications.pearson.com",
        "ocr": "https://www.ocr.org.uk",
    }

    for link in links:
        if not link:
            continue

        lower_link = link.lower()
        if ".pdf" in lower_link and ("spec" in lower_link or "syllabus" in lower_link):
            yield {
                "url": link if link.startswith("http") else f"{base_domains[board]}{link}",
                "file_type": "pdf",
                "qualification_level": qualification_level,
                "source_page": board_urls[qualification_level],
                "nation": "england",
                "source": board,
                "discovered_at": datetime.now(UTC).isoformat(),
            }
