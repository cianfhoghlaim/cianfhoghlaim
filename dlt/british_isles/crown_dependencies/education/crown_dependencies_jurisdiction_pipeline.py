"""Generic Crown Dependencies pipeline (BIEP v3).

Per the 2026-07-31-biep-v3-crown-dependencies-v1 change.

Handles the 3 Crown Dependencies (Jersey + Guernsey + Isle of Man) via
a single generic factory. The 3 jurisdictions use the English GCSE +
A-Level system (with a small number of additional local qualifications
like French Baccalauréat in Jersey).

Covers:
  - Jersey: 30 subjects × 4 levels (GCSE + A-Level + IB + French Bac) = ~120 cohorts
  - Guernsey: 30 subjects × 4 levels = ~120 cohorts
  - Isle of Man: 30 subjects × 4 levels = ~120 cohorts

= **~360 unique qualifications** across the 3 Crown Dependencies
(approximate; will be finalised at registry seed time).

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect``).
- dlt (per `.agents/skills/dlt/SKILL.md`) — the canonical destination
  factory at ``dlt.common.destinations_cianfhoghlaim`` is used.

Reference: openspec/changes/2026-07-31-biep-v3-crown-dependencies-v1/
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

CROWN_DEPENDENCIES: tuple[str, ...] = ("jersey", "guernsey", "isle_of_man")


def crown_dependencies_jurisdiction_pipeline(
    jurisdiction: str,
    dataset_name: str | None = None,
    use_md: bool = True,
):
    """The canonical generic Crown Dependencies DLT pipeline.

    Handles the 3 Crown Dependencies (Jersey + Guernsey + Isle of Man)
    via a single factory function. The jurisdiction argument selects
    which registry rows to materialise.
    """
    if jurisdiction not in CROWN_DEPENDENCIES:
        raise ValueError(
            f"jurisdiction={jurisdiction!r} not in CROWN_DEPENDENCIES. "
            f"Choose from {CROWN_DEPENDENCIES}."
        )

    from dlt.british_isles._cross.registry_api import query_by_jurisdiction

    subjects = query_by_jurisdiction(jurisdiction)
    if not subjects:
        raise ValueError(
            f"No subjects found in the registry for jurisdiction={jurisdiction!r}. "
            "Run seed_registry() first."
        )

    logger.info(
        "crown_dependencies_jurisdiction_pipeline: discovered %d subjects for %r",
        len(subjects), jurisdiction,
    )

    @dlt.resource(
        name=f"crown_dependencies_{jurisdiction}_subjects",
        write_disposition="merge",
        primary_key=["content_hash"],
    )
    def crown_dependencies_subjects():
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
    return pipeline, crown_dependencies_subjects


__all__ = [
    "crown_dependencies_jurisdiction_pipeline",
    "CROWN_DEPENDENCIES",
]