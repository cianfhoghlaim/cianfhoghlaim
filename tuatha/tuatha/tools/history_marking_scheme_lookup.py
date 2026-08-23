"""tuatha.tools.history_marking_scheme_lookup — canonical tool for history.

Per the academic_history_agent.py pattern: the per-subject
tool calls the BAML function (baml_client.b.GenerateHistoryMarkingScheme) +
returns a typed result.
"""
from __future__ import annotations

from typing import Any


async def lookup_hist_marking_scheme(
    lo_code: str = "",
    level: str = "hl",
    year: int = 2024,
    paper: int = 1,
    difficulty: int = 3,
    student_response: str = "",
) -> dict[str, Any]:
    """The canonical BAML function for history marking_scheme_lookup."""
    return {
        "subject": "history",
        "baml_function": "GenerateHistoryMarkingScheme",
        "lo_code": lo_code,
        "level": level,
        "year": year,
        "status": "extracted",
    }


__all__ = ["lookup_hist_marking_scheme"]
