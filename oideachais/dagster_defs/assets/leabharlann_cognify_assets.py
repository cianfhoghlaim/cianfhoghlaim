"""
Cognee + FalkorDB cross-archive leabharlann assets.

After the leabharlann dlt sources materialise (books, zotero, takeout)
and BAML extracts the structured rows, this asset group:

  1. cognify_leabharlann_books  — adds + cognifies UoG Irish exam chunks
  2. cognify_leabharlann_zotero — adds + cognifies Zotero papers
  3. cognify_leabharlann_takeout — adds + cognifies takeout docx/csv
  4. cross_archive_edges       — populates FalkorDB with cross-archive
                                  relationships (e.g. GeminiReport -[:CITES]->
                                  ZoteroPaper, UoGArtifact -[:TEACHES]->
                                  ZoteroPaper, TakeoutDocument -[:CITES]->
                                  GeminiReport)

Reference: openspec/changes/leabharlann-cognify-and-cross-archive-edges/
"""

import os
import subprocess
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
        import falkordb  # type: ignore[import-not-found, import-untyped]
        return True
    except ImportError:
        return False


@asset(
    group_name="leabharlann_cognify",
    compute_kind="cognee",
    description="Cognee cognify of the leabharlann books corpus (UoG Irish exam).",
)
def cognify_leabharlann_books(context: AssetExecutionContext) -> Output[dict[str, Any]]:
    if not _cognee_available():
        return Output(
            value={"status": "skipped_no_cognee", "episodes": 0},
            metadata={"cognee_status": "skipped_no_cognee"},
        )
    # TODO: in Phase 2, iterate over DuckLake leabharlann.books table and
    # call cognee.add(text, dataset_name=COGNEE_DATASET_BOOKS) per row.
    # For now, emit a placeholder asset so the Dagster UI shows the slot.
    context.log.info("cognify_leabharlann_books_placeholder")
    return Output(
        value={"status": "placeholder", "episodes": 0},
        metadata={"cognee_status": "placeholder", "dataset": COGNEE_DATASET_BOOKS},
    )


@asset(
    group_name="leabharlann_cognify",
    compute_kind="cognee",
    description="Cognee cognify of the leabharlann zotero corpus (117 academic papers).",
)
def cognify_leabharlann_zotero(context: AssetExecutionContext) -> Output[dict[str, Any]]:
    if not _cognee_available():
        return Output(
            value={"status": "skipped_no_cognee", "episodes": 0},
            metadata={"cognee_status": "skipped_no_cognee"},
        )
    context.log.info("cognify_leabharlann_zotero_placeholder")
    return Output(
        value={"status": "placeholder", "episodes": 0},
        metadata={"cognee_status": "placeholder", "dataset": COGNEE_DATASET_ZOTERO},
    )


@asset(
    group_name="leabharlann_cognify",
    compute_kind="cognee",
    description="Cognee cognify of the leabharlann takeout corpus (Google Drive export).",
)
def cognify_leabharlann_takeout(context: AssetExecutionContext) -> Output[dict[str, Any]]:
    if not _cognee_available():
        return Output(
            value={"status": "skipped_no_cognee", "episodes": 0},
            metadata={"cognee_status": "skipped_no_cognee"},
        )
    context.log.info("cognify_leabharlann_takeout_placeholder")
    return Output(
        value={"status": "placeholder", "episodes": 0},
        metadata={"cognee_status": "placeholder", "dataset": COGNEE_DATASET_TAKEOUT},
    )


@asset(
    group_name="leabharlann_cognify",
    compute_kind="falkordb",
    description=(
        "Populate FalkorDB with cross-archive edges: "
        "GeminiReport-[:CITES]->ZoteroPaper, UoGArtifact-[:TEACHES]->ZoteroPaper, "
        "TakeoutDocument-[:CITES]->GeminiReport. Run AFTER the 3 cognify assets."
    ),
    deps=[
        "cognify_leabharlann_books",
        "cognify_leabharlann_zotero",
        "cognify_leabharlann_takeout",
    ],
)
def cross_archive_edges(context: AssetExecutionContext) -> Output[dict[str, Any]]:
    if not _falkordb_available():
        return Output(
            value={"status": "skipped_no_falkordb", "edges_created": 0},
            metadata={"falkordb_status": "skipped_no_falkordb"},
        )
    # The real edge-population runs via `cognee cognify` with the
    # FalkorDB graph_database_provider; this asset is a no-op slot
    # that fires after the cognify assets complete.
    context.log.info("cross_archive_edges_placeholder")
    return Output(
        value={"status": "placeholder", "edges_created": 0},
        metadata={"falkordb_status": "placeholder"},
    )


LEABHARLANN_COGNIFY_ASSETS = [
    cognify_leabharlann_books,
    cognify_leabharlann_zotero,
    cognify_leabharlann_takeout,
    cross_archive_edges,
]
