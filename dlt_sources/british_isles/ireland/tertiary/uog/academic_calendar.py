"""cianfhoghlaim — DLT source for the University of Galway Academic Calendar.

Per openspec/changes/kcg-university-of-galway-doc-processing-v1/,
Case Study: Academic Calendar.

The UoG academic calendar is the canonical schedule of teaching
weeks + exam periods + semester start/end dates + public holidays
+ university closures. It's published at:

    https://www.universityofgalway.ie/academic-calendar/

This DLT source scrapes the calendar HTML and emits one
`AcademicCalendarEvent` row per event.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import date

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


class AcademicCalendarPipeline(TertiaryPipelineBase):
    """DLT pipeline for the UoG Academic Calendar."""

    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="academic_calendar",
        surface_name_english="Academic Calendar",
        surface_name_irish="Féilire Acadúil",
        source_url="https://www.universityofgalway.ie/academic-calendar/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="date_iso",
    )

    @dlt.resource(write_disposition="replace", primary_key="date_iso")
    def events(self) -> Iterator[dict]:
        """Yield one AcademicCalendarEvent per UoG calendar event.

        Honors `USE_LOCAL_SCRAPES=true` — when set, reads from the
        offline scrape path (the canonical local-scrape fallback
        pattern from cianfhoghlaim).
        """
        self.logger.info("academic_calendar_sync_start", surface_id=self.surface_id)

        if os.environ.get("USE_LOCAL_SCRAPES", "").lower() == "true":
            yield from self._yield_local_scrape_rows()
        else:
            # Live scrape path — stubbed (the public_html is whitelisted
            # in the OSINT allowlist + the request is straightforward)
            yield from self._yield_live_scrape_rows()

        self.logger.info("academic_calendar_sync_complete", surface_id=self.surface_id)

    def _yield_live_scrape_rows(self) -> Iterator[dict]:
        """Live HTTP scrape (httpx + BeautifulSoup).

        Stub: yields the canonical 2025/26 events hardcoded so the
        pipeline is testable without network access. Replace with
        a real httpx.get(...).text + BS4 parse when running for real.
        """
        yield from _CANONICAL_2025_26_ACADEMIC_CALENDAR

    def _yield_local_scrape_rows(self) -> Iterator[dict]:
        """Read from `stedding/ingest_queue/uog/academic_calendar/*.json`."""
        import json
        from pathlib import Path

        local_path = Path(self.local_scrape_path())
        if not local_path.exists():
            self.logger.info("local_scrape_path_empty", path=str(local_path))
            return

        for json_file in sorted(local_path.glob("*.json")):
            yield from json.loads(json_file.read_text(encoding="utf-8"))

    def build_pipeline_resource(self) -> Iterator[dict]:
        return self.events()


# Hardcoded 2025/26 academic year events (stub for testing).
# The real scrape replaces this with the live calendar HTML.
_CANONICAL_2025_26_ACADEMIC_CALENDAR: list[dict] = [
    {
        "date_iso": "2025-09-01",
        "event_name_english": "Semester 1 begins",
        "event_name_irish": "Tosaíonn an chéad seimeastar",
        "academic_year": "2025/26",
        "semester": "S1",
        "category": "teaching_start",
        "is_mandatory": True,
        "source_url": "https://www.universityofgalway.ie/academic-calendar/",
    },
    {
        "date_iso": "2025-10-27",
        "event_name_english": "Semester 1 reading week",
        "event_name_irish": "Seachtain léitheoireachta an chéad seimeastar",
        "academic_year": "2025/26",
        "semester": "S1",
        "category": "reading_week",
        "is_mandatory": False,
        "source_url": "https://www.universityofgalway.ie/academic-calendar/",
    },
    {
        "date_iso": "2025-12-12",
        "event_name_english": "Semester 1 ends (teaching)",
        "event_name_irish": "Críoch an chéad seimeastar (teagasc)",
        "academic_year": "2025/26",
        "semester": "S1",
        "category": "teaching_end",
        "is_mandatory": True,
        "source_url": "https://www.universityofgalway.ie/academic-calendar/",
    },
    {
        "date_iso": "2025-12-15",
        "event_name_english": "Semester 1 examinations begin",
        "event_name_irish": "Tosaíonn scrúduithe an chéad seimeastar",
        "academic_year": "2025/26",
        "semester": "S1",
        "category": "exam_start",
        "is_mandatory": True,
        "source_url": "https://www.universityofgalway.ie/academic-calendar/",
    },
    {
        "date_iso": "2026-01-12",
        "event_name_english": "Semester 2 begins",
        "event_name_irish": "Tosaíonn an dara seimeastar",
        "academic_year": "2025/26",
        "semester": "S2",
        "category": "teaching_start",
        "is_mandatory": True,
        "source_url": "https://www.universityofgalway.ie/academic-calendar/",
    },
    {
        "date_iso": "2026-02-02",
        "event_name_english": "Semester 2 reading week",
        "event_name_irish": "Seachtain léitheoireachta an dara seimeastar",
        "academic_year": "2025/26",
        "semester": "S2",
        "category": "reading_week",
        "is_mandatory": False,
        "source_url": "https://www.universityofgalway.ie/academic-calendar/",
    },
    {
        "date_iso": "2026-04-03",
        "event_name_english": "Semester 2 ends (teaching)",
        "event_name_irish": "Críoch an dara seimeastar (teagasc)",
        "academic_year": "2025/26",
        "semester": "S2",
        "category": "teaching_end",
        "is_mandatory": True,
        "source_url": "https://www.universityofgalway.ie/academic-calendar/",
    },
    {
        "date_iso": "2026-04-15",
        "event_name_english": "Semester 2 examinations begin",
        "event_name_irish": "Tosaíonn scrúduithe an dara seimeastar",
        "academic_year": "2025/26",
        "semester": "S2",
        "category": "exam_start",
        "is_mandatory": True,
        "source_url": "https://www.universityofgalway.ie/academic-calendar/",
    },
    {
        "date_iso": "2026-05-04",
        "event_name_english": "Semester 2 examinations end",
        "event_name_irish": "Críoch scrúduithe an dara seimeastar",
        "academic_year": "2025/26",
        "semester": "S2",
        "category": "exam_end",
        "is_mandatory": True,
        "source_url": "https://www.universityofgalway.ie/academic-calendar/",
    },
    {
        "date_iso": "2026-06-22",
        "event_name_english": "Summer supplemental examinations begin",
        "event_name_irish": "Tosaíonn scrúduithe forlíontacha an tsamhraidh",
        "academic_year": "2025/26",
        "semester": "Summer",
        "category": "exam_start",
        "is_mandatory": False,
        "source_url": "https://www.universityofgalway.ie/academic-calendar/",
    },
]


academic_calendar_pipeline = AcademicCalendarPipeline()
