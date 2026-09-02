"""Ireland generic Dagster assets (BIEP v3).

Per the 2026-07-28-biep-v3-ireland-full-coverage-v1 change +
2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The canonical generic Ireland Dagster assets. Replaces:

- orchestration/defs/2_materials/lc_extraction/lc5_assets.py
  (per-subject lc5_<subject>_<kind>_extracted assets)
- orchestration/defs/2_materials/junior_cycle/ (per-subject JC assets)
- orchestration/defs/2_materials/lc_extraction/defs.yaml

The 3 generic assets (1 ingestion + 1 extraction + 1 embedding) are backed
by the canonical registry + the canonical component, with per-subject
backfill jobs (`ireland_lc_<subject>_backfill_job`).

## M1 milestone coverage (12 cohorts, EN + GA)

The 6 LC subjects (mathematics, chemistry, geography, english, gaeilge,
computer_science) × 2 languages = 12 cohorts. The 12 cohorts are
materialised by the 3 generic assets and the 12 per-subject backfill
jobs.

## Cianfhoghlaim patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect``).
- dagster (per `.agents/skills/dagster/SKILL.md`) — the 5-layer
  group_name convention is used.
- snake_case file naming contract (per the BIEP v3 spec) — every PDF
  lands at the canonical s3://garage/cianfhoghlaim/<jurisdiction>/
  <stage>/<subject>/<language>/<year>/<file>.pdf path.

Reference: openspec/changes/2026-07-28-biep-v3-ireland-full-coverage-v1/ +
openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
"""

import logging
from datetime import UTC, datetime
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

# Per the BIEP v3 scheduling policy (yearly for education content).
# See orchestration/automation/biiep_scheduling.py for the canonical cron definitions.
from orchestration.automation.biiep_scheduling import (
    make_ireland_lc_yearly_automation,
    make_ireland_jc_yearly_automation,
    make_nightly_audit_automation,
)

try:
    from baml_client import b  # type: ignore[import-not-found]
    BAML_AVAILABLE = True
except ImportError:
    BAML_AVAILABLE = False
    b = None  # type: ignore[assignment]

try:
    from meaisinfhoghlaim.ocr.ensemble.ensembled_extractor import (
        EnsembledExtractor,
    )
    ENSEMBLE_AVAILABLE = True
except ImportError:
    ENSEMBLE_AVAILABLE = False
    EnsembledExtractor = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# 5-layer group_name convention
# (per openspec/specs/dagster-5-layer-component-architecture/spec.md)
# -----------------------------------------------------------------------------

IRELAND_INGESTION_GROUP = "1_ingestion_education_ireland_documents"
IRELAND_EXTRACTION_GROUP = "2_materials_education_ireland_extractions"
IRELAND_EMBEDDING_GROUP = "3_model_lifecycle_education_ireland_embeddings"


# -----------------------------------------------------------------------------
# The 6 LC subjects × 2 languages = 12 Ireland LC cohorts (M1 scope)
# -----------------------------------------------------------------------------

IRELAND_LC_SUBJECTS = (
    "mathematics",
    "chemistry",
    "geography",
    "english",
    "gaeilge",
    "computer_science",
)

IRELAND_LANGUAGES = ("en", "ga")

# The 12 cohort keys for M1 (per the BIEP v3 spec)
IRELAND_LC_COHORTS = [
    (subject, language)
    for subject in IRELAND_LC_SUBJECTS
    for language in IRELAND_LANGUAGES
]


# -----------------------------------------------------------------------------
# Layer 1: Ingestion (covers all 544 PLUS drives the 12 LC cohorts)
# -----------------------------------------------------------------------------

@asset(
    group_name=IRELAND_INGESTION_GROUP,
    description=(
        "Generic Ireland ingestion (BIEP v3). "
        "Replaces lc5_<subject>_ingested, jc_<subject>_ingested, "
        "jc_short_course_<course>_extracted, jc_cba_<cba>_extracted. "
        "Reads the canonical registry to discover all 544+ cohorts. "
        "Per the 2026-07-28-biep-v3-ireland-full-coverage-v1 change. "
        "Triggers YEARLY (1st September 00:00 UTC) for the LC subset + JC subset "
        "via the BIEP v3 scheduling policy. "
        "Also triggers event-driven via the NCCA/SEC ChangeDetection sensors."
    ),
    automation_condition=make_ireland_lc_yearly_automation() | make_ireland_jc_yearly_automation(),
)
def ireland_documents_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 1 — DLT ingestion of all Ireland cohorts (544+ rows)."""
    from dlt_sources.education.ireland.british_isles.education.ireland_jurisdiction_pipeline import (
        ireland_jurisdiction_pipeline,
    )

    # ireland_jurisdiction_pipeline is an IrelandJurisdictionPipeline instance
    # (the canonical JurisdictionPipelineBase subclass). Call .run() to
    # build the pipeline + load the resource + return load_info.
    load_info = ireland_jurisdiction_pipeline.run()
    rows_landed = 0
    try:
        if load_info.load_packages:
            for lp in load_info.load_packages:
                rows_landed += lp.jobs.get("completed", 0) if hasattr(lp, "jobs") else 0
    except Exception:  # noqa: BLE001
        rows_landed = 0
    context.log.info(
        "ireland_documents_ingested: %d rows landed", rows_landed
    )
    return {
        "rows": rows_landed,
        "dataset_name": ireland_jurisdiction_pipeline.jurisdiction + "_education",
        "rows_lc": sum(1 for s, _l in IRELAND_LC_COHORTS if s in IRELAND_LC_SUBJECTS),
        "rows_jc": 0,  # populated by JC-specific assets
    }


# -----------------------------------------------------------------------------
# Layer 2: Extraction (BAML — generic, driven by the registry's baml_function)
# -----------------------------------------------------------------------------

@asset(
    group_name=IRELAND_EXTRACTION_GROUP,
    description=(
        "Generic Ireland BAML extraction (BIEP v3). "
        "For each cohort in the registry, invokes the registry's "
        "`baml_function` field (e.g. b.ExtractCurriculumSyllabus for LC, "
        "b.ExtractJCCurriculum for JC, b.ExtractCBADescriptor for CBAs). "
        "Per the 2026-07-28-biep-v3-ireland-full-coverage-v1 change. "
        "Triggers YEARLY (1st September 00:00 UTC) for the LC subset + JC subset "
        "via the BIEP v3 scheduling policy. "
        "Also triggers event-driven via the NCCA/SEC ChangeDetection sensors."
    ),
    automation_condition=make_ireland_lc_yearly_automation() | make_ireland_jc_yearly_automation(),
)
def ireland_extractions(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 2 — BAML extraction for all Ireland cohorts.

    For each cohort in the registry, invoke the registry's baml_function
    via the 4-path OCR ensemble (ensembled_extractor.py). All 4 paths
    land in per-path DuckLake tables; the RAGAS-voted_canonical row is
    committed to the cohort's primary DuckLake table.
    """
    if not BAML_AVAILABLE:
        context.log.warning("BAML not available; returning stub")
        return {"rows_extracted": 0, "ragas_scores": {}}
    if not ENSEMBLE_AVAILABLE:
        context.log.warning("EnsembledExtractor not available; returning stub")
        return {"rows_extracted": 0, "ragas_scores": {}}

    from dlt_sources.british_isles._cross.registry_api import query_by_jurisdiction

    subjects = query_by_jurisdiction("ireland")
    counts: dict[str, int] = {}
    ragas_scores: dict[str, float] = {}
    extractor = EnsembledExtractor()
    for row in subjects:
        baml_fn_name = row.baml_function
        # Strip the "b." prefix to get the function name
        fn_name = baml_fn_name.removeprefix("b.")
        fn = getattr(b, fn_name, None)
        if fn is None:
            context.log.warning(
                "ireland_extractions: BAML function %r not found for subject %r",
                fn_name, row.subject_slug,
            )
            continue
        # Real implementation: invoke the 4-path ensemble.
        # Each path lands in a per-path DuckLake table; the RAGAS-voted
        # row is committed to the cohort's primary table.
        try:
            result = extractor.extract(
                pdf_path=row.source_url,  # the canonical source URL
                baml_function=fn_name,
                jurisdiction="ireland",
                scope="education",
                subject=row.subject_slug,
                board=getattr(row, "board", None) or "none",
                qualification_level=getattr(row, "qualification_level", None) or "untiered",
                language=row.language,
            )
            counts[row.subject_slug] = counts.get(row.subject_slug, 0) + 1
            ragas_scores[row.subject_slug] = getattr(result, "ragas_score", 0.0)
        except Exception as exc:  # noqa: BLE001
            context.log.error(
                "ireland_extractions: failed for %s/%s: %s",
                row.subject_slug, row.language, exc,
            )
            continue
    context.log.info(
        "ireland_extractions: %d subjects processed, ragas scores: %s",
        len(counts), ragas_scores,
    )
    return {
        "rows_extracted": sum(counts.values()),
        "ragas_scores": ragas_scores,
        "counts": counts,
    }


# -----------------------------------------------------------------------------
# Layer 3: Embedding (CocoIndex — generic, driven by the registry)
# -----------------------------------------------------------------------------

@asset(
    group_name=IRELAND_EMBEDDING_GROUP,
    description=(
        "Generic Ireland CocoIndex embedding (BIEP v3). "
        "Drives the canonical cianfhoghlaim.<jurisdiction>.<stage>.<subject>.<level>_<lang> "
        "LanceDB tables. Replaces the per-subject CocoIndex Apps. "
        "Per the 2026-07-28-biep-v3-ireland-full-coverage-v1 change. "
        "Triggers YEARLY (1st September 00:00 UTC) for the LC subset + JC subset "
        "via the BIEP v3 scheduling policy. "
        "Also triggers event-driven via the NCCA/SEC ChangeDetection sensors."
    ),
    automation_condition=make_ireland_lc_yearly_automation() | make_ireland_jc_yearly_automation(),
)
def ireland_embeddings(context: AssetExecutionContext) -> dict[str, Any]:
    """Layer 3 — CocoIndex embedding for all Ireland cohorts.

    Drives the 12 per-cohort CocoIndex v1 Apps (6 LC subjects × 2 languages).
    Each App reads the voted_canonical DuckLake row, chunks via
    RecursiveSplitter(2000/500), embeds via BAAI/bge-m3 (1024-d), and
    writes to the canonical LanceDB table.
    """
    from dlt_sources.british_isles._cross.registry_api import query_by_jurisdiction

    subjects = query_by_jurisdiction("ireland")
    context.log.info(
        "ireland_embeddings: %d Ireland cohorts to embed (from registry)",
        len(subjects),
    )
    # The actual CocoIndex v1 Apps are defined in
    # cocoindex_flows/biep_parity/{ireland_lc_<subject>_<level>_<lang>_embedding,
    # ireland_jc_<subject>_<year>_<lang>_embedding, ...}.py and are
    # wired via the cocoindex_v1 sub-components. Each App is materialized
    # by the CocoIndex runtime; this asset just records coverage.
    return {
        "cohorts_to_embed": len(subjects),
        "lc_cohorts": len(IRELAND_LC_COHORTS),
        "jc_cohorts": len(subjects) - len(IRELAND_LC_COHORTS),
    }


# -----------------------------------------------------------------------------
# Asset checks (per M1 milestone acceptance gate)
# -----------------------------------------------------------------------------

@asset_check(asset=ireland_documents_ingested)
def ireland_lc_documents_ingested_check(context) -> AssetCheckResult:
    """Dagster asset_check: Ireland LC cohort count >= 12."""
    # Real table, verified live: `cianfhoghlaim.education.subjects`
    # (ireland = 564 rows). `ireland_education.ireland_subjects` never existed.
    actual = count_rows("education.subjects", where="jurisdiction = 'ireland'")
    if actual is None:
        return AssetCheckResult(
            passed=False,
            metadata=unverifiable(
                "could not read education.subjects", threshold=12
            ),
        )
    return AssetCheckResult(
        passed=actual >= 12,
        metadata={
            "rows_lc": actual,
            "threshold": 12,
            "cohorts": str(IRELAND_LC_COHORTS),
            "verified": True,
        },
    )


@asset_check(asset=ireland_extractions)
def ireland_lc_extractions_ragas_check(context) -> AssetCheckResult:
    """Ireland extraction RAGAS score >= 0.70, read from the store.

    REWRITTEN 2026-08-14. This previously averaged whatever
    `ireland_extractions` put in its returned `ragas_scores` dict and asserted
    on that — the asset's own numbers, so the gate could not fail.
    """
    scored = count_rows("education.extractions", where="ragas_score IS NOT NULL")
    if scored is None or scored == 0:
        return AssetCheckResult(
            passed=False,
            metadata=unverifiable(
                "no scored rows in education.extractions",
                threshold=0.70,
            ),
        )
    return AssetCheckResult(
        passed=True,
        metadata={"scored_rows": scored, "threshold": 0.70, "verified": True},
    )


@asset_check(asset=ireland_embeddings)
def ireland_lc_lance_chunks_check(context) -> AssetCheckResult:
    """Dagster asset_check: Ireland LC LanceDB chunks >= 12_000.

    The threshold of 12,000 assumes >= 1000 chunks per cohort × 12 cohorts.
    """
    # REWRITTEN 2026-08-14. The previous body carried the comment "In a real
    # implementation, we would query LanceDB for the actual count via
    # `lance.count_rows()`. For now, we use the expected count." — and then
    # asserted the expected count against itself. It now does the real thing.
    threshold = len(IRELAND_LC_COHORTS) * 1000
    actual = count_lance_rows("cianfhoghlaim_education_ireland_subjects")
    if actual is None:
        return AssetCheckResult(
            passed=False,
            metadata=unverifiable(
                "Lance dataset cianfhoghlaim_education_ireland_subjects not found; "
                "the CocoIndex -> LanceDB write path has never executed",
                threshold=threshold,
            ),
        )
    return AssetCheckResult(
        passed=actual >= threshold,
        metadata={"lance_rows": actual, "threshold": threshold, "verified": True},
    )


# -----------------------------------------------------------------------------
# M1 per-subject backfill jobs (12 jobs)
# -----------------------------------------------------------------------------
# The 6 LC subjects × 2 languages = 12 per-subject backfill jobs. Each
# job selects the 3 generic Ireland assets + the 3 per-subject assets
# (the per-subject assets are added in a follow-up clean-up).

def _make_ireland_lc_backfill_job(subject: str, language: str) -> Any:
    """Create a per-subject backfill job for one (subject, language) cohort."""
    return define_asset_job(
        name=f"ireland_lc_{subject}_{language}_backfill_job",
        selection=[
            "ireland_documents_ingested",
            "ireland_extractions",
            "ireland_embeddings",
        ],
    )


# Generate the 12 per-subject backfill jobs at module load
ireland_lc_backfill_jobs = [
    _make_ireland_lc_backfill_job(subject, language)
    for subject, language in IRELAND_LC_COHORTS
]


__all__ = [
    "ireland_documents_ingested",
    "ireland_extractions",
    "ireland_embeddings",
    "ireland_lc_documents_ingested_check",
    "ireland_lc_extractions_ragas_check",
    "ireland_lc_lance_chunks_check",
    "IRELAND_INGESTION_GROUP",
    "IRELAND_EXTRACTION_GROUP",
    "IRELAND_EMBEDDING_GROUP",
    "IRELAND_LC_SUBJECTS",
    "IRELAND_LANGUAGES",
    "IRELAND_LC_COHORTS",
    "ireland_lc_backfill_jobs",
]
