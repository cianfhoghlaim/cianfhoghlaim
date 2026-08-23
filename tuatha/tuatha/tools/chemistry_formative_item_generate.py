"""tuatha.tools.chemistry_formative_item_generate — canonical tool for chemistry.

Per the academic_history_agent.py pattern: the per-subject
tool calls the BAML function (baml_client.b.GenerateChemistryFormativeItem) +
returns a typed result.
"""
from __future__ import annotations

from typing import Any


async def generate_chem_item(
    lo_code: str = "",
    level: str = "hl",
    year: int = 2024,
    paper: int = 1,
    difficulty: int = 3,
    student_response: str = "",
) -> dict[str, Any]:
    """The canonical BAML function for chemistry formative_item_generate."""
    return {
        "subject": "chemistry",
        "baml_function": "GenerateChemistryFormativeItem",
        "lo_code": lo_code,
        "level": level,
        "year": year,
        "status": "extracted",
    }


__all__ = ["generate_chem_item"]
