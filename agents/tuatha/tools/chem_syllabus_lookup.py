"""chem_syllabus_lookup — Look up NCCA Chemistry learning outcomes."""
from __future__ import annotations

from typing import Any


async def lookup_chem_lo(
    topic: str,
    level: str = "lc_hl",
    language: str = "en",
    limit: int = 10,
) -> list[dict[str, Any]]:
    try:
        from cianfhoghlaim.lancedb.search import semantic_search

        results = await semantic_search(
            table=f"oideachais.lc.chemistry.{level}_{language}",
            query=topic,
            embed_model="BAAI/bge-m3",
            top_k=limit,
        )
        return [
            {
                "lo_code": r.get("metadata", {}).get("lo_code", ""),
                "topic": topic,
                "competency_text_en": r.get("metadata", {}).get("competency_text_en", ""),
                "score": r.get("score", 0.0),
            }
            for r in results
        ]
    except Exception:
        return []