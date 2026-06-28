"""Ireland Junior Cycle — English (Plan 1 ACTIVE).

Stage: Junior Cycle (ages 12–15, 1st–3rd Year). Authority: NCCA.
Primary URL: https://ncca.ie/en/junior-cycle/

The 2014 Framework for Junior Cycle introduced:
- New subject specifications (English, Irish, Maths, Science, etc.)
- Ongoing reporting (instead of formal state exams at Junior Cycle)
- Wellbeing programme (400 hours)
- Short courses (CSPE, SPHE short course)

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

NATION = "ie"
STAGE = "junior_cycle"
LANGUAGE = "english"
PRIMARY_URL = "https://ncca.ie/en/junior-cycle/"

SUBJECTS = (
    "english", "irish", "mathematics", "history", "geography", "science",
    "french", "german", "spanish", "italian", "classical-studies",
    "music", "visual-art", "home-economics", "wood-technology",
    "engineering", "graphics", "technology", "business-studies",
    "civic-social-political-education", "social-personal-health-education",
    "physical-education", "religious-education", "wellbeing",
)

SAMPLING_RATE = 1.0
CHUNK_SIZE_TOKENS = 1024
OVERLAP_TOKENS = 128


def is_plan1_active() -> bool:
    return True
