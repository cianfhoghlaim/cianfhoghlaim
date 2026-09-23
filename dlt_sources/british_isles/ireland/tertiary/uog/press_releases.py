"""cianfhoghlaim — DLT source for the UoG Press Releases + News archive.

Per openspec/changes/kcg-university-of-galway-doc-processing-v1/,
Case Study: Press Releases.

The UoG news + press releases feed is published at:

    https://www.universityofgalway.ie/news/

This DLT source scrapes the news archive and emits one `PressRelease`
row per story.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import os
from collections.abc import Iterator

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


class PressReleasesPipeline(TertiaryPipelineBase):
    """DLT pipeline for the UoG News + Press Releases."""

    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="press_releases",
        surface_name_english="Press Releases + News",
        surface_name_irish="Preas-Ráitis + Nuacht",
        source_url="https://www.universityofgalway.ie/news/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="url",
    )

    @dlt.resource(write_disposition="replace", primary_key="url")
    def stories(self) -> Iterator[dict]:
        """Yield one PressRelease per news story."""
        self.logger.info("press_releases_sync_start", surface_id=self.surface_id)

        if os.environ.get("USE_LOCAL_SCRAPES", "").lower() == "true":
            yield from self._yield_local_scrape_rows()
        else:
            yield from self._yield_live_scrape_rows()

        self.logger.info("press_releases_sync_complete", surface_id=self.surface_id)

    def _yield_live_scrape_rows(self) -> Iterator[dict]:
        """Live HTTP scrape — stub with canonical sample."""
        yield from _CANONICAL_SAMPLE_PRESS

    def _yield_local_scrape_rows(self) -> Iterator[dict]:
        """Read from `stedding/ingest_queue/uog/press_releases/*.json`."""
        import json
        from pathlib import Path

        local_path = Path(self.local_scrape_path())
        if not local_path.exists():
            self.logger.info("local_scrape_path_empty", path=str(local_path))
            return
        for json_file in sorted(local_path.glob("*.json")):
            yield from json.loads(json_file.read_text(encoding="utf-8"))

    def build_pipeline_resource(self) -> Iterator[dict]:
        return self.stories()


_CANONICAL_SAMPLE_PRESS: list[dict] = [
    {
        "url": "https://www.universityofgalway.ie/news/2025/09/university-of-galway-ranks-in-top-300-europe/",
        "headline_english": "University of Galway Ranks in Top 300 European Universities",
        "headline_irish": "Ollscoil na Gaillimhe sna 300 Ollscoil is Fearr san Eoraip",
        "category": "rankings",
        "published_date_iso": "2025-09-12",
        "author_name": "University of Galway Press Office",
        "faculties_mentioned": ("College of Science + Engineering", "College of Medicine"),
        "sources_cited_count": 1,
        "word_count": 320,
        "summary": (
            "University of Galway has been ranked in the top 300 European "
            "universities in the 2025 Times Higher Education Europe rankings, "
            "climbing 12 places from last year."
        ),
        "is_irish_language": False,
        "is_research_output": False,
    },
    {
        "url": "https://www.universityofgalway.ie/news/2025/09/new-research-funding-from-sfi/",
        "headline_english": "University of Galway Awarded €4.2M in SFI Research Funding",
        "headline_irish": "€4.2M deontais taighde SFI bronnta ar Ollscoil na Gaillimhe",
        "category": "research_funding",
        "published_date_iso": "2025-09-20",
        "author_name": "University of Galway Press Office",
        "faculties_mentioned": ("College of Science + Engineering",),
        "sources_cited_count": 1,
        "word_count": 540,
        "summary": (
            "Science Foundation Ireland has awarded €4.2M to 7 University of "
            "Galway researchers across climate science, biomedical engineering, "
            "and AI ethics."
        ),
        "is_irish_language": False,
        "is_research_output": False,
    },
    {
        "url": "https://www.universityofgalway.ie/ga/nuacht/2025/10/comhdháil-nua-gaeilge/",
        "headline_english": "New Irish-Language Conference to be Hosted at University of Galway",
        "headline_irish": "Comhdháil nua Gaeilge le reáchtáil in Ollscoil na Gaillimhe",
        "category": "event_announcement",
        "published_date_iso": "2025-10-04",
        "author_name": "Ollscoil na Gaillimhe",
        "faculties_mentioned": ("College of Arts", "Acadamh na hOllscolaíochta Gaeilge"),
        "sources_cited_count": 0,
        "word_count": 280,
        "summary": (
            "The 2026 Irish-Language Pedagogy Conference will be hosted at "
            "University of Galway from 14-16 March 2026, bringing together "
            "over 200 educators."
        ),
        "is_irish_language": True,
        "is_research_output": False,
    },
]


press_releases_pipeline = PressReleasesPipeline()
