"""Wales jurisdiction pipeline (BIEP v3 — generic).

Per the 2026-07-30-biep-v3-sct-wls-ni-v1 change +
2026-08-10-biep-v3-preflight-bug-fixes-v1 inheritance refactor +
2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The canonical generic Wales DLT pipeline. Replaces the per-board
per-subject DLT source in
`dlt_sources/british_isles/wales/education/wjec/syllabus_source.py`
(which is the cache-only scaffold).

This file reads the canonical registry
(`cianfhoghlaim.education._registry.subjects` filtered by
`jurisdiction='wales'`) and materialises the 160 Wales cohorts:

  - 80 WJEC subjects × 2 qualification levels (GCSE + A-Level) × 1
    language (cy = Cymraeg / Welsh) = 160 cohorts

The Welsh-medium overlay (cy language) is the BIEP v3 v1 spec default per
the 2026-08-13 systematic download change. English-medium subjects
can be loaded separately via the `baml_function` field of the registry.

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

# The canonical Wales cache root
WALES_CACHE_ROOT = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "wales"

# The 2 WJEC qualification levels
WALES_LEVELS: tuple[str, ...] = ("gcse", "a_level")

# The 1 Wales awarding body
WALES_BOARD: str = "wjec"

# The 1 working language (Welsh-medium subjects are flagged via the
# language field (cy = Cymraeg / Welsh))
WALES_LANGUAGE: str = "cy"


class WalesJurisdictionPipeline(JurisdictionPipelineBase):
    """Wales jurisdiction pipeline (BIEP v3)."""

    STAGE = "gcse"  # canonical Wales stage (GCSE = the BIEP v3 default)

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
            "wales_jurisdiction_pipeline: discovered %d subjects for "
            "jurisdiction=%r",
            len(subjects), self.jurisdiction,
        )

        for row in subjects:
            yield self.subject_to_row(row, self.STAGE)


wales_jurisdiction_pipeline = WalesJurisdictionPipeline("wales")


__all__ = [
    "WalesJurisdictionPipeline",
    "wales_jurisdiction_pipeline",
    "WALES_CACHE_ROOT",
    "WALES_LEVELS",
    "WALES_BOARD",
    "WALES_LANGUAGE",
]
