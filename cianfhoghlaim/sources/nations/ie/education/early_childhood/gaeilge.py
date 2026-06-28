"""Ireland Early Childhood education — Gaeilge (Plan 1 ACTIVE).

Aistear, an curaclam luath-óige. Údarás: An Chomhairle Náisiúnta Curaclaim
agus Measúnachta (NCCA).

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

NATION = "ie"
STAGE = "early_childhood"
LANGUAGE = "gaeilge"
PRIMARY_URL = "https://ncca.ie/ga/luath-og/"

# 4 théamaí Aistear
AISTEAR_THEMES = ("folláine", "céannacht agus muintearas",
                  "cumarsáid", "fiosrúchán agus smaoineamh")

SAMPLING_RATE = 1.0
CHUNK_SIZE_TOKENS = 512
OVERLAP_TOKENS = 64


def is_plan1_active() -> bool:
    return True