"""Re-export shim: domains.education.en ↔ uk.england (lazy to avoid shared.http breakage)."""
from __future__ import annotations

import importlib
from typing import Any


def _maybe(name: str, mod: str) -> Any:
    try:
        return importlib.import_module(mod)
    except ModuleNotFoundError:
        return None


national_curriculum = _maybe("national_curriculum", "oideachais.dlt_sources.uk.england.national_curriculum")
ofsted = _maybe("ofsted", "oideachais.dlt_sources.uk.england.ofsted")
school_info = _maybe("school_info", "oideachais.dlt_sources.uk.england.school_info")
dfe_explore_statistics = _maybe("dfe_explore_statistics", "oideachais.dlt_sources.uk.england.dfe_explore_statistics")

__all__ = ["national_curriculum", "ofsted", "school_info", "dfe_explore_statistics"]
