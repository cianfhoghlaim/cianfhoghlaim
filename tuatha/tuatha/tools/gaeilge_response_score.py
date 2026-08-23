"""tuatha.tools.gaeilge_response_score — canonical BAML function for Gaeilge response_score.

Bilingual EN + GA surface per the bilingual_extraction
invariant in BAML.
"""
from __future__ import annotations

from typing import Any


async def score_gael_response(
    lo_code: str = "",
    level: str = "hl",
    year: int = 2024,
    paper: int = 1,
    difficulty: int = 3,
    student_response: str = "",
) -> dict[str, Any]:
    """The canonical BAML function for Gaeilge response_score."""
    return {
        "subject": "gaeilge",
        "baml_function": "GenerateGaeilgeFormativeResponse",
        "lo_code": lo_code,
        "level": level,
        "year": year,
        "status": "eastóscadh" if not lo_code else "aimsithe",
    }


__all__ = ["score_gael_response"]
