"""
Curriculum Registry - Subject taxonomy and URL resolution for Wales.

Provides a centralized registry for:
- Subject configuration and metadata (Welsh curriculum)
- Key stage-based subject filtering
- Source-specific URL resolution (Hwb, WJEC, CBAC)
- Crawl configuration generation

Adapted from the Ireland curriculum registry pattern.

Usage:
    from sruth.oideachais.dlt_sources.wales.curriculum_registry import (
        SubjectRegistry,
        URLResolver,
    )

    registry = SubjectRegistry.from_default()
    resolver = URLResolver(registry)

    # Get all subjects for a key stage
    subjects = registry.get_subjects_for_key_stage("ks4")

    # Get crawl config for a specific subject
    configs = resolver.resolve_urls("ks4", "mathematics", "en")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# Default path to wales_curriculum_index.json
DEFAULT_INDEX_PATH = (
    Path(__file__).parent.parent.parent /
    "firecrawl_configs" / "curriculum" / "wales_curriculum_index.json"
)


@dataclass
class SourceConfig:
    """Configuration for a Welsh curriculum source (Hwb, WJEC, CBAC)."""

    name: str
    base_url: str
    language_prefixes: dict[str, str]  # {"en": "", "cy": "/cy"}

    def get_full_url(self, path: str, language: str = "en") -> str:
        """Get full URL for a path in the given language."""
        prefix = self.language_prefixes.get(language, "")
        return f"{self.base_url}{prefix}{path}"


@dataclass
class SubjectConfig:
    """Configuration for a Welsh curriculum subject."""

    slug: str
    name: dict[str, str]  # {"en": "Mathematics", "cy": "Mathemateg"}
    key_stages: list[str]  # ["ks3", "ks4"]
    qualification_type: str | None = None  # "gcse", "a_level"
    aole: str | None = None  # Area of Learning and Experience
    urls: dict[str, str] = field(default_factory=dict)  # source -> path

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SubjectConfig:
        """Create SubjectConfig from dictionary."""
        return cls(
            slug=data["slug"],
            name=data["name"],
            key_stages=data.get("key_stages", []),
            qualification_type=data.get("qualification_type"),
            aole=data.get("aole"),
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
    """Configuration for a Welsh key stage."""

    slug: str
    name: dict[str, str]
    age_range: str
    years: int | None = None
    certification: str | None = None
    description: dict[str, str] | None = None

    @classmethod
    def from_dict(cls, slug: str, data: dict[str, Any]) -> KeyStageConfig:
        """Create KeyStageConfig from dictionary."""
        return cls(
            slug=slug,
            name=data["name"],
            age_range=data.get("age_range", ""),
            years=data.get("years"),
            certification=data.get("certification"),
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
    Registry for Welsh curriculum subjects loaded from wales_curriculum_index.json.

    Provides methods for querying subjects by key stage, slug, and other criteria.
    """

    def __init__(
        self,
        subjects: list[SubjectConfig],
        key_stages: dict[str, KeyStageConfig],
        sources: dict[str, SourceConfig],
        aole: dict[str, Any] | None = None,
    ):
        self._subjects = {s.slug: s for s in subjects}
        self._key_stages = key_stages
        self._sources = sources
        self._aole = aole or {}

        # Build index by key stage for fast lookup
        self._subjects_by_key_stage: dict[str, list[SubjectConfig]] = {}
        for subject in subjects:
            for key_stage in subject.key_stages:
                if key_stage not in self._subjects_by_key_stage:
                    self._subjects_by_key_stage[key_stage] = []
                self._subjects_by_key_stage[key_stage].append(subject)

        logger.info(
            "wales_subject_registry_loaded",
            subject_count=len(subjects),
            key_stage_count=len(key_stages),
            source_count=len(sources),
        )

    @classmethod
    def from_json(cls, index_path: Path) -> SubjectRegistry:
        """Load registry from wales_curriculum_index.json file."""
        with open(index_path) as f:
            data = json.load(f)

        # Parse sources
        sources = {}
        for name, source_data in data.get("sources", {}).items():
            sources[name] = SourceConfig(
                name=name,
                base_url=source_data["base_url"],
                language_prefixes=source_data.get("languages", {"en": "", "cy": ""}),
            )

        # Parse key stages
        key_stages = {}
        for slug, ks_data in data.get("key_stages", {}).items():
            key_stages[slug] = KeyStageConfig.from_dict(slug, ks_data)

        # Parse subjects
        subjects = [SubjectConfig.from_dict(s) for s in data.get("subjects", [])]

        # Get AoLE data
        aole = data.get("areas_of_learning_experience", {})

        return cls(subjects, key_stages, sources, aole)

    @classmethod
    def from_default(cls) -> SubjectRegistry:
        """Load registry from the default wales_curriculum_index.json location."""
        if not DEFAULT_INDEX_PATH.exists():
            logger.warning(
                "wales_curriculum_index_not_found",
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
        key_stage: str | None = None,
        source: str | None = None,
        aole: str | None = None,
    ) -> list[SubjectConfig]:
        """
        Search subjects by multiple criteria.

        Args:
            key_stage: Filter by key stage
            source: Filter by source availability
            aole: Filter by Area of Learning and Experience

        Returns:
            List of matching subjects
        """
        results = list(self._subjects.values())

        if key_stage:
            results = [s for s in results if key_stage in s.key_stages]

        if source:
            results = [s for s in results if source in s.urls]

        if aole:
            results = [s for s in results if s.aole == aole]

        return results


class URLResolver:
    """
    Resolves subjects to source-specific crawl configurations for Wales.

    Uses the SubjectRegistry to generate Firecrawl-compatible configurations
    for crawling Welsh curriculum content.
    """

    # Key stage path mappings (for URL generation)
    KEY_STAGE_PATH_MAPPING: dict[str, dict[str, str]] = {
        "foundation": {"en": "foundation-phase", "cy": "cyfnod-sylfaen"},
        "ks2": {"en": "key-stage-2", "cy": "cyfnod-allweddol-2"},
        "ks3": {"en": "key-stage-3", "cy": "cyfnod-allweddol-3"},
        "ks4": {"en": "key-stage-4", "cy": "cyfnod-allweddol-4"},
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
            key_stage: Education key stage (ks3, ks4, etc.)
            subject: Subject slug
            language: Language code (en, cy)

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
            # Handle compound source names like "wjec_literature"
            base_source = source_name.split("_")[0]
            source = self._registry.get_source(base_source)
            if not source:
                continue

            include_paths = self._build_include_paths(base_source, key_stage, path, language)
            exclude_paths = self._build_exclude_paths(base_source)

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
            sources = ["hwb", "wjec", "cbac"]

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
        if source == "hwb":
            # Hwb uses /cy/ prefix for Welsh
            lang_prefix = "/cy" if language == "cy" else ""
            # Handle both English and Welsh curriculum paths
            curriculum_paths = ["/curriculum-for-wales/*", "/cwricwlwm-i-gymru/*"]
            return [f"{lang_prefix}{subject_path}*"] + curriculum_paths

        elif source in ("wjec", "cbac"):
            # WJEC/CBAC qualification paths
            return [f"{subject_path}*"]

        return [subject_path]

    def _build_key_stage_include_paths(
        self,
        source: str,
        key_stage: str,
        language: str,
    ) -> list[str]:
        """Build include paths for a full key stage crawl."""
        if source == "hwb":
            lang_prefix = "/cy" if language == "cy" else ""
            ks_path = self.KEY_STAGE_PATH_MAPPING.get(key_stage, {}).get(language, key_stage)
            return [
                f"{lang_prefix}/curriculum-for-wales/*",
                f"{lang_prefix}/cwricwlwm-i-gymru/*",
            ]

        elif source in ("wjec", "cbac"):
            # WJEC/CBAC qualification paths
            return ["/qualifications/*", "/cymwysterau/*"]

        return [f"/{key_stage}/*"]

    def _build_exclude_paths(self, source: str) -> list[str]:
        """Build exclude paths for Firecrawl."""
        common_excludes = [
            "/search",
            "/login",
            "/sitemap",
            "/api",
        ]

        if source == "hwb":
            return common_excludes

        elif source in ("wjec", "cbac"):
            return common_excludes + ["/login", "/register"]

        return common_excludes

    def get_all_subjects_for_key_stage(self, key_stage: str) -> list[str]:
        """Get all subject slugs for a key stage."""
        subjects = self._registry.get_subjects_for_key_stage(key_stage)
        return [s.slug for s in subjects]
