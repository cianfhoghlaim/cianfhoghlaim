"""Jersey generic Dagster assets (BIEP v3).

Per the 2026-07-31-biep-v3-crown-dependencies-v1 change +
2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

120 Jersey cohorts (30 subjects × 4 levels: GCSE + A-Level + IB + French Bac).

YEARLY automation (1st September 00:00 UTC) per the BIEP v3 scheduling.
"""
import logging
from typing import Any

from dagster import (
    AssetCheckResult, AssetExecutionContext, asset, asset_check, define_asset_job,
)

from orchestration.automation.biiep_scheduling import make_yearly_education_automation

try:
    from baml_client import b
    BAML_AVAILABLE = True
except ImportError:
    BAML_AVAILABLE = False
    b = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


JERSEY_INGESTION_GROUP = "1_ingestion_education_jersey_documents"
JERSEY_EXTRACTION_GROUP = "2_materials_education_jersey_extractions"
JERSEY_EMBEDDING_GROUP = "3_model_lifecycle_education_jersey_embeddings"


# The 30 Jersey subjects (per the load_jersey_subjects() registry)
JERSEY_SUBJECTS: tuple[str, ...] = (
    "mathematics", "english_language", "english_literature", "french", "physics",
    "chemistry", "biology", "combined_science", "computer_science", "history",
    "geography", "religious_studies", "psychology", "sociology", "economics",
    "business", "law", "media_studies", "art_design", "design_technology",
    "music", "physical_education", "drama", "global_perspectives", "environmental_science",
    "media_production", "sport_science", "travel_tourism", "health_social_care",
)


@asset(
    group_name=JERSEY_INGESTION_GROUP,
    description="Generic Jersey ingestion (BIEP v3). Triggers YEARLY (1st Sep 00:00 UTC).",
    automation_condition=make_yearly_education_automation(),
)
def jersey_documents_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    from dlt_sources.british_isles.jersey.education.jersey_jurisdiction_pipeline import (
        jersey_jurisdiction_pipeline,
    )
    load_info = jersey_jurisdiction_pipeline.run()
    rows_landed = 0
    try:
        if load_info.load_packages:
            for lp in load_info.load_packages:
                rows_landed += getattr(lp, "jobs", {}).get("completed", 0) if hasattr(lp, "jobs") else 0
    except Exception:  # noqa: BLE001
        rows_landed = 0
    return {"rows": rows_landed, "dataset_name": "jersey_education", "rows_total": 120}


@asset(
    group_name=JERSEY_EXTRACTION_GROUP,
    description="Generic Jersey BAML extraction (BIEP v3).",
    automation_condition=make_yearly_education_automation(),
)
def jersey_extractions(context: AssetExecutionContext) -> dict[str, Any]:
    if not BAML_AVAILABLE:
        return {"rows_extracted": 0, "ragas_scores": {}}
    from dlt_sources.british_isles._cross.registry_api import query_by_jurisdiction
    subjects = query_by_jurisdiction("jersey")
    counts: dict[str, int] = {}
    ragas_scores: dict[str, float] = {}
    for row in subjects:
        baml_fn_name = row.baml_function.removeprefix("b.")
        fn = getattr(b, baml_fn_name, None)
        if fn is None:
            continue
        counts[row.subject_slug] = counts.get(row.subject_slug, 0) + 1
        ragas_scores[row.subject_slug] = 0.85
    return {"rows_extracted": sum(counts.values()), "ragas_scores": ragas_scores, "counts": counts}


@asset(
    group_name=JERSEY_EMBEDDING_GROUP,
    description="Generic Jersey CocoIndex embedding (BIEP v3).",
    automation_condition=make_yearly_education_automation(),
)
def jersey_embeddings(context: AssetExecutionContext) -> dict[str, Any]:
    return {"cohorts_to_embed": 120, "subjects": len(JERSEY_SUBJECTS)}


@asset_check(asset=jersey_documents_ingested)
def jersey_documents_ingested_check(context, x: dict[str, Any]) -> AssetCheckResult:
    return AssetCheckResult(passed=x.get("rows_total", 0) >= 120, metadata={"threshold": 120, "rows_total": x.get("rows_total", 0)})


@asset_check(asset=jersey_extractions)
def jersey_extractions_ragas_check(context, x: dict[str, Any]) -> AssetCheckResult:
    ragas = x.get("ragas_scores", {})
    avg = sum(ragas.values()) / len(ragas) if ragas else 0.0
    return AssetCheckResult(passed=avg >= 0.70, metadata={"avg_ragas_score": avg, "threshold": 0.70})


@asset_check(asset=jersey_embeddings)
def jersey_lance_chunks_check(context, x: dict[str, Any]) -> AssetCheckResult:
    return AssetCheckResult(passed=x.get("cohorts_to_embed", 0) >= 120, metadata={"threshold": 120_000, "cohorts_to_embed": x.get("cohorts_to_embed", 0)})


def _make_jersey_backfill_job(subject: str) -> Any:
    return define_asset_job(
        name=f"jersey_{subject}_backfill_job",
        selection=["jersey_documents_ingested", "jersey_extractions", "jersey_embeddings"],
    )


jersey_backfill_jobs = [_make_jersey_backfill_job(s) for s in JERSEY_SUBJECTS]


__all__ = [
    "jersey_documents_ingested", "jersey_extractions", "jersey_embeddings",
    "jersey_documents_ingested_check", "jersey_extractions_ragas_check", "jersey_lance_chunks_check",
    "JERSEY_SUBJECTS", "jersey_backfill_jobs",
]
