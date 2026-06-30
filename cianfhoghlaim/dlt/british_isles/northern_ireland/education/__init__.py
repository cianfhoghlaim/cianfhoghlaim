"""oideachais.dlt_sources.ni.education package init — re-export shim.

Phase 3D canonical path: ni/education (per cross-domain-registry).
"""
from __future__ import annotations

import importlib
from typing import Any


def _maybe(name: str, mod: str) -> Any:
    """Import a module; return None if the upstream is broken."""
    try:
        return importlib.import_module(mod)
    except ModuleNotFoundError:
        return None


ccea_curriculum = _maybe(
    "ccea_curriculum", "oideachais.dlt_sources.ni.education._ccea_curriculum_helpers"
)
education_ni = _maybe("education_ni", "oideachais.dlt_sources.ni.education.education_ni")
etini = _maybe("etini", "oideachais.dlt_sources.ni.education.etini")
nisra = _maybe("nisra", "oideachais.dlt_sources.ni.statistics.nisra")

# Phase 3D per-source re-exports.
from dlt_sources.ni.education._ccea_curriculum_helpers import NI_CURRICULUM_URLS
from dlt_sources.ni.education.ccea_qualifications import ccea_qualifications_source
from dlt_sources.ni.education.irish_medium_ni import irish_medium_ni_source
from dlt_sources.ni.education.ni_curriculum import ni_curriculum_source

__all__ = [
    "NI_CURRICULUM_URLS",
    "ccea_curriculum",
    "ccea_qualifications_source",
    "education_ni",
    "etini",
    "irish_medium_ni_source",
    "ni_curriculum_source",
    "nisra",
]
