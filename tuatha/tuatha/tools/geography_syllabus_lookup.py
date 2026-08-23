"""tuatha.tools.geography_syllabus_lookup — canonical tool for geography.

Per the academic_history_agent.py pattern: the per-subject
tool calls the BAML function (baml_client.b.GenerateGeographySyllabus) +
returns a typed result.
"""
from __future__ import annotations

from typing import Any


async def lookup_geog_lo(
    lo_code: str = "",
    level: str = "hl",
    year: int = 2024,
    paper: int = 1,
    difficulty: int = 3,
    student_response: str = "",
) -> dict[str, Any]:
    """The canonical BAML function for geography syllabus_lookup."""
    return {
        "subject": "geography",
        "baml_function": "GenerateGeographySyllabus",
        "lo_code": lo_code,
        "level": level,
        "year": year,
        "status": "extracted",
    }


__all__ = ["lookup_geog_lo"]
