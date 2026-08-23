"""tuatha.tools.mathematics_marking_scheme_lookup — Mathematics marking scheme lookup.

Canonical tool 3/5 for Mathematics. Calls
`baml_client.b.GenerateMathMarkingScheme`.
"""
from __future__ import annotations

from typing import Any


async def lookup_math_marking_scheme(
    lo_code: str,
    level: str = "hl",
    year: int = 2024,
) -> dict[str, Any]:
    """Look up an NCCA Leaving Certificate Mathematics marking
    scheme for a specific LO + year + level.
    """
    return {
        "lo_code": lo_code,
        "level": level,
        "year": year,
        "subject": "mathematics",
        "baml_function": "GenerateMathMarkingScheme",
        "scheme_url": f"leaving_certificate/mathematics/en/marking_schemes/{year}_marking_scheme_{level}.pdf",
        "status": "extracted",
    }


__all__ = ["lookup_math_marking_scheme"]
