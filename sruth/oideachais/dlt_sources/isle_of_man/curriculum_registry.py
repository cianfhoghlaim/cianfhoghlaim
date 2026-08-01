"""
Curriculum Registry - Subject taxonomy and URL resolution for Isle of Man.

Provides a centralized registry for:
- Subject configuration and metadata (Isle of Man curriculum)
- Key stage-based subject filtering
- Source-specific URL resolution (DESC, Culture Vannin, Learn Manx)
- Crawl configuration generation

Adapted from the Wales curriculum registry pattern.

Usage:
    from sruth.oideachais.dlt_sources.isle_of_man.curriculum_registry import (
        SubjectRegistry,
        URLResolver,
    )

    registry = SubjectRegistry.from_default()
    resolver = URLResolver(registry)

    # Get all subjects for a key stage
    subjects = registry.get_subjects_for_key_stage("secondary")

    # Get crawl config for a specific subject
    configs = resolver.resolve_urls("secondary", "manx", "en")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# Default path to isle_of_man_curriculum_index.json
DEFAULT_INDEX_PATH = (
    Path(__file__).parent.parent.parent /
    "firecrawl_configs" / "curriculum" / "isle_of_man_curriculum_index.json"
)


@dataclass
class SourceConfig:
    """Configuration for an Isle of Man curriculum source (DESC, Culture Vannin, etc.)."""

    name: str
    base_url: str
    language_prefixes: dict[str, str]  # {"en": "", "gv": ""} - limited Manx content

    def get_full_url(self, path: str, language: str = "en") -> str:
        """Get full URL for a path in the given language."""
        prefix = self.language_prefixes.get(language, "")
        return f"{self.base_url}{prefix}{path}"


@dataclass
class SubjectConfig:
    """Configuration for an Isle of Man curriculum subject."""

    slug: str
    name: dict[str, str]  # {"en": "Manx", "gv": "Gaelg"}
    key_stages: list[str]  # ["foundation", "primary", "secondary", "higher"]
    qualification_type: str | None = None  # Manx qualification types
    urls: dict[str, str] = field(default_factory=dict)  # source -> path

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SubjectConfig:
        """Create SubjectConfig from dictionary."""
        return cls(
            slug=data["slug"],
            name=data["name"],
            key_stages=data.get("key_stages", []),
            qualification_type=data.get("qualification_type"),
            urls=data.get("urls", {}),
        )

    def is_in_key_stage(self, key_stage: str) -> bool:
        """Check if subject is available in a specific key stage."""
        return key_stage in self.key_stages

    def get_url_for_source(self, source: str) -> str | None:
        """Get URL path for a specific source."""
        return self.urls.get(source)

    def get_available_sources(self) -> list[str]:
        """Get list of sources that have URLs for this subject."""
        return list(self.urls.keys())


@dataclass
class KeyStageConfig:
    """Configuration for an Isle of Man key stage."""

    slug: str
    name: dict[str, str]
    age_range: str
    years: int | None = None

    @classmethod
    def from_dict(cls, slug: str, data: dict[str, Any]) -> KeyStageConfig:
        """Create KeyStageConfig from dictionary."""
        return cls(
            slug=slug,
            name=data["name"],
            age_range=data.get("age_range", ""),
            years=data.get("years"),
        )


@dataclass
class ManxQualificationConfig:
    """Configuration for a Manx Gaelic qualification."""

    slug: str
    name: dict[str, str]
    level: str | None = None
    description: str | None = None

    @classmethod
    def from_dict(cls, slug: str, data: dict[str, Any]) -> ManxQualificationConfig:
        """Create ManxQualificationConfig from dictionary."""
        return cls(
            slug=slug,
            name=data["name"],
            level=data.get("level"),
            description=data.get("description"),
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
    Registry for Isle of Man curriculum subjects loaded from isle_of_man_curriculum_index.json.

    Provides methods for querying subjects by key stage, slug, and other criteria.
    """

    def __init__(
        self,
        subjects: list[SubjectConfig],
        key_stages: dict[str, KeyStageConfig],
        qualifications: dict[str, ManxQualificationConfig],
        sources: dict[str, SourceConfig],
        cultural_context: dict[str, Any] | None = None,
        learning_resources: dict[str, Any] | None = None,
    ):
        self._subjects = {s.slug: s for s in subjects}
        self._key_stages = key_stages
        self._qualifications = qualifications
        self._sources = sources
        self._cultural_context = cultural_context or {}
        self._learning_resources = learning_resources or {}

        # Build index by key stage for fast lookup
        self._subjects_by_key_stage: dict[str, list[SubjectConfig]] = {}
        for subject in subjects:
            for key_stage in subject.key_stages:
                if key_stage not in self._subjects_by_key_stage:
                    self._subjects_by_key_stage[key_stage] = []
                self._subjects_by_key_stage[key_stage].append(subject)

        logger.info(
            "isle_of_man_subject_registry_loaded",
            subject_count=len(subjects),
            key_stage_count=len(key_stages),
            qualification_count=len(qualifications),
            source_count=len(sources),
        )

    @classmethod
    def from_json(cls, index_path: Path) -> SubjectRegistry:
        """Load registry from isle_of_man_curriculum_index.json file."""
        with open(index_path) as f:
            data = json.load(f)

        # Parse sources
        sources = {}
        for name, source_data in data.get("sources", {}).items():
            sources[name] = SourceConfig(
                name=name,
                base_url=source_data["base_url"],
                language_prefixes=source_data.get("languages", {"en": "", "gv": ""}),
            )

        # Parse key stages
        key_stages = {}
        for slug, ks_data in data.get("key_stages", {}).items():
            key_stages[slug] = KeyStageConfig.from_dict(slug, ks_data)

        # Parse Manx qualifications
        qualifications = {}
        for slug, qual_data in data.get("manx_qualifications", {}).items():
            qualifications[slug] = ManxQualificationConfig.from_dict(slug, qual_data)

        # Parse subjects
        subjects = [SubjectConfig.from_dict(s) for s in data.get("subjects", [])]

        # Get cultural context and learning resources
        cultural_context = data.get("cultural_context", {})
        learning_resources = data.get("learning_resources", {})

        return cls(subjects, key_stages, qualifications, sources, cultural_context, learning_resources)

    @classmethod
    def from_default(cls) -> SubjectRegistry:
        """Load registry from the default isle_of_man_curriculum_index.json location."""
        if not DEFAULT_INDEX_PATH.exists():
            logger.warning(
                "isle_of_man_curriculum_index_not_found",
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

    def get_subjects_for_key_stage(self, key_stage: str) -> list[SubjectConfig]:
        """Get all subjects available in a specific key stage."""
        return self._subjects_by_key_stage.get(key_stage, [])

    def get_key_stage(self, slug: str) -> KeyStageConfig | None:
        """Get a key stage by its slug."""
        return self._key_stages.get(slug)

    def get_all_key_stages(self) -> list[KeyStageConfig]:
        """Get all key stages."""
        return list(self._key_stages.values())

    def get_key_stage_slugs(self) -> list[str]:
        """Get all key stage slugs."""
        return list(self._key_stages.keys())

    def get_qualification(self, slug: str) -> ManxQualificationConfig | None:
        """Get a Manx qualification by its slug."""
        return self._qualifications.get(slug)

    def get_all_qualifications(self) -> list[ManxQualificationConfig]:
        """Get all Manx qualifications."""
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

    def get_cultural_context(self) -> dict[str, Any]:
        """Get cultural context information."""
        return self._cultural_context

    def get_learning_resources(self) -> dict[str, Any]:
        """Get learning resources configuration."""
        return self._learning_resources

    def search_subjects(
        self,
        key_stage: str | None = None,
        source: str | None = None,
        qualification_type: str | None = None,
    ) -> list[SubjectConfig]:
        """
        Search subjects by multiple criteria.

        Args:
            key_stage: Filter by key stage
            source: Filter by source availability
            qualification_type: Filter by qualification type

        Returns:
            List of matching subjects
        """
        results = list(self._subjects.values())

        if key_stage:
            results = [s for s in results if key_stage in s.key_stages]

        if source:
            results = [s for s in results if source in s.urls]

        if qualification_type:
            results = [s for s in results if s.qualification_type == qualification_type]

        return results


class URLResolver:
    """
    Resolves subjects to source-specific crawl configurations for Isle of Man.

    Uses the SubjectRegistry to generate Firecrawl-compatible configurations
    for crawling Isle of Man curriculum content.
    """

    # Key stage path mappings (for URL generation)
    KEY_STAGE_PATH_MAPPING: dict[str, dict[str, str]] = {
        "foundation": {"en": "foundation-stage", "gv": "bun-toshee"},
        "primary": {"en": "primary", "gv": "bun-scoill"},
        "secondary": {"en": "secondary", "gv": "yn-scoill"},
        "higher": {"en": "higher-education", "gv": "ynsagh"},
    }

    def __init__(self, registry: SubjectRegistry):
        self._registry = registry

    def resolve_urls(
        self,
        key_stage: str,
        subject: str,
        language: str = "en",
    ) -> dict[str, CrawlConfig]:
        """
        Resolve crawl configurations for a subject across all available sources.

        Args:
            key_stage: Education key stage (foundation, primary, secondary, higher)
            subject: Subject slug
            language: Language code (en, gv)

        Returns:
            Dict mapping source name to CrawlConfig
        """
        subject_config = self._registry.get_subject(subject)
        if not subject_config:
            logger.warning("subject_not_found", subject=subject)
            return {}

        if key_stage not in subject_config.key_stages:
            logger.warning(
                "subject_not_in_key_stage",
                subject=subject,
                key_stage=key_stage,
                available_key_stages=subject_config.key_stages,
            )
            return {}

        configs = {}

        for source_name, path in subject_config.urls.items():
            source = self._registry.get_source(source_name)
            if not source:
                continue

            include_paths = self._build_include_paths(source_name, key_stage, path, language)
            exclude_paths = self._build_exclude_paths(source_name)

            configs[source_name] = CrawlConfig(
                source=source_name,
                base_url=source.base_url,
                include_paths=include_paths,
                exclude_paths=exclude_paths,
            )

        return configs

    def resolve_key_stage_urls(
        self,
        key_stage: str,
        language: str = "en",
        sources: list[str] | None = None,
    ) -> dict[str, CrawlConfig]:
        """
        Resolve crawl configurations for an entire key stage.

        Args:
            key_stage: Education key stage
            language: Language code
            sources: Optional list of sources to include (default: all)

        Returns:
            Dict mapping source name to CrawlConfig
        """
        if sources is None:
            sources = ["desc", "culture_vannin", "learn_manx", "manx_music"]

        configs = {}

        for source_name in sources:
            source = self._registry.get_source(source_name)
            if not source:
                continue

            include_paths = self._build_key_stage_include_paths(source_name, key_stage, language)
            exclude_paths = self._build_exclude_paths(source_name)

            configs[source_name] = CrawlConfig(
                source=source_name,
                base_url=source.base_url,
                include_paths=include_paths,
                exclude_paths=exclude_paths,
                max_pages=200,  # Higher limit for full key stage crawl
            )

        return configs

    def _build_include_paths(
        self,
        source: str,
        key_stage: str,
        subject_path: str,
        language: str,
    ) -> list[str]:
        """Build include paths for Firecrawl based on source type."""
        if source == "desc":
            # DESC education paths
            return [f"{subject_path}*"]

        elif source == "culture_vannin":
            # Culture Vannin Manx language and culture paths
            return [f"{subject_path}*"]

        elif source == "learn_manx":
            # Learn Manx language learning paths
            return [f"{subject_path}*"]

        elif source == "manx_music":
            # Manx Music education resources
            return [f"{subject_path}*"]

        return [subject_path]

    def _build_key_stage_include_paths(
        self,
        source: str,
        key_stage: str,
        language: str,
    ) -> list[str]:
        """Build include paths for a full key stage crawl."""
        if source == "desc":
            # DESC education paths
            return ["/education/*"]

        elif source == "culture_vannin":
            # Culture Vannin Manx language and culture
            return ["/manxlanguage/*", "/schools/*"]

        elif source == "learn_manx":
            # Learn Manx language learning
            return ["/learning/*"]

        elif source == "manx_music":
            # Manx Music education resources
            return ["/schools/*", "/school-resources/*"]

        return [f"/{key_stage}/*"]

    def _build_exclude_paths(self, source: str) -> list[str]:
        """Build exclude paths for Firecrawl."""
        common_excludes = [
            "/search",
            "/login",
            "/sitemap",
            "/api",
        ]

        return common_excludes

    def get_all_subjects_for_key_stage(self, key_stage: str) -> list[str]:
        """Get all subject slugs for a key stage."""
        subjects = self._registry.get_subjects_for_key_stage(key_stage)
        return [s.slug for s in subjects]


__all__ = [
    "SubjectConfig",
    "KeyStageConfig",
    "ManxQualificationConfig",
    "SourceConfig",
    "CrawlConfig",
    "SubjectRegistry",
    "URLResolver",
    "DEFAULT_INDEX_PATH",
]
