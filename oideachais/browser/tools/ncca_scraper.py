"""NCCA Curriculum scraper for curriculumonline.ie.

Extracts curriculum specifications, learning outcomes, and resources
from the National Council for Curriculum and Assessment website.

Features:
- Bilingual content extraction (English and Irish)
- PDF specification download
- Learning outcome structured extraction
- Subject hierarchy navigation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import structlog
from sruth.browser.tools.base_scraper import (
    BaseDomainScraper,
    MediaType,
    StorageResult,
)

logger = structlog.get_logger()


class EducationLevel(str, Enum):
    """Irish education cycle levels."""

    PRIMARY = "primary"
    JUNIOR_CYCLE = "junior-cycle"
    SENIOR_CYCLE = "senior-cycle"
    TRANSITION_YEAR = "transition-year"


@dataclass
class LearningOutcome:
    """Structured learning outcome from curriculum."""

    code: str  # e.g., "JC-M-1.1"
    strand: str
    strand_unit: str
    description: str
    description_ga: str | None = None  # Irish translation
    examples: list[str] = field(default_factory=list)
    cross_curricular_links: list[str] = field(default_factory=list)


@dataclass
class CurriculumResource:
    """Resource linked from curriculum page."""

    title: str
    url: str
    resource_type: str  # pdf, video, interactive, link
    language: str  # en, ga
    description: str | None = None


@dataclass
class NCCASubject:
    """NCCA curriculum subject data."""

    subject: str
    subject_ga: str | None
    level: EducationLevel
    language: str  # en or ga
    url: str
    specification_pdf_url: str | None = None
    strands: list[dict[str, Any]] = field(default_factory=list)
    learning_outcomes: list[LearningOutcome] = field(default_factory=list)
    resources: list[CurriculumResource] = field(default_factory=list)
    assessment_info: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class NCCAScraper(BaseDomainScraper):
    """Scraper for NCCA curriculum website (curriculumonline.ie).

    Extracts:
    - Subject specifications (PDF)
    - Learning outcomes per strand/unit
    - Cross-curricular links
    - Assessment information
    - Teacher resources

    Supports both English and Irish language versions.
    """

    domain = "curriculumonline.ie"
    rate_limit_seconds = 1.5  # Be respectful to government sites
    requires_javascript = True

    # Base URLs
    BASE_URL_EN = "https://curriculumonline.ie/en"
    BASE_URL_GA = "https://curriculumonline.ie/ga"

    # Subject URL patterns
    SUBJECT_PATTERNS = {
        EducationLevel.JUNIOR_CYCLE: "{base}/junior-cycle/{subject}/",
        EducationLevel.SENIOR_CYCLE: "{base}/senior-cycle/{subject}/",
        EducationLevel.PRIMARY: "{base}/primary/{subject}/",
    }

    def get_extraction_schema(self) -> dict[str, Any]:
        """Get BAML/JSON schema for NCCA curriculum extraction."""
        return {
            "type": "object",
            "properties": {
                "subject": {"type": "string", "description": "Subject name"},
                "subject_ga": {
                    "type": "string",
                    "description": "Subject name in Irish",
                    "nullable": True,
                },
                "level": {
                    "type": "string",
                    "enum": ["primary", "junior-cycle", "senior-cycle"],
                },
                "specification_pdf_url": {
                    "type": "string",
                    "format": "uri",
                    "description": "URL to specification PDF",
                    "nullable": True,
                },
                "strands": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "name_ga": {"type": "string", "nullable": True},
                            "description": {"type": "string"},
                            "strand_units": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "learning_outcome_codes": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                "learning_outcomes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "strand": {"type": "string"},
                            "strand_unit": {"type": "string"},
                            "description": {"type": "string"},
                            "description_ga": {"type": "string", "nullable": True},
                        },
                    },
                },
                "resources": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "url": {"type": "string", "format": "uri"},
                            "resource_type": {"type": "string"},
                            "language": {"type": "string"},
                        },
                    },
                },
            },
            "required": ["subject", "level"],
        }

    async def scrape(
        self,
        url: str,
        *,
        download_pdf: bool = True,
        extract_learning_outcomes: bool = True,
        language: str = "en",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Scrape NCCA curriculum page.

        Args:
            url: URL of the curriculum page.
            download_pdf: Whether to download specification PDF.
            extract_learning_outcomes: Whether to extract detailed LOs.
            language: Language version ('en' or 'ga').
            **kwargs: Additional parameters.

        Returns:
            Scraped curriculum data as dictionary.
        """
        logger.info("ncca_scrape_start", url=url, language=language)

        # Navigate to page
        nav_result = await self.navigate_to(url, handle_cookies=True)
        if not nav_result.success:
            return {"success": False, "error": nav_result.error, "url": url}

        # Extract main curriculum content
        curriculum_data = await self._extract_curriculum_content(language)

        # Extract specification PDF link if available
        if download_pdf:
            pdf_result = await self._extract_and_download_pdf()
            if pdf_result.success:
                curriculum_data["specification_pdf"] = {
                    "url": pdf_result.source_url,
                    "s3_key": pdf_result.s3_key,
                    "size_bytes": pdf_result.size_bytes,
                    "hash": pdf_result.content_hash,
                }

        # Extract detailed learning outcomes
        if extract_learning_outcomes:
            learning_outcomes = await self._extract_learning_outcomes()
            curriculum_data["learning_outcomes"] = learning_outcomes

        # Extract resources
        resources = await self._extract_resources()
        curriculum_data["resources"] = resources

        logger.info(
            "ncca_scrape_complete",
            url=url,
            subject=curriculum_data.get("subject"),
            outcomes_count=len(curriculum_data.get("learning_outcomes", [])),
            resources_count=len(resources),
        )

        return {
            "success": True,
            "url": url,
            "language": language,
            "data": curriculum_data,
        }

    async def _extract_curriculum_content(self, language: str) -> dict[str, Any]:
        """Extract main curriculum content from current page."""
        instruction = """
        Extract the curriculum information from this page:
        - Subject name (in both English and Irish if available)
        - Education level (primary, junior-cycle, or senior-cycle)
        - Strands and strand units
        - Any assessment information
        - Rationale and aims if present
        """

        result = await self.extract_page(instruction, self.get_extraction_schema())

        if result.success and result.content:
            return result.content.get("extracted", result.content)

        return {}

    async def _extract_and_download_pdf(self) -> StorageResult:
        """Find and download curriculum specification PDF."""
        # Look for PDF download link
        elements = await self.backend.observe(
            "Find the curriculum specification PDF download link or button"
        )

        if not elements:
            return StorageResult(
                success=False,
                media_type=MediaType.PDF,
                source_url="",
                error="No PDF link found",
            )

        # Extract the PDF URL
        extraction = await self.extract_page(
            "Extract the URL of the curriculum specification PDF",
            {
                "type": "object",
                "properties": {
                    "pdf_url": {"type": "string", "format": "uri"},
                },
            },
        )

        if extraction.success and extraction.content:
            pdf_url = extraction.content.get("pdf_url") or extraction.content.get(
                "extracted", {}
            ).get("pdf_url")
            if pdf_url:
                return await self.download_media(
                    pdf_url,
                    MediaType.PDF,
                    bucket="sruth-curriculum",
                    prefix="ncca/specifications",
                )

        return StorageResult(
            success=False,
            media_type=MediaType.PDF,
            source_url="",
            error="Could not extract PDF URL",
        )

    async def _extract_learning_outcomes(self) -> list[dict[str, Any]]:
        """Extract structured learning outcomes."""
        instruction = """
        Extract all learning outcomes from this curriculum page.
        For each learning outcome, extract:
        - The outcome code (e.g., JC-M-1.1)
        - The strand it belongs to
        - The strand unit
        - The full description
        - The Irish translation if available
        - Any examples provided
        """

        result = await self.extract_page(
            instruction,
            {
                "type": "object",
                "properties": {
                    "learning_outcomes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "code": {"type": "string"},
                                "strand": {"type": "string"},
                                "strand_unit": {"type": "string"},
                                "description": {"type": "string"},
                                "description_ga": {"type": "string", "nullable": True},
                                "examples": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                        },
                    },
                },
            },
        )

        if result.success and result.content:
            content = result.content.get("extracted", result.content)
            return content.get("learning_outcomes", [])

        return []

    async def _extract_resources(self) -> list[dict[str, Any]]:
        """Extract linked resources from curriculum page."""
        instruction = """
        Extract all resources and links from this curriculum page.
        For each resource, extract:
        - Title
        - URL
        - Type (pdf, video, interactive, link)
        - Language (en or ga)
        - Description if available
        """

        result = await self.extract_page(
            instruction,
            {
                "type": "object",
                "properties": {
                    "resources": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "url": {"type": "string"},
                                "resource_type": {"type": "string"},
                                "language": {"type": "string"},
                                "description": {"type": "string", "nullable": True},
                            },
                        },
                    },
                },
            },
        )

        if result.success and result.content:
            content = result.content.get("extracted", result.content)
            return content.get("resources", [])

        return []

    async def scrape_subject_list(
        self,
        level: EducationLevel,
        language: str = "en",
    ) -> list[dict[str, str]]:
        """Scrape list of subjects for a given education level.

        Args:
            level: Education level (junior-cycle, senior-cycle, primary).
            language: Language version ('en' or 'ga').

        Returns:
            List of subjects with name and URL.
        """
        base_url = self.BASE_URL_EN if language == "en" else self.BASE_URL_GA

        if level == EducationLevel.JUNIOR_CYCLE:
            url = f"{base_url}/junior-cycle/"
        elif level == EducationLevel.SENIOR_CYCLE:
            url = f"{base_url}/senior-cycle/"
        else:
            url = f"{base_url}/primary/"

        nav_result = await self.navigate_to(url, handle_cookies=True)
        if not nav_result.success:
            return []

        instruction = """
        Extract all subject names and their URLs from the subjects listing.
        For each subject, get the English name, Irish name if shown, and the link URL.
        """

        result = await self.extract_page(
            instruction,
            {
                "type": "object",
                "properties": {
                    "subjects": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "name_ga": {"type": "string", "nullable": True},
                                "url": {"type": "string"},
                            },
                        },
                    },
                },
            },
        )

        if result.success and result.content:
            content = result.content.get("extracted", result.content)
            return content.get("subjects", [])

        return []
