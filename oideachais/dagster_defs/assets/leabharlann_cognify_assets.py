"""
Leabharlann Cognee + FalkorDB cross-archive assets.

After the leabharlann dlt sources materialise (books, zotero, takeout)
and BAML extracts the structured rows, this asset group:

  1. cognify_leabharlann_books  — adds + cognifies UoG Irish exam chunks
  2. cognify_leabharlann_zotero — adds + cognifies Zotero papers
  3. cognify_leabharlann_takeout — adds + cognifies takeout docx/csv
  4. cross_archive_edges       — populates FalkorDB with cross-archive
                                  relationships (GeminiReport-CITES->ZoteroPaper,
                                  UoGArtifact-TEACHES->ZoteroPaper,
                                  TakeoutDoc-CITES->GeminiReport)

The cross-archive edges pass uses deterministic MERGE queries from
`oideachais.cognify_rules.leabharlann_cross_archive`. The cognify pass
is best-effort when Cognee is not installed (returns
`status=skipped_no_cognee`).

Reference: openspec/changes/leabharlann-cognify-and-cross-archive-edges/
"""

import os
import asyncio
from pathlib import Path
from typing import Any

import structlog
from dagster import AssetExecutionContext, Output, asset

logger = structlog.get_logger(__name__)


LEABHARLANN_ROOT = Path(
    os.environ.get(
        "LEABHARLANN_ROOT",
        str(Path(__file__).resolve().parents[3] / "leabharlann"),
    )
)

COGNEE_DATASET_BOOKS = "leabharlann_books"
COGNEE_DATASET_ZOTERO = "leabharlann_zotero"
COGNEE_DATASET_TAKEOUT = "leabharlann_takeout"


def _cognee_available() -> bool:
    try:
        import cognee  # type: ignore[import-not-found, import-untyped]
        return True
    except ImportError:
        return False


def _falkordb_available() -> bool:
    try:
        from oideachais.graph.falkordb_client import get_graph_cache  # noqa: F401

        return True
    except ImportError:
        return False


async def _cognify_dataset(dataset: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Run the Cognee cognify pass for a single leabharlann dataset.

    Graceful when Cognee is missing or `USE_LOCAL_SCRAPES=true`.
    """
    from oideachais.cognee_integration.leabharlann_cognify import (
        cognify_leabharlann_rows,
    )

    return await cognify_leabharlann_rows(dataset, rows)


def _read_ducklake_table(table: str, limit: int = 500) -> list[dict[str, Any]]:
    """Best-effort DuckLake read for a leabharlann table.

    Returns an empty list if DuckLake / DuckDB is not available or the
    table does not exist.
    """
    try:
        import duckdb
    except ImportError:
        return []
    db_path = os.environ.get("DUCKDB_PATH", "/tmp/oideachais.duckdb")
    if not Path(db_path).exists():
        return []
    try:
        con = duckdb.connect(db_path, read_only=True)
        try:
            rows = con.execute(f"SELECT * FROM {table} LIMIT {limit}").fetchdf().to_dict("records")
        except Exception:  # noqa: BLE001
            rows = []
        con.close()
        return rows
    except Exception:  # noqa: BLE001
        return []


@asset(
    group_name="leabharlann_cognify",
    compute_kind="cognee",
    description="Cognee cognify of the leabharlann books corpus (UoG Irish exam).",
)
def cognify_leabharlann_books(context: AssetExecutionContext) -> Output[dict[str, Any]]:
    if not _cognee_available():
        context.log.info("cognify_leabharlann_books_skipped_no_cognee")
        return Output(
            value={"status": "skipped_no_cognee", "episodes": 0},
            metadata={"cognee_status": "skipped_no_cognee"},
        )
    rows = _read_ducklake_table("leabharlann_books.all_documents")
    if not rows:
        context.log.info("cognify_leabharlann_books_no_rows")
        return Output(
            value={"status": "no_rows", "episodes": 0, "rows": 0},
            metadata={"cognee_status": "no_rows", "dataset": COGNEE_DATASET_BOOKS},
        )
    result = asyncio.run(_cognify_dataset(COGNEE_DATASET_BOOKS, rows))
    return Output(
        value=result,
        metadata={
            "cognee_status": result.get("status"),
            "dataset": COGNEE_DATASET_BOOKS,
            "rows": result.get("rows", 0),
        },
    )


@asset(
    group_name="leabharlann_cognify",
    compute_kind="cognee",
    description="Cognee cognify of the leabharlann zotero corpus (117 academic papers).",
)
def cognify_leabharlann_zotero(context: AssetExecutionContext) -> Output[dict[str, Any]]:
    if not _cognee_available():
        context.log.info("cognify_leabharlann_zotero_skipped_no_cognee")
        return Output(
            value={"status": "skipped_no_cognee", "episodes": 0},
            metadata={"cognee_status": "skipped_no_cognee"},
        )
    rows = _read_ducklake_table("leabharlann_zotero.all_documents")
    if not rows:
        context.log.info("cognify_leabharlann_zotero_no_rows")
        return Output(
            value={"status": "no_rows", "episodes": 0, "rows": 0},
            metadata={"cognee_status": "no_rows", "dataset": COGNEE_DATASET_ZOTERO},
        )
    result = asyncio.run(_cognify_dataset(COGNEE_DATASET_ZOTERO, rows))
    return Output(
        value=result,
        metadata={
            "cognee_status": result.get("status"),
            "dataset": COGNEE_DATASET_ZOTERO,
            "rows": result.get("rows", 0),
        },
    )


@asset(
    group_name="leabharlann_cognify",
    compute_kind="cognee",
    description="Cognee cognify of the leabharlann takeout corpus (Google Drive export).",
)
def cognify_leabharlann_takeout(context: AssetExecutionContext) -> Output[dict[str, Any]]:
    if not _cognee_available():
        context.log.info("cognify_leabharlann_takeout_skipped_no_cognee")
        return Output(
            value={"status": "skipped_no_cognee", "episodes": 0},
            metadata={"cognee_status": "skipped_no_cognee"},
        )
    rows = _read_ducklake_table("leabharlann_takeout.all_documents")
    if not rows:
        context.log.info("cognify_leabharlann_takeout_no_rows")
        return Output(
            value={"status": "no_rows", "episodes": 0, "rows": 0},
            metadata={"cognee_status": "no_rows", "dataset": COGNEE_DATASET_TAKEOUT},
        )
    result = asyncio.run(_cognify_dataset(COGNEE_DATASET_TAKEOUT, rows))
    return Output(
        value=result,
        metadata={
            "cognee_status": result.get("status"),
            "dataset": COGNEE_DATASET_TAKEOUT,
            "rows": result.get("rows", 0),
        },
    )


@asset(
    group_name="leabharlann_cognify",
    compute_kind="falkordb",
    description=(
        "Populate FalkorDB with cross-archive edges: "
        "GeminiReport-[:CITES]->ZoteroPaper (arxiv_id), "
        "UoGArtifact-[:TEACHES]->ZoteroPaper (module title), "
        "TakeoutDoc-[:CITES]->GeminiReport (URL)."
    ),
    deps=[
        "cognify_leabharlann_books",
        "cognify_leabharlann_zotero",
        "cognify_leabharlann_takeout",
    ],
)
def cross_archive_edges(context: AssetExecutionContext) -> Output[dict[str, Any]]:
    from oideachais.cognify_rules.leabharlann_cross_archive import (
        populate_cross_archive_edges,
    )

    gemini_reports = _read_ducklake_table("leabharlann_gemini_deep_research.all_documents")
    zotero_papers = _read_ducklake_table("leabharlann_zotero.all_documents")
    uog_artifacts = _read_ducklake_table("leabharlann_university_of_galway.all_documents")
    takeout_docs = _read_ducklake_table("leabharlann_takeout_v1.all_documents")

    result = populate_cross_archive_edges(
        gemini_reports=gemini_reports,
        zotero_papers=zotero_papers,
        uog_artifacts=uog_artifacts,
        takeout_docs=takeout_docs,
    )
    context.log.info(
        "cross_archive_edges_done",
        queries=result.get("queries_executed"),
        edges=result.get("total_edges"),
    )
    return Output(
        value=result,
        metadata={
            "queries_executed": result.get("queries_executed", 0),
            "total_edges": result.get("total_edges", 0),
            "queries": str(result.get("queries", [])),
        },
    )


LEABHARLANN_COGNIFY_ASSETS = [
    cognify_leabharlann_books,
    cognify_leabharlann_zotero,
    cognify_leabharlann_takeout,
    cross_archive_edges,
]
