"""Re-export shim: wls/education (canonical path, Phase 3D)."""
from __future__ import annotations

import importlib
from typing import Any


def _maybe(name: str, mod: str) -> Any:
    try:
        return importlib.import_module(mod)
    except ModuleNotFoundError:
        return None


curriculum_for_wales = _maybe(
    "curriculum_for_wales", "cianfhoghlaim.cianfhoghlaim.dlt.british_isles.wales.education._curriculum_for_wales_helpers"
)
estyn = _maybe("estyn", "cianfhoghlaim.cianfhoghlaim.dlt.british_isles.wales.education.estyn")
statswales = _maybe("statswales", "cianfhoghlaim.cianfhoghlaim.dlt.british_isles.wales.statistics.statswales")

# Phase 3D per-source re-exports.
from dlt_sources.british_isles.wales.education.curriculum_for_wales import curriculum_for_wales_source
from dlt_sources.british_isles.wales.education.welsh_medium import welsh_medium_source
from dlt_sources.british_isles.wales.education.wjec_qualifications import wjec_qualifications_source

__all__ = [
    "curriculum_for_wales",
    "curriculum_for_wales_source",
    "estyn",
    "statswales",
    "welsh_medium_source",
    "wjec_qualifications_source",
]
