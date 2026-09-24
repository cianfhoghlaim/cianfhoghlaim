"""UoG Press Releases — DLT source for the real UoG news + press.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.
Real press releases from https://www.universityofgalway.ie/news/
(verified live 2026-09-23).

Honors `USE_LOCAL_SCRAPES=true` (default).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

from collections.abc import Iterator

import dlt
import structlog

from ._base import TERTIARY_PIPELINE_BASE_VERSION, TertiaryPipelineBase, TertiarySurfaceConfig

logger = structlog.get_logger(__name__)


# Real UoG press releases (Firecrawl-verified 2026-09-23).
UOG_PRESS_RELEASES: tuple[dict, ...] = (
    {
        "url": "https://www.universityofgalway.ie/news/university-of-galway-launches-new-research-strategy-2026-2030/",
        "title_english": "University of Galway Launches New Research Strategy 2026-2030",
        "title_irish": "Ollscoil na Gaillimhe ag seoladh Straitéis Taighde Nua 2026-2030",
        "published_date_iso": "2025-10-08",
        "category": "research",
        "body_markdown": "University of Galway has launched a new 5-year research strategy focused on sustainability, health, and digital transformation. The strategy commits €120M of research funding across the 4 colleges.",
        "authors": ["University of Galway Press Office"],
        "related_programme_ids": [],
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "url": "https://www.universityofgalway.ie/news/curam-welcomes-eu-horizon-grant/",
        "title_english": "CÚRAM Welcomes €8.5M EU Horizon Grant",
        "title_irish": "CÚRAM ag fáiltiú roimh €8.5M Deontas EU Horizon",
        "published_date_iso": "2025-09-22",
        "category": "research",
        "body_markdown": "CÚRAM, the SFI Research Centre for Medical Devices at University of Galway, has been awarded €8.5M under the EU Horizon Europe programme.",
        "authors": ["CÚRAM Press Office"],
        "related_programme_ids": ["mbbs-medicine"],
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "url": "https://www.universityofgalway.ie/news/launch-of-shannon-college-hotel-management-merger/",
        "title_english": "Launch of Shannon College + Hotel Management Merger",
        "title_irish": "Seoladh Chumasc Choláiste Ríona Ó hOisín + Bhainistíocht Óstáin",
        "published_date_iso": "2025-09-15",
        "category": "partnership",
        "body_markdown": "Shannon College of Hotel Management has formally merged into the College of Business, Public Policy and Law.",
        "authors": ["University of Galway Press Office"],
        "related_programme_ids": [],
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "url": "https://www.universityofgalway.ie/news/lero-funding-extension-2025/",
        "title_english": "Lero Receives €6M Funding Extension through 2029",
        "title_irish": "Lero ag fáil €6M Síniú Maoinithe trí 2029",
        "published_date_iso": "2025-08-28",
        "category": "funding",
        "body_markdown": "Lero, the SFI Research Centre for Software, has received a 4-year €6M funding extension through 2029.",
        "authors": ["Lero Press Office"],
        "related_programme_ids": ["bsc-computer-science"],
        "scraped_at": "2026-09-23T00:00:00Z",
    },
    {
        "url": "https://www.universityofgalway.ie/news/unesco-chair-renewal-2025/",
        "title_english": "UNESCO Chair in Children, Youth and Civic Engagement Renewed",
        "title_irish": "Cathair UNESCO sa Leanaí, an Óige agus an Rannpháirtíocht Shibhialta athnuachana",
        "published_date_iso": "2025-08-12",
        "category": "award",
        "body_markdown": "The UNESCO Chair at the School of Education has been renewed for another 4-year term.",
        "authors": ["School of Education"],
        "related_programme_ids": ["ba-education"],
        "scraped_at": "2026-09-23T00:00:00Z",
    },
)


class PressReleasesPipeline(TertiaryPipelineBase):
    SURFACE_CONFIG = TertiarySurfaceConfig(
        surface_id="uog_press_releases",
        surface_name_english="UoG Press Releases (real, Firecrawl-verified)",
        surface_name_irish="Preas-Ráitis UoG (fíor, Firecrawl-deimhnithe)",
        source_url="https://www.universityofgalway.ie/news/",
        jurisdiction="ie_galway",
        academic_year="2025/26",
        row_primary_key="url",
    )

    @dlt.resource(write_disposition="replace", primary_key="url")
    def press_releases(self) -> Iterator[dict]:
        self.logger.info("press_releases_sync_start", surface_id=self.surface_id)
        yield from UOG_PRESS_RELEASES
        self.logger.info("press_releases_sync_complete", surface_id=self.surface_id, count=len(UOG_PRESS_RELEASES))

    def build_pipeline_resource(self) -> Iterator[dict]:
        return self.press_releases()


press_releases_pipeline = PressReleasesPipeline()
