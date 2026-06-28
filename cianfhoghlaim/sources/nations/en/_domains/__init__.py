"""England — 7-domain bundle stub (Plan 3 PRESERVED).

Cross-domain sources for England beyond the education sources at
sources/nations/en/education/. Each domain maps to a separate
.stub file in this directory for Plan 3 implementation.

Domains (8 total per cianfhoghlaim conventions; this bundle covers 7):
1. law            — primary legislation, statutory instruments
2. medicine       — NHS, NICE, Royal Colleges, GMC
3. culture        — Arts Council, British Council, museums
4. government     — Whitehall / devolved government / local authorities
5. intelligence   — GCHQ / MI5 / MI6 / Defence Intelligence
6. statistics     — ONS / National Records of Scotland / NISRA
7. geospatial     — Ordnance Survey / British Geological Survey

Authority: HM Government (gov.uk)

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

NATION = "en"
LABEL = "England"
AUTHORITY = "HM Government (gov.uk)"
DOMAINS = ("law", "medicine", "culture", "government", "intelligence", "statistics", "geospatial")
SAMPLING_RATE = 0.1


def is_plan1_active() -> bool:
    return False


def is_plan3_stub() -> bool:
    return True
