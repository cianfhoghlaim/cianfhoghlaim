"""Jersey jurisdiction pipeline (BIEP v3 — generic).

Per the 2026-07-31-biep-v3-crown-dependencies-v1 change +
2026-08-10-biep-v3-preflight-bug-fixes-v1 inheritance refactor +
2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The canonical generic Jersey DLT pipeline. Replaces the cache-only
scaffold at `dlt_sources/british_isles/jersey/education/island/jersey_education.py`.

Jersey has its own curriculum (a hybrid of English GCSE + French
Baccalauréat). The Jersey Curriculum is administered by the States of
Jersey Education Department.

This file reads the canonical registry
(`cianfhoghlaim.education._registry.subjects` filtered by
`jurisdiction='jersey'`) and materialises the 120 Jersey cohorts:

  - 30 subjects × 4 qualification levels (GCSE + A-Level + IB + French
    Bac) × 1 language (en) = 120 cohorts

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect``).
- dlt (per `.agents/skills/dlt/SKILL.md`) — the canonical destination
  factory at ``dlt_sources.common.destinations_cianfhoghlaim`` is used.
- JurisdictionPipelineBase (per the 2026-08-10 preflight change) —
  inherits shared boilerplate.

Reference: openspec/changes/2026-07-31-biep-v3-crown-dependencies-v1/
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

# The canonical Jersey cache root
JERSEY_CACHE_ROOT = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "jersey"

# The 4 Jersey qualification levels (English GCSE + A-Level + IB + French Bac)
JERSEY_LEVELS: tuple[str, ...] = ("gcse", "a_level", "ib", "french_bac")

# The 1 Jersey awarding body
JERSEY_BOARD: str = "jersey"

# The 1 working language (English; French Baccalauréat is taught in French
# but the BIEP v3 v1 spec uses the English metadata)
JERSEY_LANGUAGE: str = "en"


class JerseyJurisdictionPipeline(JurisdictionPipelineBase):
    """Jersey jurisdiction pipeline (BIEP v3)."""

    STAGE = "gcse"  # canonical Jersey stage (GCSE = the BIEP v3 default)

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
            "jersey_jurisdiction_pipeline: discovered %d subjects for "
            "jurisdiction=%r",
            len(subjects), self.jurisdiction,
        )

        for row in subjects:
            yield self.subject_to_row(row, self.STAGE)


jersey_jurisdiction_pipeline = JerseyJurisdictionPipeline("jersey")


__all__ = [
    "JerseyJurisdictionPipeline",
    "jersey_jurisdiction_pipeline",
    "JERSEY_CACHE_ROOT",
    "JERSEY_LEVELS",
    "JERSEY_BOARD",
    "JERSEY_LANGUAGE",
]
