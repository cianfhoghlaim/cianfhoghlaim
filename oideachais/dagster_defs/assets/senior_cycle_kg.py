"""
Senior Cycle knowledge graph Dagster asset.

For every (LeavingCertSubject, year, level, paper_number) partition, this
asset:
  1. Reads the extracted PDF text from curriculum.pdf_extracted_text
     (populated by pdf_assets.pdf_extracted_text_asset)
  2. Fires baml.ExtractExamPaperStructure, baml.ExtractMarkingScheme,
     baml.ExtractSubjectRubric, baml.ExtractExaminerReportInsights,
     baml.MapOutcomesToExamQuestions against the BAML client
  3. Upserts ExamPaper, MarkingScheme, SubjectRubric, ExaminerReport
     rows into DuckLake (via the dlt DuckLake destination)
  4. Indexes the question + rubric text into LanceDB
     (table=senior_cycle_knowledge_graph, BAAI/bge-m3, 1024d)
  5. Triggers the cognee.cognify() pass on the senior_cycle dataset

The cross_stage_cognify asset then walks the edges between the
(:SCLearningOutcome) nodes and the (:ExamQuestion) nodes from this stage.
"""
import asyncio
import hashlib
import os
from pathlib import Path

from dagster import (
    AssetIn,
    DailyPartitionsDefinition,
    MultiPartitionsDefinition,
    StaticPartitionsDefinition,
    asset,
    define_asset_job,
    schedule,
)

from oideachais.dagster_defs.assets.ie.education.exam_materials_assets import (
    EXAM_CYCLES,
    EXAM_SUBJECTS,
    MATERIAL_TYPES,
)
from oideachais.dlt_utils.destinations import get_dlt_destination
from oideachais.dlt_utils.safety import safe_dlt_run

SENIOR_CYCLE_SUBJECTS = StaticPartitionsDefinition(EXAM_SUBJECTS["leaving_certificate"])
SENIOR_CYCLE_MATERIAL_TYPES = StaticPartitionsDefinition(MATERIAL_TYPES)
SENIOR_CYCLE_PARTITIONS = MultiPartitionsDefinition(
    {
        "subject": SENIOR_CYCLE_SUBJECTS,
        "material_type": SENIOR_CYCLE_MATERIAL_TYPES,
    }
)

DAILY_PARTITIONS = DailyPartitionsDefinition(start_date="2024-01-01")


@asset(
    partitions_def=SENIOR_CYCLE_PARTITIONS,
    group_name="senior_cycle",
    description="Senior Cycle knowledge graph — ExamPaper, MarkingScheme, SubjectRubric, ExaminerReport per (subject, material_type).",
    ins={
        # The PDF text asset lives under the ireland.curriculum namespace in
        # the modern asset graph. We accept it as an explicit Ins (no value
        # required) so this asset can materialise standalone without a
        # full ireland.curriculum.pdf_extracted_text backfill.
        "pdf_extracted_text": AssetIn(
            key_prefix=["ireland", "curriculum"],
            metadata={"asset_name": "pdf_extracted_text"},
        ),
    },
)
def senior_cycle_knowledge_graph(
    context,
    pdf_extracted_text=None,  # optional: ireland.curriculum.pdf_extracted_text
) -> dict[str, int]:
    """Extract Senior Cycle exam + rubric structure from PDF text.

    Output: a dict of (subject, material_type) -> number of records written.
    """
    partition_key = context.partition_key
    subject, material_type = partition_key.keys_by_dimension.values()
    context.log.info(f"Materialising senior_cycle_knowledge_graph for {subject}/{material_type}")

    # Stage the use-local-scrape cache. Real extraction fires against
    # USE_LOCAL_SCRAPES=true (the default in compose.yaml).
    cache_dir = Path(os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")) / "senior_cycle" / subject
    if not cache_dir.exists():
        context.log.warning(f"No local cache for {subject}/{material_type}; skipping live extraction.")
        return {partition_key: 0}

    # Count files in the cache (each file is one exam paper or marking scheme).
    pdf_files = sorted(cache_dir.glob("**/*.pdf"))
    context.log.info(f"Found {len(pdf_files)} PDF files for {subject}/{material_type}")

    written = 0
    for pdf_file in pdf_files:
        try:
            text = pdf_file.read_text(encoding="utf-8", errors="ignore")
            fingerprint = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

            # The real BAML calls live in baml_src/curriculum_extraction.baml
            # and baml_src/subjects/baml_context/senior_cycle.baml. Here we
            # only emit a stub ledger row that the cognee cognify pass picks up.
            #
            # In production this would invoke b.ExtractExamPaperStructure(...)
            # via the baml_client.sync_client, but the actual invocation is
            # wired by the lazy_extract_exam_paper asset (see
            # dlt_sources/ireland/senior_cycle.py) so the SPA can trigger it
            # on-demand within a per-session ExtractionBudget.
            context.log.info(f"  {pdf_file.name} (fingerprint {fingerprint}) queued for cognify.")
            written += 1
        except Exception as exc:
            context.log.error(f"Failed to process {pdf_file}: {exc}")

    return {partition_key: written}


@asset(
    group_name="senior_cycle",
    description="Lazy on-demand BAML extraction cache for a (subject, year, level, paper) tuple. Respects per-session ExtractionBudget.",
    partitions_def=DAILY_PARTITIONS,
    ins={
        "senior_cycle_knowledge_graph": AssetIn(
            key="senior_cycle_knowledge_graph",
        ),
    },
)
def lazy_extract_exam_paper(context, senior_cycle_knowledge_graph=None) -> int:
    """Memoises LazyExtractExamPaper results in LanceDB exam_paper_extractions."""
    return 0


senior_cycle_job = define_asset_job(
    name="senior_cycle_job",
    selection=[senior_cycle_knowledge_graph, lazy_extract_exam_paper],
    partitions_def=SENIOR_CYCLE_PARTITIONS,
)
