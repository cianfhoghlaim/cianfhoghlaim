"""
Tertiary DLT source — CAO courses, NUI/HEI matriculation, QQI FET awards,
Apprenticeships. Sources from CAO.ie + 8+ NUI/IoT/HEI sites.

Honors USE_LOCAL_SCRAPES=true to read from /stedding/ingest_queue/tertiary/
cache. Live scraping uses Skyvern/Stagehand for the JS-heavy CAO dropdowns.
"""
from __future__ import annotations

import os
from pathlib import Path

import dlt


TERTIARY_CACHE_DIR = Path(os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")) / "tertiary"


@dlt.resource(name="cao_courses", write_disposition="merge", primary_key=["course_code", "year"])
def cao_courses():
    """CAO course listings, per year.

    Real extraction fires b.ExtractCAOCourseList against the
    baml_subjects/baml_context/tertiary.baml system prompt.
    """
    if not TERTIARY_CACHE_DIR.exists():
        return
    courses = TERTIARY_CACHE_DIR / "cao_courses"
    if courses.exists():
        for json_file in sorted(courses.glob("**/*.json")):
            import json as _json
            for course in _json.loads(json_file.read_text()):
                yield course


@dlt.resource(name="matriculation_rules", write_disposition="merge", primary_key=["institution", "subject", "minimum_grade"])
def matriculation_rules():
    """NUI/HEI matriculation rules, per institution."""
    if not TERTIARY_CACHE_DIR.exists():
        return
    rules = TERTIARY_CACHE_DIR / "matriculation"
    if rules.exists():
        for json_file in sorted(rules.glob("**/*.json")):
            import json as _json
            for rule in _json.loads(json_file.read_text()):
                yield rule


@dlt.resource(name="qqi_fet_awards", write_disposition="merge", primary_key=["award_code"])
def qqi_fet_awards():
    """QQI FET (Further Education & Training) awards."""
    if not TERTIARY_CACHE_DIR.exists():
        return
    qqi = TERTIARY_CACHE_DIR / "qqi"
    if qqi.exists():
        for json_file in sorted(qqi.glob("**/*.json")):
            import json as _json
            for award in _json.loads(json_file.read_text()):
                yield award


@dlt.resource(name="apprenticeships", write_disposition="merge", primary_key=["programme_code"])
def apprenticeships():
    """Apprenticeship programme listings."""
    if not TERTIARY_CACHE_DIR.exists():
        return
    apps = TERTIARY_CACHE_DIR / "apprenticeships"
    if apps.exists():
        for json_file in sorted(apps.glob("**/*.json")):
            import json as _json
            for prog in _json.loads(json_file.read_text()):
                yield prog


@dlt.resource(name="application_timelines", write_disposition="merge", primary_key=["course_code", "year"])
def application_timelines():
    """CAO application timeline (open/close/rounds) per (course_code, year)."""
    if not TERTIARY_CACHE_DIR.exists():
        return
    tl = TERTIARY_CACHE_DIR / "timelines"
    if tl.exists():
        for json_file in sorted(tl.glob("**/*.json")):
            import json as _json
            for entry in _json.loads(json_file.read_text()):
                yield entry


@dlt.source(name="tertiary_courses")
def tertiary_courses():
    """Tertiary DLT source — CAO + matriculation + QQI + Apprenticeships + timeline."""
    yield cao_courses
    yield matriculation_rules
    yield qqi_fet_awards
    yield apprenticeships
    yield application_timelines
