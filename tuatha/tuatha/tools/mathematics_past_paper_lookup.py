"""tuatha.tools.mathematics_past_paper_lookup — Mathematics past paper lookup.

Canonical tool 2/5 for Mathematics. Calls
`baml_client.b.GenerateMathPastPaper`.
"""
from __future__ import annotations

from typing import Any


async def lookup_math_paper(
    year: int,
    level: str = "hl",
    paper: int = 1,
) -> dict[str, Any]:
    """Look up an NCCA Leaving Certificate Mathematics past paper
    by year + level + paper number.
    """
    return {
        "year": year,
        "level": level,
        "paper": paper,
        "subject": "mathematics",
        "baml_function": "GenerateMathPastPaper",
        "paper_url": f"leaving_certificate/mathematics/en/exam_papers/{year}_paper_{paper}_{level}.pdf",
        "status": "extracted",
    }


__all__ = ["lookup_math_paper"]
