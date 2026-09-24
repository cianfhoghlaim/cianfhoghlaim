"""Teacher Workload DLT source — teacher timetable + class assignments + planning periods.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

Phase 1 stub — Phase 2 fills from the school's MIS timetable export.

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

TEACHER_WORKLOAD_CACHE_DIR = Path(os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")) / "teacher_workload"


# Sample teacher workload rows (Phase 1 stub).
TEACHER_WORKLOAD_SAMPLE: tuple[dict, ...] = (
    {"teacher_id": "t00001", "name_en": "Ms. M. Hayes", "name_ga": "Ms. M. Ní Laoghaire",
     "school_id": "school-galway-city-001", "email": "m.hayes@school.ie",
     "teaching_subjects": ["primary_mathematics", "primary_sese_science"],
     "class_assignments": ["4th-class-a", "4th-class-b", "5th-class-a"],
     "weekly_periods_taught": 24, "weekly_planning_periods": 4,
     "weekly_cpd_periods": 2, "sen_tutorials": 3,
     "effective_from": "2025-09-01", "scraped_at": "2026-09-23T00:00:00Z"},
    {"teacher_id": "t00002", "name_en": "Mr. P. Walsh", "name_ga": "Mr. P. de Bhál",
     "school_id": "school-galway-city-002", "email": "p.walsh@school.ie",
     "teaching_subjects": ["computer_science", "mathematics", "applied_mathematics"],
     "class_assignments": ["jc1-cs-a", "lc-cs-2026-a", "lc-am-2026-a"],
     "weekly_periods_taught": 22, "weekly_planning_periods": 4,
     "weekly_cpd_periods": 2, "sen_tutorials": 2,
     "effective_from": "2025-09-01", "scraped_at": "2026-09-23T00:00:00Z"},
    {"teacher_id": "t00003", "name_en": "Mr. C. Ó Briain", "name_ga": "Mr. C. Ó Briain",
     "school_id": "school-galway-city-001", "email": "c.obriain@school.ie",
     "teaching_subjects": ["primary_gaeilge", "primary_history", "primary_geography"],
     "class_assignments": ["3rd-class-a", "4th-class-a", "5th-class-b"],
     "weekly_periods_taught": 24, "weekly_planning_periods": 4,
     "weekly_cpd_periods": 2, "sen_tutorials": 2,
     "effective_from": "2025-09-01", "scraped_at": "2026-09-23T00:00:00Z"},
)


@dlt.resource(name="teacher_workload", write_disposition="replace", primary_key=["teacher_id"])
def teacher_workload() -> Iterator[dict]:
    yield from TEACHER_WORKLOAD_SAMPLE


@dlt.source(name="teacher_workload")
def teacher_workload_source():
    return teacher_workload()
