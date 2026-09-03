"""Northern Ireland jurisdiction pipeline (BIEP v3 — generic).

Per the 2026-07-30-biep-v3-sct-wls-ni-v1 change +
2026-08-10-biep-v3-preflight-bug-fixes-v1 inheritance refactor +
2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The canonical generic Northern Ireland DLT pipeline. Replaces the
per-board per-subject DLT source in
`dlt_sources/british_isles/northern_ireland/education/ccea/syllabus_source.py`
(which is the cache-only scaffold).

This file reads the canonical registry
(`cianfhoghlaim.education._registry.subjects` filtered by
`jurisdiction='northern_ireland'`) and materialises the 70 NI cohorts:

  - 35 CCEA subjects × 2 qualification levels (GCSE + A-Level) × 1
    language (en) = 70 cohorts

The Irish-medium (Gaeltacht) overlay is flagged via the language field
and can be loaded separately via the `baml_function` field of the
registry.

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect``).
- dlt (per `.agents/skills/dlt/SKILL.md`) — the canonical destination
  factory at ``dlt_sources.common.destinations_cianfhoghlaim`` is used.
- JurisdictionPipelineBase (per the 2026-08-10 preflight change) —
  inherits shared boilerplate.

Reference: openspec/changes/2026-07-30-biep-v3-sct-wls-ni-v1/
Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from dlt_sources.british_isles._cross.jurisdiction_pipeline_base import (
    JurisdictionPipelineBase,
)

logger = logging.getLogger(__name__)

# The canonical Northern Ireland cache root
NORTHERN_IRELAND_CACHE_ROOT = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "northern_ireland"

# The 2 CCEA qualification levels
NORTHERN_IRELAND_LEVELS: tuple[str, ...] = ("gcse", "a_level")

# The 1 NI awarding body
NORTHERN_IRELAND_BOARD: str = "ccea"

# The 1 working language (English)
NORTHERN_IRELAND_LANGUAGE: str = "en"


class NorthernIrelandJurisdictionPipeline(JurisdictionPipelineBase):
    """Northern Ireland jurisdiction pipeline (BIEP v3)."""

    STAGE = "gcse"  # canonical NI stage (GCSE = the BIEP v3 default)

    def build_pipeline_resource(self):
        """Yield one row per (subject, level) cohort from the registry."""
        from dlt_sources.british_isles._cross.registry_api import query_by_jurisdiction

        subjects = query_by_jurisdiction(self.jurisdiction)
        if not subjects:
            raise ValueError(
                f"No subjects found in the registry for "
                f"jurisdiction={self.jurisdiction!r}. "
                "Run seed_registry() first."
            )

        logger.info(
            "northern_ireland_jurisdiction_pipeline: discovered %d subjects for "
            "jurisdiction=%r",
            len(subjects), self.jurisdiction,
        )

        for row in subjects:
            yield self.subject_to_row(row, self.STAGE)


northern_ireland_jurisdiction_pipeline = NorthernIrelandJurisdictionPipeline("northern_ireland")


__all__ = [
    "NorthernIrelandJurisdictionPipeline",
    "northern_ireland_jurisdiction_pipeline",
    "NORTHERN_IRELAND_CACHE_ROOT",
    "NORTHERN_IRELAND_LEVELS",
    "NORTHERN_IRELAND_BOARD",
    "NORTHERN_IRELAND_LANGUAGE",
]
