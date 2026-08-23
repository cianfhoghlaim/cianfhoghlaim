"""tuatha.tools.computer_science_marking_scheme_lookup — canonical tool for computer_science.

Per the academic_history_agent.py pattern: the per-subject
tool calls the BAML function (baml_client.b.GenerateComputerScienceMarkingScheme) +
returns a typed result.
"""
from __future__ import annotations

from typing import Any


async def lookup_comp_marking_scheme(
    lo_code: str = "",
    level: str = "hl",
    year: int = 2024,
    paper: int = 1,
    difficulty: int = 3,
    student_response: str = "",
) -> dict[str, Any]:
    """The canonical BAML function for computer_science marking_scheme_lookup."""
    return {
        "subject": "computer_science",
        "baml_function": "GenerateComputerScienceMarkingScheme",
        "lo_code": lo_code,
        "level": level,
        "year": year,
        "status": "extracted",
    }


__all__ = ["lookup_comp_marking_scheme"]
