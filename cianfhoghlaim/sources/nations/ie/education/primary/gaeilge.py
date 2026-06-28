"""Ireland Primary education — Gaeilge (Plan 1 ACTIVE).

Bunscoil, aicmí naíonáin shóisearacha go dtí an séú rang.

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

NATION = "ie"
STAGE = "primary"
LANGUAGE = "gaeilge"
PRIMARY_URL = "https://ncca.ie/ga/bhunscoil/"

CURRICULUM_AREAS = (
    "gaeilge", "béarla", "matamaitic", "sese", "sphe",
    "oideachas-ealaíon", "corpoideachas", "oideachas-creidimh",
)

SAMPLING_RATE = 1.0
CHUNK_SIZE_TOKENS = 1024
OVERLAP_TOKENS = 128


def is_plan1_active() -> bool:
    return True
