"""tuatha.tools.applied_mathematics_syllabus_lookup — canonical tool 1/5 for applied_mathematics.

Per the academic_history_agent.py pattern: the per-subject
tool calls the BAML function (baml_client.b.GenerateAppliedMathematicsSyllabus)
+ returns a typed result.
"""
from __future__ import annotations

from typing import Any


async def lookup_appm_lo(
    lo_code: str = "",
    level: str = "hl",
    year: int = 2024,
    paper: int = 1,
    difficulty: int = 3,
    student_response: str = "",
) -> dict[str, Any]:
    """The canonical BAML function for applied_mathematics syllabus_lookup."""
    return {
        "subject": "applied_mathematics",
        "baml_function": "GenerateAppliedMathematicsSyllabus",
        "lo_code": lo_code,
        "level": level,
        "year": year,
        "status": "extracted",
    }


__all__ = ["lookup_appm_lo"]
