"""Ireland Leaving Certificate — Gaeilge (Plan 1 ACTIVE).

An Ardteistiméireacht. Údarás: Coimisiún na Scrúduithe Stáit (SEC).

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

NATION = "ie"
STAGE = "leaving_cert"
LANGUAGE = "gaeilge"
PRIMARY_URL = "https://www.examinations.ie/ga/"

LC_PROGRAMMES = ("ardteistiméireacht", "ardteistiméireacht-fheidhmeach",
                "ardteistiméireacht-ghairmoideachais",
                "ardteistiméireacht-naisc")

SAMPLING_RATE = 0.5
CHUNK_SIZE_TOKENS = 2048
OVERLAP_TOKENS = 256


def is_plan1_active() -> bool:
    return True
