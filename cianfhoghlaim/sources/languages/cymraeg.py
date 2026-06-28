"""Cymraeg (Welsh) — full source profile (Plan 2 stub).

Welsh is the primary national language of Wales. Welsh-medium education
(Welsh-medium schools + S4C) is well-established. Plan 2 preserves a
stub; full Plan 3 implementation will add the 7 domains.

Coverage (Plan 2 stub):
- sources/nations/wls/education/{early_childhood,primary,secondary}/cymraeg.py

Coverage (Plan 3 future):
- law, medicine, culture, government, statistics, geospatial
- Welsh-language media (BBC Cymru, S4C) + legislation (Senedd Cymru)

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

# Plan 2 preserved (Wales)
PLAN_2_SOURCES: tuple[str, ...] = (
    "sources.nations.wls.education.early_childhood.cymraeg",
    "sources.nations.wls.education.primary.cymraeg",
    "sources.nations.wls.education.secondary.cymraeg",
)

# ISO 639-1 + ISO 639-3 codes for Welsh
ISO_CODES: tuple[str, ...] = ("cy", "cy-GB", "wel")


def is_active_in_plan1() -> bool:
    """Cymraeg is NOT in Plan 1; it's a Plan 2 stub."""
    return False
