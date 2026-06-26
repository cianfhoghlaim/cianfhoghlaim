"""Re-export shim: domains.education.wls ↔ uk.wales (lazy)."""
from __future__ import annotations

import importlib
from typing import Any


def _maybe(name: str, mod: str) -> Any:
    try:
        return importlib.import_module(mod)
    except ModuleNotFoundError:
        return None


curriculum_for_wales = _maybe("curriculum_for_wales", "oideachais.dlt_sources.uk.wales.curriculum_for_wales")
estyn = _maybe("estyn", "oideachais.dlt_sources.wls.education.estyn")
statswales = _maybe("statswales", "oideachais.dlt_sources.wls.statistics.statswales")

__all__ = ["curriculum_for_wales", "estyn", "statswales"]
