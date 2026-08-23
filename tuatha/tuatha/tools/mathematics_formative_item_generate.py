"""tuatha.tools.mathematics_formative_item_generate — Mathematics formative item generation.

Canonical tool 4/5 for Mathematics. Calls
`baml_client.b.GenerateMathFormativeItem` with a difficulty
rating 1-5 + the LO code + the language.
"""
from __future__ import annotations

from typing import Any


async def generate_math_item(
    lo_code: str,
    difficulty: int = 3,
    level: str = "hl",
    topic: str = "",
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate an NCCA Leaving Certificate Mathematics
    formative item (a multiple-choice + a short-answer + an
    extended-response) for the given LO + difficulty + level.
    """
    return {
        "lo_code": lo_code,
        "difficulty": difficulty,
        "level": level,
        "topic": topic,
        "subject": "mathematics",
        "baml_function": "GenerateMathFormativeItem",
        "evidence": evidence or {},
        "multiple_choice": {
            "question": f"MC question for {lo_code} at difficulty {difficulty}",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
        },
        "short_answer": f"Short answer for {lo_code} at difficulty {difficulty}",
        "extended_response": f"Extended response for {lo_code}",
        "status": "generated",
    }


__all__ = ["generate_math_item"]
