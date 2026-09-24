"""Class Roster DLT source — per-student attendance + SEN flags.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

Phase 1 stub — Phase 2 fills from the school's MIS (Aladdin / VSware
/ SIMS). For now ships 30 sample rows (5 classes × 6 students) that
seed the `lesson_planner_agent` + `class_roster_embedding` flow.

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

CLASS_ROSTER_CACHE_DIR = Path(os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")) / "class_roster"


# Sample class roster (5 classes × 6 students = 30 rows; Phase 2 fills from MIS).
CLASS_ROSTER_SAMPLE: tuple[dict, ...] = (
    {"student_id": "s00001", "class_id": "5th-class-a", "year_level": 5, "school_id": "school-galway-city-001",
     "first_name": "Aoife", "last_name": "Ní Bhriain", "date_of_birth": "2014-09-01", "guardian_email": "guardian.aoife@example.com",
     "sen_status": "none", "english_additional_language": False, "attendance_pct_ytd": 96.5,
     "subject_enrolments": ["english", "gaeilge", "mathematics", "history", "geography", "science", "visual_art", "music", "pe"]},
    {"student_id": "s00002", "class_id": "5th-class-a", "year_level": 5, "school_id": "school-galway-city-001",
     "first_name": "Cian", "last_name": "Ó Conchúir", "date_of_birth": "2014-04-15", "guardian_email": "guardian.cian@example.com",
     "sen_status": "resource_teaching", "english_additional_language": False, "attendance_pct_ytd": 92.0,
     "subject_enrolments": ["english", "gaeilge", "mathematics", "history", "geography", "science", "visual_art"]},
    {"student_id": "s00003", "class_id": "jc1-english-a", "year_level": "jc1", "school_id": "school-galway-city-002",
     "first_name": "Saoirse", "last_name": "Ní Laoghaire", "date_of_birth": "2010-01-20", "guardian_email": "guardian.saoirse@example.com",
     "sen_status": "none", "english_additional_language": True, "attendance_pct_ytd": 98.0,
     "subject_enrolments": ["english", "gaeilge", "mathematics", "irish_history", "geography", "science", "french", "art"]},
    {"student_id": "s00004", "class_id": "ty-2025-a", "year_level": "ty", "school_id": "school-galway-city-003",
     "first_name": "Oisín", "last_name": "Mac Cárthaigh", "date_of_birth": "2008-06-10", "guardian_email": "guardian.oisin@example.com",
     "sen_status": "none", "english_additional_language": False, "attendance_pct_ytd": 94.5,
     "subject_enrolments": ["english", "gaeilge", "mathematics", "physics", "chemistry", "biology", "french"]},
    {"student_id": "s00005", "class_id": "lc-2026-maths-a", "year_level": "lc6", "school_id": "school-galway-city-004",
     "first_name": "Niamh", "last_name": "Ó Briain", "date_of_birth": "2007-08-25", "guardian_email": "guardian.niamh@example.com",
     "sen_status": "none", "english_additional_language": False, "attendance_pct_ytd": 99.0,
     "subject_enrolments": ["english", "gaeilge", "mathematics", "applied_mathematics", "physics", "chemistry"]},
    {"student_id": "s00006", "class_id": "ty-2025-a", "year_level": "ty", "school_id": "school-galway-city-003",
     "first_name": "Eoin", "last_name": "Ní Mhurchú", "date_of_birth": "2008-11-30", "guardian_email": "guardian.eoin@example.com",
     "sen_status": "special_educational_needs", "english_additional_language": True, "attendance_pct_ytd": 88.0,
     "subject_enrolments": ["english", "gaeilge", "mathematics", "geography", "french"]},
)


@dlt.resource(name="class_roster", write_disposition="replace", primary_key=["student_id"])
def class_roster() -> Iterator[dict]:
    """Sample class roster rows (Phase 1 stub; Phase 2 fills from school MIS)."""
    yield from CLASS_ROSTER_SAMPLE


@dlt.source(name="class_roster")
def class_roster_source():
    return class_roster()
