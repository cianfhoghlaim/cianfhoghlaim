"""
Source Adapters - Normalize output from different curriculum sources.

Provides adapters that:
- Handle source-specific URL patterns
- Normalize crawled page data to consistent format
- Extract metadata (cycle, subject) from URLs
- Support bilingual content (English/Irish)

Usage:
    from oideachais.dlt_sources.common.source_adapters import (
        CurriculumOnlineAdapter,
        NCCAAdapter,
        ExaminationsAdapter,
        NormalizedPage,
    )

    adapter = CurriculumOnlineAdapter()
    page = adapter.normalize_page(raw_firecrawl_result)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol
from urllib.parse import parse_qs, urlparse

import structlog
from dlt_sources.common.incremental import compute_content_hash

logger = structlog.get_logger(__name__)


@dataclass
class NormalizedPage:
    """
    Normalized page data from any curriculum source.

    Provides a consistent interface regardless of which source
    (curriculumonline, ncca, examinations) the page came from.
    """

    url: str
    title: str | None
    content: str  # Markdown content
    content_hash: str
    language: str
    cycle: str | None
    subject: str | None
    source: str
    crawled_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for DLT resource output."""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "content_hash": self.content_hash,
            "language": self.language,
            "cycle": self.cycle,
            "subject": self.subject,
            "source": self.source,
            "crawled_at": self.crawled_at.isoformat(),
            "metadata": self.metadata,
        }


class SourceAdapter(Protocol):
    """Protocol for curriculum source adapters."""

    name: str

    def get_base_url(self, language: str) -> str:
        """Get the base URL for the source in the given language."""
        ...

    def get_include_paths(self, cycle: str, subject: str | None, language: str) -> list[str]:
        """Get Firecrawl include paths for crawling."""
        ...

    def normalize_page(
        self,
        raw_page: dict[str, Any],
        cycle: str | None = None,
        subject: str | None = None,
        language: str = "en",
    ) -> NormalizedPage:
        """Normalize a raw Firecrawl page result."""
        ...

    def extract_cycle_from_url(self, url: str) -> str | None:
        """Extract the education cycle from a URL."""
        ...

    def extract_subject_from_url(self, url: str) -> str | None:
        """Extract the subject from a URL."""
        ...


class CurriculumOnlineAdapter:
    """
    Adapter for curriculumonline.ie.

    URL patterns:
    - English: /junior-cycle/junior-cycle-subjects/mathematics/
    - Irish: /ga-ie/junior-cycle/junior-cycle-subjects/matamaitic/
    """

    name = "curriculumonline"

    # Cycle path mappings
    CYCLE_PATHS = {
        "early-childhood": "early_childhood",
        "primary": "primary",
        "junior-cycle": "junior_cycle",
        "senior-cycle": "senior_cycle",
    }

    # Reverse mapping for URL generation
    CYCLE_TO_PATH = {v: k for k, v in CYCLE_PATHS.items()}

    def get_base_url(self, language: str) -> str:
        """Get base URL for curriculumonline.ie."""
        return "https://www.curriculumonline.ie"

    def get_include_paths(
        self,
        cycle: str,
        subject: str | None,
        language: str,
    ) -> list[str]:
        """Get include paths for Firecrawl."""
        lang_prefix = "/ga-ie" if language == "ga" else ""
        cycle_path = self.CYCLE_TO_PATH.get(cycle, cycle)

        if subject:
            return [f"{lang_prefix}/{cycle_path}/*{subject}*"]
        return [f"{lang_prefix}/{cycle_path}/*"]

    def normalize_page(
        self,
        raw_page: dict[str, Any],
        cycle: str | None = None,
        subject: str | None = None,
        language: str = "en",
    ) -> NormalizedPage:
        """Normalize a raw Firecrawl page result."""
        metadata = raw_page.get("metadata", {})
        url = metadata.get("sourceURL", raw_page.get("url", ""))
        content = raw_page.get("markdown", "")

        # Extract cycle and subject from URL if not provided
        detected_cycle = cycle or self.extract_cycle_from_url(url)
        detected_subject = subject or self.extract_subject_from_url(url)
        detected_language = self._detect_language_from_url(url) or language

        # Compute content hash
        content_hash = compute_content_hash(content) if content else ""

        links = raw_page.get("links", [])
        if not links and content:
            import re
            md_links = [match.split(" ")[0] for match in re.findall(r"\]\((http[^\)]+)\)", content)]
            links.extend(md_links)
        if links and "links" not in metadata:
            metadata["links"] = list(set(links))

        return NormalizedPage(
            url=url,
            title=metadata.get("title"),
            content=content,
            content_hash=content_hash,
            language=detected_language,
            cycle=detected_cycle,
            subject=detected_subject,
            source=self.name,
            crawled_at=datetime.now(UTC),
            metadata={
                "description": metadata.get("description"),
                "links": raw_page.get("links", []),
            },
        )

    def extract_cycle_from_url(self, url: str) -> str | None:
        """Extract cycle from curriculumonline.ie URL."""
        parsed = urlparse(url)
        path = parsed.path.lower()

        # Remove /ga-ie prefix if present
        if path.startswith("/ga-ie"):
            path = path[6:]

        # Match cycle patterns
        for url_cycle, normalized_cycle in self.CYCLE_PATHS.items():
            if f"/{url_cycle}/" in path or path.startswith(f"/{url_cycle}"):
                return normalized_cycle

        return None

    def extract_subject_from_url(self, url: str) -> str | None:
        """Extract subject from curriculumonline.ie URL."""
        parsed = urlparse(url)
        path = parsed.path.lower()

        # Pattern: /junior-cycle/junior-cycle-subjects/mathematics/
        # or: /senior-cycle/senior-cycle-subjects/physics/
        subjects_match = re.search(
            r"/(?:junior-cycle|senior-cycle)-subjects/([^/]+)",
            path,
        )
        if subjects_match:
            return subjects_match.group(1).replace("-", "_")

        # Pattern: /short-courses/coding/
        short_course_match = re.search(r"/short-courses/([^/]+)", path)
        if short_course_match:
            return short_course_match.group(1).replace("-", "_")

        return None

    def _detect_language_from_url(self, url: str) -> str | None:
        """Detect language from URL prefix."""
        parsed = urlparse(url)
        if parsed.path.startswith("/ga-ie"):
            return "ga"
        return "en"


class NCCAAdapter:
    """
    Adapter for ncca.ie.

    URL patterns:
    - English: /en/junior-cycle/subjects-and-short-courses/mathematics/
    - Irish: /ga/an-tsraith-shoisearach/abhar-agus-gearrchursa/matamaitic/
    """

    name = "ncca"

    # Cycle path mappings (English)
    CYCLE_PATHS_EN = {
        "early-childhood": "early_childhood",
        "primary": "primary",
        "junior-cycle": "junior_cycle",
        "senior-cycle": "senior_cycle",
    }

    # Cycle path mappings (Irish)
    CYCLE_PATHS_GA = {
        "an-luath-oige": "early_childhood",
        "bunscoil": "primary",
        "an-tsraith-shoisearach": "junior_cycle",
        "an-tsraith-shinsearach": "senior_cycle",
    }

    # Reverse mapping
    CYCLE_TO_PATH_EN = {v: k for k, v in CYCLE_PATHS_EN.items()}
    CYCLE_TO_PATH_GA = {
        "early_childhood": "an-luath-oige",
        "primary": "bunscoil",
        "junior_cycle": "an-tsraith-shoisearach",
        "senior_cycle": "an-tsraith-shinsearach",
    }

    def get_base_url(self, language: str) -> str:
        """Get base URL for ncca.ie."""
        return "https://ncca.ie"

    def get_include_paths(
        self,
        cycle: str,
        subject: str | None,
        language: str,
    ) -> list[str]:
        """Get include paths for Firecrawl."""
        lang_prefix = "/ga" if language == "ga" else "/en"

        if language == "ga":
            cycle_path = self.CYCLE_TO_PATH_GA.get(cycle, cycle)
        else:
            cycle_path = self.CYCLE_TO_PATH_EN.get(cycle, cycle)

        if subject:
            return [f"{lang_prefix}/{cycle_path}/*{subject}*"]
        return [f"{lang_prefix}/{cycle_path}/*"]

    def normalize_page(
        self,
        raw_page: dict[str, Any],
        cycle: str | None = None,
        subject: str | None = None,
        language: str = "en",
    ) -> NormalizedPage:
        """Normalize a raw Firecrawl page result."""
        metadata = raw_page.get("metadata", {})
        url = metadata.get("sourceURL", raw_page.get("url", ""))
        content = raw_page.get("markdown", "")

        # Extract cycle and subject from URL if not provided
        detected_cycle = cycle or self.extract_cycle_from_url(url)
        detected_subject = subject or self.extract_subject_from_url(url)
        detected_language = self._detect_language_from_url(url) or language

        content_hash = compute_content_hash(content) if content else ""

        links = raw_page.get("links", [])
        if not links and content:
            import re
            md_links = [match.split(" ")[0] for match in re.findall(r"\]\((http[^\)]+)\)", content)]
            links.extend(md_links)
        if links and "links" not in metadata:
            metadata["links"] = list(set(links))

        return NormalizedPage(
            url=url,
            title=metadata.get("title"),
            content=content,
            content_hash=content_hash,
            language=detected_language,
            cycle=detected_cycle,
            subject=detected_subject,
            source=self.name,
            crawled_at=datetime.now(UTC),
            metadata={
                "description": metadata.get("description"),
                "links": raw_page.get("links", []),
            },
        )

    def extract_cycle_from_url(self, url: str) -> str | None:
        """Extract cycle from ncca.ie URL."""
        parsed = urlparse(url)
        path = parsed.path.lower()

        # Check English paths
        if path.startswith("/en"):
            for url_cycle, normalized_cycle in self.CYCLE_PATHS_EN.items():
                if f"/{url_cycle}/" in path or f"/{url_cycle}" == path[3:]:
                    return normalized_cycle

        # Check Irish paths
        elif path.startswith("/ga"):
            for url_cycle, normalized_cycle in self.CYCLE_PATHS_GA.items():
                if f"/{url_cycle}/" in path or f"/{url_cycle}" == path[3:]:
                    return normalized_cycle

        return None

    def extract_subject_from_url(self, url: str) -> str | None:
        """Extract subject from ncca.ie URL."""
        parsed = urlparse(url)
        path = parsed.path.lower()

        # Pattern: /en/senior-cycle/curriculum-developments/mathematics/
        curriculum_match = re.search(
            r"/curriculum-developments/([^/]+)",
            path,
        )
        if curriculum_match:
            return curriculum_match.group(1).replace("-", "_")

        # Pattern: /en/junior-cycle/subjects-and-short-courses/mathematics/
        subjects_match = re.search(
            r"/subjects-and-short-courses/([^/]+)",
            path,
        )
        if subjects_match:
            return subjects_match.group(1).replace("-", "_")

        return None

    def _detect_language_from_url(self, url: str) -> str | None:
        """Detect language from URL prefix."""
        parsed = urlparse(url)
        if parsed.path.startswith("/ga"):
            return "ga"
        elif parsed.path.startswith("/en"):
            return "en"
        return None


class ExaminationsAdapter:
    """
    Adapter for examinations.ie.

    URL patterns:
    - English: /?l=en&mc=ex&sc=eb
    - Irish: /?l=ir&mc=ex&sc=eb
    - Archive: /exammaterialarchive/
    """

    name = "examinations"

    # Content type path mappings
    CONTENT_TYPE_PATHS = {
        "examiner_reports": "/archive/examiners_reports/",
        "exam_materials": "/exammaterialarchive/",
        "statistics": "/statistics/",
        "circulars": "/schools/circulars/",
    }

    def get_base_url(self, language: str) -> str:
        """Get base URL for examinations.ie."""
        return "https://www.examinations.ie"

    def get_include_paths(
        self,
        cycle: str,
        subject: str | None,
        language: str,
    ) -> list[str]:
        """Get include paths for Firecrawl."""
        # Examinations.ie doesn't use cycle/subject in paths
        # All exam materials are in the archive
        paths = [
            "/exammaterialarchive/*",
            "/archive/examiners_reports/*",
        ]

        if subject:
            # Add subject-specific filter
            paths = [f"{p}*{subject}*" for p in paths]

        return paths

    def normalize_page(
        self,
        raw_page: dict[str, Any],
        cycle: str | None = None,
        subject: str | None = None,
        language: str = "en",
    ) -> NormalizedPage:
        """Normalize a raw Firecrawl page result."""
        metadata = raw_page.get("metadata", {})
        url = metadata.get("sourceURL", raw_page.get("url", ""))
        content = raw_page.get("markdown", "")

        # Extract subject and year from URL if not provided
        detected_subject = subject or self.extract_subject_from_url(url)
        detected_language = self._detect_language_from_url(url) or language
        detected_year = self._extract_year_from_url(url)

        content_hash = compute_content_hash(content) if content else ""

        links = raw_page.get("links", [])
        if not links and content:
            import re
            md_links = [match.split(" ")[0] for match in re.findall(r"\]\((http[^\)]+)\)", content)]
            links.extend(md_links)
        if links and "links" not in metadata:
            metadata["links"] = list(set(links))

        return NormalizedPage(
            url=url,
            title=metadata.get("title"),
            content=content,
            content_hash=content_hash,
            language=detected_language,
            cycle=cycle,  # SEC covers both Junior Cycle and Leaving Cert
            subject=detected_subject,
            source=self.name,
            crawled_at=datetime.now(UTC),
            metadata={
                "description": metadata.get("description"),
                "links": raw_page.get("links", []),
                "year": detected_year,
                "content_type": self._detect_content_type(url),
            },
        )

    def extract_cycle_from_url(self, url: str) -> str | None:
        """Extract cycle from examinations.ie URL."""
        url_lower = url.lower()

        # Check for Junior Cycle / Junior Certificate
        if "junior" in url_lower or "jc_" in url_lower:
            return "junior_cycle"

        # Check for Leaving Certificate
        if "leaving" in url_lower or "lc_" in url_lower:
            return "senior_cycle"

        return None

    def extract_subject_from_url(self, url: str) -> str | None:
        """Extract subject from examinations.ie URL."""
        # Pattern: /archive/examiners_reports/cer_2023/LC_English.pdf
        pdf_match = re.search(r"/(?:LC|JC)_([A-Za-z_]+)\.pdf", url)
        if pdf_match:
            return pdf_match.group(1).lower().replace("_", " ")

        # Pattern in archive paths
        archive_match = re.search(r"/([A-Za-z_]+)(?:_\d+)?\.pdf", url)
        if archive_match:
            subject = archive_match.group(1).lower()
            # Filter out non-subject matches
            if subject not in ("index", "readme", "info"):
                return subject

        return None

    def _detect_language_from_url(self, url: str) -> str | None:
        """Detect language from URL query parameter."""
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        lang = params.get("l", [""])[0]
        if lang == "ir":
            return "ga"
        elif lang == "en":
            return "en"

        return None

    def _extract_year_from_url(self, url: str) -> int | None:
        """Extract year from URL."""
        # Pattern: cer_2023 or _2023 or /2023/
        year_match = re.search(r"(?:cer_|_|/)(\d{4})(?:/|\.|\b)", url)
        if year_match:
            try:
                return int(year_match.group(1))
            except ValueError:
                pass
        return None

    def _detect_content_type(self, url: str) -> str | None:
        """Detect content type from URL."""
        url_lower = url.lower()

        if "examiners_reports" in url_lower or "examiner" in url_lower:
            return "examiner_report"
        elif "marking_scheme" in url_lower or "marking" in url_lower:
            return "marking_scheme"
        elif "statistics" in url_lower:
            return "statistics"
        elif "circular" in url_lower:
            return "circular"
        elif ".pdf" in url_lower:
            return "exam_paper"

        return None


def get_adapter(source_name: str) -> SourceAdapter:
    """
    Get the appropriate adapter for a source.

    Args:
        source_name: Name of the source (curriculumonline, ncca, examinations)

    Returns:
        SourceAdapter instance

    Raises:
        ValueError: If source_name is not recognized
    """
    adapters: dict[str, SourceAdapter] = {
        "curriculumonline": CurriculumOnlineAdapter(),
        "ncca": NCCAAdapter(),
        "examinations": ExaminationsAdapter(),
    }

    adapter = adapters.get(source_name)
    if not adapter:
        raise ValueError(f"Unknown source: {source_name}. Valid sources: {list(adapters.keys())}")

    return adapter


def get_all_adapters() -> dict[str, SourceAdapter]:
    """Get all available source adapters."""
    return {
        "curriculumonline": CurriculumOnlineAdapter(),
        "ncca": NCCAAdapter(),
        "examinations": ExaminationsAdapter(),
    }
