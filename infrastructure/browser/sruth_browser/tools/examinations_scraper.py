"""
SEC Examinations.ie Scraper for Irish State Examination Materials.

Uses browser automation (Stagehand) to interact with dropdown menus and download:
- Past exam papers (1999-2024)
- Marking schemes
- Chief Examiner Reports
- Statistics

The examinations.ie site requires JavaScript and dropdown interaction,
making browser automation necessary.

Rate Limiting: 1 request/second (government site)

Usage:
    from sruth_browser.tools.examinations_scraper import (
        scrape_exam_materials,
        scrape_all_subjects,
        ExamMaterial,
    )

    # Single subject
    async for material in scrape_exam_materials(
        subject="Mathematics",
        years=[2023, 2024],
        level="leaving_certificate",
    ):
        print(material.pdf_url)

    # All subjects
    materials = await scrape_all_subjects(
        level="leaving_certificate",
        years=range(2020, 2025),
    )
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from urllib.parse import urljoin

from ..backends.router import get_router
from ..browser_types import BrowserOperation, ExtractionFormat

logger = logging.getLogger(__name__)

# Base URLs
EXAMINATIONS_BASE_URL = "https://www.examinations.ie"
EXAM_ARCHIVE_URL = "https://www.examinations.ie/exammaterialarchive/"
STATISTICS_URL = "https://www.examinations.ie/statistics/"

# Rate limiting (1 req/sec for government site)
RATE_LIMIT_SECONDS = 1.0


class ExamLevel(str, Enum):
    """Examination levels."""

    LEAVING_CERTIFICATE = "leaving-certificate"
    JUNIOR_CYCLE = "junior-cycle"
    LCA = "leaving-certificate-applied"


class ExamMaterialType(str, Enum):
    """Types of exam materials."""

    PAPER = "paper"
    MARKING_SCHEME = "marking_scheme"
    EXAMINER_REPORT = "examiner_report"
    AURAL = "aural"
    SAMPLE = "sample"
    STATISTICS = "statistics"


@dataclass
class ExamMaterial:
    """A single exam material (paper, marking scheme, report)."""

    # Identifiers
    subject: str
    year: int
    level: str  # leaving_certificate, junior_cycle
    material_type: ExamMaterialType

    # Content
    pdf_url: str
    title: str | None = None

    # Metadata
    paper_number: int | None = None  # Paper 1, Paper 2, etc.
    exam_level: str | None = None  # Higher, Ordinary, Foundation
    language: str = "en"  # en or ga

    # Processing
    content_hash: str | None = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "subject": self.subject,
            "year": self.year,
            "level": self.level,
            "material_type": self.material_type.value,
            "pdf_url": self.pdf_url,
            "title": self.title,
            "paper_number": self.paper_number,
            "exam_level": self.exam_level,
            "language": self.language,
            "content_hash": self.content_hash,
            "scraped_at": self.scraped_at.isoformat(),
        }


# Subject mappings (SEC uses different names)
SEC_SUBJECT_MAPPING = {
    "mathematics": "Mathematics",
    "english": "English",
    "gaeilge": "Irish",
    "biology": "Biology",
    "chemistry": "Chemistry",
    "physics": "Physics",
    "geography": "Geography",
    "history": "History",
    "french": "French",
    "german": "German",
    "spanish": "Spanish",
    "accounting": "Accounting",
    "business": "Business",
    "economics": "Economics",
    "art": "Art",
    "music": "Music",
    "home-economics": "Home Economics",
    "computer-science": "Computer Science",
    "agricultural-science": "Agricultural Science",
    "applied-mathematics": "Applied Mathematics",
    "classical-studies": "Classical Studies",
    "construction-studies": "Construction Studies",
    "design-and-communication-graphics": "Design and Communication Graphics",
    "engineering": "Engineering",
    "italian": "Italian",
    "japanese": "Japanese",
    "latin": "Latin",
    "physical-education": "Physical Education",
    "physics-and-chemistry": "Physics and Chemistry",
    "politics-and-society": "Politics and Society",
    "religious-education": "Religious Education",
    "technology": "Technology",
    # Junior Cycle specific
    "science": "Science",
    "business-studies": "Business Studies",
    "graphics": "Graphics",
    "wood-technology": "Wood Technology",
    "visual-art": "Visual Art",
    "classics": "Classics",
}


def _classify_material_type(url: str, title: str | None = None) -> ExamMaterialType:
    """Classify exam material type from URL/title."""
    text = f"{url} {title or ''}".lower()

    if "marking" in text or "scheme" in text or "ms_" in text:
        return ExamMaterialType.MARKING_SCHEME
    elif "examiner" in text or "report" in text or "cer_" in text:
        return ExamMaterialType.EXAMINER_REPORT
    elif "aural" in text or "audio" in text or "listening" in text:
        return ExamMaterialType.AURAL
    elif "sample" in text:
        return ExamMaterialType.SAMPLE
    elif "stat" in text:
        return ExamMaterialType.STATISTICS
    else:
        return ExamMaterialType.PAPER


def _extract_paper_number(url: str, title: str | None = None) -> int | None:
    """Extract paper number from URL/title."""
    text = f"{url} {title or ''}"

    # Match "Paper 1", "Paper 2", "P1", "P2", etc.
    match = re.search(r"(?:paper|p)[\s_-]?(\d)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def _extract_exam_level(url: str, title: str | None = None) -> str | None:
    """Extract exam level (Higher/Ordinary/Foundation) from URL/title."""
    text = f"{url} {title or ''}".lower()

    if "higher" in text or "_h_" in text or "_hl_" in text:
        return "Higher"
    elif "ordinary" in text or "_o_" in text or "_ol_" in text:
        return "Ordinary"
    elif "foundation" in text or "_f_" in text or "_fl_" in text:
        return "Foundation"
    elif "common" in text:
        return "Common"
    return None


async def scrape_exam_materials(
    subject: str,
    years: list[int] | None = None,
    level: str = "leaving_certificate",
    language: str = "en",
    include_marking_schemes: bool = True,
    include_examiner_reports: bool = True,
) -> AsyncIterator[ExamMaterial]:
    """
    Scrape exam materials for a subject using browser automation.

    The exam archive page uses a JavaScript-driven cascading form:
    1. Accept terms checkbox (id: MaterialArchive__noTable__cbv__AgreeCheck)
    2. "Choose Type" dropdown (Exam Papers, Marking Schemes, etc.)
    3. Level dropdown (appears after type selection)
    4. Subject dropdown (appears after level selection)
    5. Year dropdown (appears after subject selection)
    6. Submit to view results with PDF links

    Args:
        subject: Subject slug (e.g., "mathematics")
        years: Years to scrape (default: 2020-2024)
        level: Exam level (leaving_certificate, junior_cycle)
        language: Language code (en, ga)
        include_marking_schemes: Include marking schemes
        include_examiner_reports: Include examiner reports

    Yields:
        ExamMaterial objects
    """
    if years is None:
        years = list(range(2020, 2025))

    sec_subject = SEC_SUBJECT_MAPPING.get(subject, subject.replace("-", " ").title())

    # Map our level enum to SEC dropdown labels
    level_labels = {
        "leaving_certificate": "Leaving Certificate",
        "junior_cycle": "Junior Cycle",
        "leaving_certificate_applied": "Leaving Cert Applied",
    }
    level_display = level_labels.get(level, "Leaving Certificate")

    # Determine material type selector label
    # The site has separate dropdown entries for different material types
    # e.g., "Exam Papers", "Marking Schemes"
    material_type_labels = ["Exam Papers"]
    if include_marking_schemes:
        material_type_labels.append("Marking Schemes")

    router = get_router()
    if not router._backends:
        try:
            from ..backends.selfhosted.stagehand_backend import StagehandBackend
            router.register_backend(StagehandBackend())
        except ImportError:
            pass

    backend_type = await router.select_backend(BrowserOperation.EXTRACTION)
    if not backend_type:
        logger.error("No browser backend available")
        return

    backend = router.get_backend(backend_type)

    try:
        await backend.initialize()

        for material_type_label in material_type_labels:
            logger.info(f"Scraping {sec_subject} {material_type_label}")

            # Start fresh for each material type (dropdown state is sticky)
            nav_result = await backend.navigate(EXAM_ARCHIVE_URL)
            if not nav_result.success:
                logger.error(f"Failed to navigate to exam archive: {nav_result.error}")
                return

            # Wait for page to load
            await asyncio.sleep(2)

            # Step 1: Accept Terms & Conditions checkbox
            logger.info("Accepting terms and conditions checkbox")
            agree_result = await backend.interact(
                "Check the 'I have read, understand and accept the Terms and Conditions' checkbox"
            )
            if not agree_result.success:
                logger.error(f"Failed to accept terms: {agree_result.error}")
                continue
            await asyncio.sleep(RATE_LIMIT_SECONDS)

            # Step 2: Select "Choose Type" dropdown
            logger.info(f"Selecting material type: {material_type_label}")
            type_result = await backend.interact(
                f"Select '{material_type_label}' from the 'Choose Type' dropdown menu"
            )
            if not type_result.success:
                logger.error(f"Failed to select type: {type_result.error}")
                continue
            await asyncio.sleep(RATE_LIMIT_SECONDS)

            # Step 3: Select Level dropdown
            logger.info(f"Selecting level: {level_display}")
            level_result = await backend.interact(
                f"Select '{level_display}' from the level dropdown menu"
            )
            if not level_result.success:
                logger.error(f"Failed to select level: {level_result.error}")
                continue
            await asyncio.sleep(RATE_LIMIT_SECONDS)

            # Step 4: Select Subject dropdown
            logger.info(f"Selecting subject: {sec_subject}")
            subject_result = await backend.interact(
                f"Select '{sec_subject}' from the subject dropdown menu"
            )
            if not subject_result.success:
                logger.error(f"Failed to select subject: {subject_result.error}")
                continue
            await asyncio.sleep(RATE_LIMIT_SECONDS)

            for year in years:
                logger.info(f"Scraping {sec_subject} {material_type_label} {year}")

                # Step 5: Select Year
                year_result = await backend.interact(
                    f"Select '{year}' from the year dropdown menu"
                )
                if not year_result.success:
                    logger.warning(f"Failed to select year {year}: {year_result.error}")
                    continue
                await asyncio.sleep(RATE_LIMIT_SECONDS)

                # Step 6: Submit the form (click View/Search button)
                submit_result = await backend.interact(
                    "Click the 'View' or 'Search' or 'Submit' button to show exam material results"
                )
                if not submit_result.success:
                    logger.warning(f"Failed to submit for {year}: {submit_result.error}")
                    continue
                await asyncio.sleep(3)  # Wait for results to load

                # Step 7: Extract PDF links from results
                extraction_result = await backend.extract(
                    url="",
                    prompt="""
                    Extract all PDF download links from the exam material results on this page.
                    For each link found, extract:
                    - url: Full URL to the PDF file (possibly relative to examinations.ie)
                    - title: Link text or description (e.g. "Higher Level Paper 1")
                    Return as a list of objects with url and title fields.
                    """,
                    formats=[ExtractionFormat.STRUCTURED],
                    schema={
                        "type": "object",
                        "properties": {
                            "links": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "url": {"type": "string"},
                                        "title": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                )

                if not extraction_result.success or not extraction_result.content:
                    logger.warning(f"No results found for {sec_subject} {year}")
                    continue

                # Process extracted links
                links = extraction_result.content
                if isinstance(links, dict):
                    links = links.get("extracted", links)
                    links = links.get("links", links.get("results", [links] if isinstance(links, dict) else links))

                if not isinstance(links, list):
                    logger.warning(f"Unexpected links format for {sec_subject} {year}: {type(links)}")
                    continue

                for link in links:
                    if isinstance(link, str):
                        url = link
                        title = None
                    elif isinstance(link, dict):
                        url = link.get("url") or link.get("href", "")
                        title = link.get("title") or link.get("text")
                    else:
                        continue

                    if not url:
                        continue

                    # Accept both .pdf and other document URLs
                    if not url.endswith(".pdf") and ".pdf" not in url:
                        continue

                    if not url.startswith("http"):
                        url = urljoin(EXAMINATIONS_BASE_URL, url)

                    material_type = _classify_material_type(url, title)

                    if material_type == ExamMaterialType.MARKING_SCHEME and not include_marking_schemes:
                        continue
                    if material_type == ExamMaterialType.EXAMINER_REPORT and not include_examiner_reports:
                        continue

                    yield ExamMaterial(
                        subject=subject,
                        year=year,
                        level=level,
                        material_type=material_type,
                        pdf_url=url,
                        title=title,
                        paper_number=_extract_paper_number(url, title),
                        exam_level=_extract_exam_level(url, title),
                        language=language,
                        content_hash=hashlib.sha256(url.encode()).hexdigest()[:16],
                    )

                # Rate limiting between years
                await asyncio.sleep(RATE_LIMIT_SECONDS)

            # Rate limiting between material types
            await asyncio.sleep(RATE_LIMIT_SECONDS * 2)

    finally:
        if backend and hasattr(backend, "close"):
            await backend.close()


async def scrape_all_subjects(
    level: str = "leaving_certificate",
    years: list[int] | None = None,
    language: str = "en",
    subjects: list[str] | None = None,
) -> list[ExamMaterial]:
    """
    Scrape exam materials for all subjects.

    Args:
        level: Exam level
        years: Years to scrape
        language: Language code
        subjects: Optional list of subjects (default: all)

    Returns:
        List of all ExamMaterial objects
    """
    if subjects is None:
        subjects = list(SEC_SUBJECT_MAPPING.keys())

    all_materials = []

    for subject in subjects:
        logger.info(f"Scraping {subject}")
        async for material in scrape_exam_materials(
            subject=subject,
            years=years,
            level=level,
            language=language,
        ):
            all_materials.append(material)

        # Rate limit between subjects
        await asyncio.sleep(RATE_LIMIT_SECONDS * 2)

    return all_materials


async def scrape_examiner_reports(
    subject: str | None = None,
    years: list[int] | None = None,
    level: str = "leaving_certificate",
) -> AsyncIterator[ExamMaterial]:
    """
    Scrape Chief Examiner Reports specifically.

    Args:
        subject: Subject slug (None for all subjects)
        years: Years to scrape
        level: Exam level

    Yields:
        ExamMaterial objects for examiner reports only
    """
    subjects = [subject] if subject else list(SEC_SUBJECT_MAPPING.keys())

    for subj in subjects:
        async for material in scrape_exam_materials(
            subject=subj,
            years=years,
            level=level,
            include_marking_schemes=False,
            include_examiner_reports=True,
        ):
            if material.material_type == ExamMaterialType.EXAMINER_REPORT:
                yield material


async def scrape_statistics(
    years: list[int] | None = None,
) -> AsyncIterator[ExamMaterial]:
    """
    Scrape examination statistics.

    Args:
        years: Years to scrape

    Yields:
        ExamMaterial objects for statistics files
    """
    if years is None:
        years = list(range(2015, 2025))

    router = get_router()
    backend = await router.select_backend(BrowserOperation.EXTRACTION)

    try:
        await backend.initialize()

        # Navigate to statistics page
        await backend.navigate(STATISTICS_URL)
        await asyncio.sleep(2)

        for year in years:
            # Select year
            await backend.interact(f"Select or click on '{year}' to view statistics")
            await asyncio.sleep(RATE_LIMIT_SECONDS)

            # Extract download links
            extraction_result = await backend.extract(
                url="",
                prompt="""
                Extract all downloadable file links (CSV, PDF, XLS) for statistics.
                For each link, extract url and title.
                """,
                formats=[ExtractionFormat.STRUCTURED],
                schema={
                    "type": "object",
                    "properties": {
                        "links": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "url": {"type": "string"},
                                    "title": {"type": "string"},
                                },
                            },
                        },
                    },
                },
            )

            if extraction_result.success and extraction_result.content:
                links = extraction_result.content
                if isinstance(links, dict):
                    links = links.get("extracted", links)
                    links = links.get("links", [links] if isinstance(links, dict) else links)

                for link in links:
                    url = link.get("url") if isinstance(link, dict) else link
                    title = link.get("title") if isinstance(link, dict) else None

                    if url:
                        if not url.startswith("http"):
                            url = urljoin(EXAMINATIONS_BASE_URL, url)

                        yield ExamMaterial(
                            subject="statistics",
                            year=year,
                            level="all",
                            material_type=ExamMaterialType.STATISTICS,
                            pdf_url=url,
                            title=title,
                        )

    finally:
        if backend and hasattr(backend, "close"): await backend.close()


# Sync wrappers for DLT compatibility


def scrape_exam_materials_sync(
    subject: str,
    years: list[int] | None = None,
    level: str = "leaving_certificate",
    language: str = "en",
) -> list[ExamMaterial]:
    """Synchronous wrapper for scrape_exam_materials."""

    async def _collect():
        materials = []
        async for m in scrape_exam_materials(subject, years, level, language):
            materials.append(m)
        return materials

    return asyncio.run(_collect())


def scrape_all_subjects_sync(
    level: str = "leaving_certificate",
    years: list[int] | None = None,
    language: str = "en",
    subjects: list[str] | None = None,
) -> list[ExamMaterial]:
    """Synchronous wrapper for scrape_all_subjects."""
    return asyncio.run(scrape_all_subjects(level, years, language, subjects))
