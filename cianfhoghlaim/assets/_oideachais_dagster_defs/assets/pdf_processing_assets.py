"""
Dagster assets for the 6-stage PDF processing pipeline.

Per `openspec/specs/oideachais-pdf-processing/spec.md` (the 7th spec
added in the 2026-06-29 OCR/VLM registry change), the PDF
processing pipeline runs as 3 Dagster assets:
- `pdf_processing_syllabus` (for NCCA syllabus PDFs)
- `pdf_processing_past_paper` (for SEC past paper PDFs)
- `pdf_processing_marking_scheme` (for SEC marking-scheme PDFs)

Each asset invokes the 6-stage pipeline on a (subject, year, paper)
tuple and writes the results to DuckLake + LanceDB + Cognee + Graphiti.

These assets are auto-discovered by the `pdf_processing_assets.py`
module via the `defs.yaml` mount point.
"""

from __future__ import annotations

import logging
import os
import warnings
from pathlib import Path
from typing import Any

from dagster import (
    AssetExecutionContext,
    AssetKey,
    DailyPartitionsDefinition,
    MaterializeResult,
    MetadataValue,
    asset,
)

warnings.filterwarnings("ignore", category=DeprecationWarning)

from cianfhoghlaim.assets._oideachais_dagster_defs.assets.pdf_processing import (  # noqa: E402
    PDFProcessingPipeline,
)

logger = logging.getLogger(__name__)

# Daily partition: one materialisation per day, partitioned by date.
daily_partitions = DailyPartitionsDefinition(start_date="2026-06-01")


# ─── Asset: syllabus PDFs ───
@asset(
    key=AssetKey(["pdf_processing", "syllabus"]),
    group_name="pdf_processing",
    partitions_def=daily_partitions,
    compute_kind="python",
    description=(
        "Run the 6-stage PDF processing pipeline on NCCA syllabus PDFs. "
        "Reads from stedding/ingest_queue/ncca.ie/ + writes to "
        "ducklake://oideachais.assets.official_documents.syllabi.{subject}.{year}."
    ),
    metadata={
        "spec": "oideachais-pdf-processing",
        "registry": "cianfhoghlaim.ocr.models.VISION_MODELS (24 entries, Unsloth-first)",
    },
)
def pdf_processing_syllabus(
    context: AssetExecutionContext,
) -> MaterializeResult:
    """Materialise the 6-stage pipeline for NCCA syllabus PDFs."""
    return _run_pipeline_asset(context, document_type="syllabus")


# ─── Asset: past paper PDFs ───
@asset(
    key=AssetKey(["pdf_processing", "past_paper"]),
    group_name="pdf_processing",
    partitions_def=daily_partitions,
    compute_kind="python",
    description=(
        "Run the 6-stage PDF processing pipeline on SEC past paper PDFs. "
        "Reads from stedding/ingest_queue/examinations.ie/ + writes to "
        "ducklake://oideachais.assets.official_documents.past_papers.{subject}.{year}.{paper}."
    ),
    metadata={
        "spec": "oideachais-pdf-processing",
        "registry": "cianfhoghlaim.ocr.models.VISION_MODELS (24 entries, Unsloth-first)",
    },
)
def pdf_processing_past_paper(
    context: AssetExecutionContext,
) -> MaterializeResult:
    """Materialise the 6-stage pipeline for SEC past paper PDFs."""
    return _run_pipeline_asset(context, document_type="past_paper")


# ─── Asset: marking scheme PDFs ───
@asset(
    key=AssetKey(["pdf_processing", "marking_scheme"]),
    group_name="pdf_processing",
    partitions_def=daily_partitions,
    compute_kind="python",
    description=(
        "Run the 6-stage PDF processing pipeline on SEC marking-scheme PDFs. "
        "Reads from stedding/ingest_queue/examinations.ie/marking-schemes/ "
        "+ writes to ducklake://oideachais.assets.official_documents.marking_schemes.{subject}.{year}.{paper}."
    ),
    metadata={
        "spec": "oideachais-pdf-processing",
        "registry": "cianfhoghlaim.ocr.models.VISION_MODELS (24 entries, Unsloth-first)",
    },
)
def pdf_processing_marking_scheme(
    context: AssetExecutionContext,
) -> MaterializeResult:
    """Materialise the 6-stage pipeline for SEC marking-scheme PDFs."""
    return _run_pipeline_asset(context, document_type="marking_scheme")


# ─── Asset implementation ───
def _run_pipeline_asset(
    context: AssetExecutionContext,
    document_type: str,
) -> MaterializeResult:
    """Common implementation: find PDFs, run the 6-stage pipeline, return Dagster metadata."""
    from datetime import datetime
    today = context.partition_key
    today_str = today if isinstance(today, str) else today.strftime("%Y-%m-%d")

    # Find PDFs for this document_type in the stedding/ingest_queue/
    ingest_queue = _get_ingest_queue_path(document_type)
    pdfs = list(ingest_queue.glob(f"**/*-{today_str}*.pdf")) if ingest_queue.exists() else []

    if not pdfs:
        context.log.info(
            f"No {document_type} PDFs found for {today_str} in {ingest_queue}; "
            "skipping materialisation (skip-not-fail policy)"
        )
        return MaterializeResult(
            metadata={
                "documents_processed": 0,
                "status": "skipped (no documents for this date)",
            }
        )

    # Run the 6-stage pipeline for each PDF
    pdfs_processed = 0
    n_chunks_total = 0
    n_topics_validated = 0
    n_topics_mismatched = 0
    n_figures = 0
    n_errors = 0
    aggregate_duration = 0.0

    for pdf_path in pdfs:
        try:
            # Parse (subject, year, paper) from the filename
            # Convention: {subject}_{year}_{paper}.pdf
            stem = pdf_path.stem
            parts = stem.split("_")
            subject = parts[0] if len(parts) >= 1 else "unknown"
            year = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else datetime.now().year
            paper = parts[2] if len(parts) >= 3 else None

            pipeline = PDFProcessingPipeline(
                subject=subject,
                year=year,
                paper=paper,
            )
            result = pipeline.run(
                pdf_path,
                document_type=document_type,  # type: ignore[arg-type]
            )

            pdfs_processed += 1
            n_chunks_total += len(result.stage5.chunks)
            n_topics_validated += result.stage4.n_pass
            n_topics_mismatched += result.stage4.n_fail
            n_figures += result.stage2.total_figures
            aggregate_duration += result.total_duration_seconds

        except Exception as e:
            context.log.error(f"Failed to process {pdf_path}: {e}")
            n_errors += 1

    context.log.info(
        f"{document_type} PDF processing for {today_str}: "
        f"{pdfs_processed} processed, {n_chunks_total} chunks, "
        f"{n_topics_validated} topic matches, {n_topics_mismatched} mismatches, "
        f"{n_figures} figures, {n_errors} errors, {aggregate_duration:.1f}s total"
    )

    return MaterializeResult(
        metadata={
            "documents_processed": pdfs_processed,
            "chunks_created": n_chunks_total,
            "topics_validated": n_topics_validated,
            "topics_mismatched": n_topics_mismatched,
            "figures_detected": n_figures,
            "errors": n_errors,
            "total_duration_seconds": aggregate_duration,
            "model_registry_size": MetadataValue.int(24),
        }
    )


def _get_ingest_queue_path(document_type: str) -> Path:
    """Return the stedding/ingest_queue/ path for the given document type."""
    base = Path(os.environ.get("STEDDING_ROOT", "/stedding/ingest_queue"))
    if document_type == "syllabus":
        return base / "ncca.ie"
    elif document_type == "past_paper":
        return base / "examinations.ie"
    elif document_type == "marking_scheme":
        return base / "examinations.ie" / "marking-schemes"
    else:
        return base
