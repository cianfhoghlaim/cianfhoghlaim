

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


"""comp_syllabus_lookup — Look up NCCA Computer Science learning outcomes."""
from __future__ import annotations

from typing import Any


async def lookup_comp_lo(topic: str, level: str = "lc_hl", language: str = "en", limit: int = 10) -> list[dict[str, Any]]:
    try:
        from cianfhoghlaim.lancedb.search import semantic_search
        results = await semantic_search(table=f"oideachais.lc.computer_science.{level}_{language}", query=topic, embed_model=_resolve_embedder(), top_k=limit)
        return [{"lo_code": r.get("metadata", {}).get("lo_code", ""), "topic": topic, "score": r.get("score", 0.0)} for r in results]
    except Exception:
        return []


async def lookup_comp_paper(topic: str, level: str = "lc_hl", year: int | None = None, limit: int = 5) -> list[dict[str, Any]]:
    try:
        import duckdb
        con = duckdb.connect("./data/computer_science.duckdb", read_only=True)
        where = ["subject = 'computer_science'", f"level = '{level}'", f"text ILIKE '%{topic}%'"]
        if year is not None:
            where.append(f"year = {year}")
        query = f"SELECT item_id, lo_code, text, marks, year, source_pdf FROM comp_paper_items WHERE {' AND '.join(where)} LIMIT {limit}"
        rows = con.execute(query).fetchall()
        return [{"item_id": r[0], "lo_code": r[1], "text": r[2], "marks": r[3], "year": r[4], "source_pdf": r[5]} for r in rows]
    except Exception:
        return []


async def lookup_comp_marking_scheme(lo_code: str) -> dict[str, Any]:
    try:
        import duckdb
        con = duckdb.connect("./data/computer_science.duckdb", read_only=True)
        row = con.execute("SELECT lo_code, marks_per_step, text_en, text_ga, source_pdf FROM comp_marking_schemes WHERE lo_code = ? LIMIT 1", [lo_code]).fetchone()
        if row is None:
            return {"lo_code": lo_code, "error": "no marking scheme found"}
        return {"lo_code": row[0], "marks_per_step": row[1], "text_en": row[2], "text_ga": row[3], "source_pdf": row[4]}
    except Exception:
        return {"lo_code": lo_code, "error": "marking scheme lookup failed"}


async def generate_comp_item(lo_code: str, difficulty: int, evidence: dict[str, Any], level: str = "lc_hl", topic: str = "") -> dict[str, Any]:
    """`evidence` (`CompEvidenceLink`-shaped: source_pdf, source_page,
    excerpt_ga, excerpt_en, ncca_url) is required — see
    `docs-informed-quest-and-credential-generation-v1`.
    """
    try:
        from cianfhoghlaim.baml_client import b
        import uuid
        item = b.GenerateCompFormativeItem(lo_code=lo_code, difficulty=difficulty, level=level, topic=topic, evidence=evidence)
        return {"id": item.id or str(uuid.uuid4()), "lo_code": item.lo_code, "level": item.level, "topic": item.topic, "difficulty": item.difficulty, "prompt_en": item.prompt.text_en, "expected_answer_en": item.expected_answer.text_en, "marking_scheme_en": item.marking_scheme.text_en, "hints": [{"en": h.text_en, "ga": h.text_ga} for h in item.hints], "feedback_channel": item.feedback_channel, "est_time_minutes": item.est_time_minutes}
    except Exception as exc:
        return {"lo_code": lo_code, "error": f"Item generation failed: {exc}"}


async def score_comp_response(item_id: str, student_response: str, response_format: str = "code", time_taken_seconds: int = 0, hints_used: int = 0) -> dict[str, Any]:
    try:
        from cianfhoghlaim.baml_client import b
        import duckdb
        con = duckdb.connect("./data/computer_science.duckdb", read_only=True)
        item_row = con.execute("SELECT item_json FROM comp_quest_items WHERE id = ? LIMIT 1", [item_id]).fetchone()
        if item_row is None:
            return {"item_id": item_id, "error": "item not found"}
        item = item_row[0]
        score = b.ScoreCompFormativeResponse(item=item, attempt={"item_id": item_id, "student_response": student_response, "response_format": response_format, "time_taken_seconds": time_taken_seconds, "hints_used": hints_used})
        if score.badge_earned:
            try:
                from cianfhoghlaim.tuatha.badges import issue_badge
                await issue_badge(student_id=None, framework="ncca-lc", level=score.lo_code.split("-")[-2] if "-" in score.lo_code else "hl", subject="computer_science", competency_code=score.lo_code, agent_issuer="comp_agent", evidence={"item_id": item_id, "response": student_response, "score_pct": score.partial_credit_pct})
            except ImportError:
                pass
        return {"item_id": score.item_id, "lo_code": score.lo_code, "total_marks": score.total_marks, "marks_awarded": score.marks_awarded, "partial_credit_pct": score.partial_credit_pct, "feedback_en": score.feedback_en, "feedback_ga": score.feedback_ga, "badge_earned": score.badge_earned}
    except Exception as exc:
        return {"item_id": item_id, "error": f"Scoring failed: {exc}"}