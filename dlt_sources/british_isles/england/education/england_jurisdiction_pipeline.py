"""England jurisdiction pipeline (BIEP v3 — generic).

Per the 2026-07-29-biep-v3-england-full-coverage-v1 change +
2026-08-10-biep-v3-preflight-bug-fixes-v1 inheritance refactor.

The canonical generic England DLT pipeline. Replaces the per-board
per-subject DLT sources in
`dlt/british_isles/england/education/subjects/_factory.py` (which
generated 54 per-board per-subject per-level source functions).

This single file reads the canonical registry
(`cianfhoghlaim.education._registry.subjects` filtered by
`jurisdiction='england'`) and materialises the 276 England cohorts:

  - 43 GCSE subjects × 3 boards (AQA + OCR + Edexcel) = 129 cohorts
  - 49 A-Level subjects × 3 boards = 147 cohorts
  - 88 + 88 distinct subjects per board = 264 distinct per-board cohorts
  - 43 GCSE + 49 A-Level × 3 = **276 unique qualifications**

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect``).
- dlt (per `.agents/skills/dlt/SKILL.md`) — the canonical destination
  factory at ``dlt.common.destinations_cianfhoghlaim`` is used.
- JurisdictionPipelineBase (per the 2026-08-10 preflight change) —
  inherits shared boilerplate.

Reference: openspec/changes/2026-07-29-biep-v3-england-full-coverage-v1/
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from dlt.british_isles._cross.jurisdiction_pipeline_base import (
    JurisdictionPipelineBase,
)

logger = logging.getLogger(__name__)

ENGLAND_CACHE_ROOT = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "england"

# The 3 England awarding bodies
ENGLAND_BOARDS: tuple[str, ...] = ("aqa", "ocr", "edexcel")

# The 2 qualification levels
ENGLAND_LEVELS: tuple[str, ...] = ("gcse", "a_level")


class EnglandJurisdictionPipeline(JurisdictionPipelineBase):
    """England jurisdiction pipeline (BIEP v3)."""

    STAGE = "gcse"

    def build_pipeline_resource(self):
        """Yield one row per (board, subject, level) cohort from the registry."""
        from dlt.british_isles._cross.registry_api import query_by_jurisdiction

        subjects = query_by_jurisdiction(self.jurisdiction)
        if not subjects:
            raise ValueError(
                f"No subjects found in the registry for "
                f"jurisdiction={self.jurisdiction!r}. "
                "Run seed_registry() first."
            )

        logger.info(
            "england_jurisdiction_pipeline: discovered %d subjects for "
            "jurisdiction=%r",
            len(subjects), self.jurisdiction,
        )

        for row in subjects:
            yield self.subject_to_row(row, self.STAGE)


england_jurisdiction_pipeline = EnglandJurisdictionPipeline("england")


__all__ = [
    "EnglandJurisdictionPipeline",
    "england_jurisdiction_pipeline",
    "ENGLAND_CACHE_ROOT",
    "ENGLAND_BOARDS",
    "ENGLAND_LEVELS",
]