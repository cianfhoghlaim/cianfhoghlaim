"""
Curriculum Registry - Subject taxonomy and URL resolution for Scotland.

Provides a centralized registry for:
- Subject configuration and metadata (Scottish curriculum)
- Curriculum level-based subject filtering
- Source-specific URL resolution (Education Scotland, SQA, Bòrd na Gàidhlig)
- Crawl configuration generation

Adapted from the Wales curriculum registry pattern.

Usage:
    from sruth.oideachais.dlt_sources.scotland.curriculum_registry import (
        SubjectRegistry,
        URLResolver,
    )

    registry = SubjectRegistry.from_default()
    resolver = URLResolver(registry)

    # Get all subjects for a curriculum level
    subjects = registry.get_subjects_for_level("fourth")

    # Get crawl config for a specific subject
    configs = resolver.resolve_urls("fourth", "mathematics", "en")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# Default path to scotland_curriculum_index.json
DEFAULT_INDEX_PATH = (
    Path(__file__).parent.parent.parent /
    "firecrawl_configs" / "curriculum" / "scotland_curriculum_index.json"
)


@dataclass
class SourceConfig:
    """Configuration for a Scottish curriculum source (Education Scotland, SQA, etc.)."""

    name: str
    base_url: str
    language_prefixes: dict[str, str]  # {"en": "", "gd": "/gd"}

    def get_full_url(self, path: str, language: str = "en") -> str:
        """Get full URL for a path in the given language."""
        prefix = self.language_prefixes.get(language, "")
        return f"{self.base_url}{prefix}{path}"


@dataclass
class SubjectConfig:
    """Configuration for a Scottish curriculum subject."""

    slug: str
    name: dict[str, str]  # {"en": "Mathematics", "gd": "Matamataig"}
    levels: list[str]  # ["first", "second", "third", "fourth"]
    qualification_type: list[str] | None = None  # ["national_5", "higher", "advanced_higher"]
    urls: dict[str, str] = field(default_factory=dict)  # source -> path

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SubjectConfig:
        """Create SubjectConfig from dictionary."""
        return cls(
            slug=data["slug"],
            name=data["name"],
            levels=data.get("levels", []),
            qualification_type=data.get("qualification_type"),
            urls=data.get("urls", {}),
        )

    def is_in_level(self, level: str) -> bool:
        """Check if subject is available in a specific curriculum level."""
        return level in self.levels

    def get_url_for_source(self, source: str) -> str | None:
        """Get URL path for a specific source."""
        return self.urls.get(source)

    def get_available_sources(self) -> list[str]:
        """Get list of sources that have URLs for this subject."""
        return list(self.urls.keys())


@dataclass
class LevelConfig:
    """Configuration for a Scottish curriculum level."""

    slug: str
    name: dict[str, str]
    age_range: str
    stage: str | None = None
    senior_phase: bool = False

    @classmethod
    def from_dict(cls, slug: str, data: dict[str, Any]) -> LevelConfig:
        """Create LevelConfig from dictionary."""
        return cls(
            slug=slug,
            name=data["name"],
            age_range=data.get("age_range", ""),
            stage=data.get("stage"),
            senior_phase=data.get("senior_phase", False),
        )


@dataclass
class QualificationConfig:
    """Configuration for a Scottish qualification."""

    slug: str
    name: dict[str, str]
    age: str
    level: str | None = None
    equivalent: list[str] | None = None

    @classmethod
    def from_dict(cls, slug: str, data: dict[str, Any]) -> QualificationConfig:
        """Create QualificationConfig from dictionary."""
        return cls(
            slug=slug,
            name=data["name"],
            age=data.get("age", ""),
            level=data.get("level"),
            equivalent=data.get("equivalent"),
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
    Registry for Scottish curriculum subjects loaded from scotland_curriculum_index.json.

    Provides methods for querying subjects by curriculum level, slug, and other criteria.
    """

    def __init__(
        self,
        subjects: list[SubjectConfig],
        levels: dict[str, LevelConfig],
        qualifications: dict[str, QualificationConfig],
        sources: dict[str, SourceConfig],
    ):
        self._subjects = {s.slug: s for s in subjects}
        self._levels = levels
        self._qualifications = qualifications
        self._sources = sources

        # Build index by level for fast lookup
        self._subjects_by_level: dict[str, list[SubjectConfig]] = {}
        for subject in subjects:
            for level in subject.levels:
                if level not in self._subjects_by_level:
                    self._subjects_by_level[level] = []
                self._subjects_by_level[level].append(subject)

        logger.info(
            "scotland_subject_registry_loaded",
            subject_count=len(subjects),
            level_count=len(levels),
            qualification_count=len(qualifications),
            source_count=len(sources),
        )

    @classmethod
    def from_json(cls, index_path: Path) -> SubjectRegistry:
        """Load registry from scotland_curriculum_index.json file."""
        with open(index_path) as f:
            data = json.load(f)

        # Parse sources
        sources = {}
        for name, source_data in data.get("sources", {}).items():
            sources[name] = SourceConfig(
                name=name,
                base_url=source_data["base_url"],
                language_prefixes=source_data.get("languages", {"en": "", "gd": ""}),
            )

        # Parse curriculum levels
        levels = {}
        for slug, level_data in data.get("curriculum_levels", {}).items():
            levels[slug] = LevelConfig.from_dict(slug, level_data)

        # Parse qualifications
        qualifications = {}
        for slug, qual_data in data.get("qualifications", {}).items():
            qualifications[slug] = QualificationConfig.from_dict(slug, qual_data)

        # Parse subjects
        subjects = [SubjectConfig.from_dict(s) for s in data.get("subjects", [])]

        return cls(subjects, levels, qualifications, sources)

    @classmethod
    def from_default(cls) -> SubjectRegistry:
        """Load registry from the default scotland_curriculum_index.json location."""
        if not DEFAULT_INDEX_PATH.exists():
            logger.warning(
                "scotland_curriculum_index_not_found",
                path=str(DEFAULT_INDEX_PATH),
            )
            return cls([], {}, {}, {})
        return cls.from_json(DEFAULT_INDEX_PATH)

    def get_subject(self, slug: str) -> SubjectConfig | None:
        """Get a subject by its slug."""
        return self._subjects.get(slug)

    def get_all_subjects(self) -> list[SubjectConfig]:
        """Get all subjects."""
        return list(self._subjects.values())

    def get_subjects_for_level(self, level: str) -> list[SubjectConfig]:
        """Get all subjects available in a specific curriculum level."""
        return self._subjects_by_level.get(level, [])

    def get_level(self, slug: str) -> LevelConfig | None:
        """Get a curriculum level by its slug."""
        return self._levels.get(slug)

    def get_all_levels(self) -> list[LevelConfig]:
        """Get all curriculum levels."""
        return list(self._levels.values())

    def get_level_slugs(self) -> list[str]:
        """Get all curriculum level slugs."""
        return list(self._levels.keys())

    def get_qualification(self, slug: str) -> QualificationConfig | None:
        """Get a qualification by its slug."""
        return self._qualifications.get(slug)

    def get_all_qualifications(self) -> list[QualificationConfig]:
        """Get all qualifications."""
        return list(self._qualifications.values())

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
        level: str | None = None,
        source: str | None = None,
        qualification_type: str | None = None,
    ) -> list[SubjectConfig]:
        """
        Search subjects by multiple criteria.

        Args:
            level: Filter by curriculum level
            source: Filter by source availability
            qualification_type: Filter by qualification type

        Returns:
            List of matching subjects
        """
        results = list(self._subjects.values())

        if level:
            results = [s for s in results if level in s.levels]

        if source:
            results = [s for s in results if source in s.urls]

        if qualification_type:
            results = [s for s in results if s.qualification_type and qualification_type in s.qualification_type]

        return results


class URLResolver:
    """
    Resolves subjects to source-specific crawl configurations for Scotland.

    Uses the SubjectRegistry to generate Firecrawl-compatible configurations
    for crawling Scottish curriculum content.
    """

    # Curriculum level path mappings (for URL generation)
    LEVEL_PATH_MAPPING: dict[str, dict[str, str]] = {
        "early": {"en": "early-level", "gd": "ire-innic"},
        "first": {"en": "first-level", "gd": "ire-chiùil"},
        "second": {"en": "second-level", "gd": "ire-dàna"},
        "third": {"en": "third-level", "gd": "ire-treas"},
        "fourth": {"en": "fourth-level", "gd": "ire-ceathrach"},
    }

    def __init__(self, registry: SubjectRegistry):
        self._registry = registry

    def resolve_urls(
        self,
        level: str,
        subject: str,
        language: str = "en",
    ) -> dict[str, CrawlConfig]:
        """
        Resolve crawl configurations for a subject across all available sources.

        Args:
            level: Curriculum level (first, second, third, fourth)
            subject: Subject slug
            language: Language code (en, gd)

        Returns:
            Dict mapping source name to CrawlConfig
        """
        subject_config = self._registry.get_subject(subject)
        if not subject_config:
            logger.warning("subject_not_found", subject=subject)
            return {}

        if level not in subject_config.levels:
            logger.warning(
                "subject_not_in_level",
                subject=subject,
                level=level,
                available_levels=subject_config.levels,
            )
            return {}

        configs = {}

        for source_name, path in subject_config.urls.items():
            # Handle compound source names like "sqa_n5"
            base_source = source_name.split("_")[0]
            source = self._registry.get_source(base_source)
            if not source:
                continue

            include_paths = self._build_include_paths(base_source, level, path, language)
            exclude_paths = self._build_exclude_paths(base_source)

            configs[source_name] = CrawlConfig(
                source=source_name,
                base_url=source.base_url,
                include_paths=include_paths,
                exclude_paths=exclude_paths,
            )

        return configs

    def resolve_level_urls(
        self,
        level: str,
        language: str = "en",
        sources: list[str] | None = None,
    ) -> dict[str, CrawlConfig]:
        """
        Resolve crawl configurations for an entire curriculum level.

        Args:
            level: Curriculum level
            language: Language code
            sources: Optional list of sources to include (default: all)

        Returns:
            Dict mapping source name to CrawlConfig
        """
        if sources is None:
            sources = ["education_scotland", "sqa", "bord_na_gaidhlig"]

        configs = {}

        for source_name in sources:
            source = self._registry.get_source(source_name)
            if not source:
                continue

            include_paths = self._build_level_include_paths(source_name, level, language)
            exclude_paths = self._build_exclude_paths(source_name)

            configs[source_name] = CrawlConfig(
                source=source_name,
                base_url=source.base_url,
                include_paths=include_paths,
                exclude_paths=exclude_paths,
                max_pages=200,  # Higher limit for full level crawl
            )

        return configs

    def _build_include_paths(
        self,
        source: str,
        level: str,
        subject_path: str,
        language: str,
    ) -> list[str]:
        """Build include paths for Firecrawl based on source type."""
        if source == "education_scotland":
            # Education Scotland uses /gd prefix for Scottish Gaelic
            lang_prefix = "/gd" if language == "gd" else ""
            # Handle both English and Gaelic curriculum paths
            curriculum_paths = ["/curriculum-for-excellence/*"]
            return [f"{lang_prefix}{subject_path}*"] + curriculum_paths

        elif source == "sqa":
            # SQA past paper and qualification paths
            return [f"{subject_path}*"]

        elif source == "bord_na_gaidhlig":
            # Bòrd na Gàidhlig Gaelic language resources
            return [f"{subject_path}*"]

        return [subject_path]

    def _build_level_include_paths(
        self,
        source: str,
        level: str,
        language: str,
    ) -> list[str]:
        """Build include paths for a full curriculum level crawl."""
        if source == "education_scotland":
            lang_prefix = "/gd" if language == "gd" else ""
            return [
                f"{lang_prefix}/curriculum-for-excellence/*",
            ]

        elif source == "sqa":
            # SQA qualification paths by level
            return ["/pastpapers/*", "/qualifications/*"]

        elif source == "bord_na_gaidhlig":
            # Gaelic language resources
            return ["/*"]

        return [f"/{level}/*"]

    def _build_exclude_paths(self, source: str) -> list[str]:
        """Build exclude paths for Firecrawl."""
        common_excludes = [
            "/search",
            "/login",
            "/sitemap",
            "/api",
        ]

        if source == "education_scotland":
            return common_excludes

        elif source == "sqa":
            return common_excludes + ["/login", "/register"]

        elif source == "bord_na_gaidhlig":
            return common_excludes

        return common_excludes

    def get_all_subjects_for_level(self, level: str) -> list[str]:
        """Get all subject slugs for a curriculum level."""
        subjects = self._registry.get_subjects_for_level(level)
        return [s.slug for s in subjects]


__all__ = [
    "SubjectConfig",
    "LevelConfig",
    "QualificationConfig",
    "SourceConfig",
    "CrawlConfig",
    "SubjectRegistry",
    "URLResolver",
    "DEFAULT_INDEX_PATH",
]
