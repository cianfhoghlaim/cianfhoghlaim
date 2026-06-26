"""oideachais.dlt_sources.ie.culture — Ireland cultural-heritage sub-package.

Per Phase 3D, each DLT source lives in its own file. The per-source
functions are re-exported at this package level for backward
compatibility with consumers that do
`from dlt_sources.ie.culture import duchas_source, ...`.

Modules that fail to import upstream are lazy-loaded to keep the
package import resilient (e.g. `duchas.py` references a missing
`shared.http` module — a pre-existing fragility flagged in
`oideachais/dagster_defs/definitions.py:74-87`).
"""
from __future__ import annotations

import importlib
from typing import Any


def _maybe_func(mod_path: str, attr: str) -> Any:
    """Return a *deferred* attribute. Importing the module happens on
    first access, so a broken upstream module does not block the
    package import."""
    class _LazyAttr:
        def __getattr__(self, item):
            m = importlib.import_module(mod_path)
            return getattr(m, attr)

    return _LazyAttr()


# Phase 3D per-source re-exports (one function per file).
# Known-good eager re-exports:
from dlt_sources.ie.culture.heritage import ie_culture_heritage_source  # noqa: F401
from dlt_sources.ie.culture.canuint import canuint_source  # noqa: F401
from dlt_sources.ie.culture.canuint_search import canuint_search_source  # noqa: F401
from dlt_sources.ie.culture.canuint_audio import canuint_audio_source  # noqa: F401
from dlt_sources.ie.culture.canuint_dialect_summary import (  # noqa: F401
    canuint_dialect_summary_source,
)
from dlt_sources.ie.culture.canuint_word_alignment import (  # noqa: F401
    canuint_word_alignment_source,
)
from dlt_sources.ie.culture.logainm import logainm_source  # noqa: F401
from dlt_sources.ie.culture.tearma import tearma_source  # noqa: F401
from dlt_sources.ie.culture.tearma_search import tearma_search_source  # noqa: F401
from dlt_sources.ie.culture.ainm import ainm_source  # noqa: F401
from dlt_sources.ie.culture.gaois_combined import gaois_combined_source  # noqa: F401

# Lazy re-exports (may be broken upstream).
duchas_source = _maybe_func("dlt_sources.ie.culture.duchas", "duchas_source")
duchas_images_source = _maybe_func(
    "dlt_sources.ie.culture.duchas_images", "duchas_images_source"
)
hidden_heritages_source = _maybe_func(
    "dlt_sources.ie.culture.hidden_heritages", "hidden_heritages_source"
)
local_education_documents_source = _maybe_func(
    "dlt_sources.ie.culture.local_education_documents",
    "local_education_documents_source",
)
local_documents_by_subject_source = _maybe_func(
    "dlt_sources.ie.culture.local_documents_by_subject",
    "local_documents_by_subject_source",
)


__all__ = [
    "ie_culture_heritage_source",
    "duchas_source",
    "canuint_source",
    "canuint_search_source",
    "canuint_audio_source",
    "canuint_dialect_summary_source",
    "canuint_word_alignment_source",
    "duchas_images_source",
    "hidden_heritages_source",
    "logainm_source",
    "tearma_source",
    "tearma_search_source",
    "ainm_source",
    "gaois_combined_source",
    "local_education_documents_source",
    "local_documents_by_subject_source",
]