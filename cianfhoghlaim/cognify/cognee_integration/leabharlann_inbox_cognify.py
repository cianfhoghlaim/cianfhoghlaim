"""
Leabharlann Email Inbox Cognify — 4th leabharlann cognify dataset.

The `oideachais_email_inbox` dataset extends the 3 existing
leabharlann cognify datasets (books, zotero, takeout) with 4 new
node types: `EmailThread`, `EmailAccount`, `LegalCase`, `ResearchLink`.

The cognify pass is async; the 3 cross-archive edge rules live in
`oideachais.cognify_rules.leabharlann_inbox_cross_archive`.

Reference: openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/
"""

from __future__ import annotations

import json
import os
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


DATASET_INBOX = "oideachais_email_inbox"

# 4 node types in the inbox graph.
NODE_TYPES = [
    "EmailThread",
    "EmailAccount",
    "LegalCase",
    "ResearchLink",
]

# 3 edge types in the inbox cross-archive graph.
EDGE_TYPES = [
    "EmailThread-RELATES_TO->LegalCase",
    "EmailThread-CITES->ResearchPDF",
    "EmailAccount-OWNS->Person",
]


async def cognify_inbox_rows(
    rows: list[dict[str, Any]],
    *,
    dataset: str = DATASET_INBOX,
) -> dict[str, Any]:
    """Cognify a batch of inbox rows into the Cognee graph.

    The function is a no-op in test mode (`USE_LOCAL_SCRAPES=true`)
    and a `cognee.add` + `cognee.cognify` call in production.

    Parameters
    ----------
    rows
        A list of dicts. For email threads, the expected shape is
        `{"thread_id": ..., "account": ..., "subject": ...,
         "messages": [...], "baml_class": ..., "baml_urgency": ...}`.
    dataset
        Override dataset name. Defaults to `oideachais_email_inbox`.
    """
    if dataset != DATASET_INBOX:
        raise ValueError(f"unknown inbox dataset: {dataset}")

    if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true":
        logger.info(
            "leabharlann_inbox_cognify_skipped_stub_mode",
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
        logger.warning("cognee_not_available_skipping_inbox_cognify", dataset=dataset)
        return {
            "dataset": dataset,
            "rows": len(rows),
            "edges": 0,
            "stub": True,
        }

    for row in rows:
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
    """Serialise a BAML-extracted inbox row to a Cognee-friendly text blob."""
    return json.dumps(row, default=str, sort_keys=True)


__all__ = [
    "DATASET_INBOX",
    "NODE_TYPES",
    "EDGE_TYPES",
    "_row_to_text",
    "cognify_inbox_rows",
]
