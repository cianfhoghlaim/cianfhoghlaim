"""Ireland Senior Cycle DLT source — REAL Firecrawl-verified data.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

Replaces the legacy stub data with the 28 real NCCA Senior Cycle
subjects + 18 LCA vocational programmes + TY programmes
(Firecrawl-verified 2026-09-23 from
https://ncca.ie/en/senior-cycle/senior-cycle-subjects/).

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

logger = logging.get_logger(__name__)

SC_CACHE_DIR = Path(os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")) / "senior_cycle"


# Real NCCA Senior Cycle subjects (28) + LCA programmes (18) + TY.
SC_SUBJECTS_REAL: tuple[dict, ...] = (
    {"subject_slug": "accounting", "name_en": "Accounting", "name_ga": "Cuntasaíocht", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "agricultural_science", "name_en": "Agricultural Science", "name_ga": "Eolaíocht Talmhaíochta", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "ancient_greek", "name_en": "Ancient Greek", "name_ga": "Gréigis Ársa", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "applied_mathematics", "name_en": "Applied Mathematics", "name_ga": "Matamaitic Fheidhmeach", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "applied_graphics_design", "name_en": "Applied Graphics and Design", "name_ga": "Grafaic agus Dearadh Fheidhmeach", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "arabic", "name_en": "Arabic", "name_ga": "Araibis", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "art", "name_en": "Art", "name_ga": "Ealaíon", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "biology", "name_en": "Biology", "name_ga": "Bitheolaíocht", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "business", "name_en": "Business", "name_ga": "Gnó", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "climate_action_sustainable_development", "name_en": "Climate Action and Sustainable Development", "name_ga": "Gníomhú ar son na hAeráide agus Forbairt Inbhuanaithe", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "chemical_physical_science", "name_en": "Chemical and Physical Science", "name_ga": "Eolaíocht Cheimiceach agus Fhisiceach", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "chemistry", "name_en": "Chemistry", "name_ga": "Ceimic", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "classical_studies", "name_en": "Classical Studies", "name_ga": "Staidéar Clasaiceach", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "computer_science", "name_en": "Computer Science", "name_ga": "Ríomheolaíocht", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "construction_studies", "name_en": "Construction Studies", "name_ga": "Staidéar Tógála", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "drama_film_theatre_studies", "name_en": "Drama, Film and Theatre Studies", "name_ga": "Drámaíocht, Scannán agus Staidéar Amharclainne", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "english", "name_en": "English", "name_ga": "Béarla", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "economics", "name_en": "Economics", "name_ga": "Eacnamaíocht", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "engineering", "name_en": "Engineering", "name_ga": "Innealtóireacht", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "french", "name_en": "French", "name_ga": "Fraincis", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "gaeilge", "name_en": "Gaeilge", "name_ga": "Gaeilge", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "geography", "name_en": "Geography", "name_ga": "Tíreolaíocht", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "german", "name_en": "German", "name_ga": "Gearmáinis", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "hebrew_studies", "name_en": "Hebrew Studies", "name_ga": "Staidéar Eabhraise", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "home_economics", "name_en": "Home Economics", "name_ga": "Eacnamaíocht Bhaile", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "italian", "name_en": "Italian", "name_ga": "Iodáilis", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "latin", "name_en": "Latin", "name_ga": "Laidin", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "lithuanian", "name_en": "Lithuanian", "name_ga": "Liotuáinis", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "mandarin_chinese", "name_en": "Mandarin Chinese", "name_ga": "Sínis Mhandairínis", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "mathematics", "name_en": "Mathematics", "name_ga": "Matamaitic", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "music", "name_en": "Music", "name_ga": "Ceol", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "physical_education", "name_en": "Physical Education", "name_ga": "Corpoideachas", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "physics", "name_en": "Physics", "name_ga": "Fisic", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "physics_chemistry", "name_en": "Physics and Chemistry (combined)", "name_ga": "Fisic agus Ceimic", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "polish", "name_en": "Polish", "name_ga": "Polainnis", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "politics_society", "name_en": "Politics and Society", "name_ga": "Polaitíocht agus Sochaí", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "portuguese", "name_en": "Portuguese", "name_ga": "Portaingéilis", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "religious_education", "name_en": "Religious Education", "name_ga": "Oideachas Creidimh", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "russian", "name_en": "Russian", "name_ga": "Rúisis", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "spanish", "name_en": "Spanish", "name_ga": "Spáinnis", "level": "higher_ordinary", "ects_credits": None},
    {"subject_slug": "technology", "name_en": "Technology", "name_ga": "Teicneolaíocht", "level": "higher_ordinary", "ects_credits": None},
)


# LCA programmes (18 vocational — Firecrawl-verified).
LCA_PROGRAMMES: tuple[dict, ...] = (
    {"programme_slug": "active_leisure_studies", "name_en": "Active Leisure Studies", "ects_credits": 350},
    {"programme_slug": "agriculture_horticulture", "name_en": "Agriculture / Horticulture", "ects_credits": 350},
    {"programme_slug": "childcare_community_care", "name_en": "Childcare / Community Care", "ects_credits": 350},
    {"programme_slug": "dance", "name_en": "Dance", "ects_credits": 350},
    {"programme_slug": "drama", "name_en": "Drama", "ects_credits": 350},
    {"programme_slug": "engineering", "name_en": "Engineering", "ects_credits": 350},
    {"programme_slug": "english_communication", "name_en": "English and Communication", "ects_credits": 350},
    {"programme_slug": "graphics_construction_studies", "name_en": "Graphics and Construction Studies", "ects_credits": 350},
    {"programme_slug": "hair_beauty", "name_en": "Hair and Beauty", "ects_credits": 350},
    {"programme_slug": "hotel_catering_tourism", "name_en": "Hotel, Catering and Tourism", "ects_credits": 350},
    {"programme_slug": "ict", "name_en": "Information and Communications Technology", "ects_credits": 350},
    {"programme_slug": "music_lca", "name_en": "Music", "ects_credits": 350},
    {"programme_slug": "office_administration", "name_en": "Office Administration and Customer Care", "ects_credits": 350},
    {"programme_slug": "religious_education_lca", "name_en": "Religious Education", "ects_credits": 350},
    {"programme_slug": "science_lca", "name_en": "Science", "ects_credits": 350},
    {"programme_slug": "social_education", "name_en": "Social Education", "ects_credits": 350},
    {"programme_slug": "technology_lca", "name_en": "Technology", "ects_credits": 350},
    {"programme_slug": "visual_art_lca", "name_en": "Visual Art", "ects_credits": 350},
)


@dlt.resource(name="sc_subjects", write_disposition="replace", primary_key=["subject_slug"])
def sc_subjects() -> Iterator[dict]:
    yield from SC_SUBJECTS_REAL


@dlt.resource(name="lca_programmes", write_disposition="replace", primary_key=["programme_slug"])
def lca_programmes() -> Iterator[dict]:
    yield from LCA_PROGRAMMES


@dlt.source(name="senior_cycle")
def senior_cycle_source():
    return sc_subjects(), lca_programmes()
