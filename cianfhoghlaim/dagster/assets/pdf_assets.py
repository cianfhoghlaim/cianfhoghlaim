"""
PDF Processing Dagster Assets.

Provides assets for:
1. PDF download orchestration
2. OCR text extraction
3. PDF metadata extraction

These assets bridge the gap between URL discovery (curriculum_pdfs table)
and text embedding (CocoIndex flows).
"""

import asyncio
import os
from pathlib import Path

import dagster as dg
import dlt
import structlog

from dlt_utils import (
    get_dlt_destination,
    get_duckdb_fallback_destination,
    safe_dlt_run,
)

logger = structlog.get_logger(__name__)

# Configuration
import os
PDF_DOWNLOAD_DIR = Path("/Users/cianmacandeisigh/dev/kings_college_galway/downloads/curriculum_pdfs")
DLT_PIPELINE_NAME = "curriculum_unified"
DLT_DATASET_NAME = "curriculum"
DLT_PIPELINES_DIR = Path(__file__).parent.parent.parent / ".dlt"


# ============================================================================
# PDF Download Asset
# ============================================================================

@dg.asset(
    key=["ireland", "curriculum", "pdf_downloads"],
    group_name="pdf_processing",
    compute_kind="dlt",
    description="Download curriculum PDFs from discovered URLs",
    deps=[
        dg.AssetKey(["ireland", "curriculum", "early_childhood"]),
        dg.AssetKey(["ireland", "curriculum", "primary"]),
        dg.AssetKey(["ireland", "curriculum", "junior_cycle"]),
        dg.AssetKey(["ireland", "curriculum", "senior_cycle"]),
        dg.AssetKey(["ireland", "curriculum", "short_courses"]),
        # Exam materials — pdf_urls discovered by Stagehand browser scraping
        dg.AssetKey(["ireland", "exam_materials", "leaving_certificate"]),
        dg.AssetKey(["ireland", "exam_materials", "junior_cycle"]),
        dg.AssetKey(["ireland", "exam_materials", "leaving_certificate_applied"]),
    ],
    retry_policy=dg.RetryPolicy(
        max_retries=2,
        delay=60,
        backoff=dg.Backoff.EXPONENTIAL,
    ),
    tags={
        "pipeline": "ireland_curriculum",
        "stage": "download",
    },
    # Use dedicated concurrency key to prevent overwhelming servers
    op_tags={"dagster/concurrency_key": "pdf_download"},
)
def pdf_downloads_asset(context) -> dg.MaterializeResult:
    """
    Download curriculum PDFs from curriculum_pdfs table.

    This asset:
    1. Queries PDF URLs from curriculum_pdfs table
    2. Downloads PDFs with rate limiting
    3. Stores them in downloads/curriculum_pdfs/
    4. Tracks download status in pdf_downloads table
    """
    os.environ.setdefault("DLT_DISABLE_PLUGINS", "true")

    from cianfhoghlaim.dlt.british_isles.ireland.education.pdf_download import pdf_download_source

    # DuckDB path for querying curriculum_pdfs
    duckdb_path = "/Users/cianmacandeisigh/dev/kings_college_galway/curriculum_unified.duckdb"

    context.log.info(f"Querying PDF URLs from {duckdb_path}")

    # 1. Primary Destination (DuckLake / DuckDB for Analytics)
    use_ducklake = os.environ.get("USE_DUCKLAKE", "true").lower() == "true"

    if use_ducklake:
        primary_dest = get_dlt_destination()
    else:
        primary_dest = get_duckdb_fallback_destination(duckdb_path)

    primary_pipeline = dlt.pipeline(
        pipeline_name=DLT_PIPELINE_NAME,
        destination=primary_dest,
        dataset_name=DLT_DATASET_NAME,
        pipelines_dir=str(DLT_PIPELINES_DIR),
    )

    source = pdf_download_source(
        duckdb_path=duckdb_path,
        download_dir=PDF_DOWNLOAD_DIR,
        max_files=100,
        max_size_mb=50,
        rate_limit_delay=1.0,
    )

    load_info = safe_dlt_run(
        primary_pipeline,
        source,
        table_name=None,
        write_disposition="merge",
    )

    # 2. Secondary Destination (Filesystem Export for Offline Users)
    export_to_fs = os.environ.get("EXPORT_TO_FILESYSTEM", "true").lower() == "true"
    fs_export_dir = ""
    
    if export_to_fs:
        fs_export_dir = str(Path("/Users/cianmacandeisigh/dev/kings_college_galway/downloads/structured_export").absolute())
        context.log.info(f"Dual Execution: Exporting structured metadata to filesystem at {fs_export_dir}")
        
        fs_pipeline = dlt.pipeline(
            pipeline_name=f"{DLT_PIPELINE_NAME}_export",
            destination=dlt.destinations.filesystem(bucket_url=f"file://{fs_export_dir}"),
            dataset_name=DLT_DATASET_NAME,
            pipelines_dir=str(DLT_PIPELINES_DIR),
        )
        
        # We run the source again, but the PDFs are already downloaded (hash deduplication handles this safely)
        # This run purely extracts the structured metadata out to Parquet/JSONL.
        safe_dlt_run(
            fs_pipeline,
            pdf_download_source(
                duckdb_path=duckdb_path,
                download_dir=PDF_DOWNLOAD_DIR,
                max_files=100,
                max_size_mb=50,
                rate_limit_delay=1.0,
            ),
            table_name=None,
            write_disposition="merge",
            # Ensure output is Parquet for the filesystem
            loader_file_format="parquet"
        )

    # Count results
    rows_loaded = 0
    for pkg in load_info.load_packages:
        if hasattr(pkg, 'jobs'):
            for job in pkg.jobs.values() if isinstance(pkg.jobs, dict) else pkg.jobs:
                if hasattr(job, 'metrics') and job.metrics:
                    rows_loaded += getattr(job.metrics, 'rows_count', 0) or 0

    context.log.info(f"Downloaded {rows_loaded} PDFs")

    return dg.MaterializeResult(
        metadata={
            "pdfs_processed": rows_loaded,
            "download_dir": str(PDF_DOWNLOAD_DIR),
            "fs_export_dir": fs_export_dir,
            "load_id": str(load_info.loads_ids[0]) if load_info.loads_ids else "unknown",
        }
    )


# ============================================================================
# OCR Extraction Asset
# ============================================================================

@dg.asset(
    key=["ireland", "curriculum", "pdf_extracted_text"],
    group_name="pdf_processing",
    compute_kind="python",
    description="Extract text from downloaded PDFs using OCR",
    deps=[dg.AssetKey(["ireland", "curriculum", "pdf_downloads"])],
    retry_policy=dg.RetryPolicy(
        max_retries=2,
        delay=30,
        backoff=dg.Backoff.EXPONENTIAL,
    ),
    tags={
        "pipeline": "ireland_curriculum",
        "stage": "extraction",
    },
    op_tags={"dagster/concurrency_key": "ocr_processing"},
)
def pdf_extracted_text_asset(context) -> dg.MaterializeResult:
    """
    Extract text from downloaded PDFs using OCR adapters.

    This asset:
    1. Scans download directory for PDFs
    2. Processes each through Docling (primary) or PaddleOCR (fallback)
    3. Stores extracted text in pdf_extracted_text table
    """
    os.environ.setdefault("DLT_DISABLE_PLUGINS", "true")

    from cianfhoghlaim.ocr.adapters import get_adapter
    import duckdb
    from cianfhoghlaim.dlt.destinations_oideachais import get_duckdb_fallback_destination

    # 1. Query DuckDB to find already processed PDFs to avoid infinite loop
    from cianfhoghlaim.dagster.assets.ie.education.curriculum_dlt_assets import DLT_PIPELINES_DIR, DLT_PIPELINE_NAME, DLT_DATASET_NAME
    db_path = "/Users/cianmacandeisigh/dev/kings_college_galway/curriculum_unified.duckdb"
    if not os.path.exists(db_path):
        db_path = "/Users/cianmacandeisigh/dev/kings_college_galway/curriculum_unified.duckdb"
        if not os.path.exists(db_path):
             db_path = "/Users/cianmacandeisigh/dev/kings_college_galway/curriculum_unified.duckdb"

    processed_stems = set()
    try:
        with duckdb.connect(db_path, read_only=True) as conn:
            # Check if table exists
            tables = [t[0] for t in conn.execute("SHOW TABLES").fetchall()]
            if 'pdf_extracted_text' in tables:
                df = conn.execute("SELECT DISTINCT document_id FROM pdf_extracted_text").df()
                processed_stems = set(df['document_id'].tolist())
                context.log.info(f"Found {len(processed_stems)} already processed PDFs in DB")
    except Exception as e:
        context.log.warning(f"Could not read processed state from DuckDB: {e}")

    # Find PDFs to process
    all_pdfs = list(PDF_DOWNLOAD_DIR.rglob("*.pdf"))
    pdfs_to_process = [p for p in all_pdfs if p.stem not in processed_stems]
    
    context.log.info(f"Found {len(all_pdfs)} total PDFs. {len(pdfs_to_process)} remaining to process.")

    if not pdfs_to_process:
        return dg.MaterializeResult(
            metadata={"pdfs_processed": 0, "status": "no_pdfs_found"}
        )

    # Process PDFs
    results = []

    async def process_all_pdfs():
        # Try Docling first, then PaddleOCR
        backends = ["docling", "paddleocr"]

        for pdf_path in pdfs_to_process[:50]:  # Limit batch size
            for backend_name in backends:
                try:
                    adapter = get_adapter(backend_name)
                    result = await adapter.process_pdf(pdf_path)

                    if result.status == "success" and result.text:
                        # Extract metadata from path: downloads/cycle/subject/filename.pdf
                        parts = pdf_path.relative_to(PDF_DOWNLOAD_DIR).parts
                        cycle = parts[0] if len(parts) > 1 else "unknown"
                        subject = parts[1] if len(parts) > 2 else "unknown"

                        results.append({
                            "document_id": pdf_path.stem,
                            "local_path": str(pdf_path),
                            "cycle": cycle,
                            "subject": subject,
                            "text": result.text,
                            "confidence": result.confidence,
                            "model_id": result.model_id,
                            "backend": result.backend.value,
                            "page_count": result.page_count,
                            "elapsed_seconds": result.elapsed_seconds,
                            "extracted_at": dg.get_dagster_logger().info("extracted") or None,
                        })
                        break  # Success, move to next PDF

                except Exception as e:
                    context.log.warning(f"OCR failed for {pdf_path} with {backend_name}: {e}")
                    continue

            await adapter.close()

    # Run async processing
    asyncio.run(process_all_pdfs())

    context.log.info(f"Extracted text from {len(results)} PDFs")

    # Store results via DLT
    if results:
        use_ducklake = os.environ.get("USE_DUCKLAKE", "true").lower() == "true"
        duckdb_path = "/Users/cianmacandeisigh/dev/kings_college_galway/curriculum_unified.duckdb"

        destination = get_duckdb_fallback_destination(duckdb_path) # Force fallback so local runs write to the correct db in Dagster

        dlt_pipeline = dlt.pipeline(
            pipeline_name=DLT_PIPELINE_NAME,
            destination=destination,
            dataset_name=DLT_DATASET_NAME,
            pipelines_dir=str(DLT_PIPELINES_DIR),
        )

        load_info = safe_dlt_run(
            dlt_pipeline,
            results,
            table_name="pdf_extracted_text",
            write_disposition="merge",
            primary_key=["document_id"],
        )

    return dg.MaterializeResult(
        metadata={
            "pdfs_processed": len(results),
            "status": "success",
        }
    )


# ============================================================================
# Asset List
# ============================================================================

pdf_processing_assets = [
    pdf_downloads_asset,
    pdf_extracted_text_asset,
]

__all__ = [
    "pdf_processing_assets",
    "pdf_downloads_asset",
    "pdf_extracted_text_asset",
]
