"""Ireland Leaving Certificate — English (Plan 1 ACTIVE).

The Leaving Certificate (Ardteistiméireacht) is the terminal examination of
the Senior Cycle. Authority: State Examinations Commission (SEC).
Primary URL: https://www.examinations.ie/

This source covers:
- All SEC syllabi for Leaving Certificate subjects
- Past exam papers (1967–present)
- Marking schemes (chief examiner reports)
- SEC candidate statistics
- LC Applied, LC Vocational Programme (LCVP), LC Links Programme (LCLP)

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

NATION = "ie"
STAGE = "leaving_cert"
LANGUAGE = "english"
PRIMARY_URL = "https://www.examinations.ie/"

LC_PROGRAMMES = ("leaving-certificate", "leaving-certificate-applied",
                "leaving-certificate-vocational-programme",
                "leaving-certificate-links-programme")

# All Leaving Certificate subjects (cross-reference with senior_cycle/english.py)
LC_SUBJECTS = (
    "english", "gaeilge", "mathematics", "biology", "chemistry", "physics",
    "agricultural-science", "applied-mathematics", "physics-and-chemistry",
    "computer-science", "design-communication-graphics", "engineering",
    "technology", "construction-studies", "manufacturing-processes",
    "design-and-manufacture", "geography", "history", "economics",
    "business", "accounting", "music", "visual-art", "drama",
    "film-and-screen-media", "french", "german", "spanish", "italian",
    "japanese", "russian", "arabic", "polish", "portuguese", "latvian",
    "lithuanian", "romanian", "home-economics", "religious-education",
    "physical-education", "politics-and-society",
    "media-and-communication",
)

# SEC papers span 1967 → present; ~10K+ PDF documents.
SAMPLING_RATE = 0.5  # Half-sample to start; full sample in Plan 2.
CHUNK_SIZE_TOKENS = 2048  # SEC exam papers are dense; larger chunks.
OVERLAP_TOKENS = 256


def is_plan1_active() -> bool:
    return True
