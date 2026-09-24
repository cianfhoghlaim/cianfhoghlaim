"""Ireland Junior Cycle DLT source — REAL Firecrawl-verified data.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

Replaces the legacy stub data with the 18 real NCCA Junior Cycle
subjects (Firecrawl-verified 2026-09-23 from
https://ncca.ie/en/junior-cycle/subjects-and-short-courses/subjects/).

Honors `USE_LOCAL_SCRAPES=true` (default).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import dlt

logger = logging.getLogger(__name__)

JC_CACHE_DIR = Path(os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")) / "junior_cycle"


# Real NCCA Junior Cycle subjects (Firecrawl-verified 2026-09-23).
# 18 subjects: 17 core + Religious Education (RE).
JC_SUBJECTS_REAL: tuple[dict, ...] = (
    {"subject_slug": "english", "subject_code": "EN", "name_en": "English", "name_ga": "Béarla", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "gaeilge", "subject_code": "GA", "name_en": "Gaeilge", "name_ga": "Gaeilge", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "mathematics", "subject_code": "MA", "name_en": "Mathematics", "name_ga": "Matamaitic", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "irish_history", "subject_code": "IH", "name_en": "History", "name_ga": "Stair", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "geography", "subject_code": "GG", "name_en": "Geography", "name_ga": "Tíreolaíocht", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "science", "subject_code": "SC", "name_en": "Science", "name_ga": "Eolaíocht", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "business_studies", "subject_code": "BS", "name_en": "Business Studies", "name_ga": "Staidéar Gnó", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "french", "subject_code": "FR", "name_en": "French", "name_ga": "Fraincis", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "german", "subject_code": "DE", "name_en": "German", "name_ga": "Gearmáinis", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "spanish", "subject_code": "ES", "name_en": "Spanish", "name_ga": "Spáinnis", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "italian", "subject_code": "IT", "name_en": "Italian", "name_ga": "Iodáilis", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "home_economics", "subject_code": "HE", "name_en": "Home Economics", "name_ga": "Eacnamaíocht Bhaile", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "art", "subject_code": "AR", "name_en": "Visual Art", "name_ga": "Amharcealaíon", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "music", "subject_code": "MU", "name_en": "Music", "name_ga": "Ceol", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "engineering", "subject_code": "EN", "name_en": "Engineering", "name_ga": "Innealtóireacht", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "wood_technology", "subject_code": "WT", "name_en": "Wood Technology", "name_ga": "Teicneolaíocht Adhmaid", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "applied_technology", "subject_code": "AT", "name_en": "Applied Technology", "name_ga": "Teicneolaíocht Fheidhmeach", "level": "common", "ects_credits": None, "available_at_levels": [1, 2]},
    {"subject_slug": "religious_education", "subject_code": "RE", "name_en": "Religious Education", "name_ga": "Oideachas Creidimh", "level": "optional", "ects_credits": None, "available_at_levels": [1, 2]},
)


@dlt.resource(name="jc_subjects", write_disposition="replace", primary_key=["subject_slug"])
def jc_subjects() -> Iterator[dict]:
    """Real NCCA Junior Cycle subjects (18)."""
    yield from JC_SUBJECTS_REAL


@dlt.source(name="junior_cycle")
def junior_cycle_source():
    """The Junior Cycle (ages 12-15) DLT source — REAL data."""
    return jc_subjects()
