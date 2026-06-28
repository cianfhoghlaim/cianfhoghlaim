"""Wales education — Cymraeg (Plan 2 PRESERVED stub).

wls is one of the 6 active nations in cianfhoghlaim (Plan 2 stub).
primary: ages 5-11 / Key Stage 1-2 / P1-P7.

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

NATION = "wls"
STAGE = "primary"
LANGUAGE = "cymraeg"
PRIMARY_URL = "https://hwb.gov.wales/curriculum-for-wales"

SAMPLING_RATE = 0.1  # Stub: 10% sample until full Plan 2 implementation.
CHUNK_SIZE_TOKENS = 1024
OVERLAP_TOKENS = 128


def is_plan1_active() -> bool:
    return False


def is_plan2_stub() -> bool:
    return True
