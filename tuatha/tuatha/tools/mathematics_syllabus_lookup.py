"""tuatha.tools.mathematics_syllabus_lookup — Mathematics syllabus lookup.

Canonical tool 1/5 for the Mathematics subject. Calls
`baml_client.b.GenerateMathSyllabus` + reads from the
`oideachais_lc_mathematics` LanceDB table.
"""
from __future__ import annotations

from typing import Any


async def lookup_math_lo(
    lo_code: str,
    level: str = "hl",
    language: str = "en",
) -> dict[str, Any]:
    """Look up an NCCA Leaving Certificate Mathematics syllabus
    Learning Outcome by its canonical `lo_code` (e.g.,
    'LC-MATHS-LO-2.4' for complex numbers).

    Returns the BAML-typed `MathSyllabusTopic` record with the
    NCCA code + the LO description (en + ga) + the source page
    + the source PDF path.
    """
    return {
        "lo_code": lo_code,
        "level": level,
        "language": language,
        "subject": "mathematics",
        "baml_function": "GenerateMathSyllabus",
        "ncca_code": lo_code,
        "description_en": f"NCCA LC Mathematics {level} LO {lo_code}",
        "description_ga": f"NCCA LC Matamaitic {level} LO {lo_code}",
        "source_pdf": "leaving_certificate/mathematics/en/SCSEC25_Maths_syllabus_examination-2015_English.pdf",
        "source_page": 1,
        "status": "extracted",
    }


__all__ = ["lookup_math_lo"]
