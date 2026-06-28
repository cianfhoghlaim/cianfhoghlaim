"""Gaeilge (Irish) — full source profile (cianfhoghlaim Plan 1 active).

Gaeilge is the primary national language of Ireland (Plan 1) and a
significant minority language in Northern Ireland (Plan 2 stub). All
Ireland education sources include a Gaeilge parallel.

Coverage (Plan 1):
- Ireland education (5 stages × GA) at sources/nations/ie/education/*/gaeilge.py
- leabharlann/gaeilge/ subdir (45 docs)

Coverage (Plan 2 stub):
- Northern Ireland (sources/nations/ni/education/*/gaeilge.py) — partial
  coverage for Irish-medium schools (Gaelscoileanna).

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

# Plan 1 active: every Gaeilge source for Ireland education + leabharlann
PLAN_1_SOURCES: tuple[str, ...] = (
    # Ireland — 5 educational stages × Gaeilge
    "sources.nations.ie.education.early_childhood.gaeilge",
    "sources.nations.ie.education.primary.gaeilge",
    "sources.nations.ie.education.junior_cycle.gaeilge",
    "sources.nations.ie.education.senior_cycle.gaeilge",
    "sources.nations.ie.education.leaving_cert.gaeilge",
    # leabharlann/gaeilge/ — 45 Irish-language texts
    "leabharlann.gaeilge",
)

# Plan 2 stub: NI Gaelscoil network
PLAN_2_STUB_NATIONS: tuple[str, ...] = ("ni",)

# ISO 639-1 + ISO 639-3 codes for Irish
ISO_CODES: tuple[str, ...] = ("ga", "ga-IE", "gle")


def is_active_in_plan1() -> bool:
    """Gaeilge is the primary Plan 1 language for Ireland."""
    return True
