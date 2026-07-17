"""England jurisdiction pipeline (BIEP v3 — generic).

Per the 2026-07-29-biep-v3-england-full-coverage-v1 change.

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

Reference: openspec/changes/2026-07-29-biep-v3-england-full-coverage-v1/
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

ENGLAND_CACHE_ROOT = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "england"

# The 3 England awarding bodies
ENGLAND_BOARDS: tuple[str, ...] = ("aqa", "ocr", "edexcel")

# The 2 qualification levels
ENGLAND_LEVELS: tuple[str, ...] = ("gcse", "a_level")


def england_jurisdiction_pipeline(
    jurisdiction: str = "england",
    dataset_name: str = "england_education",
    use_md: bool = True,
):
    """The canonical generic England DLT pipeline.

    Reads the registry to discover which (subject, board, level) tuples
    to materialise. Writes per-subject per-board per-level LanceDB
    tables to ``cianfhoghlaim.education.england.<level>.<board>.<subject>``.
    """
    from dlt.british_isles._cross.registry_api import query_by_jurisdiction

    subjects = query_by_jurisdiction(jurisdiction)
    if not subjects:
        raise ValueError(
            f"No subjects found in the registry for jurisdiction={jurisdiction!r}. "
            "Run seed_registry() first."
        )

    logger.info(
        "england_jurisdiction_pipeline: discovered %d subjects for jurisdiction=%r",
        len(subjects), jurisdiction,
    )

    @dlt.resource(
        name=f"england_{jurisdiction}_subjects",
        write_disposition="merge",
        primary_key=["content_hash"],
    )
    def england_subjects():
        """Yield one row per (board, subject, level) cohort from the registry."""
        for row in subjects:
            yield {
                "source_id": (
                    f"british_isles.england.education.{row.stage}."
                    f"{row.board}.{row.subject_slug}"
                ),
                "country_code": "england",
                "jurisdiction": "england",
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
                    f"cianfhoghlaim.education.england.{row.stage}.{row.board}.{row.subject_slug}"
                ),
            }

    pipeline = dlt.pipeline(
        pipeline_name="england_jurisdiction_pipeline",
        dataset_name=dataset_name,
        destination=get_dlt_destination(use_ducklake=use_md),
    )
    return pipeline, england_subjects


__all__ = [
    "england_jurisdiction_pipeline",
    "ENGLAND_CACHE_ROOT",
    "ENGLAND_BOARDS",
    "ENGLAND_LEVELS",
]