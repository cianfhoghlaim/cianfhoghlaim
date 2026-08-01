"""
Partition Definitions for Celtic Education Platform.

Enables independent pipeline execution per domain while supporting
cross-domain enrichment at the top of the Dagster hierarchy.

Partition Hierarchy:
- domain_partitions: ireland, uk, celtic (top-level independence)
- nation_partitions: 8 nations for granular execution
- language_partitions: 6 Celtic languages
- dialect_partitions: Munster, Connacht, Ulster dialect regions
"""
from __future__ import annotations

from dagster import (
    MultiPartitionsDefinition,
    StaticPartitionsDefinition,
    DynamicPartitionsDefinition,
)


# ============================================================================
# Top-Level Domain Partitions (for pipeline independence)
# ============================================================================

domain_partitions = StaticPartitionsDefinition(
    ["ireland", "uk", "celtic"]
)
"""Top-level domain partitions - run Ireland, UK, or Celtic independently."""


# ============================================================================
# Nation Partitions (granular UK/Irish execution)
# ============================================================================

nation_partitions = StaticPartitionsDefinition([
    "ireland",
    "england",
    "scotland",
    "wales",
    "northern_ireland",
    "isle_of_man",
    "jersey",
    "guernsey",
])
"""Nation partitions for granular per-nation pipeline execution."""

# UK-specific subset
uk_nation_partitions = StaticPartitionsDefinition([
    "england",
    "scotland",
    "wales",
    "northern_ireland",
])
"""UK nation partitions (excludes Crown Dependencies)."""

# Crown Dependencies
crown_dependency_partitions = StaticPartitionsDefinition([
    "isle_of_man",
    "jersey",
    "guernsey",
])
"""Crown Dependency partitions."""


# ============================================================================
# Celtic Language Partitions
# ============================================================================

language_partitions = StaticPartitionsDefinition([
    "ga",  # Irish
    "gd",  # Scottish Gaelic
    "cy",  # Welsh
    "gv",  # Manx
    "kw",  # Cornish
    "br",  # Breton
])
"""Celtic language partitions for language-specific processing."""

# Language pairs for translation
source_language_partitions = StaticPartitionsDefinition([
    "en",  # English source
    "ga",  # Irish source
    "cy",  # Welsh source
])
"""Source language partitions for translation pipelines."""


# ============================================================================
# Dialect Partitions (from Canuint provinces)
# ============================================================================

dialect_partitions = StaticPartitionsDefinition([
    "munster",
    "connacht",
    "ulster",
    "standard",
])
"""Irish dialect partitions matching Canuint pronunciation areas."""

# Dialect area partitions (more granular)
dialect_area_partitions = DynamicPartitionsDefinition(
    name="dialect_areas"
)
"""Dynamic dialect area partitions (populated from Canuint area_id values)."""


# ============================================================================
# Education Source Partitions (Ireland)
# ============================================================================

ireland_source_partitions = StaticPartitionsDefinition([
    "curriculumonline",  # Primary curriculum specs
    "ncca",              # NCCA curriculum framework
    "examinations",      # SEC exam papers & reports
    "cso",               # Education statistics
])
"""Ireland education source partitions."""


# ============================================================================
# NCCA-Specific Partitions (Cycle × Subject × Language) - DEPRECATED
# ============================================================================
# NOTE: These 208/780 partition schemes are DEPRECATED.
# Use partitions_v2.ireland_curriculum_partitions (4 partitions) instead.
# Subject selection is now handled via runtime config, not partition keys.

# Educational cycles (aligned with NCCA structure)
ireland_cycle_partitions = StaticPartitionsDefinition([
    "early_childhood",
    "primary",
    "junior_cycle",
    "senior_cycle",
])
"""Ireland educational cycle partitions."""

# Common subjects (most common for partitioned crawling)
# Note: This is a subset - add more subjects as needed
ireland_subject_partitions = StaticPartitionsDefinition([
    # Core subjects
    "english",
    "irish",
    "mathematics",
    # STEM
    "science",
    "technology",
    "engineering",
    # Humanities
    "history",
    "geography",
    "religious_education",
    # Languages
    "french",
    "german",
    "spanish",
    # Arts
    "art",
    "music",
    "drama",
    # Wellbeing
    "pe",
    "sphe",
    "cspe",
    "wellbeing",
    # Business & Economics
    "business",
    "economics",
    "home_economics",
    # Applied
    "applied_technology",
    "graphics",
    "wood_technology",
    "metalwork",
])
"""Ireland subject partitions for curriculum content."""

# NCCA multi-partition: (Cycle__Subject) × Language
# Dagster only supports 2-dimensional multi-partitions
# Combine cycle and subject into single dimension using double underscore separator
# (Dagster doesn't allow |, [, ], or , in partition keys)
# Creates: (4 × 26) × 2 = 208 partition combinations

# Generate cycle__subject combinations
_ncca_cycle_subject_combos = [
    f"{cycle}__{subject}"
    for cycle in ["early_childhood", "primary", "junior_cycle", "senior_cycle"]
    for subject in [
        "english", "irish", "mathematics", "science", "technology", "engineering",
        "history", "geography", "religious_education", "french", "german", "spanish",
        "art", "music", "drama", "pe", "sphe", "cspe", "wellbeing",
        "business", "economics", "home_economics", "applied_technology",
        "graphics", "wood_technology", "metalwork",
    ]
]

ncca_multipartitions = MultiPartitionsDefinition({
    "cycle_subject": StaticPartitionsDefinition(_ncca_cycle_subject_combos),
    "language": StaticPartitionsDefinition(["en", "ga"]),
})
"""NCCA multi-partition: (cycle__subject) × language."""

# Reduced NCCA partitions (for initial testing - core subjects only)
# Creates: (3 × 3) × 2 = 18 partition combinations
_ncca_core_cycle_subject_combos = [
    f"{cycle}__{subject}"
    for cycle in ["primary", "junior_cycle", "senior_cycle"]
    for subject in ["english", "irish", "mathematics"]
]

ncca_core_multipartitions = MultiPartitionsDefinition({
    "cycle_subject": StaticPartitionsDefinition(_ncca_core_cycle_subject_combos),
    "language": StaticPartitionsDefinition(["en", "ga"]),
})
"""NCCA core multi-partition (reduced set for testing)."""

# SEC Examinations: (Subject__Year) × Level
# Dagster only supports 2-dimensional multi-partitions
# Creates: (26 × 10) × 3 = 780 partition combinations
_sec_subject_year_combos = [
    f"{subject}__{year}"
    for subject in [
        "english", "irish", "mathematics", "science", "technology", "engineering",
        "history", "geography", "religious_education", "french", "german", "spanish",
        "art", "music", "drama", "pe", "sphe", "cspe", "wellbeing",
        "business", "economics", "home_economics", "applied_technology",
        "graphics", "wood_technology", "metalwork",
    ]
    for year in [str(y) for y in range(2015, 2025)]
]

sec_multipartitions = MultiPartitionsDefinition({
    "subject_year": StaticPartitionsDefinition(_sec_subject_year_combos),
    "level": StaticPartitionsDefinition([
        "leaving_cert_higher",
        "leaving_cert_ordinary",
        "junior_cycle",
    ]),
})
"""SEC multi-partition: subject__year × level."""


# ============================================================================
# Education Source Partitions (UK)
# ============================================================================

england_source_partitions = StaticPartitionsDefinition([
    "dfe",       # Department for Education
    "ofsted",    # Inspectorate
    "aqa",       # Exam board
    "ocr",       # Exam board
    "edexcel",   # Exam board
])
"""England education source partitions."""

scotland_source_partitions = StaticPartitionsDefinition([
    "education_scotland",  # Curriculum body
    "sqa",                 # Exam body
    "hmie",                # Inspectorate
])
"""Scotland education source partitions."""

wales_source_partitions = StaticPartitionsDefinition([
    "curriculum_for_wales",  # Welsh curriculum
    "wjec",                  # Exam board
    "estyn",                 # Inspectorate
])
"""Wales education source partitions."""

ni_source_partitions = StaticPartitionsDefinition([
    "ccea",     # Exam board
    "eti",      # Inspectorate
    "deni",     # Department
])
"""Northern Ireland education source partitions."""


# ============================================================================
# Celtic Corpus Source Partitions
# ============================================================================

celtic_source_partitions = StaticPartitionsDefinition([
    "duchas",    # Folklore collection
    "canuint",   # Pronunciation recordings
    "tearma",    # Terminology
    "logainm",   # Placenames
    "treebank",  # Universal Dependencies
])
"""Celtic corpus source partitions."""


# ============================================================================
# Geospatial Source Partitions
# ============================================================================

geospatial_source_partitions = StaticPartitionsDefinition([
    "geohive",          # Irish boundaries (GeoHive.ie)
    "cso_small_areas",  # Irish Small Areas (18,641)
    "ons_lsoa",         # UK LSOAs
    "met_office",       # UK weather
    "ordnance_survey",  # Irish/UK mapping
])
"""Geospatial data source partitions."""


# ============================================================================
# Multi-Dimensional Partitions
# ============================================================================

# Ireland: source × language
ireland_multipartitions = MultiPartitionsDefinition({
    "source": ireland_source_partitions,
    "language": StaticPartitionsDefinition(["en", "ga"]),
})
"""Ireland multi-partition: source × language."""

# Celtic: corpus × language
celtic_multipartitions = MultiPartitionsDefinition({
    "corpus": celtic_source_partitions,
    "language": language_partitions,
})
"""Celtic multi-partition: corpus × language."""

# UK: nation × source type
uk_multipartitions = MultiPartitionsDefinition({
    "nation": uk_nation_partitions,
    "source_type": StaticPartitionsDefinition([
        "curriculum",
        "examinations",
        "statistics",
        "inspections",
    ]),
})
"""UK multi-partition: nation × source type."""

# Geospatial: source × region
geospatial_multipartitions = MultiPartitionsDefinition({
    "source": geospatial_source_partitions,
    "region": StaticPartitionsDefinition([
        "ireland",
        "northern_ireland",
        "scotland",
        "wales",
        "england",
    ]),
})
"""Geospatial multi-partition: source × region."""


# ============================================================================
# Partition Helpers
# ============================================================================

def get_dialect_for_province(province: str) -> str:
    """Map Canuint province to dialect region."""
    mapping = {
        "Cúige Mumhan": "munster",
        "Cúige Connacht": "connacht",
        "Cúige Uladh": "ulster",
        "Caighdeán Oifigiúil": "standard",
    }
    return mapping.get(province, "standard")


def get_nation_for_domain(domain: str) -> list[str]:
    """Get nations belonging to a domain."""
    domain_nations = {
        "ireland": ["ireland"],
        "uk": ["england", "scotland", "wales", "northern_ireland"],
        "celtic": ["ireland", "scotland", "wales"],
    }
    return domain_nations.get(domain, [])


def get_languages_for_nation(nation: str) -> list[str]:
    """Get Celtic languages relevant to a nation."""
    nation_languages = {
        "ireland": ["ga"],
        "scotland": ["gd"],
        "wales": ["cy"],
        "northern_ireland": ["ga"],
        "isle_of_man": ["gv"],
        "england": ["kw"],  # Cornwall
    }
    return nation_languages.get(nation, [])


# ============================================================================
# Partition Key Generators
# ============================================================================

def generate_ireland_partition_keys(
    sources: list[str] | None = None,
    languages: list[str] | None = None,
) -> list[dict[str, str]]:
    """Generate partition keys for Ireland multi-partition."""
    sources = sources or ["curriculumonline", "ncca", "examinations", "cso"]
    languages = languages or ["en", "ga"]

    return [
        {"source": source, "language": lang}
        for source in sources
        for lang in languages
    ]


def generate_celtic_partition_keys(
    corpora: list[str] | None = None,
    languages: list[str] | None = None,
) -> list[dict[str, str]]:
    """Generate partition keys for Celtic multi-partition."""
    corpora = corpora or ["duchas", "canuint", "tearma", "logainm", "treebank"]
    languages = languages or ["ga", "gd", "cy", "gv", "kw", "br"]

    return [
        {"corpus": corpus, "language": lang}
        for corpus in corpora
        for lang in languages
    ]


def generate_uk_partition_keys(
    nations: list[str] | None = None,
    source_types: list[str] | None = None,
) -> list[dict[str, str]]:
    """Generate partition keys for UK multi-partition."""
    nations = nations or ["england", "scotland", "wales", "northern_ireland"]
    source_types = source_types or ["curriculum", "examinations", "statistics", "inspections"]

    return [
        {"nation": nation, "source_type": st}
        for nation in nations
        for st in source_types
    ]


def generate_ncca_partition_keys(
    cycles: list[str] | None = None,
    subjects: list[str] | None = None,
    languages: list[str] | None = None,
) -> list[dict[str, str]]:
    """Generate partition keys for NCCA multi-partition.

    Args:
        cycles: List of cycles (default: all 4)
        subjects: List of subjects (default: all 26)
        languages: List of languages (default: en, ga)

    Returns:
        List of partition key dicts matching Dagster 2D format:
        {"cycle_subject": "primary__mathematics", "language": "en"}
    """
    cycles = cycles or ["early_childhood", "primary", "junior_cycle", "senior_cycle"]
    subjects = subjects or [
        "english", "irish", "mathematics", "science", "technology", "engineering",
        "history", "geography", "religious_education", "french", "german", "spanish",
        "art", "music", "drama", "pe", "sphe", "cspe", "wellbeing",
        "business", "economics", "home_economics", "applied_technology",
        "graphics", "wood_technology", "metalwork",
    ]
    languages = languages or ["en", "ga"]

    return [
        {"cycle_subject": f"{cycle}__{subject}", "language": lang}
        for cycle in cycles
        for subject in subjects
        for lang in languages
    ]


def generate_ncca_core_partition_keys(
    languages: list[str] | None = None,
) -> list[dict[str, str]]:
    """Generate partition keys for NCCA core (reduced) multi-partition.

    Uses only 3 cycles × 3 subjects = 9 combinations per language.
    """
    return generate_ncca_partition_keys(
        cycles=["primary", "junior_cycle", "senior_cycle"],
        subjects=["english", "irish", "mathematics"],
        languages=languages or ["en", "ga"],
    )


def parse_ncca_partition_key(partition_key: dict[str, str]) -> dict[str, str]:
    """Parse NCCA partition key dict into cycle, subject, language.

    Args:
        partition_key: {"cycle_subject": "primary__mathematics", "language": "en"}

    Returns:
        {"cycle": "primary", "subject": "mathematics", "language": "en"}
    """
    cycle_subject = partition_key.get("cycle_subject", "primary__mathematics")
    # Split on double underscore (but handle cycle names with single underscores)
    parts = cycle_subject.split("__")
    return {
        "cycle": parts[0],
        "subject": parts[1] if len(parts) > 1 else "mathematics",
        "language": partition_key.get("language", "en"),
    }


def generate_sec_partition_keys(
    subjects: list[str] | None = None,
    years: list[str] | None = None,
    levels: list[str] | None = None,
) -> list[dict[str, str]]:
    """Generate partition keys for SEC examinations multi-partition.

    Args:
        subjects: List of subjects (default: all)
        years: List of years as strings (default: 2015-2024)
        levels: List of exam levels (default: all 3)

    Returns:
        List of partition key dicts matching Dagster 2D format:
        {"subject_year": "mathematics__2023", "level": "leaving_cert_higher"}
    """
    subjects = subjects or [
        "english", "irish", "mathematics", "science", "technology", "engineering",
        "history", "geography", "religious_education", "french", "german", "spanish",
        "art", "music", "drama", "pe", "sphe", "cspe", "wellbeing",
        "business", "economics", "home_economics", "applied_technology",
        "graphics", "wood_technology", "metalwork",
    ]
    years = years or [str(y) for y in range(2015, 2025)]
    levels = levels or ["leaving_cert_higher", "leaving_cert_ordinary", "junior_cycle"]

    return [
        {"subject_year": f"{subject}__{year}", "level": level}
        for subject in subjects
        for year in years
        for level in levels
    ]


def parse_sec_partition_key(partition_key: dict[str, str]) -> dict[str, str]:
    """Parse SEC partition key dict into subject, year, level.

    Args:
        partition_key: {"subject_year": "mathematics__2023", "level": "leaving_cert_higher"}

    Returns:
        {"subject": "mathematics", "year": "2023", "level": "leaving_cert_higher"}
    """
    subject_year = partition_key.get("subject_year", "mathematics__2023")
    parts = subject_year.split("__")
    return {
        "subject": parts[0],
        "year": parts[1] if len(parts) > 1 else "2023",
        "level": partition_key.get("level", "leaving_cert_higher"),
    }
