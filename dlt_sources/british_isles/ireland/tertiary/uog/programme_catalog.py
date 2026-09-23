"""cianfhoghlaim — DLT source for the University of Galway Public Course Catalog.

Per openspec/changes/kcg-university-of-galway-doc-processing-v1/,
Case Study: Course Catalog.

The UoG public course catalog is the canonical listing of all
undergraduate + postgraduate courses. Published at:

    https://www.universityofgalway.ie/courses/

This DLT source scrapes the catalog and emits one
`CourseOutline` row per (course_code, academic_year).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import os
from collections.abc import Iterator

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


class ProgrammeCatalogPipeline(TertiaryPipelineBase):
    """DLT pipeline for the UoG Public Course Catalog."""

    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="course_catalog",
        surface_name_english="Course Catalog",
        surface_name_irish="Catalog Cúrsaí",
        source_url="https://www.universityofgalway.ie/courses/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="course_code",
    )

    @dlt.resource(write_disposition="replace", primary_key="course_code")
    def courses(self) -> Iterator[dict]:
        """Yield one CourseOutline per (course_code, academic_year)."""
        self.logger.info("course_catalog_sync_start", surface_id=self.surface_id)

        if os.environ.get("USE_LOCAL_SCRAPES", "").lower() == "true":
            yield from self._yield_local_scrape_rows()
        else:
            yield from self._yield_live_scrape_rows()

        self.logger.info("course_catalog_sync_complete", surface_id=self.surface_id)

    def _yield_live_scrape_rows(self) -> Iterator[dict]:
        """Live HTTP scrape (httpx + BS4) — stub with canonical samples."""
        yield from _CANONICAL_SAMPLE_COURSES

    def _yield_local_scrape_rows(self) -> Iterator[dict]:
        """Read from `stedding/ingest_queue/uog/course_catalog/*.json`."""
        import json
        from pathlib import Path

        local_path = Path(self.local_scrape_path())
        if not local_path.exists():
            self.logger.info("local_scrape_path_empty", path=str(local_path))
            return

        for json_file in sorted(local_path.glob("*.json")):
            yield from json.loads(json_file.read_text(encoding="utf-8"))

    def build_pipeline_resource(self) -> Iterator[dict]:
        return self.courses()


# Canonical sample courses (stub for testing — replace with live scrape)
_CANONICAL_SAMPLE_COURSES: list[dict] = [
    {
        "course_code": "CS203",
        "course_title_english": "Data Structures",
        "course_title_irish": "Struchtúir Sonraí",
        "level": "undergraduate",
        "year_of_study": 2,
        "semester": "S1",
        "ects_credits": 5,
        "faculty": "College of Science + Engineering",
        "school": "School of Computer Science",
        "campus": "Galway (main campus)",
        "mode": "full_time",
        "delivery_language": "en",
        "academic_year": "2025/26",
        "lecturer_lead": "Dr M. Hayes",
        "description_short": "Lists, stacks, queues, trees, graphs; complexity analysis.",
        "learning_outcomes_count": 6,
        "assessment_methods": ("exam", "continuous_assessment", "practical"),
        "prerequisite_course_codes": ("CS102",),
        "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-computer-science.html",
        "source_url": "https://www.universityofgalway.ie/courses/",
    },
    {
        "course_code": "MA101",
        "course_title_english": "Calculus I",
        "course_title_irish": "Calcalas I",
        "level": "undergraduate",
        "year_of_study": 1,
        "semester": "S1",
        "ects_credits": 5,
        "faculty": "College of Science + Engineering",
        "school": "School of Mathematics, Statistics + Applied Mathematics",
        "campus": "Galway (main campus)",
        "mode": "full_time",
        "delivery_language": "en",
        "academic_year": "2025/26",
        "lecturer_lead": "Dr A. Ní Mhurchú",
        "description_short": "Limits, derivatives, basic integration; foundations of calculus.",
        "learning_outcomes_count": 5,
        "assessment_methods": ("exam", "continuous_assessment"),
        "prerequisite_course_codes": (),
        "syllabus_url": "https://www.universityofgalway.ie/programmes/bsc-mathematical-science.html",
        "source_url": "https://www.universityofgalway.ie/courses/",
    },
    {
        "course_code": "ED116",
        "course_title_english": "History of Irish Education",
        "course_title_irish": "Stair Oideachais na hÉireann",
        "level": "undergraduate",
        "year_of_study": 1,
        "semester": "S2",
        "ects_credits": 5,
        "faculty": "College of Arts",
        "school": "School of Education",
        "campus": "Galway (main campus)",
        "mode": "full_time",
        "delivery_language": "en",
        "academic_year": "2025/26",
        "lecturer_lead": "Dr C. Ó Briain",
        "description_short": "History of Irish education from hedge schools to modern university system.",
        "learning_outcomes_count": 4,
        "assessment_methods": ("essay", "exam"),
        "prerequisite_course_codes": (),
        "syllabus_url": "https://www.universityofgalway.ie/programmes/ba-education.html",
        "source_url": "https://www.universityofgalway.ie/courses/",
    },
    {
        "course_code": "GA101",
        "course_title_english": "Ceart na Gaeilge 1",
        "course_title_irish": "Ceart na Gaeilge 1",
        "level": "undergraduate",
        "year_of_study": 1,
        "semester": "S1 + S2",
        "ects_credits": 10,
        "faculty": "College of Arts",
        "school": "Acadamh na hOllscolaíochta Gaeilge",
        "campus": "Gaeltacht na Gaillimhe",
        "mode": "full_time",
        "delivery_language": "ga",
        "academic_year": "2025/26",
        "lecturer_lead": "An Dr S. Ní Laoghaire",
        "description_short": "Standard Irish grammar (noun declensions, verb tenses, syntax); year-long.",
        "learning_outcomes_count": 5,
        "assessment_methods": ("continuous_assessment", "exam", "oral"),
        "prerequisite_course_codes": (),
        "syllabus_url": "https://www.universityofgalway.ie/programmes/gaeilge.html",
        "source_url": "https://www.universityofgalway.ie/courses/",
    },
]


programme_catalog_pipeline = ProgrammeCatalogPipeline()
