"""Re-export shim: domains.education.sct ↔ uk.scotland (lazy)."""
from __future__ import annotations

import importlib
from typing import Any


def _maybe(name: str, mod: str) -> Any:
    try:
        return importlib.import_module(mod)
    except ModuleNotFoundError:
        return None


curriculum_for_excellence = _maybe("curriculum_for_excellence", "oideachais.dlt_sources.uk.scotland.curriculum_for_excellence")
gov_scot_statistics = _maybe("gov_scot_statistics", "oideachais.dlt_sources.sct.statistics.gov_scot_statistics")
insight_benchmarking = _maybe("insight_benchmarking", "oideachais.dlt_sources.sct.education.insight_benchmarking")
simd = _maybe("simd", "oideachais.dlt_sources.sct.statistics.simd")

__all__ = [
    "curriculum_for_excellence",
    "gov_scot_statistics",
    "insight_benchmarking",
    "simd",
]
