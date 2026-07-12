"""Dagster L2 — Dúchas BAML extraction assets (3 extraction flows).

Added 2026-07-17 by the
`openspec/changes/2026-07-17-gaois-celtic-language-pipeline-v1/`
change. Calls `b.ExtractDuchasManuscript`, `b.ExtractDuchasImageBoundingBox`,
and `b.ExtractDuchasTranscription` over the ingested Dúchas DuckLake rows.

LlamaSwap routing per the shared table:
- Dúchas → `molmo2-8b` (specialist) for manuscript extraction
- Dúchas → `dots-ocr` (specialist) for bbox layout
- Dúchas → `qwen3-vl-8b` (workhorse) for transcription
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    from cianfhoghlaim.meaisinfhoghlaim.models.routing import (  # type: ignore[import-not-found]
        route_language,
        get_baml_client,
    )
    _ROUTING_AVAILABLE = True
except Exception:
    _ROUTING_AVAILABLE = False
    route_language = None  # type: ignore[assignment]
    get_baml_client = None  # type: ignore[assignment]


try:
    from baml_client import b  # type: ignore[import-not-found]
    _BAML_AVAILABLE = True
except Exception:
    _BAML_AVAILABLE = False
    b = None  # type: ignore[assignment]


def extract_duchas_manuscripts(
    manuscript_rows: list[dict[str, Any]],
    language: str = "ga",
) -> list[dict[str, Any]]:
    """Extract BAML-typed records for Dúchas manuscript pages.

    Uses `b.ExtractDuchasManuscript` (added in this change).
    """
    if not _BAML_AVAILABLE or b is None:
        logger.warning("baml_unavailable: extract_duchas_manuscripts")
        return []

    client_name = get_baml_client("duchas", language) if _ROUTING_AVAILABLE else "LlamaSwapReasoningClient"
    logger.info("extract_duchas_manuscripts routing=%s n=%d", client_name, len(manuscript_rows))

    results = []
    for row in manuscript_rows:
        try:
            extracted = b.ExtractDuchasManuscript(
                xml_record=row.get("xml_record", ""),
                image_path=row.get("image_path"),
            )
            results.append({**row, "extracted": extracted, "routing_client": client_name})
        except Exception as exc:  # noqa: BLE001 - defensive
            logger.warning("duchas_manuscript_extract_failed: %s", exc)
            continue
    return results


def extract_duchas_bboxes(
    bbox_rows: list[dict[str, Any]],
    collection: str = "cbes",
) -> list[dict[str, Any]]:
    """Extract the 5-level bbox alignment from manuscript pages.

    Uses `b.ExtractDuchasImageBoundingBox` (added in this change).
    Dispatches via `molmo2-8b` (diagram pointing) + `dots-ocr` (layout).
    """
    if not _BAML_AVAILABLE or b is None:
        logger.warning("baml_unavailable: extract_duchas_bboxes")
        return []

    client_name = get_baml_client("duchas", collection) if _ROUTING_AVAILABLE else "LlamaSwapReasoningClient"
    logger.info("extract_duchas_bboxes routing=%s collection=%s n=%d", client_name, collection, len(bbox_rows))

    results = []
    for row in bbox_rows:
        try:
            extracted = b.ExtractDuchasImageBoundingBox(
                image_path=row.get("image_path", ""),
                transcript=row.get("transcript", ""),
                collection=row.get("collection", collection),
            )
            results.append({**row, "extracted": extracted, "routing_client": client_name})
        except Exception as exc:  # noqa: BLE001 - defensive
            logger.warning("duchas_bbox_extract_failed: %s", exc)
            continue
    return results


def extract_duchas_transcriptions(
    transcription_rows: list[dict[str, Any]],
    collection: str = "cbes",
    language_hint: str | None = "ga",
) -> list[dict[str, Any]]:
    """Extract line-by-line transcriptions from handwritten manuscript pages.

    Uses `b.ExtractDuchasTranscription` (added in this change).
    """
    if not _BAML_AVAILABLE or b is None:
        logger.warning("baml_unavailable: extract_duchas_transcriptions")
        return []

    client_name = get_baml_client("duchas", collection) if _ROUTING_AVAILABLE else "LlamaSwapReasoningClient"
    logger.info("extract_duchas_transcriptions routing=%s collection=%s n=%d", client_name, collection, len(transcription_rows))

    results = []
    for row in transcription_rows:
        try:
            extracted = b.ExtractDuchasTranscription(
                handwritten_image=row.get("handwritten_image", ""),
                collection=row.get("collection", collection),
                language_hint=language_hint,
            )
            results.append({**row, "extracted": extracted, "routing_client": client_name})
        except Exception as exc:  # noqa: BLE001 - defensive
            logger.warning("duchas_transcription_extract_failed: %s", exc)
            continue
    return results


__all__ = [
    "extract_duchas_manuscripts",
    "extract_duchas_bboxes",
    "extract_duchas_transcriptions",
]