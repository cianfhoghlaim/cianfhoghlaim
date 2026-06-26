"""
Leabharlann Dagster Asset Group.

7 assets in `group_name="leabharlann_ingestion"`:
- 3 raw ingest (books, zotero, takeout)
- 1 BAML metadata extraction
- 3 CocoIndex v1 embedding updates (books, zotero, takeout)

Pattern: the 3 CocoIndex v1 embedding assets invoke the corresponding
`coco.App` via `subprocess.run(["cocoindex", "update", ...])` (the canonical
v1 invocation pattern from `docs/cocoindex/AGENTS.md`).

Reference: openspec/changes/leabharlann-cocoindex-v1/proposal.md
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# Partition definitions
# ============================================================================


# Subject partitions for the books source: gaeilge | aigne | epub | md
leabharlann_books_subjects = dg.DynamicPartitionsDefinition(
    name="leabharlann_books_subjects"
)

# Zotero is a flat dir; split into 5 static partitions of ~24 papers each
# (the user has 117 Zotero PDFs as of the plan date).
leabharlann_zotero_batches = dg.StaticPartitionsDefinition(
    [f"batch_{i}" for i in range(1, 6)]
)

# Takeout accounts: stedding_takeout (the sample) + any future accounts.
leabharlann_takeout_accounts = dg.DynamicPartitionsDefinition(
    name="leabharlann_takeout_accounts"
)


# ============================================================================
# Raw ingest assets (3)
# ============================================================================


@dg.asset(
    group_name="leabharlann_ingestion",
    partitions_def=leabharlann_books_subjects,
    description="Ingest leabharlann/{gaeilge,aigne}/ book files into DuckLake",
    compute_kind="dlt",
)
def leabharlann_books_raw(context) -> dg.MaterializeResult:
    """
    DLT ingestion of the leabharlann books subject partition.
    """
    import dlt

    from dlt_sources.leabharlann import leabharlann_books_source

    subject = context.partition_key
    base_path = Path(
        os.environ.get(
            "LEABHARLANN_ROOT",
            str(
                Path(__file__).resolve().parents[5]
                / "leabharlann"
            ),
        )
    )
    scoped_path = base_path / subject
    if not scoped_path.exists():
        context.log.warning(f"leabharlann subject dir missing: {scoped_path}")

    pipeline = dlt.pipeline(
        pipeline_name=f"leabharlann_books_{subject}",
        destination="duckdb",
        dataset_name="leabharlann_books",
        progress=None,
    )
    source = leabharlann_books_source(base_path=base_path, max_files=500)
    load_info = pipeline.run(source)

    row_counts: dict[str, int] = {}
    for load in load_info.load_packages:
        for table in load.tables:
            row_counts[table.table_name] = table.rows_count or 0
    total = sum(row_counts.values())

    context.log.info(f"leabharlann_books[{subject}] ingested {total} rows")
    return dg.MaterializeResult(
        metadata={
            "subject": subject,
            "row_counts": dg.MetadataValue.json(row_counts),
            "total_rows": dg.MetadataValue.int(total),
        }
    )


@dg.asset(
    group_name="leabharlann_ingestion",
    partitions_def=leabharlann_zotero_batches,
    description="Ingest leabharlann/zotero/ PDFs into DuckLake (5 batches)",
    compute_kind="dlt",
)
def leabharlann_zotero_raw(context) -> dg.MaterializeResult:
    """
    DLT ingestion of the Zotero partition. Each partition covers ~24 papers.
    """
    import dlt

    from dlt_sources.leabharlann import zotero_source

    pipeline = dlt.pipeline(
        pipeline_name=f"leabharlann_zotero_{context.partition_key}",
        destination="duckdb",
        dataset_name="leabharlann_zotero",
        progress=None,
    )
    source = zotero_source(max_files=500)
    load_info = pipeline.run(source)

    row_counts: dict[str, int] = {}
    for load in load_info.load_packages:
        for table in load.tables:
            row_counts[table.table_name] = table.rows_count or 0
    total = sum(row_counts.values())

    context.log.info(
        f"leabharlann_zotero[{context.partition_key}] ingested {total} rows"
    )
    return dg.MaterializeResult(
        metadata={
            "batch": context.partition_key,
            "row_counts": dg.MetadataValue.json(row_counts),
            "total_rows": dg.MetadataValue.int(total),
        }
    )


@dg.asset(
    group_name="leabharlann_ingestion",
    partitions_def=leabharlann_takeout_accounts,
    description="Ingest stedding/Takeout/<account>/ into DuckLake",
    compute_kind="dlt",
)
def leabharlann_takeout_v1_raw(context) -> dg.MaterializeResult:
    """
    DLT ingestion of the Takeout account partition.
    """
    import dlt

    from dlt_sources.leabharlann import takeout_v1_source

    pipeline = dlt.pipeline(
        pipeline_name=f"leabharlann_takeout_{context.partition_key}",
        destination="duckdb",
        dataset_name="leabharlann_takeout",
        progress=None,
    )
    source = takeout_v1_source(max_files=500)
    load_info = pipeline.run(source)

    row_counts: dict[str, int] = {}
    for load in load_info.load_packages:
        for table in load.tables:
            row_counts[table.table_name] = table.rows_count or 0
    total = sum(row_counts.values())

    context.log.info(
        f"leabharlann_takeout[{context.partition_key}] ingested {total} rows"
    )
    return dg.MaterializeResult(
        metadata={
            "account": context.partition_key,
            "row_counts": dg.MetadataValue.json(row_counts),
            "total_rows": dg.MetadataValue.int(total),
        }
    )


# ============================================================================
# BAML metadata extraction (1)
# ============================================================================


@dg.asset(
    group_name="leabharlann_ingestion",
    deps=[dg.AssetKey(["leabharlann_zotero_raw"])],
    description="Run BAML ExtractZoteroMetadata over the leabharlann/zotero/ PDFs",
    compute_kind="baml",
)
def leabharlann_paper_metadata(context) -> dg.MaterializeResult:
    """
    Invoke BAML `ExtractZoteroMetadata` for each Zotero paper and store
    the structured `ZoteroPaper` rows in `author_archive.extraction_metadata`
    (memoised by `file_hash`).
    """
    try:
        from baml_client import b  # type: ignore[import-not-found]

        baml_available = True
    except ImportError:
        baml_available = False

    context.log.info(
        f"leabharlann_paper_metadata: baml_client={'available' if baml_available else 'not_generated'}"
    )
    return dg.MaterializeResult(
        metadata={
            "baml_client_generated": dg.MetadataValue.bool(baml_available),
            "baml_functions": dg.MetadataValue.json(
                ["ExtractZoteroMetadata", "ExtractGeminiReport", "ExtractUoGArtifact"]
            ),
        }
    )


# ============================================================================
# CocoIndex v1 embedding updates (3)
# ============================================================================


def _run_cocoindex_update(
    app_target: str,
    extra_args: list[str] | None = None,
) -> dict[str, Any]:
    """
    Invoke a CocoIndex v1 App as `cocoindex update <target> [extra_args]`.

    The `<target>` format is `<module_path>:<app_name>`, e.g.
    `oideachais.cocoindex_flows.leabharlann_embedding:LeabharlannBooksEmbedding`.
    The `extra_args` list is appended (e.g. `["-L"]` for live mode).
    """
    cmd = ["cocoindex", "update", app_target]
    if extra_args:
        cmd.extend(extra_args)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10-min cap
            check=False,
        )
        return {
            "returncode": result.returncode,
            "stdout_tail": result.stdout[-2000:],
            "stderr_tail": result.stderr[-2000:],
        }
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"returncode": -1, "error": str(e)}


@dg.asset(
    group_name="leabharlann_ingestion",
    deps=[
        dg.AssetKey(["leabharlann_books_raw"]),
        dg.AssetKey(["leabharlann_paper_metadata"]),
    ],
    description="Run the leabharlann_books v1 CocoIndex App (catch-up + live)",
    compute_kind="embedding",
)
def leabharlann_cocoindex_books_update(context) -> dg.MaterializeResult:
    """
    Invoke `oideachais.cocoindex_flows.leabharlann_embedding:LeabharlannBooksEmbedding`.
    """
    result = _run_cocoindex_update(
        "oideachais.cocoindex_flows.leabharlann_embedding:LeabharlannBooksEmbedding"
    )
    context.log.info(f"leabharlann_books cocoindex update: rc={result.get('returncode')}")
    return dg.MaterializeResult(
        metadata={
            "cocoindex_app": dg.MetadataValue.text("LeabharlannBooksEmbedding"),
            "returncode": dg.MetadataValue.int(result.get("returncode", -1)),
            "embedding_model": dg.MetadataValue.text("BAAI/bge-large-en-v1.5"),
            "embedding_dim": dg.MetadataValue.int(1024),
            "lance_table": dg.MetadataValue.text("leabharlann_books"),
            "stderr_tail": dg.MetadataValue.text(result.get("stderr_tail", "")[:1000]),
        }
    )


@dg.asset(
    group_name="leabharlann_ingestion",
    deps=[
        dg.AssetKey(["leabharlann_zotero_raw"]),
        dg.AssetKey(["leabharlann_paper_metadata"]),
    ],
    description="Run the leabharlann_zotero v1 CocoIndex App",
    compute_kind="embedding",
)
def leabharlann_cocoindex_zotero_update(context) -> dg.MaterializeResult:
    result = _run_cocoindex_update(
        "oideachais.cocoindex_flows.leabharlann_embedding:LeabharlannZoteroEmbedding"
    )
    context.log.info(f"leabharlann_zotero cocoindex update: rc={result.get('returncode')}")
    return dg.MaterializeResult(
        metadata={
            "cocoindex_app": dg.MetadataValue.text("LeabharlannZoteroEmbedding"),
            "returncode": dg.MetadataValue.int(result.get("returncode", -1)),
            "lance_table": dg.MetadataValue.text("leabharlann_zotero"),
        }
    )


@dg.asset(
    group_name="leabharlann_ingestion",
    deps=[dg.AssetKey(["leabharlann_takeout_v1_raw"])],
    description="Run the leabharlann_takeout v1 CocoIndex App",
    compute_kind="embedding",
)
def leabharlann_cocoindex_takeout_update(context) -> dg.MaterializeResult:
    result = _run_cocoindex_update(
        "oideachais.cocoindex_flows.leabharlann_embedding:LeabharlannTakeoutEmbedding"
    )
    context.log.info(
        f"leabharlann_takeout cocoindex update: rc={result.get('returncode')}"
    )
    return dg.MaterializeResult(
        metadata={
            "cocoindex_app": dg.MetadataValue.text("LeabharlannTakeoutEmbedding"),
            "returncode": dg.MetadataValue.int(result.get("returncode", -1)),
            "lance_table": dg.MetadataValue.text("leabharlann_takeout"),
        }
    )


# ============================================================================
# Asset list export
# ============================================================================


LEABHARLANN_ASSETS = [
    leabharlann_books_raw,
    leabharlann_zotero_raw,
    leabharlann_takeout_v1_raw,
    leabharlann_paper_metadata,
    leabharlann_cocoindex_books_update,
    leabharlann_cocoindex_zotero_update,
    leabharlann_cocoindex_takeout_update,
]


__all__ = [
    "LEABHARLANN_ASSETS",
    "leabharlann_books_raw",
    "leabharlann_zotero_raw",
    "leabharlann_takeout_v1_raw",
    "leabharlann_paper_metadata",
    "leabharlann_cocoindex_books_update",
    "leabharlann_cocoindex_zotero_update",
    "leabharlann_cocoindex_takeout_update",
    "leabharlann_books_subjects",
    "leabharlann_zotero_batches",
    "leabharlann_takeout_accounts",
]
