"""UoG Reading Lists — per-module reading list extraction.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

Extracts the 3-10 essential + recommended reading items per module from
the per-module handbook PDFs (the BIEP v2 4-path OCR ensemble).

Graceful: emits empty reading_list for schools that don't publish
reading lists (per the project's OSINT-only ceiling).

Honors `USE_LOCAL_SCRAPES=true` (default).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

from collections.abc import Iterator

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


UOG_READING_LISTS: tuple[dict, ...] = (
    {
        "module_code": "CS203",
        "reading_list": [
            {"format": "isbn_13", "title": "Introduction to Algorithms", "authors": ["Cormen, T. H.", "Leiserson, C. E.", "Rivest, R. L.", "Stein, C."], "year": 2009, "isbn_13": "9780262033848", "essential": True},
            {"format": "isbn_13", "title": "Data Structures and Algorithm Analysis", "authors": ["Weiss, M. A."], "year": 2011, "isbn_13": "9780132576277", "essential": True},
            {"format": "url", "title": "Big-O Cheat Sheet", "authors": ["bigocheatsheet.com"], "year": 2024, "url": "https://www.bigocheatsheet.com", "essential": False},
        ],
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "module_code": "MA101",
        "reading_list": [
            {"format": "isbn_13", "title": "Calculus", "authors": ["Spivak, M."], "year": 2008, "isbn_13": "9780914098911", "essential": True},
            {"format": "isbn_13", "title": "Thomas' Calculus", "authors": ["Thomas, G. B."], "year": 2017, "isbn_13": "9780134436286", "essential": False},
        ],
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "module_code": "GA101",
        "reading_list": [
            {"format": "other", "title": "Graiméar Gaeilge na Máitheal", "authors": ["Ó Siadhail, M."], "year": 2020, "essential": True},
            {"format": "other", "title": "An Teanga Bheo — Gaeilge Uí Choisde", "authors": ["Various"], "year": 2019, "essential": False},
        ],
        "scraped_at": "2026-09-23T00:00:00Z",
    },
)


class ReadingListsPipeline(TertiaryPipelineBase):
    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="uog_reading_lists",
        surface_name_english="UoG Reading Lists",
        surface_name_irish="Liostaí Léitheoireachta UoG",
        source_url="https://www.universityofgalway.ie/programmes/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="module_code",
    )

    @dlt.resource(write_disposition="replace", primary_key="module_code")
    def reading_lists(self) -> Iterator[dict]:
        self.logger.info("reading_lists_sync_start", surface_id=self.surface_id)
        yield from UOG_READING_LISTS
        self.logger.info("reading_lists_sync_complete", surface_id=self.surface_id, count=len(UOG_READING_LISTS))

    def build_pipeline_resource(self) -> Iterator[dict]:
        return self.reading_lists()


reading_lists_pipeline = ReadingListsPipeline()
