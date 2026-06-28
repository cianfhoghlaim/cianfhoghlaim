"""Northern Ireland education — English (Plan 2 PRESERVED stub).

ni is one of the 6 active nations in cianfhoghlaim (Plan 2 stub).
secondary: ages 11-18 / Key Stage 3-5 / GCSE / A-level / National 5 / Higher / Advanced Higher.

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

NATION = "ni"
STAGE = "secondary"
LANGUAGE = "english"
PRIMARY_URL = "https://ccea.org.uk/"

SAMPLING_RATE = 0.1  # Stub: 10% sample until full Plan 2 implementation.
CHUNK_SIZE_TOKENS = 1024
OVERLAP_TOKENS = 128


def is_plan1_active() -> bool:
    return False


def is_plan2_stub() -> bool:
    return True
