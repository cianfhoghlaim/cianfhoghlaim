"""Generic multi-jurisdiction pipeline for Scotland + Wales + NI (BIEP v3).

Per the 2026-07-30-biep-v3-sct-wls-ni-v1 change +
2026-08-10-biep-v3-preflight-bug-fixes-v1 inheritance refactor.

Handles 3 jurisdictions (scotland + wales + northern_ireland) via a
single generic factory. The canonical BAML function
`ExtractUKQualSpec(board: AwardingBody, ...)` is reused — only the
per-board enum (SQA / WJEC / CCEA) differs.

Covers:
  - Scotland: 50 SCQF subjects × 3 levels (National 5 + Higher + Adv Higher) × 2 langs = 600
  - Wales: 80 WJEC subjects × 2 levels (GCSE + A-Level) × 2 langs = 640
  - Northern Ireland: 35 CCEA subjects × 2 levels (GCSE + A-Level) × 2 langs = 280

= **1,520 unique qualifications** across the 3 jurisdictions.

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect``).
- dlt (per `.agents/skills/dlt/SKILL.md`) — the canonical destination
  factory at ``dlt_sources.common.destinations_cianfhoghlaim`` is used.
- JurisdictionPipelineBase (per the 2026-08-10 preflight change) —
  inherits shared boilerplate.

Reference: openspec/changes/2026-07-30-biep-v3-sct-wls-ni-v1/
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from dlt_sources.british_isles._cross.jurisdiction_pipeline_base import (
    JurisdictionPipelineBase,
)

logger = logging.getLogger(__name__)

# The 3 jurisdictions covered by this generic pipeline
SCT_WLS_NI_JURISDICTIONS: tuple[str, ...] = (
    "scotland", "wales", "northern_ireland",
)

# Cache root for all 3
SCT_WLS_NI_CACHE_ROOT = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
)


class SctWlsNiJurisdictionPipeline(JurisdictionPipelineBase):
    """Scotland / Wales / Northern Ireland jurisdiction pipeline (BIEP v3)."""

    STAGE = "gcse"
    VALID_JURISDICTIONS = SCT_WLS_NI_JURISDICTIONS

    def build_pipeline_resource(self):
        """Yield one row per (board, subject, level) cohort from the registry."""
        from dlt_sources.british_isles._cross.registry_api import query_by_jurisdiction

        subjects = query_by_jurisdiction(self.jurisdiction)
        if not subjects:
            raise ValueError(
                f"No subjects found in the registry for "
                f"jurisdiction={self.jurisdiction!r}. "
                "Run seed_registry() first."
            )

        logger.info(
            "sct_wls_ni_jurisdiction_pipeline: discovered %d subjects for "
            "jurisdiction=%r",
            len(subjects), self.jurisdiction,
        )

        for row in subjects:
            yield self.subject_to_row(row, self.STAGE)


# Pre-built instances for the 3 jurisdictions covered by this pipeline.
sct_wls_ni_scotland_pipeline = SctWlsNiJurisdictionPipeline("scotland")
sct_wls_ni_wales_pipeline = SctWlsNiJurisdictionPipeline("wales")
sct_wls_ni_northern_ireland_pipeline = SctWlsNiJurisdictionPipeline("northern_ireland")


def sct_wls_ni_jurisdiction_pipeline(
    jurisdiction: str,
    dataset_name: str | None = None,
    use_md: bool = True,
):
    """The canonical generic Scotland/Wales/NI DLT pipeline factory.

    Covers the 3 jurisdictions (scotland + wales + northern_ireland) via
    a single factory. The jurisdiction argument selects which registry
    rows to materialise.
    """
    return SctWlsNiJurisdictionPipeline(jurisdiction, use_md=use_md)


__all__ = [
    "SctWlsNiJurisdictionPipeline",
    "sct_wls_ni_jurisdiction_pipeline",
    "sct_wls_ni_scotland_pipeline",
    "sct_wls_ni_wales_pipeline",
    "sct_wls_ni_northern_ireland_pipeline",
    "SCT_WLS_NI_JURISDICTIONS",
    "SCT_WLS_NI_CACHE_ROOT",
]