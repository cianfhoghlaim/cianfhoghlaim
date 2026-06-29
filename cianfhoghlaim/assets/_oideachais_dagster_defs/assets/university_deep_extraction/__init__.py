"""University deep extraction — Dagster assets (5 assets, group `university_deep_extraction`).

Case study: University of Galway. Re-exported from `uog_assets.py`.

See `openspec/changes/university-of-galway-deep-extraction/`.
"""
from __future__ import annotations

from .uog_assets import (
    UNIVERSITY_GROUP,
    UOG_PRE_RESEARCH_GOAL,
    uog_assets,
    uog_bulk_scrape,
    uog_extract_courses,
    uog_extract_modules,
    uog_extract_programmes,
    uog_pre_research,
)

__all__ = [
    "UNIVERSITY_GROUP",
    "UOG_PRE_RESEARCH_GOAL",
    "uog_pre_research",
    "uog_bulk_scrape",
    "uog_extract_courses",
    "uog_extract_modules",
    "uog_extract_programmes",
    "uog_assets",
]
