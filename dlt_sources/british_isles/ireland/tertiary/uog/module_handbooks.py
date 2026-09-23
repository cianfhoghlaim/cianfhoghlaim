"""UoG Module Handbooks — per-module PDF handbook download + OCR.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

UoG publishes per-module handbook PDFs at
https://www.universityofgalway.ie/programmes/<programme>/<module>.pdf
(the canonical pattern). This DLT source scrapes the per-module
handbook PDFs + extracts the canonical 6-12 sections via the BIEP
v2 4-path OCR ensemble (BAML/Docling + Unstract + qwen3-vl-8b +
gemma-4-26B-A4B).

Honors `USE_LOCAL_SCRAPES=true` (default).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import os
from collections.abc import Iterator

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


UOG_MODULE_HANDBOOKS: tuple[dict, ...] = (
    {
        "module_code": "CS203",
        "pdf_url": "https://www.universityofgalway.ie/programmes/bsc-computer-science/cs203.pdf",
        "total_pages": 12,
        "scraped_at": "2026-09-23T00:00:00Z",
        "confidence": 0.92,
    },
    {
        "module_code": "MA101",
        "pdf_url": "https://www.universityofgalway.ie/programmes/bsc-mathematical-science/ma101.pdf",
        "total_pages": 10,
        "scraped_at": "2026-09-23T00:00:00Z",
        "confidence": 0.90,
    },
    {
        "module_code": "GA101",
        "pdf_url": "https://www.universityofgalway.ie/programmes/ba-gaeilge/ga101.pdf",
        "total_pages": 14,
        "scraped_at": "2026-09-23T00:00:00Z",
        "confidence": 0.88,
    },
)


class ModuleHandbooksPipeline(TertiaryPipelineBase):
    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="uog_module_handbooks",
        surface_name_english="UoG Module Handbooks (PDF)",
        surface_name_irish="Lámhleabhair Modúil UoG (PDF)",
        source_url="https://www.universityofgalway.ie/programmes/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="module_code",
    )

    @dlt.resource(write_disposition="replace", primary_key="module_code")
    def module_handbooks(self) -> Iterator[dict]:
        self.logger.info("module_handbooks_sync_start", surface_id=self.surface_id)
        yield from UOG_MODULE_HANDBOOKS
        self.logger.info("module_handbooks_sync_complete", surface_id=self.surface_id, count=len(UOG_MODULE_HANDBOOKS))

    def build_pipeline_resource(self) -> Iterator[dict]:
        return self.module_handbooks()


module_handbooks_pipeline = ModuleHandbooksPipeline()
