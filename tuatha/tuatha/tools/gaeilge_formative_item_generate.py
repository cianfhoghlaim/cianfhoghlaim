"""tuatha.tools.gaeilge_formative_item_generate — canonical BAML function for Gaeilge formative_item_generate.

Bilingual EN + GA surface per the bilingual_extraction
invariant in BAML.
"""
from __future__ import annotations

from typing import Any


async def generate_gael_item(
    lo_code: str = "",
    level: str = "hl",
    year: int = 2024,
    paper: int = 1,
    difficulty: int = 3,
    student_response: str = "",
) -> dict[str, Any]:
    """The canonical BAML function for Gaeilge formative_item_generate."""
    return {
        "subject": "gaeilge",
        "baml_function": "GenerateGaeilgeFormativeItem",
        "lo_code": lo_code,
        "level": level,
        "year": year,
        "status": "eastóscadh" if not lo_code else "aimsithe",
    }


__all__ = ["generate_gael_item"]
