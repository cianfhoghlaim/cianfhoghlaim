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
    "national_curriculum", "oideachais.dlt_sources.en.education._national_curriculum_helpers"
)
ofsted = _maybe("ofsted", "oideachais.dlt_sources.en.education.ofsted")
school_info = _maybe("school_info", "oideachais.dlt_sources.en.education.school_info")
dfe_explore_statistics = _maybe(
    "dfe_explore_statistics", "oideachais.dlt_sources.en.statistics.dfe_explore_statistics"
)

# Per-source functions (Phase 3D: one function per file).
from dlt_sources.en.education.national_curriculum import national_curriculum_source  # noqa: F401
from dlt_sources.en.education.aqa_qualifications import aqa_qualifications_source  # noqa: F401
from dlt_sources.en.education.edexcel_qualifications import edexcel_qualifications_source  # noqa: F401
from dlt_sources.en.education.ocr_qualifications import ocr_qualifications_source  # noqa: F401
from dlt_sources.en.education.all_exam_boards import all_exam_boards_source  # noqa: F401
from dlt_sources.en.education._national_curriculum_helpers import (  # noqa: F401
    GOV_UK_CURRICULUM_URLS,
    EXAM_BOARD_URLS,
)


__all__ = [
    "national_curriculum",
    "ofsted",
    "school_info",
    "dfe_explore_statistics",
    "national_curriculum_source",
    "aqa_qualifications_source",
    "edexcel_qualifications_source",
    "ocr_qualifications_source",
    "all_exam_boards_source",
    "GOV_UK_CURRICULUM_URLS",
    "EXAM_BOARD_URLS",
]