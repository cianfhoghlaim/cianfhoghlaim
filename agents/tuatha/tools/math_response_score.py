"""math_response_score — Score a student's attempt at a formative item.

Backed by BAML `qpack_mathematics.baml` `ScoreMathFormativeResponse`.

If the score is >= 80%, emits a SkillTreeBadge to the `badges`
subsystem for the daily Merkle anchor.

Used by `math_agent` tool #5.
"""
from __future__ import annotations

from typing import Any


async def score_math_response(
    item_id: str,
    student_response: str,
    response_format: str = "text",
    time_taken_seconds: int = 0,
    hints_used: int = 0,
) -> dict[str, Any]:
    """Score a student's attempt and (if eligible) emit a SkillTreeBadge."""
    try:
        from cianfhoghlaim.baml_client import b  # type: ignore

        # 1. Load the item from DuckDB (cached by the math_quest_pack asset)
        import duckdb

        con = duckdb.connect("./data/mathematics.duckdb", read_only=True)
        item_row = con.execute(
            "SELECT item_json FROM math_quest_items WHERE id = ? LIMIT 1",
            [item_id],
        ).fetchone()
        if item_row is None:
            return {"item_id": item_id, "error": "item not found"}
        item = item_row[0]

        # 2. Score via BAML
        score = b.ScoreMathFormativeResponse(
            item=item,
            attempt={
                "item_id": item_id,
                "student_response": student_response,
                "response_format": response_format,
                "time_taken_seconds": time_taken_seconds,
                "hints_used": hints_used,
            },
        )

        # 3. Emit a SkillTreeBadge if eligible
        if score.badge_earned:
            try:
                from cianfhoghlaim.tuatha.badges import issue_badge

                badge = await issue_badge(
                    student_id=None,  # Resolved from session in the real flow
                    framework="ncca-lc",
                    level=score.lo_code.split("-")[-2] if "-" in score.lo_code else "hl",
                    subject="mathematics",
                    competency_code=score.lo_code,
                    agent_issuer="math_agent",
                    evidence={
                        "item_id": item_id,
                        "response": student_response,
                        "score_pct": score.partial_credit_pct,
                        "feedback_en": score.feedback_en,
                    },
                )
            except ImportError:
                # badges submodule not yet built (Phase 4 of the openspec change)
                badge = None

        return {
            "item_id": score.item_id,
            "lo_code": score.lo_code,
            "total_marks": score.total_marks,
            "marks_awarded": score.marks_awarded,
            "marks_per_step": score.marks_per_step,
            "is_correct": score.is_correct,
            "partial_credit_pct": score.partial_credit_pct,
            "feedback_en": score.feedback_en,
            "feedback_ga": score.feedback_ga,
            "next_recommended_lo": score.next_recommended_lo,
            "badge_earned": score.badge_earned,
        }
    except Exception as exc:
        return {"item_id": item_id, "error": f"Scoring failed: {exc}"}