

def _resolve_embedder() -> str:
    """Resolve the canonical embedder from MODEL_REGISTRY.

    Per the `centralized-model-registry` capability, the canonical
    embedder is resolved from MODEL_REGISTRY at runtime
    (CIANFHOGHLAIM_EMBED_MODEL env var overrides). Falls back to
    "BAAI/bge-m3" if the registry import fails.
    """
    try:
        from meaisinfhoghlaim.models import MODEL_REGISTRY
        return MODEL_REGISTRY.resolve("embedder", "default")
    except Exception:
        return "BAAI/bge-m3"


"""gael_syllabus_lookup — Look up NCCA Gaeilge learning outcomes.

Backed by BAML `qpack_gaeilge.baml` `ExtractGaelLOStatement` + LanceDB
semantic search over the Gaeilge quest-pack embeddings.

Used by `gael_agent` tool #1.
"""
from __future__ import annotations

from typing import Any


async def lookup_gael_lo(
    topic: str,
    level: str = "lc_hl",
    language: str = "ga",
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Return NCCA Gaeilge learning outcomes matching `topic`."""
    try:
        from cianfhoghlaim.lancedb.search import semantic_search

        results = await semantic_search(
            table=f"oideachais.lc.gaeilge.{level}_{language}",
            query=topic,
            embed_model=_resolve_embedder(),
            top_k=limit,
        )
        return [
            {
                "lo_code": r.get("metadata", {}).get("lo_code", ""),
                "topic": topic,
                "competency_text_ga": r.get("metadata", {}).get("competency_text_ga", ""),
                "competency_text_en": r.get("metadata", {}).get("competency_text_en"),
                "score": r.get("score", 0.0),
                "evidence": r.get("metadata", {}).get("evidence", {}),
            }
            for r in results
        ]
    except Exception:
        return []