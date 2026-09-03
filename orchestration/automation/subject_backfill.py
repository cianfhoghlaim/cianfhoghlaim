"""Subject-scoped backfill job — BIEP v3 P2.

Per the 2026-08-08-biep-v3-production-readiness-v1 change.

Selects only the 3 assets (ingestion + extraction + embedding) for the
specific (jurisdiction, stage, subject_slug) scope. Provides a stable
run key based on object hash so duplicate backfills dedupe.
"""
from __future__ import annotations

from dagster import define_asset_job


def make_subject_backfill_job(jurisdiction: str, stage: str, subject_slug: str):
    """Create a subject-scoped backfill job for one (jurisdiction, stage, subject)."""
    return define_asset_job(
        name=f"{jurisdiction}_{stage}_{subject_slug}_backfill",
        selection=[
            f"{jurisdiction}_documents_ingested",
            f"{jurisdiction}_extractions",
            f"{jurisdiction}_embeddings",
        ],
        description=f"Subject-scoped backfill: {jurisdiction}/{stage}/{subject_slug}",
    )


__all__ = ["make_subject_backfill_job"]
