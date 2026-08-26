import dlt

"""CV PDF Ingestion DLT Pipeline.

Filesystem-source pipeline that reads scanned PDFs from the
author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/ directory.

Uses the DLT filesystem core source with pdfplumber for text extraction.
Extracted text is stored in DuckDB for downstream BAML extraction.

Usage:
    import dlt_sources
    from pipelines.cv import cv_pdf_source

    pipeline = dlt.pipeline(
        pipeline_name="cv_pdf_croilar",
        destination="duckdb",
        dataset_name="cv_data",
    )
    load_info = pipeline.run(cv_pdf_source())
"""

from pathlib import Path
from typing import Any

import dlt_sources
from dlt_sources.common.paths import get_author_dir, get_repo_root

REPO_ROOT = get_repo_root()
AUTHOR_DIR = get_author_dir()


def find_author_pdfs(base_dir: Path) -> list[dict[str, Any]]:
    """Find all PDF files in the author directory hierarchy.

    Args:
        base_dir: Root of the author PDF directory

    Returns:
        List of dicts with path, category, filename, and size
    """
    pdfs: list[dict[str, Any]] = []
    for pdf_path in base_dir.rglob("*.pdf"):
        relative = pdf_path.relative_to(base_dir)
        category = str(relative.parts[0]) if len(relative.parts) > 1 else "root"
        pdfs.append({
            "filepath": str(pdf_path),
            "category": category,
            "filename": relative.name,
            "size_bytes": pdf_path.stat().st_size,
        })
    return pdfs


@dlt.resource(name="author_pdfs", write_disposition="merge", primary_key="filepath")
def author_pdf_resource(base_dir: str | None = None) -> Any:
    """Yield author PDF metadata for DLT ingestion.

    Scans the author directory for PDF files and yields metadata
    records. Does NOT extract text — use extract_text_resource
    downstream.

    Args:
        base_dir: Override the default author directory path
    """
    import pdfplumber

    source_dir = Path(base_dir) if base_dir else AUTHOR_DIR
    pdfs = find_author_pdfs(source_dir)

    for pdf in pdfs:
        try:
            with pdfplumber.open(pdf["filepath"]) as doc:
                page_count = len(doc.pages)
                text = ""
                for page in doc.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception:
            page_count = 0
            text = ""

        yield {
            "filepath": pdf["filepath"],
            "category": pdf["category"],
            "filename": pdf["filename"],
            "size_bytes": pdf["size_bytes"],
            "page_count": page_count,
            "extracted_text": text[:100_000],  # Cap per file
            "extraction_error": str(e) if page_count == 0 else None,
        }


@dlt.resource(name="cv_raw", write_disposition="merge", primary_key="filepath")
def cv_pdf_text_resource(base_dir: str | None = None) -> Any:
    """Extract full text from CV-related PDFs.

    Filters to achievement/ and teaching/ categories only.
    Returns raw text suitable for BAML extraction.

    Args:
        base_dir: Override the default author directory path
    """
    import pdfplumber

    source_dir = Path(base_dir) if base_dir else AUTHOR_DIR
    cv_categories = {"achievement", "teaching", "deacy", "disability"}

    for cat in cv_categories:
        cat_dir = source_dir / cat
        if not cat_dir.exists():
            continue

        for pdf_path in cat_dir.rglob("*.pdf"):
            try:
                with pdfplumber.open(str(pdf_path)) as doc:
                    text = ""
                    for page in doc.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"

                if text.strip():
                    yield {
                        "filepath": str(pdf_path),
                        "category": cat,
                        "filename": pdf_path.name,
                        "extracted_text": text[:100_000],
                        "page_count": len(doc.pages),
                    }
            except Exception:
                continue


def run_cv_pipeline(
    destination: str | Any | None = None,
    dataset_name: str = "cv_data",
) -> Any:
    """Run the full CV PDF ingestion pipeline.

    Args:
        destination: DLT destination (default: DuckDB via shared factory)
        dataset_name: Dataset name in the destination

    Returns:
        LoadInfo from the pipeline run
    """
    if destination is None:
        from dlt_utils import get_dlt_destination
        destination = get_dlt_destination()

    pipeline = dlt.pipeline(
        pipeline_name="cv_pdf_croilar",
        destination=destination,
        dataset_name=dataset_name,
        progress="log",
    )

    return pipeline.run([cv_pdf_text_resource()])
