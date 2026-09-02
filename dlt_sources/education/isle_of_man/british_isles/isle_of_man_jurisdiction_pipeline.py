"""Isle of Man jurisdiction pipeline (BIEP v3 — generic).

Per the 2026-07-31-biep-v3-crown-dependencies-v1 change +
2026-08-10-biep-v3-preflight-bug-fixes-v1 inheritance refactor +
2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The canonical generic Isle of Man DLT pipeline. Replaces the cache-only
scaffold at `dlt_sources/british_isles/isle_of_man/education/island/isle_of_man.py`.

The Isle of Man uses the English GCSE + A-Level system. Administered by
the Isle of Man Department of Education, Sport and Culture.

This file reads the canonical registry
(`cianfhoghlaim.education._registry.subjects` filtered by
`jurisdiction='isle_of_man'`) and materialises the 120 IoM cohorts:

  - 30 subjects × 4 qualification levels (GCSE + A-Level + IB + Local)
    × 1 language (en) = 120 cohorts

## Cianfhoghlaim patterns used
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

# The canonical Isle of Man cache root
ISLE_OF_MAN_CACHE_ROOT = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "isle_of_man"

# The 4 IoM qualification levels (GCSE + A-Level + IB + Local)
ISLE_OF_MAN_LEVELS: tuple[str, ...] = ("gcse", "a_level", "ib", "local")

# The 1 IoM awarding body
ISLE_OF_MAN_BOARD: str = "isle_of_man"

# The 1 working language (English)
ISLE_OF_MAN_LANGUAGE: str = "en"


class IsleOfManJurisdictionPipeline(JurisdictionPipelineBase):
    """Isle of Man jurisdiction pipeline (BIEP v3)."""

    STAGE = "gcse"  # canonical IoM stage (GCSE = the BIEP v3 default)

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
            "isle_of_man_jurisdiction_pipeline: discovered %d subjects for "
            "jurisdiction=%r",
            len(subjects), self.jurisdiction,
        )

        for row in subjects:
            yield self.subject_to_row(row, self.STAGE)


isle_of_man_jurisdiction_pipeline = IsleOfManJurisdictionPipeline("isle_of_man")


__all__ = [
    "IsleOfManJurisdictionPipeline",
    "isle_of_man_jurisdiction_pipeline",
    "ISLE_OF_MAN_CACHE_ROOT",
    "ISLE_OF_MAN_LEVELS",
    "ISLE_OF_MAN_BOARD",
    "ISLE_OF_MAN_LANGUAGE",
]
