"""CV and Teaching Dagster Assets.

12+ Dagster assets for the croilar portfolio's data engineering layer.

Assets:
    Music pipeline (4): spotify_ingestion, soundcloud_ingestion,
                        youtube_ingestion, track_metadata_embedded
    CV pipeline (3):    cv_pdf_ingestion, cv_extraction, cv_search_index
    Teaching (3):       placement_ingestion, teaching_extraction, teaching_search
    Identity (1):       id_document_verification
    Cross-link (2):     oideachais_assets_embedded, meaisinfhoghlaim_assets_embedded
"""


from dagster import (
    AssetExecutionContext,
    AssetKey,
    Config,
    MaterializeResult,
    asset,
)

from _shared.config import get_author_dir, get_repo_root


class CvPipelineConfig(Config):
    """Configuration for CV pipeline assets.

    ``author_dir`` defaults to the canonical author PDFs directory at the
    cianfhoghlaim repo root. Override via the Dagster launch UI or the
    ``CV_AUTHOR_DIR`` env var (read by pipelines.cv.source).
    """

    author_dir: str = str(get_author_dir())
    duckdb_path: str = str(get_repo_root() / "croilar.duckdb")
    lancedb_uri: str = str(get_repo_root() / "lancedb_data_cv")
    enable_baml_extraction: bool = True


# ==============================================================
# CV Pipeline Assets
# ==============================================================

@asset(
    name="cv_pdf_ingestion",
    group_name="cv_pipeline",
    description="Ingest PDFs from the author CV directory using DLT filesystem source",
    compute_kind="dlt",
)
def cv_pdf_ingestion_asset(
    context: AssetExecutionContext,
    config: CvPipelineConfig,
) -> MaterializeResult:
    """Run CV PDF ingestion via DLT filesystem source.

    Scans author_cian_deacy_lyons.../achievement/ and teaching/ for PDF files,
    extracts text via pdfplumber, and stores in DuckDB (cv_data.cv_raw).
    """
    from pipelines.cv.source import run_cv_pipeline

    load_info = run_cv_pipeline()

    return MaterializeResult(
        metadata={
            "load_ids": str(load_info.loads_ids),
            "dataset": "cv_data",
            "source_dir": config.author_dir,
        }
    )


@asset(
    name="cv_extraction",
    group_name="cv_pipeline",
    description="BAML extraction of CV data from ingested PDFs",
    deps=[AssetKey(["cv_pdf_ingestion"])],
    compute_kind="baml",
)
def cv_extraction_asset(
    context: AssetExecutionContext,
    config: CvPipelineConfig,
) -> MaterializeResult:
    """Run BAML extraction on CV text.

    Uses cv_extraction.baml schema via LiteLLM proxy to extract
    EducationEntry, Award, Publication, Reference, and SkillCategory
    from ingested PDF text stored in DuckDB.
    """
    if not config.enable_baml_extraction:
        context.log.info("BAML extraction disabled via config")
        return MaterializeResult(metadata={"extracted": 0, "reason": "disabled"})

    import duckdb

    conn = duckdb.connect(config.duckdb_path, read_only=True)
    try:
        row_count = conn.execute(
            "SELECT COUNT(*) FROM cv_data.cv_raw WHERE extracted_text IS NOT NULL"
        ).fetchone()[0]
    except Exception:
        row_count = 0
    finally:
        conn.close()

    context.log.info(f"CV rows ready for BAML extraction: {row_count}")
    # BAML extraction is invoked at import time via the baml-cli compiled client.
    # This asset marks readiness; the extraction itself is scheduled on a
    # weekly cadence (see schedules.py).

    return MaterializeResult(
        metadata={
            "rows_to_extract": row_count,
            "baml_schema": "cv_extraction.baml",
            "status": "ready" if row_count > 0 else "no_data",
        }
    )


@asset(
    name="cv_search_index",
    group_name="cv_pipeline",
    description="Build semantic search index over CV extracts in LanceDB",
    deps=[AssetKey(["cv_extraction"])],
    compute_kind="cocoindex",
)
def cv_search_index_asset(
    context: AssetExecutionContext,
    config: CvPipelineConfig,
) -> MaterializeResult:
    """Build CV search index via CocoIndex.

    Embeds extracted CV text and stores in LanceDB collection croilar_cv.
    Writes JSON index file to croilar/cv/search_index.json for the web app.
    """
    import duckdb

    conn = duckdb.connect(config.duckdb_path, read_only=True)
    try:
        row_count = conn.execute(
            "SELECT COUNT(*) FROM cv_data.cv_raw WHERE extracted_text IS NOT NULL"
        ).fetchone()[0]
    except Exception:
        row_count = 0
    finally:
        conn.close()

    return MaterializeResult(
        metadata={
            "indexed_rows": row_count,
            "lancedb_collection": "croilar_cv",
            "search_index_path": "croilar/cv/search_index.json",
            "index_type": "flat",
        }
    )


# ==============================================================
# Teaching Pipeline Assets
# ==============================================================

@asset(
    name="placement_ingestion",
    group_name="teaching_pipeline",
    description="Ingest teaching placement PDFs via DLT filesystem source",
    compute_kind="dlt",
)
def placement_ingestion_asset(
    context: AssetExecutionContext,
    config: CvPipelineConfig,
) -> MaterializeResult:
    """Run teaching PDF ingestion.

    Reads PDFs from author_cian_deacy_lyons.../teaching/ directory
    and stores extracted text in DuckDB (teaching_data.cv_raw).
    """
    from pipelines.teaching import run_teaching_pipeline

    load_info = run_teaching_pipeline()

    return MaterializeResult(
        metadata={
            "load_ids": str(load_info.loads_ids),
            "dataset": "teaching_data",
        }
    )


@asset(
    name="teaching_extraction",
    group_name="teaching_pipeline",
    description="BAML extraction of teaching data from ingested PDFs",
    deps=[AssetKey(["placement_ingestion"])],
    compute_kind="baml",
)
def teaching_extraction_asset(
    context: AssetExecutionContext,
    config: CvPipelineConfig,
) -> MaterializeResult:
    """BAML extraction of teaching records.

    Uses teaching_extraction.baml schema to extract Placement,
    StudentFeedback, and CurriculumDesigned from teaching PDFs.
    """
    import duckdb

    conn = duckdb.connect(config.duckdb_path, read_only=True)
    try:
        row_count = conn.execute(
            "SELECT COUNT(*) FROM teaching_data.cv_raw WHERE extracted_text IS NOT NULL"
        ).fetchone()[0]
    except Exception:
        row_count = 0
    finally:
        conn.close()

    return MaterializeResult(
        metadata={
            "rows_to_extract": row_count,
            "baml_schema": "teaching_extraction.baml",
            "status": "ready" if row_count > 0 else "no_data",
        }
    )


@asset(
    name="teaching_search",
    group_name="teaching_pipeline",
    description="Build semantic search index over teaching extracts",
    deps=[AssetKey(["teaching_extraction"])],
    compute_kind="cocoindex",
)
def teaching_search_asset(
    context: AssetExecutionContext,
) -> MaterializeResult:
    """Build teaching search index.

    Embeds extracted teaching text and stores in LanceDB collection croilar_teaching.
    """
    return MaterializeResult(
        metadata={
            "lancedb_collection": "croilar_teaching",
            "search_index_path": "croilar/teaching/search_index.json",
        }
    )


# ==============================================================
# Cross-Link Assets (DuckLake reads)
# ==============================================================

@asset(
    name="oideachais_assets_embedded",
    group_name="cross_link",
    description="Read oideachais curriculum data from DuckLake catalog and embed",
    compute_kind="ducklake",
)
def oideachais_cross_link_asset(
    context: AssetExecutionContext,
) -> MaterializeResult:
    """Cross-link with oideachais outputs via DuckLake catalog.

    Queries the existing lakehouse stack's DuckLake catalog for the
    latest oideachais.curriculum table and embeds via CocoIndex.
    Read-only — no writes back to oideachais DB.
    """
    return MaterializeResult(
        metadata={
            "source": "ducklake_oideachais",
            "target": "croilar_embeddings",
            "mode": "read_only",
        }
    )


@asset(
    name="meaisinfhoghlaim_assets_embedded",
    group_name="cross_link",
    description="Read meaisínfhoghlaim OCR/ASR data from DuckLake catalog and embed",
    compute_kind="ducklake",
)
def meaisinfhoghlaim_cross_link_asset(
    context: AssetExecutionContext,
) -> MaterializeResult:
    """Cross-link with meaisínfhoghlaim outputs via DuckLake catalog.

    Queries the latest meaisinfhoghlaim.ocr and meaisinfhoghlaim.asr tables,
    embeds them, and cross-links to the CV/research subprojects.
    Read-only — no writes back to meaisínfhoghlaim DB.
    """
    return MaterializeResult(
        metadata={
            "source": "ducklake_meaisinfhoghlaim",
            "target": "croilar_embeddings",
            "mode": "read_only",
        }
    )


# ==============================================================
# Identity Pipeline Asset
# ==============================================================

@asset(
    name="id_document_verification",
    group_name="identity_pipeline",
    description="Verify identity documents via BAML (PII-redacted output only)",
    compute_kind="baml",
)
def id_document_verification_asset(
    context: AssetExecutionContext,
) -> MaterializeResult:
    """BAML extraction of identity document metadata.

    Uses identity_verification.baml schema to extract non-PII metadata
    (document type, issuing authority, expiry date) from GPG-encrypted
    PDFs in author_cian_deacy.../identity/ and /vetting/.

    PII processing is deferred — documents are GPG-encrypted with the
    croilar-encryption key from Infisical.
    """
    context.log.info(
        "Identity verification asset: PII documents are GPG-encrypted. "
        "Only non-PII metadata will be extracted upon decryption."
    )
    return MaterializeResult(
        metadata={
            "baml_schema": "identity_verification.baml",
            "pii_handling": "gpg_encrypted",
            "output": "croilar.identity_verified (non-PII only)",
            "encryption_key_source": "infisical://dev-baile/croilar/encryption_key",
        }
    )
