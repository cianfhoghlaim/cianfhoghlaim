"""oideachais.dagster_defs.assets.official_media — Dagster assets for the official-media pipeline.

Stage 0.5 of ``author-archive-v1`` adds the four scraping assets
(pre_research, bulk_scrape, condense, identify_uis) that drive the
pre-research + condensation + visual-grounding pipeline.
"""
from __future__ import annotations

from .cognify import official_media_cognify
from .embed import official_media_embed
from .extract import official_media_extract
from .hmgcc_co_creation import official_media_hmgcc_co_creation
from .resolve_sources import official_media_resolve_sources
from .scraping_assets import (
    official_media_bulk_scrape,
    official_media_condense,
    official_media_identify_uis,
    official_media_pre_research,
)

__all__ = [
    "official_media_cognify",
    "official_media_embed",
    "official_media_extract",
    "official_media_hmgcc_co_creation",
    "official_media_resolve_sources",
    "official_media_pre_research",
    "official_media_bulk_scrape",
    "official_media_condense",
    "official_media_identify_uis",
]
