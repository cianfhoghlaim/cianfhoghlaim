"""
Curriculum Registry - Subject taxonomy and URL resolution from curriculum_index.json.

Provides a centralized registry for:
- Subject configuration and metadata
- Cycle-based subject filtering
- Source-specific URL resolution
- Crawl configuration generation

Usage:
    from sruth.oideachais.dlt_sources.ireland.curriculum_registry import (
        SubjectRegistry,
        URLResolver,
    )

    registry = SubjectRegistry.from_default()
    resolver = URLResolver(registry)

    # Get all subjects for a cycle
    subjects = registry.get_subjects_for_cycle("junior_cycle")

    # Get crawl config for a specific subject
    configs = resolver.resolve_urls("junior_cycle", "mathematics", "en")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# Default path to curriculum_index.json
DEFAULT_INDEX_PATH = Path(__file__).parent.parent.parent / "firecrawl_configs" / "oideachas" / "curriculum_index.json"


@dataclass
class SourceConfig:
    """Configuration for a curriculum source (curriculumonline, ncca, examinations)."""

    name: str
    base_url: str
    language_prefixes: dict[str, str]  # {"en": "", "ga": "/ga-ie"}

    def get_full_url(self, path: str, language: str = "en") -> str:
        """Get full URL for a path in the given language."""
        prefix = self.language_prefixes.get(language, "")
        # Handle query parameter style (examinations.ie)
        if prefix.startswith("?"):
            return f"{self.base_url}{path}{prefix}"
        return f"{self.base_url}{prefix}{path}"


@dataclass
class SubjectConfig:
    """Configuration for a curriculum subject."""

    slug: str
    name: dict[str, str]  # {"en": "Mathematics", "ga": "Matamaitic"}
    cycles: list[str]  # ["junior_cycle", "senior_cycle"]
    specification_type: str  # "specification" or "syllabus"
    development_status: str  # "current", "redevelopment_tranche_1", etc.
    urls: dict[str, str] = field(default_factory=dict)  # source -> path
    levels: list[str] | None = None  # ["Foundation", "Ordinary", "Higher"]
    coursework_percentage: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SubjectConfig:
        """Create SubjectConfig from dictionary."""
        return cls(
            slug=data["slug"],
            name=data["name"],
            cycles=data.get("cycles", []),
            specification_type=data.get("specification_type", "specification"),
            development_status=data.get("development_status", "current"),
            urls=data.get("urls", {}),
            levels=data.get("levels"),
            coursework_percentage=data.get("coursework_percentage"),
        )

    def is_in_cycle(self, cycle: str) -> bool:
        """Check if subject is available in a specific cycle."""
        return cycle in self.cycles

    def get_url_for_source(self, source: str) -> str | None:
        """Get URL path for a specific source."""
        return self.urls.get(source)

    def get_available_sources(self) -> list[str]:
        """Get list of sources that have URLs for this subject."""
        return list(self.urls.keys())


@dataclass
class ShortCourseConfig:
    """Configuration for a short course."""

    slug: str
    name: dict[str, str]
    cycle: str
    urls: dict[str, str] = field(default_factory=dict)
    specification_versions: list[str] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ShortCourseConfig:
        """Create ShortCourseConfig from dictionary."""
        return cls(
            slug=data["slug"],
            name=data["name"],
            cycle=data.get("cycle", "junior_cycle"),
            urls=data.get("urls", {}),
            specification_versions=data.get("specification_versions"),
        )


@dataclass
class CycleConfig:
    """Configuration for an education cycle."""

    slug: str
    name: dict[str, str]
    age_range: str
    framework: str | None = None
    stages: int | None = None
    years: int | str | None = None
    programmes: list[str] | None = None

    @classmethod
    def from_dict(cls, slug: str, data: dict[str, Any]) -> CycleConfig:
        """Create CycleConfig from dictionary."""
        return cls(
            slug=slug,
            name=data["name"],
            age_range=data.get("age_range", ""),
            framework=data.get("framework"),
            stages=data.get("stages"),
            years=data.get("years"),
            programmes=data.get("programmes"),
        )


@dataclass
class CrawlConfig:
    """Configuration for crawling a source for a subject."""

    source: str
    base_url: str
    include_paths: list[str]
    exclude_paths: list[str] = field(default_factory=list)
    max_pages: int = 50
    max_depth: int = 3


class SubjectRegistry:
    """
    Registry for curriculum subjects loaded from curriculum_index.json.

    Provides methods for querying subjects by cycle, slug, and other criteria.
    """

    def __init__(
        self,
        subjects: list[SubjectConfig],
        short_courses: list[ShortCourseConfig],
        cycles: dict[str, CycleConfig],
        sources: dict[str, SourceConfig],
    ):
        self._subjects = {s.slug: s for s in subjects}
        self._short_courses = {sc.slug: sc for sc in short_courses}
        self._cycles = cycles
        self._sources = sources

        # Build index by cycle for fast lookup
        self._subjects_by_cycle: dict[str, list[SubjectConfig]] = {}
        for subject in subjects:
            for cycle in subject.cycles:
                if cycle not in self._subjects_by_cycle:
                    self._subjects_by_cycle[cycle] = []
                self._subjects_by_cycle[cycle].append(subject)

        logger.info(
            "subject_registry_loaded",
            subject_count=len(subjects),
            short_course_count=len(short_courses),
            cycle_count=len(cycles),
            source_count=len(sources),
        )

    @classmethod
    def from_json(cls, index_path: Path) -> SubjectRegistry:
        """Load registry from curriculum_index.json file."""
        with open(index_path) as f:
            data = json.load(f)

        # Parse sources
        sources = {}
        for name, source_data in data.get("sources", {}).items():
            sources[name] = SourceConfig(
                name=name,
                base_url=source_data["base_url"],
                language_prefixes=source_data.get("languages", {"en": "", "ga": ""}),
            )

        # Parse cycles
        cycles = {}
        for slug, cycle_data in data.get("cycles", {}).items():
            cycles[slug] = CycleConfig.from_dict(slug, cycle_data)

        # Parse subjects
        subjects = [SubjectConfig.from_dict(s) for s in data.get("subjects", [])]

        # Parse short courses
        short_courses = [ShortCourseConfig.from_dict(sc) for sc in data.get("short_courses", [])]

        return cls(subjects, short_courses, cycles, sources)

    @classmethod
    def from_default(cls) -> SubjectRegistry:
        """Load registry from the default curriculum_index.json location."""
        if not DEFAULT_INDEX_PATH.exists():
            logger.warning(
                "curriculum_index_not_found",
                path=str(DEFAULT_INDEX_PATH),
            )
            return cls([], [], {}, {})
        return cls.from_json(DEFAULT_INDEX_PATH)

    def get_subject(self, slug: str) -> SubjectConfig | None:
        """Get a subject by its slug."""
        return self._subjects.get(slug)

    def get_all_subjects(self) -> list[SubjectConfig]:
        """Get all subjects."""
        return list(self._subjects.values())

    def get_subjects_for_cycle(self, cycle: str) -> list[SubjectConfig]:
        """Get all subjects available in a specific cycle."""
        return self._subjects_by_cycle.get(cycle, [])

    def get_short_course(self, slug: str) -> ShortCourseConfig | None:
        """Get a short course by its slug."""
        return self._short_courses.get(slug)

    def get_all_short_courses(self) -> list[ShortCourseConfig]:
        """Get all short courses."""
        return list(self._short_courses.values())

    def get_cycle(self, slug: str) -> CycleConfig | None:
        """Get a cycle by its slug."""
        return self._cycles.get(slug)

    def get_all_cycles(self) -> list[CycleConfig]:
        """Get all cycles."""
        return list(self._cycles.values())

    def get_cycle_slugs(self) -> list[str]:
        """Get all cycle slugs."""
        return list(self._cycles.keys())

    def get_source(self, name: str) -> SourceConfig | None:
        """Get a source by its name."""
        return self._sources.get(name)

    def get_all_sources(self) -> list[SourceConfig]:
        """Get all sources."""
        return list(self._sources.values())

    def get_subjects_with_source(self, source: str) -> list[SubjectConfig]:
        """Get all subjects that have URLs for a specific source."""
        return [s for s in self._subjects.values() if source in s.urls]

    def search_subjects(
        self,
        cycle: str | None = None,
        source: str | None = None,
        status: str | None = None,
    ) -> list[SubjectConfig]:
        """
        Search subjects by multiple criteria.

        Args:
            cycle: Filter by cycle
            source: Filter by source availability
            status: Filter by development status

        Returns:
            List of matching subjects
        """
        results = list(self._subjects.values())

        if cycle:
            results = [s for s in results if cycle in s.cycles]

        if source:
            results = [s for s in results if source in s.urls]

        if status:
            results = [s for s in results if s.development_status == status]

        return results


class URLResolver:
    """
    Resolves subjects to source-specific crawl configurations.

    Uses the SubjectRegistry to generate Firecrawl-compatible configurations
    for crawling curriculum content.
    """

    # Cycle path mappings (for URL generation)
    CYCLE_PATH_MAPPING: dict[str, dict[str, str]] = {
        "early_childhood": {"en": "early-childhood", "ga": "an-luath-oige"},
        "primary": {"en": "primary", "ga": "bunscoil"},
        "junior_cycle": {"en": "junior-cycle", "ga": "an-tsraith-shoisearach"},
        "senior_cycle": {"en": "senior-cycle", "ga": "an-tsraith-shinsearach"},
    }

    def __init__(self, registry: SubjectRegistry):
        self._registry = registry

    def resolve_urls(
        self,
        cycle: str,
        subject: str,
        language: str = "en",
    ) -> dict[str, CrawlConfig]:
        """
        Resolve crawl configurations for a subject across all available sources.

        Args:
            cycle: Education cycle (primary, junior_cycle, senior_cycle)
            subject: Subject slug
            language: Language code (en, ga)

        Returns:
            Dict mapping source name to CrawlConfig
        """
        subject_config = self._registry.get_subject(subject)
        if not subject_config:
            logger.warning("subject_not_found", subject=subject)
            return {}

        if cycle not in subject_config.cycles:
            logger.warning(
                "subject_not_in_cycle",
                subject=subject,
                cycle=cycle,
                available_cycles=subject_config.cycles,
            )
            return {}

        configs = {}

        for source_name, path in subject_config.urls.items():
            source = self._registry.get_source(source_name)
            if not source:
                continue

            include_paths = self._build_include_paths(source_name, cycle, path, language)
            exclude_paths = self._build_exclude_paths(source_name)

            configs[source_name] = CrawlConfig(
                source=source_name,
                base_url=source.base_url,
                include_paths=include_paths,
                exclude_paths=exclude_paths,
            )

        return configs

    def resolve_cycle_urls(
        self,
        cycle: str,
        language: str = "en",
        sources: list[str] | None = None,
    ) -> dict[str, CrawlConfig]:
        """
        Resolve crawl configurations for an entire cycle.

        Args:
            cycle: Education cycle
            language: Language code
            sources: Optional list of sources to include (default: all)

        Returns:
            Dict mapping source name to CrawlConfig
        """
        if sources is None:
            sources = ["curriculumonline", "ncca", "examinations"]

        configs = {}

        for source_name in sources:
            source = self._registry.get_source(source_name)
            if not source:
                continue

            include_paths = self._build_cycle_include_paths(source_name, cycle, language)
            exclude_paths = self._build_exclude_paths(source_name)

            configs[source_name] = CrawlConfig(
                source=source_name,
                base_url=source.base_url,
                include_paths=include_paths,
                exclude_paths=exclude_paths,
                max_pages=200,  # Higher limit for full cycle crawl
            )

        return configs

    def _build_include_paths(
        self,
        source: str,
        cycle: str,
        subject_path: str,
        language: str,
    ) -> list[str]:
        """Build include paths for Firecrawl based on source type."""
        if source == "curriculumonline":
            # Curriculumonline uses path prefix for language
            lang_prefix = "/ga-ie" if language == "ga" else ""
            return [f"{lang_prefix}{subject_path}*"]

        elif source == "ncca":
            # NCCA uses /en or /ga prefix
            lang_prefix = "/ga" if language == "ga" else "/en"
            cycle_path = self.CYCLE_PATH_MAPPING.get(cycle, {}).get(language, cycle)
            return [f"{lang_prefix}/{cycle_path}{subject_path}*"]

        elif source == "examinations":
            # Examinations uses query params for language
            # Language is handled in query params, not paths
            return ["/exammaterialarchive/*", "/?*"]

        return [subject_path]

    def _build_cycle_include_paths(
        self,
        source: str,
        cycle: str,
        language: str,
    ) -> list[str]:
        """Build include paths for a full cycle crawl."""
        cycle_path = self.CYCLE_PATH_MAPPING.get(cycle, {}).get(language, cycle)

        if source == "curriculumonline":
            lang_prefix = "/ga-ie" if language == "ga" else ""
            return [f"{lang_prefix}/{cycle_path}/*"]

        elif source == "ncca":
            lang_prefix = "/ga" if language == "ga" else "/en"
            return [f"{lang_prefix}/{cycle_path}/*"]

        elif source == "examinations":
            # Examinations doesn't have cycle-based paths
            return ["/exammaterialarchive/*", "/?*"]

        return [f"/{cycle_path}/*"]

    def _build_exclude_paths(self, source: str) -> list[str]:
        """Build exclude paths for Firecrawl."""
        # Use glob-style patterns (not regex) - paths starting with / are relative to base URL
        common_excludes = [
            "/search",
            "/login",
            "/sitemap",
        ]

        if source == "curriculumonline":
            return common_excludes + ["/getmedia"]

        elif source == "ncca":
            return common_excludes + ["/media"]

        return common_excludes

    def get_all_subjects_for_cycle(self, cycle: str) -> list[str]:
        """Get all subject slugs for a cycle."""
        subjects = self._registry.get_subjects_for_cycle(cycle)
        return [s.slug for s in subjects]
