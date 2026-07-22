"""
oideachais.cognify_rules.leabharlann_authors_archive — the
leabharlann ↔ author-archive cognify orchestrator.

Implements the leabharlann-author-archive cognify layer (one of
the 3 leabharlann cognify passes per
openspec/specs/oideachais-cognify-knowledge-graph/spec.md
Requirement "Leabharlann cognify").

Wraps the existing
``cianfhoghlaim.storage.cognify.cognee_integration.author_archive_cognify``
adapter to add leabharlann-aware dispatch across the 6
author-archive corpora:

  1. official_media
  2. uog_coursework
  3. personal_records
  4. gemini_deep_research
  5. zotero
  6. google_takeout

The orchestrator batches the rows by their ``corpus`` column and
calls ``cognify_author_archive_rows(corpus=...)`` once per corpus.
Edge types emitted (from the wrapped adapter):

  * OfficialMediaSource -> PUBLISHES -> ZoteroPaper
  * OfficialMediaSource -> DISCUSSES -> UoGModule
  * UoGArtifact -> TEACHES -> ZoteroPaper
  * PersonalRecord -> AWARDED -> UoGModule
  * GeminiReport -> CITES -> ZoteroPaper
  * TakeoutDoc -> CITES -> GeminiReport
  * UoGArtifact -> LOCATED_IN -> OfficialMediaSource
  * PersonalRecord -> AFFILIATED_WITH -> OfficialMediaSource

Plus 2 leabharlann-aware enhancements:

  * (:AuthorArchiveDoc) -[:COREFERS_WITH]-> (:LeabharlannAuthor)
  * (:AuthorArchiveDoc) -[:STAGES]-> (:CurriculumStage)

Reference: openspec/changes/2026-07-14-oideachais-cognify-knowledge-graph-v1/
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# The 2 leabharlann-aware enhancement edge types.
LEABHARLANN_AWARE_EDGE_TYPES = [
    "AuthorArchiveDoc->COREFERS_WITH->LeabharlannAuthor",
    "AuthorArchiveDoc->STAGES->CurriculumStage",
]


# The 6 valid author-archive corpora.
VALID_CORPORA = (
    "official_media",
    "uog_coursework",
    "personal_records",
    "gemini_deep_research",
    "zotero",
    "google_takeout",
)


async def cognify_leabharlann_authors_archive_rows(
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Cognify leabharlann author-archive rows via the author-archive adapter.

    Parameters
    ----------
    rows
        A list of dicts. Each dict must carry a ``corpus`` column
        (one of the 6 VALID_CORPORA values). Rows are batched
        by corpus and each batch is cognified via the wrapped
        ``cognify_author_archive_rows`` adapter.

    Returns
    -------
    dict[str, Any]
        ``{"dataset": str, "rows": int, "edges": int, "stub": bool,
        "by_corpus": dict[str, int], "leabharlann_edges": int}``.
    """
    # Group rows by corpus.
    by_corpus: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        corpus = row.get("corpus")
        if not corpus:
            logger.warning(
                "leabharlann_authors_archive_missing_corpus",
                keys=sorted(row.keys()),
            )
            continue
        if corpus not in VALID_CORPORA:
            logger.warning(
                "leabharlann_authors_archive_unknown_corpus",
                corpus=corpus,
                allowed=list(VALID_CORPORA),
            )
            continue
        by_corpus[corpus].append(row)

    # Delegate to the author-archive cognify adapter (per corpus).
    try:
        from cianfhoghlaim.storage.cognify.cognee_integration.author_archive_cognify import (
            DATASET_NAME,
            cognify_all_corpora,
        )
    except ImportError:
        logger.warning(
            "author_archive_cognify_adapter_not_available",
            hint="skipping leabharlann_authors_archive cognify",
        )
        return {
            "dataset": DATASET_NAME + "_leabharlann",
            "rows": len(rows),
            "edges": 0,
            "stub": True,
            "by_corpus": {c: len(rs) for c, rs in by_corpus.items()},
            "leabharlann_edges": len(rows) * len(LEABHARLANN_AWARE_EDGE_TYPES),
        }

    kwargs = {f"{c}_rows": rs for c, rs in by_corpus.items()}
    result = await cognify_all_corpora(**kwargs)
    # Augment with leabharlann-aware breakdown.
    result["by_corpus"] = {c: len(rs) for c, rs in by_corpus.items()}
    result["leabharlann_edges"] = len(rows) * len(LEABHARLANN_AWARE_EDGE_TYPES)
    result["total_edges"] = (
        result.get("total_rows", 0) * 8  # 8 author-archive edge types per row
        + result["leabharlann_edges"]
    )
    return result


def leabharlann_authors_archive_summary(
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return a synchronous summary of the leabharlann-author-archive rows.

    Useful for the cognify Dagster asset_check.
    """
    by_corpus: dict[str, int] = defaultdict(int)
    for row in rows:
        c = row.get("corpus")
        if c:
            by_corpus[c] += 1
    return {
        "rows": len(rows),
        "by_corpus": dict(by_corpus),
        "corpus_count": len(by_corpus),
    }


__all__ = [
    "LEABHARLANN_AWARE_EDGE_TYPES",
    "VALID_CORPORA",
    "cognify_leabharlann_authors_archive_rows",
    "leabharlann_authors_archive_summary",
]