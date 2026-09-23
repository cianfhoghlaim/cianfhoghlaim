"""cianfhoghlaim — DLT source for the UoG Research Publications + Theses.

Per openspec/changes/kcg-university-of-galway-doc-processing-v1/,
Case Study: Research Outputs.

The UoG research outputs surface aggregates publicly-available
research metadata (titles, abstracts, authors, citations, theses)
across the 5 colleges + their research centres. Published at:

    https://www.universityofgalway.ie/research/

This DLT source scrapes the research outputs catalog and emits one
`ResearchOutput` row per publication.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import os
from collections.abc import Iterator

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


class ResearchOutputsPipeline(TertiaryPipelineBase):
    """DLT pipeline for the UoG Research Publications + Theses."""

    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="research_outputs",
        surface_name_english="Research Publications + Theses",
        surface_name_irish="Aschuir Thaighde",
        source_url="https://www.universityofgalway.ie/research/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="url",
    )

    @dlt.resource(write_disposition="replace", primary_key="url")
    def outputs(self) -> Iterator[dict]:
        """Yield one ResearchOutput per publication."""
        self.logger.info("research_outputs_sync_start", surface_id=self.surface_id)

        if os.environ.get("USE_LOCAL_SCRAPES", "").lower() == "true":
            yield from self._yield_local_scrape_rows()
        else:
            yield from self._yield_live_scrape_rows()

        self.logger.info("research_outputs_sync_complete", surface_id=self.surface_id)

    def _yield_live_scrape_rows(self) -> Iterator[dict]:
        """Live HTTP scrape — stub with canonical sample."""
        yield from _CANONICAL_SAMPLE_OUTPUTS

    def _yield_local_scrape_rows(self) -> Iterator[dict]:
        """Read from `stedding/ingest_queue/uog/research_outputs/*.json`."""
        import json
        from pathlib import Path

        local_path = Path(self.local_scrape_path())
        if not local_path.exists():
            self.logger.info("local_scrape_path_empty", path=str(local_path))
            return
        for json_file in sorted(local_path.glob("*.json")):
            yield from json.loads(json_file.read_text(encoding="utf-8"))

    def build_pipeline_resource(self) -> Iterator[dict]:
        return self.outputs()


_CANONICAL_SAMPLE_OUTPUTS: list[dict] = [
    {
        "url": "https://aran.library.universityofgalway.ie/handle/10379/12345",
        "title": "An Ghaeilge sa Chóras Oideachais: Aistriúchán agus Polasaí",
        "title_english": "Irish in the Education System: Translation and Policy",
        "author_names": ("S. Ní Laoghaire", "P. Mac an Bhaird"),
        "thesis_or_publication": "thesis",
        "thesis_type": "doctoral",
        "year_published": 2024,
        "faculty": "College of Arts",
        "school": "Acadamh na hOllscolaíochta Gaeilge",
        "abstract_word_count": 350,
        "doi": None,
        "language": "ga",
        "is_open_access": True,
        "is_irish_language": True,
    },
    {
        "url": "https://doi.org/10.1234/uog.2025.cs.001",
        "title": "Spectral Methods for Real-Time Acoustic Beamforming in IoT Sensor Networks",
        "title_english": None,
        "author_names": ("M. Hayes", "L. Walsh", "S. Byrne"),
        "thesis_or_publication": "publication",
        "year_published": 2025,
        "faculty": "College of Science + Engineering",
        "school": "School of Computer Science",
        "abstract_word_count": 280,
        "doi": "10.1234/uog.2025.cs.001",
        "language": "en",
        "is_open_access": True,
        "is_irish_language": False,
    },
]


research_outputs_pipeline = ResearchOutputsPipeline()
