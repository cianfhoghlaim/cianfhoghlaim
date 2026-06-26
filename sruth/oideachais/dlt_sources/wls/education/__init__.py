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
    "curriculum_for_wales", "oideachais.dlt_sources.wls.education._curriculum_for_wales_helpers"
)
estyn = _maybe("estyn", "oideachais.dlt_sources.wls.education.estyn")
statswales = _maybe("statswales", "oideachais.dlt_sources.wls.statistics.statswales")

# Phase 3D per-source re-exports.
from dlt_sources.wls.education.curriculum_for_wales import curriculum_for_wales_source  # noqa: F401
from dlt_sources.wls.education.wjec_qualifications import wjec_qualifications_source  # noqa: F401
from dlt_sources.wls.education.welsh_medium import welsh_medium_source  # noqa: F401


__all__ = [
    "curriculum_for_wales",
    "estyn",
    "statswales",
    "curriculum_for_wales_source",
    "wjec_qualifications_source",
    "welsh_medium_source",
]