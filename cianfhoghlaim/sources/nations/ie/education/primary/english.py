"""Ireland Primary education — English-language source (Plan 1 ACTIVE).

Stage: Primary School (ages 6–12, classes Junior Infants to 6th Class).
Authority: National Council for Curriculum and Assessment (NCCA).
Primary URL: https://ncca.ie/en/primary/

Curriculum areas:
- English, Gaeilge, Mathematics
- Social, Environmental and Scientific Education (SESE)
- Social, Personal and Health Education (SPHE)
- Arts Education (Music, Visual Arts, Drama)
- Physical Education
- Religious Education

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

NATION = "ie"
STAGE = "primary"
LANGUAGE = "english"
PRIMARY_URL = "https://ncca.ie/en/primary/"

# 7 primary curriculum areas
CURRICULUM_AREAS = (
    "english", "gaeilge", "mathematics", "sese", "sphe",
    "arts-education", "physical-education", "religious-education",
)

SAMPLING_RATE = 1.0
CHUNK_SIZE_TOKENS = 1024
OVERLAP_TOKENS = 128


def is_plan1_active() -> bool:
    return True
