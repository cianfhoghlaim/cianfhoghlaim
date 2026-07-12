"""Dagster L2 — UD Celtic BAML extraction assets.

Added 2026-07-17. Calls `b.ExtractUDToken` over the ingested UD Celtic
DuckLake rows. Routes via `uccix-mistral-24b` for Irish treebanks,
`gemma-4-26B-A4B` for others.
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


def extract_ud_tokens(
    token_rows: list[dict[str, Any]],
    language: str = "ga",
) -> list[dict[str, Any]]:
    """Extract BAML-typed records for UD tokens."""
    if not _BAML_AVAILABLE or b is None:
        logger.warning("baml_unavailable: extract_ud_tokens")
        return []

    client_name = get_baml_client("ud_celtic", language) if _ROUTING_AVAILABLE else "LlamaSwapReasoningClient"
    logger.info("extract_ud_tokens routing=%s n=%d", client_name, len(token_rows))

    results = []
    for row in token_rows:
        try:
            extracted = b.ExtractUDToken(
                conllu_line=str(row.get("conllu_line", "")),
                treebank=str(row.get("treebank", "")),
            )
            results.append({**row, "extracted": extracted, "routing_client": client_name})
        except Exception as exc:
            logger.warning("ud_extract_failed: %s", exc)
            continue
    return results


__all__ = ["extract_ud_tokens"]