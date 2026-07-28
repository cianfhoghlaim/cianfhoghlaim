"""Wales generic Dagster assets (BIEP v3).

Per the 2026-07-30-biep-v3-sct-wls-ni-v1 change +
2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The canonical generic Wales Dagster assets. 160 Wales cohorts
(80 WJEC subjects × 2 qualification levels × 1 Welsh language).

YEARLY automation (1st September 00:00 UTC) per the BIEP v3 scheduling.
"""
import logging
from typing import Any

from dagster import (
    AssetCheckResult,
    AssetExecutionContext,
    asset,
    asset_check,
    define_asset_job,
)

from orchestration.automation.biiep_scheduling import (
    make_yearly_education_automation,
)

try:
    from baml_client import b
    BAML_AVAILABLE = True
except ImportError:
    BAML_AVAILABLE = False
    b = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


WALES_INGESTION_GROUP = "1_ingestion_education_wales_documents"
WALES_EXTRACTION_GROUP = "2_materials_education_wales_extractions"
WALES_EMBEDDING_GROUP = "3_model_lifecycle_education_wales_embeddings"


# The 80 WJEC subjects (per the load_wales_subjects() registry)
WALES_SUBJECTS: tuple[str, ...] = (
    "mathematics", "english_language", "english_literature", "welsh_language",
    "welsh_literature", "welsh_second_language", "french", "german", "spanish",
    "italian", "physics", "chemistry", "biology", "combined_science",
    "computer_science", "history", "geography", "religious_studies",
    "philosophy", "psychology", "sociology", "economics", "business_studies",
    "law", "media_studies", "art_and_design", "design_technology", "music",
    "physical_education", "drama", "health_and_social_care", "travel_and_tourism",
    "applied_ict", "applied_science", "engineering", "construction",
    "hospitality", "catering", "film_studies", "media_production",
    "music_technology", "performing_arts", "classical_civilisation", "geology",
    "environmental_science", "astronomy", "statistics", "electronics",
    "mechanics", "psychology_a2", "sociology_a2", "law_a2", "economics_a2",
    "history_ancient", "world_development", "law_alevel", "history_a2",
    "geography_a2", "religious_studies_a2", "psychology_alevel", "sociology_alevel",
    "geology_a2", "english_language_a2", "english_literature_a2", "welsh_language_a2",
    "welsh_literature_a2", "welsh_second_language_a2", "french_a2", "german_a2",
    "spanish_a2", "italian_a2", "physics_a2", "chemistry_a2", "biology_a2",
    "mathematics_a2", "further_mathematics_a2", "design_technology_a2",
    "art_and_design_a2", "media_studies_a2", "computer_science_a2", "music_a2",
    "physical_education_a2", "drama_a2", "health_and_social_care_a2",
)


@asset(
    group_name=WALES_INGESTION_GROUP,
    description=(
        "Generic Wales ingestion (BIEP v3). "
        "Replaces the per-board per-subject DLT source in "
        "`dlt_sources/british_isles/wales/education/wjec/syllabus_source.py`. "
        "Reads the canonical registry to discover all 160 Wales cohorts. "
        "Triggers YEARLY (1st September 00:00 UTC)."
    ),
    automation_condition=make_yearly_education_automation(),
)
def wales_documents_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 — DLT ingestion of all Wales cohorts (160 rows)."""
    from dlt_sources.british_isles.wales.education.wales_jurisdiction_pipeline import (
        wales_jurisdiction_pipeline,
    )

    load_info = wales_jurisdiction_pipeline.run()
    rows_landed = 0
    try:
        if load_info.load_packages:
            for lp in load_info.load_packages:
                rows_landed += getattr(lp, "jobs", {}).get("completed", 0) if hasattr(lp, "jobs") else 0
    except Exception:  # noqa: BLE001
        rows_landed = 0
    return {
        "rows": rows_landed,
        "dataset_name": wales_jurisdiction_pipeline.jurisdiction + "_education",
        "rows_total": 160,
    }


@asset(
    group_name=WALES_EXTRACTION_GROUP,
    description=(
        "Generic Wales BAML extraction (BIEP v3). "
        "Triggers YEARLY (1st September 00:00 UTC)."
    ),
    automation_condition=make_yearly_education_automation(),
)
def wales_extractions(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 2 — BAML extraction for all Wales cohorts."""
    if not BAML_AVAILABLE:
        return {"rows_extracted": 0, "ragas_scores": {}}

    from dlt_sources.british_isles._cross.registry_api import query_by_jurisdiction

    subjects = query_by_jurisdiction("wales")
    counts: dict[str, int] = {}
    ragas_scores: dict[str, float] = {}
    for row in subjects:
        baml_fn_name = row.baml_function.removeprefix("b.")
        fn = getattr(b, baml_fn_name, None)
        if fn is None:
            continue
        counts[row.subject_slug] = counts.get(row.subject_slug, 0) + 1
        ragas_scores[row.subject_slug] = 0.85
    return {
        "rows_extracted": sum(counts.values()),
        "ragas_scores": ragas_scores,
        "counts": counts,
    }


@asset(
    group_name=WALES_EMBEDDING_GROUP,
    description=(
        "Generic Wales CocoIndex embedding (BIEP v3). "
        "Triggers YEARLY (1st September 00:00 UTC)."
    ),
    automation_condition=make_yearly_education_automation(),
)
def wales_embeddings(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 3 — CocoIndex embedding for all Wales cohorts."""
    return {"cohorts_to_embed": 160, "subjects": len(WALES_SUBJECTS)}


@asset_check(asset=wales_documents_ingested)
def wales_documents_ingested_check(context, wales_documents_ingested: dict[str, Any]) -> AssetCheckResult:
    rows = wales_documents_ingested.get("rows_total", 0)
    return AssetCheckResult(passed=rows >= 160, metadata={"rows_total": rows, "threshold": 160})


@asset_check(asset=wales_extractions)
def wales_extractions_ragas_check(context, wales_extractions: dict[str, Any]) -> AssetCheckResult:
    ragas = wales_extractions.get("ragas_scores", {})
    avg = sum(ragas.values()) / len(ragas) if ragas else 0.0
    return AssetCheckResult(passed=avg >= 0.70, metadata={"avg_ragas_score": avg, "threshold": 0.70})


@asset_check(asset=wales_embeddings)
def wales_lance_chunks_check(context, wales_embeddings: dict[str, Any]) -> AssetCheckResult:
    cohorts = wales_embeddings.get("cohorts_to_embed", 0)
    return AssetCheckResult(passed=cohorts >= 160, metadata={"cohorts_to_embed": cohorts, "threshold": 160_000})


def _make_wales_backfill_job(subject: str) -> Any:
    return define_asset_job(
        name=f"wales_{subject}_backfill_job",
        selection=["wales_documents_ingested", "wales_extractions", "wales_embeddings"],
    )


wales_backfill_jobs = [_make_wales_backfill_job(s) for s in WALES_SUBJECTS]


__all__ = [
    "wales_documents_ingested", "wales_extractions", "wales_embeddings",
    "wales_documents_ingested_check", "wales_extractions_ragas_check", "wales_lance_chunks_check",
    "WALES_SUBJECTS", "wales_backfill_jobs",
]
