"""dlt_sources.education.university.british_isles.university — British Isles tertiary pipelines.

The generalised factory + per-institution sources for the British
Isles tertiary surface. Reference:
openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
            specs/cianfhoghlaim-british-isles-tertiary-factory/spec.md
"""

from .british_isles_tertiary_factory import (
    BINation,
    BITertiaryDeepExtractionConfig,
    bitertiary_qub_source,
    bitertiary_ulster_source,
    bitertiary_universities_factory,
)

__all__ = [
    "BINation",
    "BITertiaryDeepExtractionConfig",
    "bitertiary_qub_source",
    "bitertiary_ulster_source",
    "bitertiary_universities_factory",
]
