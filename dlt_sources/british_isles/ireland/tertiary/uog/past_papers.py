"""UoG Past Papers — per-module past paper links from regexam.nuigalway.ie.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

The past papers for each module live at regexam.nuigalway.ie (the
authenticated M365-gated archive). This DLT source yields the
per-module past paper URL list once the per-user credential vault
has been unlocked (1-time manual M365 login via
`komodo run unlock-uo-portal --user <u>`).

Honors `USE_LOCAL_SCRAPES=true` (default).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

from collections.abc import Iterator

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


# Phase 1 stub — 5 sample past papers; Phase 2 fills from regexam.nuigalway.ie
# live scrape (requires per-user credential vault)
UOG_PAST_PAPERS: tuple[dict, ...] = (
    {
        "paper_id": "CS203-2024-P1",
        "module_code": "CS203",
        "year": 2024,
        "paper_number": 1,
        "pdf_url": "https://regexam.nuigalway.ie/regexam/papers/CS203-2024-P1.pdf",
        "has_marking_scheme": True,
        "marking_scheme_url": "https://regexam.nuigalway.ie/regexam/papers/CS203-2024-P1-MS.pdf",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "paper_id": "CS203-2023-P1",
        "module_code": "CS203",
        "year": 2023,
        "paper_number": 1,
        "pdf_url": "https://regexam.nuigalway.ie/regexam/papers/CS203-2023-P1.pdf",
        "has_marking_scheme": True,
        "marking_scheme_url": "https://regexam.nuigalway.ie/regexam/papers/CS203-2023-P1-MS.pdf",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "paper_id": "MA101-2024-P1",
        "module_code": "MA101",
        "year": 2024,
        "paper_number": 1,
        "pdf_url": "https://regexam.nuigalway.ie/regexam/papers/MA101-2024-P1.pdf",
        "has_marking_scheme": True,
        "marking_scheme_url": "https://regexam.nuigalway.ie/regexam/papers/MA101-2024-P1-MS.pdf",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "paper_id": "GA101-2024-P1",
        "module_code": "GA101",
        "year": 2024,
        "paper_number": 1,
        "pdf_url": "https://regexam.nuigalway.ie/regexam/papers/GA101-2024-P1.pdf",
        "has_marking_scheme": True,
        "marking_scheme_url": "https://regexam.nuigalway.ie/regexam/papers/GA101-2024-P1-MS.pdf",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "paper_id": "ED116-2024-P1",
        "module_code": "ED116",
        "year": 2024,
        "paper_number": 1,
        "pdf_url": "https://regexam.nuigalway.ie/regexam/papers/ED116-2024-P1.pdf",
        "has_marking_scheme": False,
        "marking_scheme_url": None,
        "scraped_at": "2026-09-23T00:00:00Z",
    },
)


class PastPapersPipeline(TertiaryPipelineBase):
    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="uog_past_papers",
        surface_name_english="UoG Past Papers (regexam.nuigalway.ie)",
        surface_name_irish="Seanpháipéirí Scrúdaithe UoG",
        source_url="https://regexam.nuigalway.ie/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="paper_id",
    )

    @dlt.resource(write_disposition="merge", primary_key="paper_id")
    def past_papers(self) -> Iterator[dict]:
        self.logger.info("past_papers_sync_start", surface_id=self.surface_id)
        yield from UOG_PAST_PAPERS
        self.logger.info("past_papers_sync_complete", surface_id=self.surface_id, count=len(UOG_PAST_PAPERS))

    def build_pipeline_resource(self) -> Iterator[dict]:
        return self.past_papers()


past_papers_pipeline = PastPapersPipeline()
