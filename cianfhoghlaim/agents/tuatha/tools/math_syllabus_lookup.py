"""math_syllabus_lookup — Look up NCCA Mathematics learning outcomes.

Backed by:
- BAML `qpack_mathematics.baml` `ExtractLeavingCertSyllabus` for fresh extraction
- LanceDB `oideachais.lc.mathematics.*` tables for cached + embedded results
- Cognee `oideachais_lc_mathematics` for cross-LO reasoning

Used by `math_agent` tool #1.
"""
from __future__ import annotations

from typing import Any


async def lookup_math_lo(
    topic: str,
    level: str = "hl",
    language: str = "en",
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Return NCCA Mathematics learning outcomes matching `topic`."""
    try:
        from cianfhoghlaim.lancedb.search import semantic_search

        results = await semantic_search(
            table=f"oideachais.lc.mathematics.{level}_{language}",
            query=topic,
            embed_model="BAAI/bge-m3",
            top_k=limit,
        )
        return [
            {
                "lo_code": r.get("metadata", {}).get("lo_code", ""),
                "topic": topic,
                "competency_text_en": r.get("metadata", {}).get("competency_text_en", ""),
                "competency_text_ga": r.get("metadata", {}).get("competency_text_ga"),
                "score": r.get("score", 0.0),
                "evidence": r.get("metadata", {}).get("evidence", {}),
            }
            for r in results
        ]
    except Exception:
        # Fallback: empty result on any error
        return []