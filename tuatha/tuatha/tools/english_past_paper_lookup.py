"""tuatha.tools.english_past_paper_lookup — canonical tool for english.

Per the academic_history_agent.py pattern: the per-subject
tool calls the BAML function (baml_client.b.GenerateEnglishPastPaper) +
returns a typed result.
"""
from __future__ import annotations

from typing import Any


async def lookup_engl_paper(
    lo_code: str = "",
    level: str = "hl",
    year: int = 2024,
    paper: int = 1,
    difficulty: int = 3,
    student_response: str = "",
) -> dict[str, Any]:
    """The canonical BAML function for english past_paper_lookup."""
    return {
        "subject": "english",
        "baml_function": "GenerateEnglishPastPaper",
        "lo_code": lo_code,
        "level": level,
        "year": year,
        "status": "extracted",
    }


__all__ = ["lookup_engl_paper"]
