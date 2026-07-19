"""Re-export shim: en/education (canonical path)."""
from __future__ import annotations

import importlib
from typing import Any


def _maybe(name: str, mod: str) -> Any:
    try:
        return importlib.import_module(mod)
    except ModuleNotFoundError:
        return None


# Phase 3D per-source re-exports.
national_curriculum = _maybe(
    "national_curriculum", "cianfhoghlaim.cianfhoghlaim.dlt.british_isles.england.education._national_curriculum_helpers"
)
ofsted = _maybe("ofsted", "cianfhoghlaim.cianfhoghlaim.dlt.british_isles.england.education.ofsted")
school_info = _maybe("school_info", "cianfhoghlaim.cianfhoghlaim.dlt.british_isles.england.education.school_info")
dfe_explore_statistics = _maybe(
    "dfe_explore_statistics", "cianfhoghlaim.cianfhoghlaim.dlt.british_isles.england.statistics.dfe_explore_statistics"
)

# Per-source functions (Phase 3D: one function per file).
from cianfhoghlaim.dlt.british_isles.england.education._national_curriculum_helpers import (
    EXAM_BOARD_URLS,
    GOV_UK_CURRICULUM_URLS,
)
from cianfhoghlaim.dlt.british_isles.england.education.all_exam_boards import all_exam_boards_source
from cianfhoghlaim.dlt.british_isles.england.education.aqa_qualifications import aqa_qualifications_source
from cianfhoghlaim.dlt.british_isles.england.education.edexcel_qualifications import (
    edexcel_qualifications_source,
)
from cianfhoghlaim.dlt.british_isles.england.education.national_curriculum import national_curriculum_source
from cianfhoghlaim.dlt.british_isles.england.education.ocr_qualifications import ocr_qualifications_source

__all__ = [
    "EXAM_BOARD_URLS",
    "GOV_UK_CURRICULUM_URLS",
    "all_exam_boards_source",
    "aqa_qualifications_source",
    "dfe_explore_statistics",
    "edexcel_qualifications_source",
    "national_curriculum",
    "national_curriculum_source",
    "ocr_qualifications_source",
    "ofsted",
    "school_info",
]
