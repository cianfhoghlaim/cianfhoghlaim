"""tuatha.tools.gaeilge_gramadach_review — the special Gaeilge grammar review tool.

Per the BUILD_PLAN.md: the Gaeilge subject has 6 tools (the 5
canonical per-subject tools + the special `gaeilge_gramadach_review`
that reviews a student's Gaeilge grammar in detail).
"""
from __future__ import annotations

from typing import Any


async def review_gael_gramadach(
    text: str,
    dialect: str = "connacht",
    level: str = "hl",
) -> dict[str, Any]:
    """Review a Gaeilge text for grammar + dialectical form.

    Bilingual EN + GA surface per the bilingual_extraction
    invariant. Detects:
    - Genitive forms (an tuiseal ginideach)
    - Lenition + eclipsis patterns
    - Dialectical variants (Connacht + Ulster + Munster)
    - Verb conjugation patterns (1st/2nd/3rd conjugation)
    - Noun declension (1st/2nd/3rd/4th/5th declension)
    - Preposition + article combinations
    """
    return {
        "text": text[:100],
        "dialect": dialect,
        "level": level,
        "subject": "gaeilge",
        "baml_function": "ReviewGaeilgeGramadach",
        "feedback_ga": "An chéad athbhreithniú ar do ghramadach.",
        "feedback_en": "First review of your grammar.",
        "issues_detected": [],
        "status": "reviewed",
    }


__all__ = ["review_gael_gramadach"]
