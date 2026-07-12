"""Dagster L2 — Canuint BAML extraction assets.

Added 2026-07-17. Calls `b.ExtractCanuintWordAlignment` over the
ingested Canuint DuckLake rows. Routes via `qwen3-vl-8b`.
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


def extract_canuint_alignments(
    alignment_rows: list[dict[str, Any]],
    language: str = "ga",
) -> list[dict[str, Any]]:
    """Extract BAML-typed records for Canuint word alignments.

    Uses `b.ExtractCanuintWordAlignment` (added in
    `baml/celtic/gaois/canuint.baml`).
    """
    if not _BAML_AVAILABLE or b is None:
        logger.warning("baml_unavailable: extract_canuint_alignments")
        return []

    client_name = get_baml_client("canuint", language) if _ROUTING_AVAILABLE else "LlamaSwapReasoningClient"
    logger.info("extract_canuint_alignments routing=%s n=%d", client_name, len(alignment_rows))

    results = []
    for row in alignment_rows:
        try:
            extracted = b.ExtractCanuintWordAlignment(
                recording_id=str(row.get("recording_id", "")),
                transcript=str(row.get("dialectal_text", "")),
                audio_path=row.get("audio_path"),
            )
            results.append({**row, "extracted": extracted, "routing_client": client_name})
        except Exception as exc:
            logger.warning("canuint_extract_failed: %s", exc)
            continue
    return results


__all__ = ["extract_canuint_alignments"]