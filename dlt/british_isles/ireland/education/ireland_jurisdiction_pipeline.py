"""Ireland jurisdiction pipeline (BIEP v3 — generic).

Per the 2026-07-28-biep-v3-ireland-full-coverage-v1 change.

The canonical generic Ireland DLT pipeline. Replaces ~100 per-subject
DLT source files:

  - dlt/british_isles/ireland/education/ncca_<subject>.py (6 LC subjects)
  - dlt/british_isles/ireland/education/junior_cycle_subjects/<subject>_<lang>.py (36 files)
  - dlt/british_isles/ireland/education/junior_cycle_short_courses/<course>.py (16 files)
  - dlt/british_isles/ireland/education/junior_cycle_cbas/_factory.py + 36 dynamic
  - dlt/british_isles/ireland/education/subjects/subjects/senior_cycle.py (per-subject crawl)
  - dlt/british_isles/ireland/education/leaving_cert.py (per-subject cache routing)

This single file reads the canonical registry
(`cianfhoghlaim.education._registry.subjects`) and materialises the
134+ Ireland cohorts:

  - 64 LC subjects × 3 qualification levels × 2 languages = 384 cohorts
  - 18 JC subjects × 3 years × 2 languages = 108 cohorts
  - 16 JC short courses × 1 level × 1 language = 16 cohorts
  - 36 JC CBAs × 1 year × 1 language = 36 cohorts

= **544 total cohorts** (vs the prior 6 LC + 18 JC + 16 short courses + 36 CBAs).

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect``).
- dlt (per `.agents/skills/dlt/SKILL.md`) — the canonical destination
  factory at ``dlt.common.destinations_cianfhoghlaim`` is used.
- python (the BIEP v3 generic pipeline pattern).

Reference: openspec/changes/2026-07-28-biep-v3-ireland-full-coverage-v1/
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

# The canonical Ireland cache root
IRELAND_CACHE_ROOT = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "ireland"


def ireland_jurisdiction_pipeline(
    jurisdiction: str = "ireland",
    dataset_name: str = "ireland_education",
    use_md: bool = True,
):
    """The canonical generic Ireland DLT pipeline.

    Reads the registry to discover which (subject, stage, language)
    tuples to materialise. Writes per-subject per-language LanceDB
    tables to ``cianfhoghlaim.education.ireland.<stage>.<subject>[.<variant>]``.

    Returns the DLT pipeline (call ``pipeline.run(source)`` to execute).
    """
    from dlt.british_isles._cross.registry_api import query_by_jurisdiction

    subjects = query_by_jurisdiction(jurisdiction)
    if not subjects:
        raise ValueError(
            f"No subjects found in the registry for jurisdiction={jurisdiction!r}. "
            "Run `python3 -c \"from dlt.british_isles._cross.registry_loader import seed_registry; seed_registry()\"` "
            "to seed the minimal 4-subject Ireland + 4-subject England baseline."
        )

    logger.info(
        "ireland_jurisdiction_pipeline: discovered %d subjects for jurisdiction=%r",
        len(subjects), jurisdiction,
    )

    @dlt.resource(
        name=f"ireland_{jurisdiction}_subjects",
        write_disposition="merge",
        primary_key=["content_hash"],
    )
    def ireland_subjects():
        """Yield one row per (subject, language) cohort from the registry."""
        for row in subjects:
            yield {
                "source_id": f"british_isles.ireland.education.{row.stage}.{row.subject_slug}.{row.language}",
                "country_code": "ireland",
                "jurisdiction": "ireland",
                "education_stage": row.stage,
                "subject": row.subject_slug,
                "language": row.language,
                "baml_function": row.baml_function,
                "concept": row.concept,
                "ncca_spec_code": row.ncca_spec_code,
                "source_url": row.source_url,
                "display_name_en": row.display_name_en,
                "display_name_local": row.display_name_local,
                "first_introduced": row.first_introduced,
                "last_verified": row.last_verified or datetime.now(UTC).isoformat()[:10],
                "ingested_at": datetime.now(UTC).isoformat(),
                "namespace": (
                    f"cianfhoghlaim.education.ireland.{row.stage}.{row.subject_slug}.{row.language}"
                ),
            }

    pipeline = dlt.pipeline(
        pipeline_name="ireland_jurisdiction_pipeline",
        dataset_name=dataset_name,
        destination=get_dlt_destination(use_ducklake=use_md),
    )
    return pipeline, ireland_subjects


__all__ = [
    "ireland_jurisdiction_pipeline",
    "IRELAND_CACHE_ROOT",
]