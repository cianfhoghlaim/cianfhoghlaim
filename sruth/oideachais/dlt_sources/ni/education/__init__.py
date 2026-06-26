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
from dlt_sources.ni.education.ni_curriculum import ni_curriculum_source  # noqa: F401
from dlt_sources.ni.education.ccea_qualifications import ccea_qualifications_source  # noqa: F401
from dlt_sources.ni.education.irish_medium_ni import irish_medium_ni_source  # noqa: F401
from dlt_sources.ni.education._ccea_curriculum_helpers import NI_CURRICULUM_URLS  # noqa: F401


__all__ = [
    "ccea_curriculum",
    "education_ni",
    "etini",
    "nisra",
    "ni_curriculum_source",
    "ccea_qualifications_source",
    "irish_medium_ni_source",
    "NI_CURRICULUM_URLS",
]