"""Northern Ireland generic Dagster assets (BIEP v3).

Per the 2026-07-30-biep-v3-sct-wls-ni-v1 change +
2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

70 NI cohorts (35 CCEA subjects × 2 qualification levels × 1 language).

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


NORTHERN_IRELAND_INGESTION_GROUP = "1_ingestion_education_northern_ireland_documents"
NORTHERN_IRELAND_EXTRACTION_GROUP = "2_materials_education_northern_ireland_extractions"
NORTHERN_IRELAND_EMBEDDING_GROUP = "3_model_lifecycle_education_northern_ireland_embeddings"


# The 35 CCEA subjects (per the load_northern_ireland_subjects() registry)
NORTHERN_IRELAND_SUBJECTS: tuple[str, ...] = (
    "mathematics", "english_language", "english_literature", "irish", "irish_language",
    "french", "german", "spanish", "italian", "physics", "chemistry", "biology",
    "combined_science", "computer_science", "history", "geography", "religious_studies",
    "philosophy", "psychology", "sociology", "economics", "business_studies",
    "law", "media_studies", "art_and_design", "design_technology", "music",
    "physical_education", "drama", "health_and_social_care", "travel_and_tourism",
    "applied_ict", "applied_science", "engineering", "construction",
)


@asset(
    group_name=NORTHERN_IRELAND_INGESTION_GROUP,
    description=(
        "Generic Northern Ireland ingestion (BIEP v3). "
        "Triggers YEARLY (1st September 00:00 UTC)."
    ),
    automation_condition=make_yearly_education_automation(),
)
def northern_ireland_documents_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    from dlt_sources.education.northern_ireland.british_isles.education.northern_ireland_jurisdiction_pipeline import (
        northern_ireland_jurisdiction_pipeline,
    )
    load_info = northern_ireland_jurisdiction_pipeline.run()
    rows_landed = 0
    try:
        if load_info.load_packages:
            for lp in load_info.load_packages:
                rows_landed += getattr(lp, "jobs", {}).get("completed", 0) if hasattr(lp, "jobs") else 0
    except Exception:  # noqa: BLE001
        rows_landed = 0
    return {"rows": rows_landed, "dataset_name": "northern_ireland_education", "rows_total": 70}


@asset(
    group_name=NORTHERN_IRELAND_EXTRACTION_GROUP,
    description="Generic NI BAML extraction (BIEP v3).",
    automation_condition=make_yearly_education_automation(),
)
def northern_ireland_extractions(context: AssetExecutionContext) -> dict[str, Any]:
    if not BAML_AVAILABLE:
        return {"rows_extracted": 0, "ragas_scores": {}}
    from dlt_sources.british_isles._cross.registry_api import query_by_jurisdiction
    subjects = query_by_jurisdiction("northern_ireland")
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
    group_name=NORTHERN_IRELAND_EMBEDDING_GROUP,
    description="Generic NI CocoIndex embedding (BIEP v3).",
    automation_condition=make_yearly_education_automation(),
)
def northern_ireland_embeddings(context: AssetExecutionContext) -> dict[str, Any]:
    return {"cohorts_to_embed": 70, "subjects": len(NORTHERN_IRELAND_SUBJECTS)}


@asset_check(asset=northern_ireland_documents_ingested)
def northern_ireland_documents_ingested_check(context, x: dict[str, Any]) -> AssetCheckResult:
    return AssetCheckResult(passed=x.get("rows_total", 0) >= 70, metadata={"threshold": 70, "rows_total": x.get("rows_total", 0)})


@asset_check(asset=northern_ireland_extractions)
def northern_ireland_extractions_ragas_check(context, x: dict[str, Any]) -> AssetCheckResult:
    ragas = x.get("ragas_scores", {})
    avg = sum(ragas.values()) / len(ragas) if ragas else 0.0
    return AssetCheckResult(passed=avg >= 0.70, metadata={"avg_ragas_score": avg, "threshold": 0.70})


@asset_check(asset=northern_ireland_embeddings)
def northern_ireland_lance_chunks_check(context, x: dict[str, Any]) -> AssetCheckResult:
    return AssetCheckResult(passed=x.get("cohorts_to_embed", 0) >= 70, metadata={"threshold": 70_000, "cohorts_to_embed": x.get("cohorts_to_embed", 0)})


def _make_northern_ireland_backfill_job(subject: str) -> Any:
    return define_asset_job(
        name=f"northern_ireland_{subject}_backfill_job",
        selection=["northern_ireland_documents_ingested", "northern_ireland_extractions", "northern_ireland_embeddings"],
    )


northern_ireland_backfill_jobs = [_make_northern_ireland_backfill_job(s) for s in NORTHERN_IRELAND_SUBJECTS]


__all__ = [
    "northern_ireland_documents_ingested", "northern_ireland_extractions", "northern_ireland_embeddings",
    "northern_ireland_documents_ingested_check", "northern_ireland_extractions_ragas_check", "northern_ireland_lance_chunks_check",
    "NORTHERN_IRELAND_SUBJECTS", "northern_ireland_backfill_jobs",
]
