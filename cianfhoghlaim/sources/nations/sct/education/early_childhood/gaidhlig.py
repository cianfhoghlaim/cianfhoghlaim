"""Scotland education — Gàidhlig (Plan 2 PRESERVED stub).

sct is one of the 6 active nations in cianfhoghlaim (Plan 2 stub).
early_childhood: ages 0-5 / Foundation Stage.

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

NATION = "sct"
STAGE = "early_childhood"
LANGUAGE = "gaidhlig"
PRIMARY_URL = "https://www.sqa.org.uk/sqa/56920.html"

SAMPLING_RATE = 0.1  # Stub: 10% sample until full Plan 2 implementation.
CHUNK_SIZE_TOKENS = 1024
OVERLAP_TOKENS = 128


def is_plan1_active() -> bool:
    return False


def is_plan2_stub() -> bool:
    return True
