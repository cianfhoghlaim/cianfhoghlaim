

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


"""appm_syllabus_lookup — Look up NCCA Applied Mathematics learning outcomes."""
from __future__ import annotations

from typing import Any


async def lookup_appm_lo(
    topic: str,
    language: str = "en",
    limit: int = 10,
) -> list[dict[str, Any]]:
    try:
        from cianfhoghlaim.lancedb.search import semantic_search

        results = await semantic_search(
            table=f"oideachais.lc.applied_mathematics.hl_{language}",
            query=topic,
            embed_model=_resolve_embedder(),
            top_k=limit,
        )
        return [
            {
                "lo_code": r.get("metadata", {}).get("lo_code", ""),
                "topic": topic,
                "competency_text_en": r.get("metadata", {}).get("competency_text_en", ""),
                "competency_text_ga": r.get("metadata", {}).get("competency_text_ga"),
                "score": r.get("score", 0.0),
            }
            for r in results
        ]
    except Exception:
        return []