"""Ireland Early Childhood education — English-language source (Plan 1 ACTIVE).

Stage: Aistear (Early Childhood, ages 0–6).
Authority: National Council for Curriculum and Assessment (NCCA).
Primary URL: https://ncca.ie/en/early-childhood/

Coverage:
- Aistear framework (2009, revised 2024)
- Síolta quality framework
- Better Start quality improvement programme
- Tusla early years inspectorate reports

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

NATION = "ie"
STAGE = "early_childhood"
LANGUAGE = "english"
PRIMARY_URL = "https://ncca.ie/en/early-childhood/"

# The 4 Aistear themes (well-being, identity & belonging, communicating,
# exploring & thinking) are extracted via cianfhoghlaim.core.baml.curriculum
# (function: ExtractAistearThemes).
AISTEAR_THEMES = ("well-being", "identity-and-belonging",
                  "communicating", "exploring-and-thinking")

# Sampling config for the v1 CocoIndex Ireland corpus indexer.
SAMPLING_RATE = 1.0  # Full corpus — Aistear is small.
CHUNK_SIZE_TOKENS = 512
OVERLAP_TOKENS = 64


def is_plan1_active() -> bool:
    return True
