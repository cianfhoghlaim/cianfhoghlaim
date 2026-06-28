"""Gaelg (Manx) — full source profile (Plan 2 stub).

Manx is the Celtic language of the Isle of Man. It was revived from near-extinction
in the 20th century and now has a small but growing educational provision
through the Bunscoill Ghaelgagh.

Coverage (Plan 2 stub):
- sources/nations/iom/education/{early_childhood,primary,secondary}/gaelg.py

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.

NOTE: Spelling note — "kernewek" is the alternative native spelling used by
some revivalists; the standard scholarly spelling is "kernewek" (Cornish) /
"gaelg" (Manx). Both are accepted in Unicode but the codebase uses the
scholarly forms for consistency.
"""

from __future__ import annotations

# Plan 2 preserved (Isle of Man)
PLAN_2_SOURCES: tuple[str, ...] = (
    "sources.nations.iom.education.early_childhood.gaelg",
    "sources.nations.iom.education.primary.gaelg",
    "sources.nations.iom.education.secondary.gaelg",
)

# ISO 639-1 + ISO 639-3 codes for Manx
ISO_CODES: tuple[str, ...] = ("gv", "gv-IM", "glv")


def is_active_in_plan1() -> bool:
    """Gaelg is NOT in Plan 1; it's a Plan 2 stub."""
    return False
