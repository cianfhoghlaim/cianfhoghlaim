"""Generic multi-jurisdiction pipeline for Scotland + Wales + NI (BIEP v3).

Per the 2026-07-30-biep-v3-sct-wls-ni-v1 change.

Handles 3 jurisdictions (scotland + wales + northern_ireland) via a
single generic factory. The canonical BAML function
`ExtractUKQualSpec(board: AwardingBody, ...)` is reused — only the
per-board enum (SQA / WJEC / CCEA) differs.

Covers:
  - Scotland: 50 SCQF subjects × 3 levels (National 5 + Higher + Adv Higher) = 150 cohorts
  - Wales: 80 WJEC subjects × 2 levels (GCSE + A-Level) = 160 cohorts
  - Northern Ireland: 35 CCEA subjects × 2 levels (GCSE + A-Level) = 70 cohorts

= **380 unique qualifications** across the 3 jurisdictions.

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect``).
- dlt (per `.agents/skills/dlt/SKILL.md`) — the canonical destination
  factory at ``dlt.common.destinations_cianfhoghlaim`` is used.

Reference: openspec/changes/2026-07-30-biep-v3-sct-wls-ni-v1/
"""
from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt

from dlt.common.destinations_cianfhoghlaim import (
    with_namespace,
    get_dlt_destination,
    LAKEHOUSE_DUCKDB,
)

logger = logging.getLogger(__name__)

# The 3 jurisdictions covered by this generic pipeline
SCT_WLS_NI_JURISDICTIONS: tuple[str, ...] = ("scotland", "wales", "northern_ireland")

# Cache root for all 3
SCT_WLS_NI_CACHE_ROOT = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
)


def sct_wls_ni_jurisdiction_pipeline(
    jurisdiction: str,
    dataset_name: str | None = None,
    use_md: bool = True,
):
    """The canonical generic Scotland/Wales/NI DLT pipeline.

    Covers the 3 jurisdictions (scotland + wales + northern_ireland) via
    a single factory. The jurisdiction argument selects which registry
    rows to materialise.

    Writes per-subject per-level LanceDB tables to
    ``cianfhoghlaim.education.<jurisdiction>.<stage>.<board>.<subject>``.
    """
    if jurisdiction not in SCT_WLS_NI_JURISDICTIONS:
        raise ValueError(
            f"jurisdiction={jurisdiction!r} not in SCT_WLS_NI_JURISDICTIONS. "
            f"Choose from {SCT_WLS_NI_JURISDICTIONS}."
        )

    from dlt.british_isles._cross.registry_api import query_by_jurisdiction

    subjects = query_by_jurisdiction(jurisdiction)
    if not subjects:
        raise ValueError(
            f"No subjects found in the registry for jurisdiction={jurisdiction!r}. "
            "Run seed_registry() first."
        )

    logger.info(
        "sct_wls_ni_jurisdiction_pipeline: discovered %d subjects for jurisdiction=%r",
        len(subjects), jurisdiction,
    )

    @dlt.resource(
        name=f"sct_wls_ni_{jurisdiction}_subjects",
        write_disposition="merge",
        primary_key=["content_hash"],
    )
    def sct_wls_ni_subjects():
        """Yield one row per (board, subject, level) cohort from the registry."""
        for row in subjects:
            yield {
                "source_id": (
                    f"british_isles.{jurisdiction}.education.{row.stage}."
                    f"{row.board}.{row.subject_slug}"
                ),
                "country_code": jurisdiction,
                "jurisdiction": jurisdiction,
                "education_stage": row.stage,
                "exam_board": row.board,
                "subject": row.subject_slug,
                "qualification_level": row.qualification_level or "untiered",
                "language": row.language,
                "baml_function": row.baml_function,
                "concept": row.concept,
                "source_url": row.source_url,
                "display_name_en": row.display_name_en,
                "display_name_local": row.display_name_local,
                "last_verified": row.last_verified or datetime.now(UTC).isoformat()[:10],
                "ingested_at": datetime.now(UTC).isoformat(),
                "namespace": (
                    f"cianfhoghlaim.education.{jurisdiction}.{row.stage}.{row.board}.{row.subject_slug}"
                ),
            }

    pipeline = dlt.pipeline(
        pipeline_name=f"{jurisdiction}_jurisdiction_pipeline",
        dataset_name=dataset_name or f"{jurisdiction}_education",
        destination=get_dlt_destination(use_ducklake=use_md),
    )
    return pipeline, sct_wls_ni_subjects


__all__ = [
    "sct_wls_ni_jurisdiction_pipeline",
    "SCT_WLS_NI_JURISDICTIONS",
    "SCT_WLS_NI_CACHE_ROOT",
]