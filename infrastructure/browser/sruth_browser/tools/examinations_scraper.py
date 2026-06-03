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
import os
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
    """Classify exam material type from URL/title.

    Handles both direct .pdf URLs and SEC obfuscated ?fp= URLs where
    classification must rely on title/context rather than file path.
    """
    text = f"{url} {title or ''}".lower()

    if "marking" in text or "scheme" in text or "ms_" in text or "marking_scheme" in text:
        return ExamMaterialType.MARKING_SCHEME
    elif "examiner" in text or "report" in text or "cer_" in text or "chief" in text:
        return ExamMaterialType.EXAMINER_REPORT
    elif "aural" in text or "audio" in text or "listening" in text:
        return ExamMaterialType.AURAL
    elif "sample" in text:
        return ExamMaterialType.SAMPLE
    elif "stat" in text:
        return ExamMaterialType.STATISTICS
    else:
        return ExamMaterialType.PAPER


def _material_type_from_key(key: str) -> ExamMaterialType:
    """Convert material type key string to ExamMaterialType enum."""
    mapping = {
        "exam_papers": ExamMaterialType.PAPER,
        "marking_schemes": ExamMaterialType.MARKING_SCHEME,
        "deferred_papers": ExamMaterialType.PAPER,
        "deferred_marking_schemes": ExamMaterialType.MARKING_SCHEME,
    }
    return mapping.get(key, ExamMaterialType.PAPER)


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
                    Extract all download links from the exam material results on this page.
                    The site uses obfuscated ?fp= URLs like /exammaterialarchive/?fp=96.113...
                    These ARE valid PDF download links — extract them.
                    Also extract any direct .pdf links or /qvp/ paths.
                    For each link found, extract:
                    - url: Full URL (possibly relative to examinations.ie)
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

                    # Accept .pdf links, ?fp= obfuscated URLs, /qvp/ paths
                    if not (".pdf" in url.lower() or "?fp=" in url or "/qvp/" in url.lower()):
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


async def scrape_materials_batch(
    subjects: list[str],
    years: list[int] | None = None,
    level: str = "leaving_certificate",
    language: str = "en",
    material_types: list[str] | None = None,
) -> AsyncIterator[ExamMaterial]:
    """Scrape exam materials for multiple subjects using a single browser session.

    Reuses one Stagehand initialization across all subjects, avoiding
    the 30+ second startup cost per subject.

    Args:
        subjects: List of subject slugs (e.g., ["mathematics", "english"])
        years: Years to scrape (default: 2020-2024)
        level: Exam level (leaving_certificate, junior_cycle, leaving_certificate_applied)
        language: Language code (en, ga). Both languages' papers are downloaded.
        material_types: List of types to scrape ("exam_papers", "marking_schemes").
                       Default: both.

    Yields:
        ExamMaterial objects for all subjects/years/types requested
    """
    if years is None:
        years = list(range(2020, 2025))
    if material_types is None:
        material_types = ["exam_papers", "marking_schemes"]

    level_labels = {
        "leaving_certificate": "Leaving Certificate",
        "junior_cycle": "Junior Cycle",
        "leaving_certificate_applied": "Leaving Cert Applied",
    }
    level_display = level_labels.get(level, "Leaving Certificate")

    type_dropdown_labels = {
        "exam_papers": "Exam Papers",
        "marking_schemes": "Marking Schemes",
        "deferred_papers": "Deferred Papers",
        "deferred_marking_schemes": "Deferred Marking Schemes",
    }

    router = get_router()
    if not router._backends:
        try:
            from ..backends.selfhosted.stagehand_backend import StagehandBackend
            router.register_backend(StagehandBackend())
        except ImportError:
            logger.error("No browser backend available for batch scrape")
            return

    backend_type = await router.select_backend(BrowserOperation.EXTRACTION)
    if not backend_type:
        logger.error("No browser backend selected for batch scrape")
        return

    backend = router.get_backend(backend_type)

    try:
        await backend.initialize()

        for material_type_key in material_types:
            material_type_label = type_dropdown_labels.get(material_type_key, material_type_key)

            for subject in subjects:
                sec_subject = SEC_SUBJECT_MAPPING.get(subject, subject.replace("-", " ").title())
                logger.info(f"Batch scrape: {sec_subject} {material_type_label} ({level})")

                try:
                    async for material in _scrape_single_subject_session(
                        backend=backend,
                        subject=subject,
                        sec_subject=sec_subject,
                        years=years,
                        level=level,
                        level_display=level_display,
                        material_type_key=material_type_key,
                        material_type_label=material_type_label,
                        language=language,
                    ):
                        yield material
                except Exception as e:
                    logger.error(f"subject_failed: {subject}: {e}")
                    yield ExamMaterial(
                        subject=subject,
                        year=0,
                        level=level,
                        material_type=ExamMaterialType.PAPER,
                        pdf_url="",
                        title=f"Error: {e}",
                        content_hash="error",
                    )

                await asyncio.sleep(RATE_LIMIT_SECONDS * 2)

    finally:
        if backend and hasattr(backend, "close"):
            await backend.close()


async def _scrape_single_subject_session(
    backend: Any,
    subject: str,
    sec_subject: str,
    years: list[int],
    level: str,
    level_display: str,
    material_type_key: str,
    material_type_label: str,
    language: str,
) -> AsyncIterator[ExamMaterial]:
    """Scrape a single subject using an existing browser session.

    Does NOT initialize or close the backend — caller manages the session lifecycle.
    Navigates to the archive fresh for each subject/type combo.
    """
    nav_result = await backend.navigate(EXAM_ARCHIVE_URL)
    if not nav_result.success:
        logger.error(f"Failed to navigate to exam archive: {nav_result.error}")
        return

    await asyncio.sleep(2)

    agree_result = await backend.interact(
        "Check the 'I have read, understand and accept the Terms and Conditions' checkbox"
    )
    if not agree_result.success:
        logger.error(f"Failed to accept terms for {sec_subject}: {agree_result.error}")
        return
    await asyncio.sleep(RATE_LIMIT_SECONDS)

    type_result = await backend.interact(
        f"Select '{material_type_label}' from the 'Choose Type' dropdown menu"
    )
    if not type_result.success:
        logger.error(f"Failed to select type for {sec_subject}: {type_result.error}")
        return
    await asyncio.sleep(RATE_LIMIT_SECONDS)

    # SEC cascade: Type → Year → Examination → Subject
    for year in years:
        logger.info(f"Extracting {sec_subject} {material_type_label} {year}")

        year_result = await backend.interact(
            f"Select '{year}' from the year dropdown menu"
        )
        if not year_result.success:
            logger.warning(f"Failed to select year {year}: {year_result.error}")
            continue
        await asyncio.sleep(RATE_LIMIT_SECONDS)

        level_result = await backend.interact(
            f"Select '{level_display}' from the examination dropdown menu"
        )
        if not level_result.success:
            logger.warning(f"Failed to select level for {sec_subject} {year}: {level_result.error}")
            continue
        await asyncio.sleep(RATE_LIMIT_SECONDS)

        subject_result = await backend.interact(
            f"Select '{sec_subject}' from the subject dropdown menu"
        )
        if not subject_result.success:
            logger.warning(f"Failed to select subject {sec_subject} {year}: {subject_result.error}")
            continue
        await asyncio.sleep(RATE_LIMIT_SECONDS)

        submit_result = await backend.interact(
            "Click the 'View' or 'Search' or 'Submit' button to show exam material results"
        )
        if not submit_result.success:
            logger.warning(f"Failed to submit for {sec_subject} {year}: {submit_result.error}")
            continue
        await asyncio.sleep(3)

        extraction_result = await backend.extract(
            url="",
            prompt="""
            Extract all download links from the exam material results on this page.
            The site uses obfuscated ?fp= URLs like /exammaterialarchive/?fp=96.113...
            These ARE valid PDF download links — extract them.
            Also extract any direct .pdf links or /qvp/ paths.
            For each link found, extract:
            - url: Full URL (possibly relative to examinations.ie)
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

            # Accept .pdf links, ?fp= obfuscated URLs, /qvp/ paths
            if not (".pdf" in url.lower() or "?fp=" in url or "/qvp/" in url.lower()):
                continue

            if not url.startswith("http"):
                url = urljoin(EXAMINATIONS_BASE_URL, url)

            material_type = _classify_material_type(url, title)

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

        await asyncio.sleep(RATE_LIMIT_SECONDS)


async def scrape_materials_playwright(
    subjects: list[str],
    years: list[int] | None = None,
    level: str = "leaving_certificate",
    language: str = "en",
    material_types: list[str] | None = None,
    cdp_url: str | None = None,
) -> AsyncIterator[ExamMaterial]:
    """Scrape exam materials using Playwright directly (no LLM calls).

    Uses native select_option() for dropdowns and query_selector_all()
    for PDF link extraction. Deterministic and zero LLM cost.

    Falls back to the BROWSER_CDP_URL env var or http://127.0.0.1:9223/json/version.
    """
    if years is None:
        years = list(range(2020, 2025))
    if material_types is None:
        material_types = ["exam_papers", "marking_schemes"]

    from playwright.async_api import async_playwright

    if cdp_url is None:
        cdp_url = os.environ.get("BROWSER_CDP_URL", "http://127.0.0.1:9223")

    level_selectors = {
        "leaving_certificate": "Leaving Certificate",
        "junior_cycle": "Junior Cycle",
        "leaving_certificate_applied": "Leaving Cert Applied",
    }
    type_selectors = {
        "exam_papers": "Exam Papers",
        "marking_schemes": "Marking Schemes",
        "deferred_papers": "Deferred Exam Papers",
        "deferred_marking_schemes": "Deferred Exam Marking Schemes",
    }

    level_value = level_selectors.get(level, "Leaving Certificate")

    pw = await async_playwright().start()
    try:
        if cdp_url.startswith("http"):
            import json as _json
            import urllib.request
            req = urllib.request.Request(cdp_url.rstrip("/") + "/json/version")
            with urllib.request.urlopen(req, timeout=5) as resp:
                payload = _json.loads(resp.read().decode())
            ws_url = payload["webSocketDebuggerUrl"].replace("0.0.0.0", "127.0.0.1")
        else:
            ws_url = cdp_url

        browser = await pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = context.pages[0] if context.pages else await context.new_page()

        for mt_key in material_types:
            mt_label = type_selectors.get(mt_key, mt_key)

            for subject in subjects:
                sec_subject = SEC_SUBJECT_MAPPING.get(subject, subject.replace("-", " ").title())
                logger.info(f"playwright_scrape: {sec_subject} {mt_label} ({level})")

                try:
                    async for m in _playwright_scrape_one(
                        page=page,
                        subject=subject,
                        sec_subject=sec_subject,
                        years=years,
                        level_value=level_value,
                        mt_key=mt_key,
                        mt_label=mt_label,
                        language=language,
                    ):
                        yield m
                except Exception as e:
                    logger.error(f"playwright_scrape_failed: {subject}: {e}")
                    yield ExamMaterial(
                        subject=subject,
                        year=0,
                        level=level,
                        material_type=_material_type_from_key(mt_key),
                        pdf_url="",
                        title=f"Error: {e}",
                        content_hash="error",
                    )

                await asyncio.sleep(RATE_LIMIT_SECONDS * 2)

    finally:
        await pw.stop()


async def _playwright_scrape_one(
    page: Any,
    subject: str,
    sec_subject: str,
    years: list[int],
    level_value: str,
    mt_key: str,
    mt_label: str,
    language: str,
) -> AsyncIterator[ExamMaterial]:
    """Scrape one subject/material_type using Playwright with ASP.NET progressive disclosure.

    The examinations.ie site uses ASP.NET postback-style progressive disclosure:
    1. Check terms checkbox → reveals ViewType dropdown
    2. Select ViewType (Exam Papers) → reveals YearSelect dropdown
    3. Select Year (e.g. 2024) → reveals ExaminationSelect dropdown
    4. Select Examination (Leaving Certificate) → reveals SubjectSelect dropdown
    5. Select Subject (Mathematics) → shows results after View button click

    NOTE: The method also extracts obfuscated ?fp= URLs used by the SEC for PDF downloads.
    """
    await page.goto(EXAM_ARCHIVE_URL, wait_until="domcontentloaded", timeout=30000)
    await asyncio.sleep(2)

    # 1. Check the terms checkbox (triggers ASP.NET postback to reveal dropdowns)
    cb = await page.query_selector("#MaterialArchive__noTable__cbv__AgreeCheck")
    if cb:
        try:
            is_checked = await cb.is_checked()
        except Exception:
            is_checked = False
        if not is_checked:
            await cb.click()
            # Wait for ASP.NET postback to render the ViewType dropdown
            try:
                await page.wait_for_selector(
                    "#MaterialArchive__noTable__sbv__ViewType", state="visible", timeout=10000,
                )
            except Exception:
                await asyncio.sleep(5)

    # 2. Select material type (ViewType) — triggers YearSelect dropdown
    type_select = await page.query_selector("#MaterialArchive__noTable__sbv__ViewType")
    if not type_select:
        logger.error(f"type_dropdown_not_found for {sec_subject}")
        return
    await type_select.select_option(label=mt_label)
    try:
        await page.wait_for_selector(
            "#MaterialArchive__noTable__sbv__YearSelect", state="visible", timeout=10000,
        )
    except Exception:
        await asyncio.sleep(5)

    # 3. Select year — reveals ExaminationSelect dropdown
    for year in years:
        logger.info(f"playwright_scrape: {sec_subject} {mt_label} {year}")

        year_select = await page.query_selector("#MaterialArchive__noTable__sbv__YearSelect")
        if not year_select:
            year_select = await page.query_selector("select[id*='Year']")
        if not year_select:
            logger.error(f"year_dropdown_not_found for {sec_subject}")
            return

        year_value = None
        for opt in await year_select.query_selector_all("option"):
            text = (await opt.inner_text()).strip()
            if str(year) == text:
                year_value = await opt.get_attribute("value")
                break
        if not year_value:
            logger.error(f"year_option_not_found: {year} for {sec_subject}")
            continue
        await year_select.select_option(value=year_value)
        try:
            await page.wait_for_selector(
                "#MaterialArchive__noTable__sbv__ExaminationSelect",
                state="visible", timeout=10000,
            )
        except Exception:
            await asyncio.sleep(5)

        # 4. Select examination level — reveals SubjectSelect dropdown
        exam_select = await page.query_selector("#MaterialArchive__noTable__sbv__ExaminationSelect")
        if not exam_select:
            exam_select = await page.query_selector("select[id*='Examination']")
        if not exam_select:
            logger.error(f"examination_dropdown_not_found for {sec_subject}")
            continue

        exam_value = None
        for opt in await exam_select.query_selector_all("option"):
            text = (await opt.inner_text()).strip()
            # Exact match to avoid "Leaving Certificate Applied" matching "Leaving Certificate"
            if text == level_value or (level_value.lower() == "leaving certificate" and text == level_value):
                exam_value = await opt.get_attribute("value")
                break
        if not exam_value:
            # Fallback: case-insensitive partial match (but prefer exact)
            for opt in await exam_select.query_selector_all("option"):
                text = (await opt.inner_text()).strip()
                if level_value.lower() in text.lower() and "applied" not in text.lower():
                    exam_value = await opt.get_attribute("value")
                    break
        if not exam_value:
            logger.error(f"level_option_not_found: {level_value} for {sec_subject}")
            continue
        await exam_select.select_option(value=exam_value)
        try:
            await page.wait_for_selector(
                "#MaterialArchive__noTable__sbv__SubjectSelect",
                state="visible", timeout=10000,
            )
        except Exception:
            await asyncio.sleep(5)

        # 5. Select subject
        subject_select = await page.query_selector("#MaterialArchive__noTable__sbv__SubjectSelect")
        if not subject_select:
            subject_select = await page.query_selector("select[id*='Subject']")
        if not subject_select:
            logger.error(f"subject_dropdown_not_found for {sec_subject}")
            continue

        subject_value = None
        for opt in await subject_select.query_selector_all("option"):
            text = (await opt.inner_text()).strip()
            if sec_subject.lower() in text.lower() or subject.lower().replace("-", " ") in text.lower():
                subject_value = await opt.get_attribute("value")
                break
        if not subject_value:
            logger.error(f"subject_option_not_found: {sec_subject}")
            continue
        await subject_select.select_option(value=subject_value)
        await asyncio.sleep(2)

        # 6. Click View/Submit button
        view_btn = await page.query_selector(
            "#MaterialArchive__noTable__btnView, "
            "input[type='submit'][value*='View'], "
            "input[type='submit'][value*='Search'], "
            "input[type='submit'][value*='Submit']"
        )
        if view_btn:
            await view_btn.click()
            try:
                await page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass
            await asyncio.sleep(3)

        # 7. Extract PDF links — SEC uses obfuscated ?fp= URLs
        # e.g. https://www.examinations.ie?fp=92.109.94.99.100.113...
        # Also handles direct .pdf links and /qvp/ paths.
        pdf_data = await page.evaluate("""() => {
            const results = [];
            const allLinks = document.querySelectorAll('a[href]');
            for (const a of allLinks) {
                const href = a.getAttribute('href') || '';
                const text = a.textContent.trim();
                if (href.includes('?fp=') || href.toLowerCase().includes('.pdf') ||
                    href.toLowerCase().includes('exampapers') || href.toLowerCase().includes('qvp')) {
                    results.push({url: href, title: text});
                }
            }
            return results;
        }""")

        pdf_links_found = 0
        for item in pdf_data:
            href = item.get("url", "")
            text = item.get("title", "")
            if not href:
                continue
            if not href.startswith("http"):
                href = urljoin(EXAMINATIONS_BASE_URL, href)

            material_type = _classify_material_type(href, text)

            yield ExamMaterial(
                subject=subject,
                year=year,
                level=level_value.lower().replace(" ", "_"),
                material_type=material_type,
                pdf_url=href,
                title=text or None,
                paper_number=_extract_paper_number(href, text),
                exam_level=_extract_exam_level(href, text),
                language=language,
                content_hash=hashlib.sha256(href.encode()).hexdigest()[:16],
            )
            pdf_links_found += 1

        if pdf_links_found == 0:
            logger.info(f"no_pdf_links: {sec_subject} {year} {mt_key}")
        else:
            logger.info(f"found_pdfs: {sec_subject} {year} {mt_key} count={pdf_links_found}")

        await asyncio.sleep(RATE_LIMIT_SECONDS)

    await page.goto("about:blank")


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


def scrape_materials_batch_sync(
    subjects: list[str],
    years: list[int] | None = None,
    level: str = "leaving_certificate",
    language: str = "en",
    material_types: list[str] | None = None,
) -> list[ExamMaterial]:
    """Synchronous wrapper for scrape_materials_batch (session-reused batch)."""

    async def _collect():
        materials = []
        async for m in scrape_materials_batch(subjects, years, level, language, material_types):
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


def scrape_materials_playwright_sync(
    subjects: list[str],
    years: list[int] | None = None,
    level: str = "leaving_certificate",
    language: str = "en",
    material_types: list[str] | None = None,
    cdp_url: str | None = None,
) -> list[ExamMaterial]:
    """Synchronous wrapper for scrape_materials_playwright.

    Uses Playwright directly (no LLM calls) to scrape exam materials.
    Preferred over Stagehand when CDP connection is available.
    """

    async def _collect():
        materials = []
        async for m in scrape_materials_playwright(
            subjects, years, level, language, material_types, cdp_url,
        ):
            materials.append(m)
        return materials

    return asyncio.run(_collect())
