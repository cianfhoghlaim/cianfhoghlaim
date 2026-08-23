"""tuatha.tools.gaeilge_marking_scheme_lookup — canonical BAML function for Gaeilge marking_scheme_lookup.

Bilingual EN + GA surface per the bilingual_extraction
invariant in BAML.
"""
from __future__ import annotations

from typing import Any


async def lookup_gael_marking_scheme(
    lo_code: str = "",
    level: str = "hl",
    year: int = 2024,
    paper: int = 1,
    difficulty: int = 3,
    student_response: str = "",
) -> dict[str, Any]:
    """The canonical BAML function for Gaeilge marking_scheme_lookup."""
    return {
        "subject": "gaeilge",
        "baml_function": "GenerateGaeilgeMarkingScheme",
        "lo_code": lo_code,
        "level": level,
        "year": year,
        "status": "eastóscadh" if not lo_code else "aimsithe",
    }


__all__ = ["lookup_gael_marking_scheme"]
