

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


"""math_syllabus_lookup — Look up NCCA Mathematics learning outcomes.

Per cianfhoghlaim/agents/tuatha/tools/ pattern.
Backed by:
- BAML `qpack_mathematics.baml` `ExtractLeavingCertSyllabus` for fresh extraction
- LanceDB `oideachais.lc.mathematics.<level>_<language>` for cached + embedded results
- Cognee `oideachais_lc_mathematics` for cross-LO reasoning
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
                "evidence": r.get("metadata", {}).get("evidence", {}),
            }
            for r in results
        ]
    except Exception:
        return []


async def get_math_past_papers(
    topic: str,
    level: str = "hl",
    year_from: int = 2017,
    year_to: int = 2025,
) -> list[dict[str, Any]]:
    """Return past Mathematics exam papers tagged by topic + paper + year."""
    # TODO: query MotherDuck `oideachais.lc.mathematics.past_papers`
    return []


async def get_math_marking_scheme(
    topic: str,
    paper: str = "paper-1",
    year: int = 2024,
) -> dict[str, Any]:
    """Return the marking scheme patterns + common mistakes for a topic + paper + year."""
    return {"patterns": [], "common_mistakes": []}


async def score_math_response(
    item_id: str,
    student_response: str,
    expected_answer: str,
    marking_scheme: str,
) -> dict[str, Any]:
    """Score a student response against the marking scheme via BAML."""
    try:
        from cianfhoghlaim.baml_client import b

        score = b.ScoreMathFormativeResponse(
            item_id=item_id,
            student_response=student_response,
            expected_answer=expected_answer,
            marking_scheme=marking_scheme,
        )
        return {"score_pct": score.score_pct, "feedback_en": score.feedback_en}
    except Exception:
        return {"score_pct": 0, "feedback_en": "Scoring failed"}


async def generate_math_formative_item(
    lo_code: str,
    difficulty: int = 3,
    language: str = "en",
) -> dict[str, Any]:
    """Generate a new Mathematics formative item keyed to the NCCA LO."""
    try:
        from cianfhoghlaim.baml_client import b

        item = b.GenerateMathFormativeItem(
            lo_code=lo_code,
            difficulty=difficulty,
            language=language,
        )
        return item.model_dump()
    except Exception:
        return {"error": "Generation failed"}