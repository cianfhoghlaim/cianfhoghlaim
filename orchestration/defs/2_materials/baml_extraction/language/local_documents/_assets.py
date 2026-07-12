"""Dagster L2 — Local documents BAML extraction assets.

Added 2026-07-17. Calls `b.ExtractLocalDocumentMetadata` over the
ingested local documents DuckLake rows. Routes via `qwen3-vl-8b`.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    from cianfhoghlaim.meaisinfhoghlaim.models.routing import (  # type: ignore[import-not-found]
        get_baml_client,
    )
    _ROUTING_AVAILABLE = True
except Exception:
    _ROUTING_AVAILABLE = False
    get_baml_client = None  # type: ignore[assignment]


try:
    from baml_client import b  # type: ignore[import-not-found]
    _BAML_AVAILABLE = True
except Exception:
    _BAML_AVAILABLE = False
    b = None  # type: ignore[assignment]


def extract_local_documents(
    doc_rows: list[dict[str, Any]],
    subject: str = "comp_science",
    language: str = "en",
) -> list[dict[str, Any]]:
    """Extract BAML-typed records for local documents."""
    if not _BAML_AVAILABLE or b is None:
        logger.warning("baml_unavailable: extract_local_documents")
        return []

    client_name = (
        get_baml_client("local_documents", language) if _ROUTING_AVAILABLE else "LlamaSwapReasoningClient"
    )
    logger.info("extract_local_documents routing=%s subject=%s n=%d", client_name, subject, len(doc_rows))

    results = []
    for row in doc_rows:
        try:
            extracted = b.ExtractLocalDocumentMetadata(
                file_path=str(row.get("file_path", "")),
                content_text=str(row.get("content_text", "")),
                subject=subject,
            )
            results.append({**row, "extracted": extracted, "routing_client": client_name})
        except Exception as exc:
            logger.warning("local_doc_extract_failed: %s", exc)
            continue
    return results


__all__ = ["extract_local_documents"]