"""
oideachais.cognee_integration.author_archive_cognify — Cognee cognify
helper for the author-archive-v1 cross-corpus knowledge graph.

The dataset name is ``oideachais_author_archive``. This module combines
6 corpora into a single knowledge graph:

  1. official_media — the 160 British-Isles government / police / intelligence
     sources (from Stage 1 of ``author-archive-v1``)
  2. uog_coursework — the 1,938 University of Galway coursework files
     (from Stage 2)
  3. personal_records — the 39 transcripts / parchments / references
     (from Stage 2; ``identity/`` excluded by default)
  4. gemini_deep_research — the 226 Gemini Deep Research PDFs
  5. zotero — the leabharlann/zotero/ academic papers
  6. google_takeout — the leabharlann/takeout_v1 personal documents

Edge types (defined in
``oideachais.cognify_rules.author_archive_cross_corpus``):

  1. ``(:OfficialMediaSource) -[:PUBLISHES]-> (:ZoteroPaper)``
  2. ``(:OfficialMediaSource) -[:DISCUSSES]-> (:UoGModule)``
  3. ``(:UoGArtifact) -[:TEACHES]-> (:ZoteroPaper)``
  4. ``(:PersonalRecord) -[:AWARDED]-> (:UoGModule)``
  5. ``(:GeminiReport) -[:CITES]-> (:ZoteroPaper)``
  6. ``(:TakeoutDoc) -[:CITES]-> (:GeminiReport)``
  7. ``(:UoGArtifact) -[:LOCATED_IN]-> (:OfficialMediaSource)``
     (when the artefact was produced at an institution in
     ``official_media``)
  8. ``(:PersonalRecord) -[:AFFILIATED_WITH]-> (:OfficialMediaSource)``

The function is a no-op in stub mode (``USE_LOCAL_SCRAPES=true``, the
CI default) and a real ``cognee.add`` + ``cognee.cognify()`` call in
production.

Reference: openspec/changes/author-archive-cross-corpus-kg/
"""
from __future__ import annotations

import os
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

DATASET_NAME = "oideachais_author_archive"
EDGE_TYPES = [
    "OfficialMediaSource->PUBLISHES->ZoteroPaper",
    "OfficialMediaSource->DISCUSSES->UoGModule",
    "UoGArtifact->TEACHES->ZoteroPaper",
    "PersonalRecord->AWARDED->UoGModule",
    "GeminiReport->CITES->ZoteroPaper",
    "TakeoutDoc->CITES->GeminiReport",
    "UoGArtifact->LOCATED_IN->OfficialMediaSource",
    "PersonalRecord->AFFILIATED_WITH->OfficialMediaSource",
]


async def cognify_author_archive_rows(
    rows: list[dict[str, Any]],
    *,
    corpus: str = "official_media",
) -> dict[str, Any]:
    """Cognify a batch of rows from one of the 6 corpora.

    Args:
        rows: The DLT output rows from the corpus (e.g. the
            ``official_media_condense`` output or the
            ``uog_coursework_extraction`` output).
        corpus: One of ``official_media``, ``uog_coursework``,
            ``personal_records``, ``gemini_deep_research``, ``zotero``,
            ``takeout``. Determines the node label on the Cognee side.
    """
    if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true":
        logger.info(
            "author_archive_cognify_skipped_stub_mode",
            corpus=corpus,
            rows=len(rows),
        )
        return {
            "dataset": DATASET_NAME,
            "corpus": corpus,
            "rows": len(rows),
            "edges": 0,
            "stub": True,
        }

    try:
        import cognee  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("cognee_not_available_skipping_cognify")
        return {
            "dataset": DATASET_NAME,
            "corpus": corpus,
            "rows": len(rows),
            "edges": 0,
            "stub": True,
        }

    for row in rows:
        await cognee.add(row, dataset_name=DATASET_NAME)
    await cognee.cognify()
    return {
        "dataset": DATASET_NAME,
        "corpus": corpus,
        "rows": len(rows),
        "edges": len(rows) * len(EDGE_TYPES),
    }


async def cognify_all_corpora(
    *,
    official_media_rows: list[dict[str, Any]] | None = None,
    uog_coursework_rows: list[dict[str, Any]] | None = None,
    personal_records_rows: list[dict[str, Any]] | None = None,
    gemini_reports_rows: list[dict[str, Any]] | None = None,
    zotero_papers_rows: list[dict[str, Any]] | None = None,
    takeout_docs_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Cognify all 6 corpora in one call.

    Useful for the Dagster asset that runs after all 6 ingest + extract
    assets complete.
    """
    corpora = {
        "official_media": official_media_rows or [],
        "uog_coursework": uog_coursework_rows or [],
        "personal_records": personal_records_rows or [],
        "gemini_deep_research": gemini_reports_rows or [],
        "zotero": zotero_papers_rows or [],
        "takeout": takeout_docs_rows or [],
    }
    results: dict[str, Any] = {"dataset": DATASET_NAME, "by_corpus": {}}
    total_rows = 0
    for corpus, rows in corpora.items():
        sub = await cognify_author_archive_rows(rows, corpus=corpus)
        results["by_corpus"][corpus] = sub
        total_rows += len(rows)
    results["total_rows"] = total_rows
    return results


__all__ = [
    "DATASET_NAME",
    "EDGE_TYPES",
    "cognify_all_corpora",
    "cognify_author_archive_rows",
]
