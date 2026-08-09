"""appm_response_score — Score a student's attempt at an APPM item."""
from __future__ import annotations

from typing import Any


async def score_appm_response(
    item_id: str,
    student_response: str,
    response_format: str = "text",
    time_taken_seconds: int = 0,
    hints_used: int = 0,
) -> dict[str, Any]:
    try:
        from cianfhoghlaim.baml_client import b

        import duckdb

        con = duckdb.connect("./data/applied_mathematics.duckdb", read_only=True)
        item_row = con.execute(
            "SELECT item_json FROM appm_quest_items WHERE id = ? LIMIT 1", [item_id]
        ).fetchone()
        if item_row is None:
            return {"item_id": item_id, "error": "item not found"}
        item = item_row[0]

        score = b.ScoreAppmFormativeResponse(
            item=item,
            attempt={
                "item_id": item_id,
                "student_response": student_response,
                "response_format": response_format,
                "time_taken_seconds": time_taken_seconds,
                "hints_used": hints_used,
            },
        )

        if score.badge_earned:
            try:
                from cianfhoghlaim.tuatha.badges import issue_badge
                await issue_badge(
                    student_id=None,
                    framework="ncca-lc",
                    level="hl",
                    subject="applied_mathematics",
                    competency_code=score.lo_code,
                    agent_issuer="appm_agent",
                    evidence={
                        "item_id": item_id,
                        "response": student_response,
                        "score_pct": score.partial_credit_pct,
                        "feedback_en": score.feedback_en,
                    },
                )
            except ImportError:
                pass

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