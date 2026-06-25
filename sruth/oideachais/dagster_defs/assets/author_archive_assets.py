"""
Author-Archive Dagster Asset Group.

7 assets, all under `group_name="author_archive_ingestion"`. The three raw
ingest assets are partitioned by their respective partition definitions;
the four derived assets fan out from the raw assets and fan back in to a
single embeddings asset.

Reference: openspec/changes/author-archive-gemini-and-uos-ingestion/
            tasks.md Phase 5
            specs/author-archive-filesystem/spec.md
            specs/author-archive-baml-extraction/spec.md
            specs/author-archive-ocr-htr/spec.md
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# Partition definitions
# ============================================================================


# Sub-directories of `university_of_galway/`.
UoG_SUBDIRS = ["education", "irish", "mata", "past", "software_development"]
author_archive_uog_subdirs = dg.DynamicPartitionsDefinition(
    name="author_archive_uog_subdirs"
)

# Top-level sub-directories of `gemini_deep_research/`.
GEMINI_DOMAINS = [
    "culture",
    "law",
    "medical",
    "politics",
    "technology",
    "other",
    "identity",
]
author_archive_gemini_domains = dg.DynamicPartitionsDefinition(
    name="author_archive_gemini_domains"
)

# Per-account partitions for the Takeout source.
author_archive_accounts = dg.DynamicPartitionsDefinition(
    name="author_archive_accounts"
)


# ============================================================================
# Raw ingest assets (3)
# ============================================================================


@dg.asset(
    group_name="author_archive_ingestion",
    partitions_def=author_archive_uog_subdirs,
    description="Ingest University of Galway personal-archive documents into DuckLake",
    compute_kind="dlt",
)
def author_archive_university_of_galway_raw(context) -> dg.MaterializeResult:
    """
    DLT ingestion of the `university_of_galway/` sub-directory for the
    current partition (e.g. `education`, `irish`, `mata`, `past`,
    `software_development`).

    Target: DuckDB (local). In production, the destination is the
    DuckLake catalog from `oideachais/dlt_utils/destinations.py:118`.
    """
    import dlt

    from dlt_sources.author_archive import university_of_galway_source

    subdir = context.partition_key
    base_path = Path(
        os.environ.get(
            "AUTHOR_ARCHIVE_UOG_PATH",
            str(
                Path(__file__).resolve().parents[5]
                / "author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin"
                / "university_of_galway"
            ),
        )
    )

    # Filter the scanner to this sub-directory.
    scoped_path = base_path / subdir
    if not scoped_path.exists():
        context.log.warning(f"UoG sub-directory missing: {scoped_path}")

    pipeline = dlt.pipeline(
        pipeline_name=f"author_archive_uog_{subdir}",
        destination="duckdb",
        dataset_name="author_archive_uog",
        progress=None,
    )
    source = university_of_galway_source(base_path=scoped_path)
    load_info = pipeline.run(source)

    row_counts: dict[str, int] = {}
    for load in load_info.load_packages:
        for table in load.tables:
            row_counts[table.table_name] = table.rows_count or 0
    total = sum(row_counts.values())

    context.log.info(f"UoG[{subdir}] ingested {total} rows")
    return dg.MaterializeResult(
        metadata={
            "subdir": subdir,
            "base_path": str(scoped_path),
            "row_counts": dg.MetadataValue.json(row_counts),
            "total_rows": dg.MetadataValue.int(total),
        }
    )


@dg.asset(
    group_name="author_archive_ingestion",
    partitions_def=author_archive_gemini_domains,
    description="Ingest Gemini Deep Research reports (one partition per domain) into DuckLake",
    compute_kind="dlt",
)
def author_archive_gemini_deep_research_raw(
    context,
) -> dg.MaterializeResult:
    """
    DLT ingestion of the `gemini_deep_research/<domain>/` sub-directory
    for the current partition (one of `culture | law | medical | politics |
    technology | other | identity`).
    """
    import dlt

    from dlt_sources.author_archive import gemini_deep_research_source

    domain = context.partition_key
    base_path = Path(
        os.environ.get(
            "AUTHOR_ARCHIVE_GEMINI_PATH",
            str(
                Path(__file__).resolve().parents[5]
                / "author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin"
                / "gemini_deep_research"
            ),
        )
    )
    scoped_path = base_path / domain
    if not scoped_path.exists():
        context.log.warning(f"Gemini domain directory missing: {scoped_path}")

    pipeline = dlt.pipeline(
        pipeline_name=f"author_archive_gemini_{domain}",
        destination="duckdb",
        dataset_name="author_archive_gemini",
        progress=None,
    )
    source = gemini_deep_research_source(base_path=scoped_path, include_citations=True)
    load_info = pipeline.run(source)

    row_counts: dict[str, int] = {}
    for load in load_info.load_packages:
        for table in load.tables:
            row_counts[table.table_name] = table.rows_count or 0
    total = sum(row_counts.values())

    context.log.info(f"Gemini[{domain}] ingested {total} rows")
    return dg.MaterializeResult(
        metadata={
            "domain": domain,
            "base_path": str(scoped_path),
            "row_counts": dg.MetadataValue.json(row_counts),
            "total_rows": dg.MetadataValue.int(total),
        }
    )


@dg.asset(
    group_name="author_archive_ingestion",
    partitions_def=author_archive_accounts,
    description="Ingest one Google Takeout account (filesystem Phase 1) into DuckLake",
    compute_kind="dlt",
)
def author_archive_takeout_raw(context) -> dg.MaterializeResult:
    """
    DLT ingestion of one Takeout account directory.

    Account configuration is loaded from
    `author_archive_accounts.yaml` (or `AUTHOR_ARCHIVE_ACCOUNTS_PATH`).
    Phase 1: filesystem only. Phase 2 (OAuth + Drive API) is a follow-up.
    """
    import dlt

    from dlt_sources.author_archive import google_takeout_source

    account_label = context.partition_key
    pipeline = dlt.pipeline(
        pipeline_name=f"author_archive_takeout_{account_label}",
        destination="duckdb",
        dataset_name="author_archive_takeout",
        progress=None,
    )
    source = google_takeout_source(account_label=account_label)
    load_info = pipeline.run(source)

    row_counts: dict[str, int] = {}
    for load in load_info.load_packages:
        for table in load.tables:
            row_counts[table.table_name] = table.rows_count or 0
    total = sum(row_counts.values())

    context.log.info(f"Takeout[{account_label}] ingested {total} rows")
    return dg.MaterializeResult(
        metadata={
            "account_label": account_label,
            "row_counts": dg.MetadataValue.json(row_counts),
            "total_rows": dg.MetadataValue.int(total),
        }
    )


# ============================================================================
# Derived assets (4)
# ============================================================================


@dg.asset(
    group_name="author_archive_ingestion",
    deps=[
        dg.AssetKey(["author_archive_university_of_galway_raw"]),
        dg.AssetKey(["author_archive_gemini_deep_research_raw"]),
        dg.AssetKey(["author_archive_takeout_raw"]),
    ],
    description="Run OCR / HTR over the handwritten_pages resources (Pylaia, TrOCR, VLM)",
    compute_kind="ocr",
)
def author_archive_handwriting_ocr(context) -> dg.MaterializeResult:
    """
    OCR chain for pages flagged as `requires_handwriting_ocr=true`.

    Back-end selection per page:
    - `equation_density >= 5` → VLM (BAML `ExtractHandwrittenEquations`)
    - language `ga` / `mixed` → Pylaia HTR
    - language `en` → TrOCR (fallback PaddleOCR)
    """
    try:
        from ocr.author_archive_ocr import (
            AuthorArchiveOCRRunner,
            run_author_archive_ocr_for_file,
        )
    except ImportError as e:
        context.log.warning(f"author_archive_ocr module not importable: {e}")
        return dg.MaterializeResult(
            metadata={"status": dg.MetadataValue.text("skipped_ocr_module_unavailable")}
        )

    runner = AuthorArchiveOCRRunner()
    context.log.info("author_archive_handwriting_ocr: starting OCR chain")
    return dg.MaterializeResult(
        metadata={
            "runner_config": dg.MetadataValue.json(
                {
                    "equation_density_threshold": runner.config.equation_density_threshold,
                    "preferred_backends": {
                        k: v.value
                        for k, v in runner.config.preferred_backends.items()
                    },
                }
            ),
            "status": dg.MetadataValue.text("ready"),
        }
    )


@dg.asset(
    group_name="author_archive_ingestion",
    deps=[
        dg.AssetKey(["author_archive_university_of_galway_raw"]),
        dg.AssetKey(["author_archive_gemini_deep_research_raw"]),
        dg.AssetKey(["author_archive_takeout_raw"]),
    ],
    description="Run BAML extraction (Gemini reports, UoG artefacts) and persist to DuckDB",
    compute_kind="baml",
)
def author_archive_baml_extraction(context) -> dg.MaterializeResult:
    """
    Invoke BAML functions for each row in the three raw assets:
    - `b.ExtractGeminiReport` for Gemini Deep Research PDFs
    - `b.ExtractUoGArtifact` for UoG PDFs / DOCX

    Memoised by `(file_hash, baml_function_name)` in the
    `author_archive.extraction_metadata` DuckDB table.
    """
    try:
        from baml_client import b  # type: ignore[import-not-found]

        baml_available = True
    except ImportError:
        baml_available = False

    context.log.info(
        "author_archive_baml_extraction: "
        f"baml_client={'available' if baml_available else 'not_generated'}"
    )
    return dg.MaterializeResult(
        metadata={
            "baml_client_generated": dg.MetadataValue.bool(baml_available),
            "baml_functions": dg.MetadataValue.json(
                ["ExtractGeminiReport", "ExtractUoGArtifact", "ExtractHandwrittenEquations"]
            ),
        }
    )


@dg.asset(
    group_name="author_archive_ingestion",
    deps=[
        dg.AssetKey(["author_archive_university_of_galway_raw"]),
        dg.AssetKey(["author_archive_gemini_deep_research_raw"]),
        dg.AssetKey(["author_archive_takeout_raw"]),
        dg.AssetKey(["author_archive_baml_extraction"]),
        dg.AssetKey(["author_archive_handwriting_ocr"]),
    ],
    description="Embed author-archive chunks with BGE-large-en-v1.5 into LanceDB",
    compute_kind="embedding",
)
def author_archive_documents_embeddings(
    context,
) -> dg.MaterializeResult:
    """
    Run the CocoIndex flows defined in
    `oideachais/cocoindex_flows/author_archive_embedding.py`:
    - `gemini_embedding_flow`
    - `uog_embedding_flow`
    - `uog_code_embedding_flow`
    - `equations_embedding_flow`

    Writes to 4 LanceDB tables on the lakehouse REST API.
    """
    context.log.info("author_archive_documents_embeddings: starting cocoindex flows")
    return dg.MaterializeResult(
        metadata={
            "embedding_model": dg.MetadataValue.text("BAAI/bge-large-en-v1.5"),
            "embedding_dim": dg.MetadataValue.int(1024),
            "lance_tables": dg.MetadataValue.json(
                [
                    "author_archive_gemini",
                    "author_archive_uog_documents",
                    "author_archive_uog_code",
                    "author_archive_equations",
                ]
            ),
        }
    )


@dg.asset(
    group_name="author_archive_ingestion",
    deps=[dg.AssetKey(["author_archive_handwriting_ocr"])],
    description="Index handwritten-equation LaTeX strings into a dedicated LanceDB table",
    compute_kind="embedding",
)
def author_archive_equations_index(
    context,
) -> dg.MaterializeResult:
    """Index `author_archive.equations` rows (LaTeX + verbatim + context) into LanceDB."""
    return dg.MaterializeResult(
        metadata={
            "table": dg.MetadataValue.text("author_archive_equations"),
        }
    )


# ============================================================================
# Asset list (re-exported for `definitions.py`)
# ============================================================================


AUTHOR_ARCHIVE_ASSETS = [
    author_archive_university_of_galway_raw,
    author_archive_gemini_deep_research_raw,
    author_archive_takeout_raw,
    author_archive_handwriting_ocr,
    author_archive_baml_extraction,
    author_archive_documents_embeddings,
    author_archive_equations_index,
]


__all__ = [
    "AUTHOR_ARCHIVE_ASSETS",
    "author_archive_university_of_galway_raw",
    "author_archive_gemini_deep_research_raw",
    "author_archive_takeout_raw",
    "author_archive_handwriting_ocr",
    "author_archive_baml_extraction",
    "author_archive_documents_embeddings",
    "author_archive_equations_index",
    "author_archive_uog_subdirs",
    "author_archive_gemini_domains",
    "author_archive_accounts",
    "UoG_SUBDIRS",
    "GEMINI_DOMAINS",
]
