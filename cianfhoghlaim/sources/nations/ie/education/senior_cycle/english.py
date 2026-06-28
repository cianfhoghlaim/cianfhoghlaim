"""Ireland Senior Cycle — English (Plan 1 ACTIVE).

Stage: Senior Cycle (ages 15–18, 4th–6th Year). Authority: NCCA.
Primary URL: https://ncca.ie/en/senior-cycle/

The new Senior Cycle framework (introduced 2024–2026) restructured:
- 5 reduced mandatory subjects (English, Irish, Maths, new "Climate Action
  & Sustainability", new "Wellbeing & Life Skills")
- Optional subject streams (Sciences, Business, Humanities, Arts)
- Senior Cycle PE exemption for Leaving Cert students
- Updated assessment (mix of written, project, oral, practical)

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

NATION = "ie"
STAGE = "senior_cycle"
LANGUAGE = "english"
PRIMARY_URL = "https://ncca.ie/en/senior-cycle/"

# Updated Senior Cycle subjects (post-2024 framework)
MANDATORY_SUBJECTS = (
    "english", "gaeilge", "mathematics",
    "climate-action-and-sustainability", "wellbeing-and-life-skills",
)
OPTIONAL_SUBJECTS = (
    "biology", "chemistry", "physics", "agricultural-science",
    "applied-maths", "physics-and-chemistry", "computer-science",
    "design-communication-graphics", "engineering", "technology",
    "construction-studies", "manufacturing-processes", "design-and-manufacture",
    "geography", "history", "economics", "business", "accounting",
    "music", "visual-art", "drama", "film-and-screen-media",
    "french", "german", "spanish", "italian", "japanese", "russian",
    "arabic", "polish", "portuguese", "latvian", "lithuanian", "romanian",
    "home-economics", "religious-education", "physical-education",
    "politics-and-society", "media-and-communication",
)

SAMPLING_RATE = 1.0
CHUNK_SIZE_TOKENS = 1024
OVERLAP_TOKENS = 128


def is_plan1_active() -> bool:
    return True
