"""Dagster L2 — Celtic curriculum BAML extraction assets.

Added 2026-07-17. Calls `b.ExtractCelticCurriculum`, `b.ExtractCelticGrammar`,
and `b.ExtractCelticMorphology` over the ingested Celtic curriculum
DuckLake rows. Routes via `uccix-mistral-24b` for Irish,
`gemma-4-26B-A4B` for other Celtic languages.
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


def extract_celtic_curriculum(
    spec_rows: list[dict[str, Any]],
    language: str = "ga",
) -> list[dict[str, Any]]:
    """Extract BAML-typed records for Celtic curriculum specs."""
    if not _BAML_AVAILABLE or b is None:
        logger.warning("baml_unavailable: extract_celtic_curriculum")
        return []

    client_name = (
        get_baml_client("celtic_curriculum", language) if _ROUTING_AVAILABLE else "LlamaSwapReasoningClient"
    )
    logger.info("extract_celtic_curriculum routing=%s language=%s n=%d", client_name, language, len(spec_rows))

    results = []
    for row in spec_rows:
        try:
            extracted = b.ExtractCelticCurriculum(
                text=str(row.get("content_text", "")),
                language=language,
            )
            results.append({**row, "extracted": extracted, "routing_client": client_name})
        except Exception as exc:
            logger.warning("celtic_curriculum_extract_failed: %s", exc)
            continue
    return results


def extract_celtic_grammar(
    text_rows: list[dict[str, Any]],
    language: str = "ga",
) -> list[dict[str, Any]]:
    """Extract BAML-typed records for Celtic grammar patterns."""
    if not _BAML_AVAILABLE or b is None:
        return []
    client_name = (
        get_baml_client("celtic_curriculum", language) if _ROUTING_AVAILABLE else "LlamaSwapReasoningClient"
    )
    results = []
    for row in text_rows:
        try:
            extracted = b.ExtractCelticGrammar(
                text=str(row.get("text", "")),
                language=language,
                max_patterns=int(row.get("max_patterns", 10)),
            )
            results.append({**row, "extracted": extracted, "routing_client": client_name})
        except Exception as exc:
            logger.warning("celtic_grammar_extract_failed: %s", exc)
            continue
    return results


def extract_celtic_morphology(
    text_rows: list[dict[str, Any]],
    language: str = "ga",
) -> list[dict[str, Any]]:
    """Extract BAML-typed records for Celtic morphology specs."""
    if not _BAML_AVAILABLE or b is None:
        return []
    client_name = (
        get_baml_client("celtic_curriculum", language) if _ROUTING_AVAILABLE else "LlamaSwapReasoningClient"
    )
    results = []
    for row in text_rows:
        try:
            extracted = b.ExtractCelticMorphology(
                text=str(row.get("text", "")),
                language=language,
                word_class_hint=row.get("word_class_hint"),
            )
            results.append({**row, "extracted": extracted, "routing_client": client_name})
        except Exception as exc:
            logger.warning("celtic_morphology_extract_failed: %s", exc)
            continue
    return results


__all__ = [
    "extract_celtic_curriculum",
    "extract_celtic_grammar",
    "extract_celtic_morphology",
]