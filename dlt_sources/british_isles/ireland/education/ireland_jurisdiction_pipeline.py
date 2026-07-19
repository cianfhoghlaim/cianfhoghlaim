"""Ireland jurisdiction pipeline (BIEP v3 — generic).

Per the 2026-07-28-biep-v3-ireland-full-coverage-v1 change +
2026-08-10-biep-v3-preflight-bug-fixes-v1 inheritance refactor.

The canonical generic Ireland DLT pipeline. Replaces ~100 per-subject
DLT source files. This single file reads the canonical registry
(`cianfhoghlaim.education._registry.subjects`) and materialises the
544 Ireland cohorts:

  - 64 LC subjects × 3 qualification levels × 2 languages = 384 cohorts
  - 18 JC subjects × 3 years × 2 languages = 108 cohorts
  - 16 JC short courses × 1 level × 1 language = 16 cohorts
  - 36 JC CBAs × 1 year × 1 language = 36 cohorts

= **544 total cohorts**.

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect``).
- dlt (per `.agents/skills/dlt/SKILL.md`) — the canonical destination
  factory at ``dlt.common.destinations_cianfhoghlaim`` is used.
- JurisdictionPipelineBase (per the 2026-08-10 preflight change) —
  inherits shared boilerplate.

Reference: openspec/changes/2026-07-28-biep-v3-ireland-full-coverage-v1/
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from dlt.british_isles._cross.jurisdiction_pipeline_base import (
    JurisdictionPipelineBase,
)

logger = logging.getLogger(__name__)

# The canonical Ireland cache root
IRELAND_CACHE_ROOT = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "ireland"


class IrelandJurisdictionPipeline(JurisdictionPipelineBase):
    """Ireland jurisdiction pipeline (BIEP v3)."""

    STAGE = "leaving_certificate"

    def build_pipeline_resource(self):
        """Yield one row per (subject, language) cohort from the registry."""
        from dlt.british_isles._cross.registry_api import query_by_jurisdiction

        subjects = query_by_jurisdiction(self.jurisdiction)
        if not subjects:
            raise ValueError(
                f"No subjects found in the registry for "
                f"jurisdiction={self.jurisdiction!r}. "
                "Run seed_registry() first."
            )

        logger.info(
            "ireland_jurisdiction_pipeline: discovered %d subjects for "
            "jurisdiction=%r",
            len(subjects), self.jurisdiction,
        )

        for row in subjects:
            yield self.subject_to_row(row, self.STAGE)


ireland_jurisdiction_pipeline = IrelandJurisdictionPipeline("ireland")


__all__ = [
    "IrelandJurisdictionPipeline",
    "ireland_jurisdiction_pipeline",
    "IRELAND_CACHE_ROOT",
]