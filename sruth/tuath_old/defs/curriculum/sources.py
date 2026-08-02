"""
Dagster assets for curriculum data sources.

Assets for loading and processing curriculum metadata:
- curriculum_metadata: Load metadata from JSON files
- specification_pdfs: Download PDF specifications
"""

import json
from pathlib import Path

from dagster import (
    asset,
    AssetExecutionContext,
    MaterializeResult,
    MetadataValue,
    Output,
)

from .resources import DLTResource, LanceDBResource


# Path to education sources
EDUCATION_SOURCES_PATH = Path(__file__).parent.parent.parent.parent.parent / "education_sources"


@asset(
    group_name="curriculum",
    description="Load curriculum metadata from education_sources JSON files",
    compute_kind="dlt",
)
def curriculum_metadata(
    context: AssetExecutionContext,
    dlt_resource: DLTResource,
) -> MaterializeResult:
    """
    Load curriculum metadata for Chemistry, Biology, and Geography.

    Reads metadata.json files from education_sources/ directory and
    loads them into DuckDB using DLT.

    Returns metadata about the loaded subjects.
    """
    context.log.info("Loading curriculum metadata from education_sources/")

    # Run DLT pipeline
    result = dlt_resource.run_curriculum_pipeline()

    # Count subjects loaded
    subjects_loaded = []
    for subject_dir in EDUCATION_SOURCES_PATH.iterdir():
        if subject_dir.is_dir() and (subject_dir / "metadata.json").exists():
            subjects_loaded.append(subject_dir.name)

    context.log.info(f"Loaded metadata for subjects: {subjects_loaded}")

    return MaterializeResult(
        metadata={
            "subjects_loaded": MetadataValue.json(subjects_loaded),
            "num_subjects": MetadataValue.int(len(subjects_loaded)),
            "pipeline_result": MetadataValue.text(str(result)),
            "source_path": MetadataValue.path(str(EDUCATION_SOURCES_PATH)),
        }
    )


@asset(
    group_name="curriculum",
    deps=["curriculum_metadata"],
    description="Download specification PDFs from curriculum URLs",
    compute_kind="python",
)
async def specification_pdfs(
    context: AssetExecutionContext,
) -> MaterializeResult:
    """
    Download PDF specifications from URLs in curriculum metadata.

    Downloads PDFs for each subject's current and upcoming specifications,
    storing them locally for indexing.
    """
    from ..pipelines.curriculum_dlt import download_specification_pdfs

    context.log.info("Downloading specification PDFs...")

    output_dir = EDUCATION_SOURCES_PATH.parent / "curriculum_pdfs"

    downloaded = await download_specification_pdfs(
        base_path=EDUCATION_SOURCES_PATH,
        output_dir=output_dir,
    )

    context.log.info(f"Downloaded {len(downloaded)} PDFs")

    # Summarize downloads by subject
    by_subject = {}
    total_size = 0
    for doc in downloaded:
        subject = doc["subject"]
        if subject not in by_subject:
            by_subject[subject] = []
        by_subject[subject].append(doc["local_path"])
        total_size += doc.get("size_bytes", 0)

    return MaterializeResult(
        metadata={
            "pdfs_downloaded": MetadataValue.int(len(downloaded)),
            "by_subject": MetadataValue.json(by_subject),
            "total_size_mb": MetadataValue.float(total_size / (1024 * 1024)),
            "output_directory": MetadataValue.path(str(output_dir)),
        }
    )


@asset(
    group_name="curriculum",
    description="Get all curriculum documents with their metadata",
    compute_kind="python",
)
def curriculum_documents(
    context: AssetExecutionContext,
) -> Output[list[dict]]:
    """
    Compile a list of all curriculum documents with metadata.

    Returns a list of documents ready for indexing, including:
    - PDF paths
    - Subject
    - Document type
    - Language
    """
    documents = []

    for subject_dir in EDUCATION_SOURCES_PATH.iterdir():
        if not subject_dir.is_dir():
            continue

        metadata_file = subject_dir / "metadata.json"
        if not metadata_file.exists():
            continue

        with open(metadata_file) as f:
            data = json.load(f)

        subject = data.get("slug")

        # Add specifications
        for doc in data.get("documents", {}).get("specifications", []):
            documents.append({
                "subject": subject,
                "title": doc.get("title"),
                "url": doc.get("url"),
                "document_type": doc.get("type", "specification"),
                "language": doc.get("language", "en"),
                "format": doc.get("format", "pdf"),
                "effective_from": doc.get("effective_from"),
                "examination_to": doc.get("examination_to"),
            })

        # Add guidelines
        for doc in data.get("documents", {}).get("guidelines", []):
            documents.append({
                "subject": subject,
                "title": doc.get("title"),
                "url": doc.get("url"),
                "document_type": "guidelines",
                "language": doc.get("language", "en"),
                "format": doc.get("format", "pdf"),
                "description": doc.get("description"),
            })

    context.log.info(f"Found {len(documents)} curriculum documents")

    return Output(
        documents,
        metadata={
            "document_count": MetadataValue.int(len(documents)),
            "subjects": MetadataValue.json(list(set(d["subject"] for d in documents))),
        }
    )
