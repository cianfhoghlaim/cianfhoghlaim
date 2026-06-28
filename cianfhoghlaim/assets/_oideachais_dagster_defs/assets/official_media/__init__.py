"""oideachais.dagster_defs.assets.official_media — Dagster assets for the official-media pipeline.

Stage 0.5 of ``author-archive-v1`` adds the four scraping assets
(pre_research, bulk_scrape, condense, identify_uis).

Stage 1 of ``author-archive-uog-coursework`` adds 10 assets
(mata, software, irish, education, personal_records — each with a
``_raw`` and ``_extraction`` variant).

Stage 2 of ``author-archive-cross-corpus-kg`` adds 3 assets
(cognify, cross_edges, kg_summary) for the cross-corpus knowledge
graph.

The Stage 1 and Stage 2 imports are wrapped in try/except so a branch
that lands only one stage can still import this module.
"""
from __future__ import annotations

# Stage 0.5 — scraping assets (always present)
from .author_archive_kg_assets import (
    author_archive_cognify,
    author_archive_cross_edges,
    author_archive_kg_summary,
)
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

# Stage 1 — UoG coursework (may be missing on branches that only
# have Stage 0.5 + Stage 2)
try:
    from .uog_coursework_assets import (
        author_archive_personal_records_extraction,
        author_archive_personal_records_raw,
        author_archive_uog_education_extraction,
        author_archive_uog_education_raw,
        author_archive_uog_irish_extraction,
        author_archive_uog_irish_raw,
        author_archive_uog_mata_extraction,
        author_archive_uog_mata_raw,
        author_archive_uog_software_extraction,
        author_archive_uog_software_raw,
    )
    _UOG_ASSETS_AVAILABLE = True
except ImportError:
    _UOG_ASSETS_AVAILABLE = False

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
    "author_archive_cognify",
    "author_archive_cross_edges",
    "author_archive_kg_summary",
]
if _UOG_ASSETS_AVAILABLE:
    __all__ += [
        "author_archive_uog_mata_raw",
        "author_archive_uog_mata_extraction",
        "author_archive_uog_software_raw",
        "author_archive_uog_software_extraction",
        "author_archive_uog_irish_raw",
        "author_archive_uog_irish_extraction",
        "author_archive_uog_education_raw",
        "author_archive_uog_education_extraction",
        "author_archive_personal_records_raw",
        "author_archive_personal_records_extraction",
    ]
