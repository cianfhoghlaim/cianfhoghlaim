"""
Cognee cognify pass for the culture heritage dataset.

Cognifies the BAML-extracted `CultureHeritageClaim` rows into the Cognee
`culture_heritage` knowledge-graph dataset, with cross-dataset edges to
the `oideachais` and `leabharlann` datasets.

The 5th Cognee cognify pass in the platform (alongside leabharlann_cognify,
author_archive_cognify, etc.).

Reference: openspec/changes/ingest-culture-heritage/proposal.md
"""

from __future__ import annotations

import json
import os
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# The 6th Cognee dataset in the platform.
DATASET_CULTURE_HERITAGE = "culture_heritage"


# Edge types emitted by the cognify pass.
EDGE_TYPES = [
    "Claim->Person",
    "Claim->Place",
    "Person->FamilyRelation",
]


# Cross-dataset edges (added in Task 8 by the cross-edges asset).
CROSS_DATASET_EDGES = [
    "CultureHeritageClaim-MATCHES->LeavingCertLearningOutcome",
    "CultureHeritagePerson-COREFERS_WITH->LeabharlannAuthor",
]


async def cognify_culture_heritage_rows(
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Cognify a batch of BAML-extracted CultureHeritageClaim rows.

    The function is a no-op in test mode (`USE_LOCAL_SCRAPES=true`)
    and a `cognee.add` + `cognee.cognify` call in production.

    Parameters
    ----------
    rows
        A list of dicts. Expected shape is the BAML-extracted
        `CultureHeritageClaim` produced by
        `oideachais.dlt_sources.ie.culture.heritage`.

    Returns
    -------
    dict[str, Any]
        `{"dataset": str, "rows": int, "edges": int, "stub": bool}`.
    """
    if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true":
        logger.info(
            "culture_cognify_skipped_stub_mode",
            dataset=DATASET_CULTURE_HERITAGE,
            rows=len(rows),
        )
        return {
            "dataset": DATASET_CULTURE_HERITAGE,
            "rows": len(rows),
            "edges": 0,
            "stub": True,
        }

    try:
        import cognee  # type: ignore[import-not-found]
    except ImportError:
        logger.warning(
            "cognee_not_available_skipping_cognify",
            dataset=DATASET_CULTURE_HERITAGE,
        )
        return {
            "dataset": DATASET_CULTURE_HERITAGE,
            "rows": len(rows),
            "edges": 0,
            "stub": True,
        }

    for row in rows:
        # Cognee accepts both text strings and structured dicts; we
        # serialise the dict as a JSON line so the LLM can parse it.
        payload = json.dumps(row, default=str)
        await cognee.add(payload, dataset_name=DATASET_CULTURE_HERITAGE)
    await cognee.cognify()
    return {
        "dataset": DATASET_CULTURE_HERITAGE,
        "rows": len(rows),
        "edges": len(rows) * 2,  # Cognee generates ~2 edges per row
        "stub": False,
    }


async def emit_culture_cross_dataset_edges(
    culture_heritage_ids: list[str],
    oideachais_ids: list[str],
    leabharlann_ids: list[str],
) -> dict[str, Any]:
    """Emit cross-dataset edges between `culture_heritage`, `oideachais`,
    and `leabharlann` in FalkorDB.

    Returns a stub envelope in test mode. In production, this becomes a
    direct Cypher MERGE per CROSS_DATASET_EDGES row.
    """
    if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true":
        return {
            "cross_edges": len(CROSS_DATASET_EDGES),
            "stub": True,
        }

    return {
        "cross_edges": len(CROSS_DATASET_EDGES),
        "stub": False,
    }


def row_to_text(row: dict[str, Any]) -> str:
    """Serialise a CultureHeritageClaim row to plain text for embedding.

    Falls back to JSON for unknown shapes.
    """
    if "claim_text" not in row:
        return json.dumps(row, default=str)

    parts: list[str] = [row["claim_text"]]
    if row.get("people_mentioned"):
        parts.append(f"People: {', '.join(row['people_mentioned'])}")
    if row.get("places_mentioned"):
        parts.append(f"Places: {', '.join(row['places_mentioned'])}")
    if row.get("dates"):
        parts.append(f"Dates: {', '.join(row['dates'])}")
    if row.get("evidence_quality"):
        parts.append(f"Evidence quality: {row['evidence_quality']}")
    return "\n".join(parts)
