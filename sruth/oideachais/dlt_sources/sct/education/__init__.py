"""Re-export shim: sct/education (canonical path, Phase 3D)."""
from __future__ import annotations

import importlib
from typing import Any


def _maybe(name: str, mod: str) -> Any:
    try:
        return importlib.import_module(mod)
    except ModuleNotFoundError:
        return None


curriculum_for_excellence = _maybe(
    "curriculum_for_excellence",
    "oideachais.dlt_sources.sct.education._curriculum_for_excellence_helpers",
)
gov_scot_statistics = _maybe(
    "gov_scot_statistics", "oideachais.dlt_sources.sct.statistics.gov_scot_statistics"
)
insight_benchmarking = _maybe(
    "insight_benchmarking", "oideachais.dlt_sources.sct.education.insight_benchmarking"
)
simd = _maybe("simd", "oideachais.dlt_sources.sct.statistics.simd")

# Phase 3D per-source re-exports.
from dlt_sources.sct.education.curriculum_for_excellence import (  # noqa: F401
    curriculum_for_excellence_source,
)
from dlt_sources.sct.education.sqa_qualifications import sqa_qualifications_source  # noqa: F401
from dlt_sources.sct.education.gaelic_curriculum import gaelic_curriculum_source  # noqa: F401


__all__ = [
    "curriculum_for_excellence",
    "gov_scot_statistics",
    "insight_benchmarking",
    "simd",
    "curriculum_for_excellence_source",
    "sqa_qualifications_source",
    "gaelic_curriculum_source",
]