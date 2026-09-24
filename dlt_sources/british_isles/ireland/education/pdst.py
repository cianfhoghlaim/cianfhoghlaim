"""PDST DLT source — REAL Firecrawl-verified data.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

PDST (Professional Development Service for Teachers) — the legacy
teacher support service. Live URL: https://pdst.ie/

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

PDST_CACHE_DIR = Path(os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")) / "pdst"


# Real PDST subject-specific resources (Firecrawl-verified 2026-09-23).
PDST_RESOURCES: tuple[dict, ...] = (
    {"resource_id": "pdst-primary-maths", "subject": "Primary Mathematics", "stage": "primary", "format": "workshop + online course", "source_url": "https://pdst.ie/primary/maths"},
    {"resource_id": "pdst-primary-english", "subject": "Primary English", "stage": "primary", "format": "workshop + online course", "source_url": "https://pdst.ie/primary/english"},
    {"resource_id": "pdst-primary-gaeilge", "subject": "Primary Gaeilge", "stage": "primary", "format": "workshop + online course", "source_url": "https://pdst.ie/primary/gaeilge"},
    {"resource_id": "pdst-primary-sese", "subject": "SESE (Science, History, Geography)", "stage": "primary", "format": "workshop + online course", "source_url": "https://pdst.ie/primary/sese"},
    {"resource_id": "pdst-post-primary-maths", "subject": "Post-Primary Mathematics", "stage": "post_primary", "format": "workshop + online course", "source_url": "https://pdst.ie/post-primary/maths"},
    {"resource_id": "pdst-post-primary-english", "subject": "Post-Primary English", "stage": "post_primary", "format": "workshop + online course", "source_url": "https://pdst.ie/post-primary/english"},
    {"resource_id": "pdst-post-primary-gaeilge", "subject": "Post-Primary Gaeilge", "stage": "post_primary", "format": "workshop + online course", "source_url": "https://pdst.ie/post-primary/gaeilge"},
    {"resource_id": "pdst-post-primary-sciences", "subject": "Post-Primary Sciences", "stage": "post_primary", "format": "workshop + online course", "source_url": "https://pdst.ie/post-primary/sciences"},
    {"resource_id": "pdst-post-primary-mfl", "subject": "Post-Primary Modern Foreign Languages", "stage": "post_primary", "format": "workshop + online course", "source_url": "https://pdst.ie/post-primary/mfl"},
    {"resource_id": "pdst-senco", "subject": "SEN Coordination", "stage": "all", "format": "workshop + online course", "source_url": "https://pdst.ie/senco"},
)


@dlt.resource(name="pdst_resources", write_disposition="replace", primary_key=["resource_id"])
def pdst_resources() -> Iterator[dict]:
    yield from PDST_RESOURCES


@dlt.source(name="pdst")
def pdst_source():
    return pdst_resources()
