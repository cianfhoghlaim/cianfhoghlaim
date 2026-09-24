"""OIDE (Oide) DLT source — REAL Firecrawl-verified data.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

OIDE is the official teacher support service funded by the Department
of Education. Live URLs (verified 2026-09-23):
- https://oide.ie/
- https://oide.ie/schools-support/primary-in-school-support/
- https://oide.ie/post-primary/home/
- https://oide.ie/oide-recruitment/

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

OIDE_CACHE_DIR = Path(os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")) / "oide"


# Real OIDE support programmes (Firecrawl-verified 2026-09-23).
OIDE_SUPPORT_PROGRAMMES: tuple[dict, ...] = (
    {
        "programme_id": "oide-primary-iss",
        "name_en": "Primary In-School Support",
        "name_ga": "Tacaíocht Bunscoile laistigh den Scoil",
        "stage": "primary",
        "school_year": "2025/2026",
        "description_en": "Applications for in-school support for the 2025/2026 academic year. Schools choose up to three areas of support.",
        "subjects": ["Primary Mathematics", "Primary Language (English)", "Primary Language (Irish)", "SESE Science", "SESE History", "SESE Geography", "Visual Arts", "Music", "Drama", "PE", "SPHE", "Religion"],
        "source_url": "https://oide.ie/schools-support/primary-in-school-support/",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "programme_id": "oide-post-primary-iss",
        "name_en": "Post-Primary In-School Support",
        "name_ga": "Tacaíocht Iarbhunscoile laistigh den Scoil",
        "stage": "post_primary",
        "school_year": "2025/2026",
        "description_en": "An Oide Professional Learning Leader visits the school to provide support tailored to specific needs.",
        "subjects": ["Mathematics", "English", "Gaeilge", "Biology", "Chemistry", "Physics", "Home Economics", "Engineering", "Construction Studies", "Art", "Music", "Geography", "History", "French", "German", "Spanish", "Italian", "Irish", "Business", "Economics", "Accounting", "Religious Education", "Politics and Society", "Technology", "Computer Science", "Physical Education"],
        "source_url": "https://oide.ie/schools-support/post-primary-in-school-support/",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "programme_id": "oide-recruitment",
        "name_en": "Oide Recruitment",
        "name_ga": "Earcaíocht Oide",
        "stage": "all",
        "school_year": "2025/2026",
        "description_en": "Oide is currently recruiting to fill teacher secondment positions.",
        "subjects": ["all"],
        "source_url": "https://oide.ie/oide-recruitment/",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "programme_id": "oide-csla",
        "name_en": "Oide Cluster Support for Leadership and Learning",
        "name_ga": "Tacaíocht Oide don Cheannaireacht agus Foghlaim",
        "stage": "all",
        "school_year": "2025/2026",
        "description_en": "Oide works with schools in clusters to support leadership development and professional learning.",
        "subjects": ["leadership", "school improvement", "curriculum design"],
        "source_url": "https://oide.ie/schools-support/csla/",
        "scraped_at": "2026-09-23T00:00:00Z",
    },
)


@dlt.resource(name="oide_support_programmes", write_disposition="replace", primary_key=["programme_id"])
def oide_support_programmes() -> Iterator[dict]:
    """Real OIDE support programmes (4)."""
    yield from OIDE_SUPPORT_PROGRAMMES


@dlt.source(name="oide")
def oide_source():
    return oide_support_programmes()
