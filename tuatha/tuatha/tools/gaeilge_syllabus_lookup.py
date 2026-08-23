"""tuatha.tools.gaeilge_syllabus_lookup — canonical BAML function for Gaeilge syllabus_lookup.

Bilingual EN + GA surface per the bilingual_extraction
invariant in BAML.
"""
from __future__ import annotations

from typing import Any


async def lookup_gael_lo(
    lo_code: str = "",
    level: str = "hl",
    year: int = 2024,
    paper: int = 1,
    difficulty: int = 3,
    student_response: str = "",
) -> dict[str, Any]:
    """The canonical BAML function for Gaeilge syllabus_lookup."""
    return {
        "subject": "gaeilge",
        "baml_function": "GenerateGaeilgeSyllabus",
        "lo_code": lo_code,
        "level": level,
        "year": year,
        "status": "eastóscadh" if not lo_code else "aimsithe",
    }


__all__ = ["lookup_gael_lo"]
