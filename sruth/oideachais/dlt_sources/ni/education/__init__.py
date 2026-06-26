"""oideachais.dlt_sources.ni.education package init — re-export shim.

Each nation sub-package re-exports its legacy address so that:
  * `from oideachais.dlt_sources.ni.education.ccea_curriculum import ni_curriculum_source`
    and
  * `from oideachais.dlt_sources.uk.northern_ireland.ccea_curriculum import ni_curriculum_source`
    resolve to the same callable.

The legacy `oideachais.dlt_sources.uk.__init__.py` eagerly imports every
UK sub-module; if any one of them has a broken upstream dep (the
`shared.http` module, a pre-existing fragility) it breaks the whole
re-export. We work around it by importing the specific sub-module
directly.
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


ccea_curriculum = _maybe("ccea_curriculum", "oideachais.dlt_sources.uk.northern_ireland.ccea_curriculum")
education_ni = _maybe("education_ni", "oideachais.dlt_sources.ni.education.education_ni")
etini = _maybe("etini", "oideachais.dlt_sources.ni.education.etini")
nisra = _maybe("nisra", "oideachais.dlt_sources.ni.statistics.nisra")

__all__ = ["ccea_curriculum", "education_ni", "etini", "nisra"]
