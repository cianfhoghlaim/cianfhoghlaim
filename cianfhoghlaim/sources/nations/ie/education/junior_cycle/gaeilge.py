"""Ireland Junior Cycle — Gaeilge (Plan 1 ACTIVE).

An Timpeall Réamhoideachais, 1ú–3ú Bliain.

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

NATION = "ie"
STAGE = "junior_cycle"
LANGUAGE = "gaeilge"
PRIMARY_URL = "https://ncca.ie/ga/an-timpeall-reamhoideachais/"

SAMPLING_RATE = 1.0
CHUNK_SIZE_TOKENS = 1024
OVERLAP_TOKENS = 128


def is_plan1_active() -> bool:
    return True
