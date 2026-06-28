"""Gàidhlig (Scottish Gaelic) — full source profile (Plan 2 stub).

Scottish Gaelic is a recognised minority language in Scotland with strong
educational provision (Sgoil Ghàidhlig). Plan 2 preserves a stub.

Coverage (Plan 2 stub):
- sources/nations/sct/education/{early_childhood,primary,secondary}/gaidhlig.py

Coverage (Plan 3 future):
- law, medicine, culture, government, statistics, geospatial
- Bòrd na Gàidhlig publications, Sabhal Mòr Ostaig, BBC Alba

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

# Plan 2 preserved (Scotland)
PLAN_2_SOURCES: tuple[str, ...] = (
    "sources.nations.sct.education.early_childhood.gaidhlig",
    "sources.nations.sct.education.primary.gaidhlig",
    "sources.nations.sct.education.secondary.gaidhlig",
)

# ISO 639-1 + ISO 639-3 codes for Scottish Gaelic
ISO_CODES: tuple[str, ...] = ("gd", "gd-GB", "gla")


def is_active_in_plan1() -> bool:
    """Gàidhlig is NOT in Plan 1; it's a Plan 2 stub."""
    return False
