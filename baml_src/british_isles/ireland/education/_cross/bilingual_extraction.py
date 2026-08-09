"""Bilingual GA↔EN cross-linguistic BAML extraction (per the 2026-08-10-knowledge-graph-population-v1 change).

Adds two functions to `baml_src/british_isles/ireland/education/_cross/cross_linguistic.baml`:
- ExtractBilingualLearningOutcome(en_text, ga_text) — pairs EN + GA LOs
- ExtractCrossLinguisticGA(ga_text) — extracts Irish-language concepts

The BAML function signatures live in cross_linguistic.baml; this module
is the BAML-runtime adapter that wraps `b.ExtractBilingualLearningOutcome`
+ `b.ExtractCrossLinguisticGA` for use from the cognify adapters +
Dagster asset layer.
"""
from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def extract_bilingual_lo(en_text: str, ga_text: str) -> dict[str, Any]:
    """Extract paired EN + GA Learning Outcomes from parallel syllabus text.

    Per the 2026-08-10 spec delta: returns
    `{en_lo_id, ga_lo_id, confidence, source_pairs: [(en_segment, ga_segment)]}`.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractBilingualLearningOutcome(en_text=en_text, ga_text=ga_text)
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(f"extract_bilingual_lo_failed: {e}")
        return {"error": str(e)}


def extract_cross_linguistic_ga(ga_text: str) -> dict[str, Any]:
    """Extract Irish-language concepts from a GA text snippet.

    Per the 2026-08-10 spec delta.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractCrossLinguisticGA(ga_text=ga_text)
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(f"extract_cross_linguistic_ga_failed: {e}")
        return {"error": str(e)}


__all__ = ["extract_bilingual_lo", "extract_cross_linguistic_ga"]
