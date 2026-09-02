"""Scotland jurisdiction pipeline (BIEP v3 — generic).

Per the 2026-07-30-biep-v3-sct-wls-ni-v1 change +
2026-08-10-biep-v3-preflight-bug-fixes-v1 inheritance refactor +
2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The canonical generic Scotland DLT pipeline. Replaces the per-board
per-subject DLT source in
`dlt_sources/british_isles/scotland/education/sqa/syllabus_source.py`
(which is the cache-only scaffold).

This file reads the canonical registry
(`cianfhoghlaim.education._registry.subjects` filtered by
`jurisdiction='scotland'`) and materialises the 150 Scotland cohorts:

  - 50 SCQF subjects × 3 qualification levels (National 5 + Higher +
    Advanced Higher) × 1 language (en) = 150 cohorts

## Cianfhoghlaim patterns used
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

# The canonical Scotland cache root
SCOTLAND_CACHE_ROOT = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "scotland"

# The 3 SCQF qualification levels
SCOTLAND_LEVELS: tuple[str, ...] = ("national_5", "higher", "advanced_higher")

# The 1 Scotland awarding body
SCOTLAND_BOARD: str = "sqa"

# The 1 working language (Scotland uses English + Scots Gaelic; Gaelic
# is taught through English in the BIEP v3 v1 spec per the 2026-08-13
# systematic download change)
SCOTLAND_LANGUAGE: str = "en"


class ScotlandJurisdictionPipeline(JurisdictionPipelineBase):
    """Scotland jurisdiction pipeline (BIEP v3)."""

    STAGE = "higher"  # canonical Scotland stage (Higher = the BIEP v3 default)

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
            "scotland_jurisdiction_pipeline: discovered %d subjects for "
            "jurisdiction=%r",
            len(subjects), self.jurisdiction,
        )

        for row in subjects:
            yield self.subject_to_row(row, self.STAGE)


scotland_jurisdiction_pipeline = ScotlandJurisdictionPipeline("scotland")


__all__ = [
    "ScotlandJurisdictionPipeline",
    "scotland_jurisdiction_pipeline",
    "SCOTLAND_CACHE_ROOT",
    "SCOTLAND_LEVELS",
    "SCOTLAND_BOARD",
    "SCOTLAND_LANGUAGE",
]
