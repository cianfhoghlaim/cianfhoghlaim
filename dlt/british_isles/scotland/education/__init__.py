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
    "oideachais.cianfhoghlaim.dlt.british_isles.scotland.education._curriculum_for_excellence_helpers",
)
gov_scot_statistics = _maybe(
    "gov_scot_statistics", "oideachais.cianfhoghlaim.dlt.british_isles.scotland.statistics.gov_scot_statistics"
)
insight_benchmarking = _maybe(
    "insight_benchmarking", "oideachais.cianfhoghlaim.dlt.british_isles.scotland.education.insight_benchmarking"
)
simd = _maybe("simd", "oideachais.cianfhoghlaim.dlt.british_isles.scotland.statistics.simd")

# Phase 3D per-source re-exports.
from cianfhoghlaim.dlt.british_isles.scotland.education.curriculum_for_excellence import (
    curriculum_for_excellence_source,
)
from cianfhoghlaim.dlt.british_isles.scotland.education.gaelic_curriculum import gaelic_curriculum_source
from cianfhoghlaim.dlt.british_isles.scotland.education.sqa_qualifications import sqa_qualifications_source

__all__ = [
    "curriculum_for_excellence",
    "curriculum_for_excellence_source",
    "gaelic_curriculum_source",
    "gov_scot_statistics",
    "insight_benchmarking",
    "simd",
    "sqa_qualifications_source",
]
