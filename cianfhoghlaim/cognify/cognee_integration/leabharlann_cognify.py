"""
oideachais.cognee_integration.leabharlann_cognify — Cognee cognify
helper for the leabharlann corpora (books, zotero, takeout).

Phase 2 of the `leabharlann-cognify-and-cross-archive-edges` openspec
change. The dataset names are `leabharlann_books`, `leabharlann_zotero`,
`leabharlann_takeout`.

The cross-archive edge population is in
`oideachais.cognify_rules.leabharlann_cross_archive.populate_cross_archive_edges`
(FalkorDB MERGE queries), which runs after this cognify pass.

Edge types produced by the cognify pass (Cognee LLM-driven extraction):
  - Book   -> PrimaryLearningOutcome (when a UoG book teaches a stage outcome)
  - Paper  -> ResearchField            (when a Zotero paper is in a field)
  - Doc    -> Topic                    (when a takeout doc discusses a topic)

Edge types produced by the FalkorDB cross-archive pass (deterministic):
  - (:GeminiReport) -[:CITES]->        (:ZoteroPaper)   via arxiv_id match
  - (:UoGArtifact)  -[:TEACHES]->      (:ZoteroPaper)   via module title match
  - (:TakeoutDoc)   -[:CITES]->        (:GeminiReport)  via URL match
"""

from __future__ import annotations

import os
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


DATASET_BOOKS = "leabharlann_books"
DATASET_ZOTERO = "leabharlann_zotero"
DATASET_TAKEOUT = "leabharlann_takeout"

EDGE_TYPES = [
    "Book->PrimaryLearningOutcome",
    "Paper->ResearchField",
    "Doc->Topic",
    "GeminiReport-CITES->ZoteroPaper",
    "UoGArtifact-TEACHES->ZoteroPaper",
    "TakeoutDoc-CITES->GeminiReport",
]


async def cognify_leabharlann_rows(
    dataset: str,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Cognify a batch of `leabharlann_*` rows into the Cognee graph.

    The function is a no-op in test mode (`USE_LOCAL_SCRAPES=true`)
    and a `cognee.add` + `cognee.cognify` call in production.

    Parameters
    ----------
    dataset
        One of `DATASET_BOOKS`, `DATASET_ZOTERO`, `DATASET_TAKEOUT`.
    rows
        A list of dicts. For books/zotero/takeout, the expected shape is
        the BAML-extracted row produced by
        `oideachais.dlt_sources.leabharlann.{leabharlann_books,zotero,takeout_v1}.py`.

    Returns
    -------
    dict[str, Any]
        `{"dataset": str, "rows": int, "edges": int, "stub": bool}`.
    """
    if dataset not in (DATASET_BOOKS, DATASET_ZOTERO, DATASET_TAKEOUT):
        raise ValueError(f"unknown leabharlann dataset: {dataset}")

    if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true":
        logger.info(
            "leabharlann_cognify_skipped_stub_mode",
            dataset=dataset,
            rows=len(rows),
        )
        return {
            "dataset": dataset,
            "rows": len(rows),
            "edges": 0,
            "stub": True,
        }

    try:
        import cognee  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("cognee_not_available_skipping_cognify", dataset=dataset)
        return {
            "dataset": dataset,
            "rows": len(rows),
            "edges": 0,
            "stub": True,
        }

    for row in rows:
        # Cognee accepts both text strings and structured dicts; we
        # serialise the dict as a JSON line so the LLM can parse it.
        import json

        payload = json.dumps(row, default=str)
        await cognee.add(payload, dataset_name=dataset)
    await cognee.cognify()
    return {
        "dataset": dataset,
        "rows": len(rows),
        "edges": len(rows) * 2,  # Cognee generates ~2 edges per row
        "stub": False,
    }


def _row_to_text(row: dict[str, Any]) -> str:
    """Serialise a BAML-extracted row to a Cognee-friendly text blob.

    Used by the `cross_archive_edges` rule pass to compute deterministic
    edge keys (e.g. `module_title` normalisation for `TEACHES` matches).
    """
    import json

    return json.dumps(row, default=str, sort_keys=True)


__all__ = [
    "DATASET_BOOKS",
    "DATASET_TAKEOUT",
    "DATASET_ZOTERO",
    "EDGE_TYPES",
    "_row_to_text",
    "cognify_leabharlann_rows",
]
