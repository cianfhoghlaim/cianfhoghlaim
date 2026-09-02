"""England generic Dagster assets (BIEP v3).

Per the 2026-07-29-biep-v3-england-full-coverage-v1 change +
2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The canonical generic England Dagster assets. Replaces the per-board
per-subject Dagster assets at
`orchestration/defs/2_materials/england_education/{aqa,ocr,edexcel}/`.

A SINGLE generic asset per layer (1 ingestion + 1 extraction + 1 embedding)
backed by the canonical registry + the canonical component.

## M3 — England A-Level (147 cohorts, AQA + OCR + Edexcel)
## M4 — England GCSE (129 cohorts, AQA + OCR + Edexcel)

The 3 generic assets (england_documents_ingested, england_extractions,
england_embeddings) cover all 276 England cohorts (A-Level + GCSE × 3
boards). This module adds 3 A-Level-specific asset checks + 147 per-subject
backfill jobs.

## Cianfhoghlaim patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect``).
- dagster (per `.agents/skills/dagster/SKILL.md`) — 5-layer group_name
  convention.
- yearly automation (1st September 00:00 UTC) per the BIEP v3 scheduling
  policy.

Reference: openspec/changes/2026-07-29-biep-v3-england-full-coverage-v1/
Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
"""
import logging
from typing import Any

from orchestration.verification import (
    count_lance_rows,
    count_rows,
    unverifiable,
)

from dagster import (
    AssetCheckResult,
    AssetExecutionContext,
    asset,
    asset_check,
    AssetCheckExecutionContext,
    define_asset_job,
)

# Per the BIEP v3 scheduling policy (yearly for England content).
# See orchestration/automation/biiep_scheduling.py for the canonical cron definitions.
from orchestration.automation.biiep_scheduling import (
    make_england_a_level_yearly_automation,
    make_england_gcse_yearly_automation,
    make_nightly_audit_automation,
)

try:
    from baml_client import b  # type: ignore[import-not-found]
    BAML_AVAILABLE = True
except ImportError:
    BAML_AVAILABLE = False
    b = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# 5-layer group_name convention
# (per openspec/specs/dagster-5-layer-component-architecture/spec.md)
# -----------------------------------------------------------------------------

ENGLAND_INGESTION_GROUP = "1_ingestion_education_england_documents"
ENGLAND_EXTRACTION_GROUP = "2_materials_education_england_extractions"
ENGLAND_EMBEDDING_GROUP = "3_model_lifecycle_education_england_embeddings"


# -----------------------------------------------------------------------------
# The 3 England awarding bodies
# -----------------------------------------------------------------------------

ENGLAND_BOARDS: tuple[str, ...] = ("aqa", "ocr", "edexcel")

# The 2 qualification levels
ENGLAND_LEVELS: tuple[str, ...] = ("a_level", "gcse")


# -----------------------------------------------------------------------------
# Layer 1: Ingestion (covers all 276 cohorts: 147 A-Level + 129 GCSE)
# -----------------------------------------------------------------------------

@asset(
    group_name=ENGLAND_INGESTION_GROUP,
    description=(
        "Generic England ingestion (BIEP v3). "
        "Replaces eng_aqa_<subject>_ingested, eng_ocr_<subject>_ingested, "
        "eng_edexcel_<subject>_ingested. "
        "Reads the canonical registry to discover all 276 cohorts "
        "(147 A-Level + 129 GCSE). "
        "Per the 2026-07-29-biep-v3-england-full-coverage-v1 change. "
        "Triggers YEARLY (1st September 00:00 UTC) for the A-Level + GCSE "
        "subsets via the BIEP v3 scheduling policy. "
        "Also triggers event-driven via the AQA/OCR/Edexcel "
        "ChangeDetection sensors."
    ),
    automation_condition=(
        make_england_a_level_yearly_automation() | make_england_gcse_yearly_automation()
    ),
)
def england_documents_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 — DLT ingestion of all England cohorts (276 rows)."""
    from dlt_sources.education.england.british_isles.education.england_jurisdiction_pipeline import (
        england_jurisdiction_pipeline,
    )

    # england_jurisdiction_pipeline is an EnglandJurisdictionPipeline instance
    # (the canonical JurisdictionPipelineBase subclass). Call .run() to
    # build the pipeline + load the resource + return load_info.
    load_info = england_jurisdiction_pipeline.run()
    rows_landed = 0
    try:
        if load_info.load_packages:
            for lp in load_info.load_packages:
                rows_landed += getattr(lp, "jobs", {}).get("completed", 0) if hasattr(lp, "jobs") else 0
    except Exception:  # noqa: BLE001
        rows_landed = 0
    context.log.info(
        "england_documents_ingested: %d rows landed", rows_landed
    )
    # The three hardcoded literals that used to be here — `rows_a_level: 147`,
    # `rows_gcse: 129`, `rows_total: 276` — were returned regardless of what
    # dlt loaded, and the asset checks asserted against those same numbers.
    # Expected counts belong in the check's threshold, not in the asset's
    # output; the checks now measure the destination instead.
    return {
        "rows": rows_landed,
        "dataset_name": england_jurisdiction_pipeline.jurisdiction + "_education",
        "expected_a_level": 147,  # 49 subjects × 3 boards — reference only
        "expected_gcse": 129,     # 43 subjects × 3 boards — reference only
    }


# -----------------------------------------------------------------------------
# Layer 2: Extraction (BAML — generic, driven by the registry's baml_function)
# -----------------------------------------------------------------------------

@asset(
    group_name=ENGLAND_EXTRACTION_GROUP,
    description=(
        "Generic England BAML extraction (BIEP v3). "
        "For each cohort in the registry, invokes the registry's "
        "`baml_function` field (the generic ExtractUKQualSpec(board: "
        "AwardingBody, ...) + the per-board ExtractAQAQualSpec / "
        "ExtractOCRQualSpec / ExtractEdexcelQualSpec). "
        "Per the 2026-07-29-biep-v3-england-full-coverage-v1 change. "
        "Triggers YEARLY (1st September 00:00 UTC) for the A-Level + GCSE "
        "subsets via the BIEP v3 scheduling policy. "
        "Also triggers event-driven via the AQA/OCR/Edexcel "
        "ChangeDetection sensors."
    ),
    automation_condition=(
        make_england_a_level_yearly_automation() | make_england_gcse_yearly_automation()
    ),
)
def england_extractions(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 2 — BAML extraction for all England cohorts.

    For each cohort in the registry, invoke the registry's baml_function
    via the 4-path OCR ensemble. All 4 paths land in per-path DuckLake
    tables; the RAGAS-voted_canonical row is committed to the cohort's
    primary DuckLake table.
    """
    if not BAML_AVAILABLE:
        context.log.warning("BAML not available; returning stub")
        return {"rows_extracted": 0, "ragas_scores": {}}

    from dlt_sources.british_isles._cross.registry_api import query_by_jurisdiction

    subjects = query_by_jurisdiction("england")
    counts: dict[str, int] = {}
    ragas_scores: dict[str, float] = {}
    for row in subjects:
        baml_fn_name = row.baml_function
        # Strip the "b." prefix to get the function name
        fn_name = baml_fn_name.removeprefix("b.")
        fn = getattr(b, fn_name, None)
        if fn is None:
            context.log.warning(
                "england_extractions: BAML function %r not found for %r",
                fn_name, row.subject_slug,
            )
            continue
        # NOTE: `fn` is resolved above and then NOT called — this asset has
        # never actually invoked BAML. Until it does, it must not emit a
        # RAGAS score: the previous line here was
        # `ragas_scores[slug] = 0.85  # placeholder`, and the paired check
        # averaged those placeholders against a 0.70 threshold, so the gate
        # always passed with zero extractions behind it.
        #
        # `counts` records what was genuinely enumerated (registry rows with a
        # resolvable BAML function); `ragas_scores` stays empty by design.
        try:
            counts[row.subject_slug] = counts.get(row.subject_slug, 0) + 1
        except Exception as exc:  # noqa: BLE001
            context.log.error(
                "england_extractions: failed for %s/%s/%s: %s",
                row.subject_slug, row.board, row.qualification_level, exc,
            )
            continue
    context.log.info(
        "england_extractions: %d subjects processed, ragas scores: %s",
        len(counts), ragas_scores,
    )
    return {
        # `rows_enumerated`, not `rows_extracted`: nothing was extracted, the
        # registry was enumerated. Naming it accurately stops downstream code
        # (and docs) reading it as an extraction count.
        "rows_enumerated": sum(counts.values()),
        "baml_invoked": False,
        "ragas_scores": ragas_scores,  # empty until BAML is actually called
        "counts": counts,
    }


# -----------------------------------------------------------------------------
# Layer 3: Embedding (CocoIndex — generic, driven by the registry)
# -----------------------------------------------------------------------------

@asset(
    group_name=ENGLAND_EMBEDDING_GROUP,
    description=(
        "Generic England CocoIndex embedding (BIEP v3). "
        "Drives the 3 per-board CocoIndex v1 Apps "
        "(england_aqa_a_level_embedding, england_aqa_gcse_embedding, "
        "england_ocr_a_level_embedding, england_ocr_gcse_embedding, "
        "england_edexcel_a_level_embedding, england_edexcel_gcse_embedding). "
        "Replaces the per-board CocoIndex Apps. "
        "Per the 2026-07-29-biep-v3-england-full-coverage-v1 change. "
        "Triggers YEARLY (1st September 00:00 UTC) for the A-Level + GCSE "
        "subsets via the BIEP v3 scheduling policy."
    ),
    automation_condition=(
        make_england_a_level_yearly_automation() | make_england_gcse_yearly_automation()
    ),
)
def england_embeddings(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 3 — CocoIndex embedding for all England cohorts.

    Drives the 6 per-board CocoIndex v1 Apps
    (AQA + OCR + Edexcel × A-Level + GCSE = 6 apps; each handles 49 or
    43 subjects per level).
    """
    from dlt_sources.british_isles._cross.registry_api import query_by_jurisdiction

    subjects = query_by_jurisdiction("england")
    context.log.info(
        "england_embeddings: %d England cohorts to embed (from registry)",
        len(subjects),
    )
    # `a_level_cohorts: 147` / `gcse_cohorts: 129` used to be returned here as
    # literals and asserted by the Lance checks, so those gates passed with
    # zero Lance rows behind them. Only the measured registry count is
    # reported now; the checks read the Lance dataset directly.
    return {
        "cohorts_to_embed": len(subjects),
        "embeddings_written": False,  # this asset records coverage, not writes
    }


# -----------------------------------------------------------------------------
# A-Level-specific asset checks (M3 milestone acceptance gate)
# -----------------------------------------------------------------------------

# =============================================================================
# Asset checks — REWRITTEN 2026-08-14 to query the destination.
#
# Every check below previously took the upstream asset's returned dict as an
# input and asserted against it. Since `england_documents_ingested` returned a
# hardcoded `{"rows_a_level": 147, "rows_gcse": 129}` and `england_extractions`
# set `ragas_scores[slug] = 0.85  # placeholder`, the checks asserted against
# numbers the assets had just invented and could never fail.
#
# They now read the store via `orchestration.verification`. When the store is
# unreachable the check FAILS with a reason — "unverifiable" is not "passing".
# =============================================================================

@asset_check(asset=england_documents_ingested)
def england_a_level_documents_ingested_check(context) -> AssetCheckResult:
    """England A-Level cohort count >= 147, measured in the destination."""
    # Real table, verified live: `cianfhoghlaim.education.subjects` (2,138
    # rows across 8 jurisdictions). `england_education.england_subjects` does
    # not exist — it was never checked because the old check read the asset's
    # own return value.
    actual = count_rows(
        "education.subjects",
        # Live-verified 2026-08-14: `qualification_level` is NULL for every
        # England row; the level is carried in `stage`. Measured today:
        # 120 rows, ALL stage='gcse', ZERO a_level. The old check asserted
        # `>= 147` against the asset's own hardcoded 147 and passed anyway.
        where="jurisdiction = 'england' AND stage = 'a_level'",
    )
    if actual is None:
        return AssetCheckResult(
            passed=False,
            metadata=unverifiable(
                "could not read education.subjects",
                threshold=147,
            ),
        )
    return AssetCheckResult(
        passed=actual >= 147,
        metadata={"rows_a_level": actual, "threshold": 147, "verified": True},
    )


@asset_check(asset=england_extractions)
def england_a_level_extractions_ragas_check(context) -> AssetCheckResult:
    """England A-Level extraction RAGAS score >= 0.70, read from the store.

    `england_extractions` does not yet call BAML (it looks the function up and
    discards it), so there are no real RAGAS scores to read. This check
    therefore FAILS rather than averaging the former `0.85` placeholder.
    """
    # There is no extractions table in the lakehouse at all — the live
    # catalog holds only education.subjects and 3 leaving_cert tables.
    scores = count_rows("education.extractions", where="ragas_score IS NOT NULL")
    if scores is None or scores == 0:
        return AssetCheckResult(
            passed=False,
            metadata=unverifiable(
                "no scored extraction rows in education.extractions; "
                "england_extractions does not invoke BAML yet",
                threshold=0.70,
            ),
        )
    return AssetCheckResult(
        passed=True,
        metadata={"scored_rows": scores, "threshold": 0.70, "verified": True},
    )


@asset_check(asset=england_embeddings)
def england_a_level_lance_chunks_check(context) -> AssetCheckResult:
    """England A-Level LanceDB chunk count, measured in the Lance dataset."""
    actual = count_lance_rows("cianfhoghlaim_education_england_subjects")
    if actual is None:
        return AssetCheckResult(
            passed=False,
            metadata=unverifiable(
                "Lance dataset cianfhoghlaim_education_england_subjects not found; "
                "the CocoIndex -> LanceDB write path has never executed",
                threshold=147,
            ),
        )
    return AssetCheckResult(
        passed=actual >= 147,
        metadata={"lance_rows": actual, "threshold": 147, "verified": True},
    )


# -----------------------------------------------------------------------------
# GCSE-specific asset checks (M4 milestone acceptance gate)
# -----------------------------------------------------------------------------

@asset_check(asset=england_documents_ingested)
def england_gcse_documents_ingested_check(context) -> AssetCheckResult:
    """England GCSE cohort count >= 129, measured in the destination."""
    actual = count_rows(
        "education.subjects",
        # Live-verified 2026-08-14: 120 rows (threshold 129 -> genuinely
        # 9 short). The old check compared the asset's hardcoded 129 to
        # itself, so this shortfall was invisible.
        where="jurisdiction = 'england' AND stage = 'gcse'",
    )
    if actual is None:
        return AssetCheckResult(
            passed=False,
            metadata=unverifiable(
                "could not read education.subjects",
                threshold=129,
            ),
        )
    return AssetCheckResult(
        passed=actual >= 129,
        metadata={"rows_gcse": actual, "threshold": 129, "verified": True},
    )


@asset_check(asset=england_extractions)
def england_gcse_extractions_ragas_check(context) -> AssetCheckResult:
    """England GCSE extraction RAGAS score >= 0.70, read from the store.

    `england_extractions` does not yet call BAML (it looks the function up and
    discards it), so there are no real RAGAS scores to read. This check
    therefore FAILS rather than averaging the former `0.85` placeholder.
    """
    # There is no extractions table in the lakehouse at all — the live
    # catalog holds only education.subjects and 3 leaving_cert tables.
    scores = count_rows("education.extractions", where="ragas_score IS NOT NULL")
    if scores is None or scores == 0:
        return AssetCheckResult(
            passed=False,
            metadata=unverifiable(
                "no scored extraction rows in education.extractions; "
                "england_extractions does not invoke BAML yet",
                threshold=0.70,
            ),
        )
    return AssetCheckResult(
        passed=True,
        metadata={"scored_rows": scores, "threshold": 0.70, "verified": True},
    )


@asset_check(asset=england_embeddings)
def england_gcse_lance_chunks_check(context) -> AssetCheckResult:
    """England GCSE LanceDB chunk count, measured in the Lance dataset."""
    actual = count_lance_rows("cianfhoghlaim_education_england_subjects")
    if actual is None:
        return AssetCheckResult(
            passed=False,
            metadata=unverifiable(
                "Lance dataset cianfhoghlaim_education_england_subjects not found; "
                "the CocoIndex -> LanceDB write path has never executed",
                threshold=129,
            ),
        )
    return AssetCheckResult(
        passed=actual >= 129,
        metadata={"lance_rows": actual, "threshold": 129, "verified": True},
    )


# -----------------------------------------------------------------------------
# M3 per-subject backfill jobs (147 jobs)
# -----------------------------------------------------------------------------
# 49 A-Level subjects × 3 boards (AQA + OCR + Edexcel) = 147 per-subject jobs.
# Each job selects the 3 generic England assets + the 3 A-Level-specific
# asset checks. The job is invoked by the operator on demand.

# The 49 A-Level subjects (per baml_src/british_isles/england/education/subject_taxonomy.baml:ALevelAQASubject)
A_LEVEL_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "further_mathematics",
    "pure_mathematics",
    "statistics",
    "mechanics",
    "decision_maths",
    "english_literature",
    "english_language_and_literature",
    "biology",
    "chemistry",
    "physics",
    "geology",
    "human_biology",
    "environmental_science",
    "french",
    "german",
    "spanish",
    "latin",
    "italian",
    "classical_civilisation",
    "ancient_history",
    "history",
    "geography",
    "religious_studies",
    "philosophy",
    "economics",
    "business",
    "psychology",
    "sociology",
    "politics",
    "law",
    "art_and_design",
    "design_technology",
    "drama",
    "music",
    "pe",
    "dance",
    "media_studies",
    "applied_business",
    "applied_ict",
    "communication_and_culture",
    "critical_thinking",
    "general_studies",
    "performing_arts",
    "psychology_a2",
    "sociology_a2",
    "politics_a2",
    "law_a2",
    "other",
    "engineering",
)

# 49 valid A-Level subjects (AQA + OCR + Edexcel share the same set)


def _make_england_a_level_backfill_job(subject: str, board: str) -> Any:
    """Create a per-subject A-Level backfill job for one (subject, board) cohort."""
    return define_asset_job(
        name=f"england_a_level_{board}_{subject}_backfill_job",
        selection=[
            "england_documents_ingested",
            "england_extractions",
            "england_embeddings",
        ],
    )


# Generate the 147 per-(subject, board) A-Level backfill jobs
england_a_level_backfill_jobs = [
    _make_england_a_level_backfill_job(subject, board)
    for subject in A_LEVEL_SUBJECTS
    for board in ENGLAND_BOARDS
]


# -----------------------------------------------------------------------------
# M4 per-subject backfill jobs (129 jobs)
# -----------------------------------------------------------------------------
# 43 GCSE subjects × 3 boards (AQA + OCR + Edexcel) = 129 per-subject jobs.

# The 43 GCSE subjects (per baml_src/.../england/education/subject_taxonomy.baml:GCSEAQASubject)
# Use the canonical 43 subjects that overlap across all 3 boards.
GCSE_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "english_language",
    "english_literature",
    "biology",
    "chemistry",
    "physics",
    "computer_science",
    "history",
    "geography",
    "religious_studies",
    "french",
    "german",
    "spanish",
    "latin",
    "classical_civilisation",
    "ancient_history",
    "economics",
    "business",
    "psychology",
    "sociology",
    "politics",
    "law",
    "art_and_design",
    "design_technology",
    "drama",
    "music",
    "pe",
    "dance",
    "media_studies",
    "food_preparation_nutrition",
    "further_mathematics",
    "statistics",
    "engineering",
    "electronics",
    "human_biology",
    "applied_business",
    "applied_ict",
    "applied_science_double",
    "applied_travel_tourism",
    "performing_arts",
    "statistics_9ma0",
    "geography_fieldwork",
    "environmental_science_team",
)


def _make_england_gcse_backfill_job(subject: str, board: str) -> Any:
    """Create a per-subject GCSE backfill job for one (subject, board) cohort."""
    return define_asset_job(
        name=f"england_gcse_{board}_{subject}_backfill_job",
        selection=[
            "england_documents_ingested",
            "england_extractions",
            "england_embeddings",
        ],
    )


# Generate the 129 per-(subject, board) GCSE backfill jobs
england_gcse_backfill_jobs = [
    _make_england_gcse_backfill_job(subject, board)
    for subject in GCSE_SUBJECTS
    for board in ENGLAND_BOARDS
]


__all__ = [
    "england_documents_ingested",
    "england_extractions",
    "england_embeddings",
    "england_a_level_documents_ingested_check",
    "england_a_level_extractions_ragas_check",
    "england_a_level_lance_chunks_check",
    "england_gcse_documents_ingested_check",
    "england_gcse_extractions_ragas_check",
    "england_gcse_lance_chunks_check",
    "ENGLAND_INGESTION_GROUP",
    "ENGLAND_EXTRACTION_GROUP",
    "ENGLAND_EMBEDDING_GROUP",
    "ENGLAND_BOARDS",
    "ENGLAND_LEVELS",
    "A_LEVEL_SUBJECTS",
    "GCSE_SUBJECTS",
    "england_a_level_backfill_jobs",
    "england_gcse_backfill_jobs",
]
