"""
Simplified Partition Definitions for Irish Curriculum Pipeline.

Reduces partition explosion from 208 (4 cycles × 26 subjects × 2 languages)
to 4 cycle-based partitions with subject selection at runtime via config.

Key Changes from partitions.py:
- ireland_curriculum_partitions: 4 partitions (vs 208 in ncca_multipartitions)
- Subject is now runtime config, not partition dimension
- Language is secondary partition (optional) or config

Usage:
    from cianfhoghlaim.dagster.partitions_v2 import (
        ireland_curriculum_partitions,
        get_subjects_for_group,
        CURRICULUM_CONFIG_SCHEMA,
    )

    @asset(partitions_def=ireland_curriculum_partitions)
    def my_asset(context, config):
        cycle = context.partition_key
        subjects = config.get("subjects")  # Runtime subject selection
        ...
"""

from __future__ import annotations

from typing import Any

from dagster import (
    Array,
    Field,
    MultiPartitionsDefinition,
    Noneable,
    StaticPartitionsDefinition,
)

# ============================================================================
# Simplified Curriculum Partitions (4 partitions vs 208)
# ============================================================================

ireland_curriculum_partitions = StaticPartitionsDefinition([
    "early_childhood",
    "primary",
    "junior_cycle",
    "senior_cycle",
])
"""
Ireland curriculum partitions by education cycle.

Reduces 208 partitions to 4 by moving subject selection to runtime config.
Use CURRICULUM_CONFIG_SCHEMA for subject/language configuration.
"""


# Language as optional secondary partition (8 total: 4 cycles × 2 languages)
ireland_curriculum_with_language = MultiPartitionsDefinition({
    "cycle": ireland_curriculum_partitions,
    "language": StaticPartitionsDefinition(["en", "ga"]),
})
"""
Optional: Curriculum partitions with language dimension.
Creates 8 partitions (4 cycles × 2 languages).
Use when you need language-level parallelism.
"""


# ============================================================================
# Subject Groups (for grouped processing)
# ============================================================================

# Core subjects (highest priority, run most frequently)
CORE_SUBJECTS = ["english", "irish", "mathematics"]

# Subject groups for batch processing
SUBJECT_GROUPS = {
    "core": CORE_SUBJECTS,
    "stem": ["science", "technology", "engineering", "computer_science"],
    "humanities": ["history", "geography", "religious_education"],
    "languages": ["french", "german", "spanish", "italian"],
    "arts": ["art", "music", "drama"],
    "applied": ["business", "economics", "home_economics"],
    "practical": ["applied_technology", "graphics", "wood_technology", "engineering"],
    "wellbeing": ["pe", "sphe", "cspe", "wellbeing"],
}

# All subjects (flatten groups)
ALL_SUBJECTS = list(set(s for subjects in SUBJECT_GROUPS.values() for s in subjects))


def get_subjects_for_group(group: str) -> list[str]:
    """
    Get subject slugs for a partition group.

    Args:
        group: Group name (core, stem, humanities, etc.)

    Returns:
        List of subject slugs in that group
    """
    return SUBJECT_GROUPS.get(group, [])


def get_all_subjects() -> list[str]:
    """Get all known subjects."""
    return ALL_SUBJECTS


# ============================================================================
# Config Schemas for Runtime Subject Selection
# ============================================================================

CURRICULUM_CONFIG_SCHEMA = {
    "subjects": Field(
        Noneable(Array(str)),
        default_value=None,
        description="List of subject slugs to process. None = all subjects for the cycle.",
    ),
    "languages": Field(
        Array(str),
        default_value=["en", "ga"],
        description="Languages to crawl. Default: both English and Irish.",
    ),
    "max_pages_per_subject": Field(
        int,
        default_value=50,
        description="Maximum pages to crawl per subject per source.",
    ),
    "sources": Field(
        Array(str),
        default_value=["curriculumonline", "ncca", "examinations"],
        description="Sources to include in the crawl.",
    ),
    "deduplicate": Field(
        bool,
        default_value=True,
        description="Whether to deduplicate content across sources.",
    ),
}
"""
Config schema for curriculum assets.

Enables runtime subject selection without partition explosion.

Example config:
    {
        "subjects": ["irish", "mathematics"],
        "languages": ["en", "ga"],
        "max_pages_per_subject": 30,
    }
"""

# Simplified config for common use cases
QUICK_CRAWL_CONFIG_SCHEMA = {
    "subjects": Field(Array(str), default_value=CORE_SUBJECTS),
    "languages": Field(Array(str), default_value=["en"]),
    "max_pages_per_subject": Field(int, default_value=20),
}
"""Minimal config for quick test crawls (core subjects, English only)."""


# ============================================================================
# Helper Functions
# ============================================================================

def parse_cycle_config(
    partition_key: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    """
    Parse partition key and config into crawl parameters.

    Args:
        partition_key: Cycle partition key (e.g., "junior_cycle")
        config: Runtime config dictionary

    Returns:
        Dictionary with all crawl parameters
    """
    return {
        "cycle": partition_key,
        "subjects": config.get("subjects"),  # None = all
        "languages": config.get("languages", ["en", "ga"]),
        "max_pages_per_subject": config.get("max_pages_per_subject", 50),
        "sources": config.get("sources", ["curriculumonline", "ncca", "examinations"]),
        "deduplicate": config.get("deduplicate", True),
    }


def validate_subjects(subjects: list[str] | None, cycle: str) -> list[str] | None:
    """
    Validate that requested subjects are available in the cycle.

    Args:
        subjects: List of subject slugs or None
        cycle: Education cycle

    Returns:
        Validated subject list or None
    """
    if subjects is None:
        return None

    # Import registry to check subject availability
    try:
        from cianfhoghlaim.dlt.common.curriculum_registry import (
            SubjectRegistry,
        )

        registry = SubjectRegistry.from_default()
        cycle_subjects = [s.slug for s in registry.get_subjects_for_cycle(cycle)]

        valid_subjects = [s for s in subjects if s in cycle_subjects]

        if len(valid_subjects) != len(subjects):
            invalid = set(subjects) - set(valid_subjects)
            import structlog
            logger = structlog.get_logger(__name__)
            logger.warning(
                "invalid_subjects_for_cycle",
                cycle=cycle,
                invalid_subjects=list(invalid),
            )

        return valid_subjects if valid_subjects else None

    except ImportError:
        # Registry not available, return as-is
        return subjects


# ============================================================================
# Legacy Compatibility (for gradual migration)
# ============================================================================

# Keep these for backward compatibility during migration
# Will be removed after validation

ireland_cycle_partitions = ireland_curriculum_partitions
"""Alias for backward compatibility."""

ireland_language_partitions = StaticPartitionsDefinition(["en", "ga"])
"""Language partitions (kept for assets that need separate language processing)."""


# ============================================================================
# Comparison with Old Partitions
# ============================================================================

"""
Partition Comparison:

OLD (partitions.py):
- ncca_multipartitions: 208 partitions (4 cycles × 26 subjects × 2 languages)
- ncca_core_multipartitions: 18 partitions (3 cycles × 3 subjects × 2 languages)
- sec_multipartitions: 780 partitions (26 subjects × 10 years × 3 levels)

NEW (partitions_v2.py):
- ireland_curriculum_partitions: 4 partitions (cycles only)
- ireland_curriculum_with_language: 8 partitions (cycles × languages)

Subject selection moved to runtime config:
- Before: Select partition "junior_cycle__mathematics|en"
- After: Select partition "junior_cycle" with config {"subjects": ["mathematics"]}

Benefits:
1. Reduced partition explosion (4 vs 208)
2. Dynamic subject selection at runtime
3. Easier backfills (select cycle, let config handle subjects)
4. Cleaner Dagster UI (4 partitions vs 208)
5. No partition conflicts between assets
"""
