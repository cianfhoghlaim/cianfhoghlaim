"""oideachais.cianfhoghlaim.dlt.british_isles.ireland.culture — Ireland cultural-heritage sub-package.

Per Phase 3D, each DLT source lives in its own file. The per-source
functions are re-exported at this package level for backward
compatibility with consumers that do
`from cianfhoghlaim.dlt.british_isles.ireland.culture import duchas_source, ...`.

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
from cianfhoghlaim.dlt.british_isles.ireland.culture.ainm import ainm_source
from cianfhoghlaim.dlt.british_isles.ireland.culture.canuint import canuint_source
from cianfhoghlaim.dlt.british_isles.ireland.culture.canuint_audio import canuint_audio_source
from cianfhoghlaim.dlt.british_isles.ireland.culture.canuint_dialect_summary import (
    canuint_dialect_summary_source,
)
from cianfhoghlaim.dlt.british_isles.ireland.culture.canuint_search import canuint_search_source
from cianfhoghlaim.dlt.british_isles.ireland.culture.canuint_word_alignment import (
    canuint_word_alignment_source,
)
from cianfhoghlaim.dlt.british_isles.ireland.culture.gaois_combined import gaois_combined_source
from cianfhoghlaim.dlt.british_isles.ireland.culture.heritage import ie_culture_heritage_source
from cianfhoghlaim.dlt.british_isles.ireland.culture.logainm import logainm_source
from cianfhoghlaim.dlt.british_isles.ireland.culture.tearma import tearma_source
from cianfhoghlaim.dlt.british_isles.ireland.culture.tearma_search import tearma_search_source

# Lazy re-exports (may be broken upstream).
duchas_source = _maybe_func("cianfhoghlaim.dlt.british_isles.ireland.culture.duchas", "duchas_source")
duchas_images_source = _maybe_func(
    "cianfhoghlaim.dlt.british_isles.ireland.culture.duchas_images", "duchas_images_source"
)
hidden_heritages_source = _maybe_func(
    "cianfhoghlaim.dlt.british_isles.ireland.culture.hidden_heritages", "hidden_heritages_source"
)
local_education_documents_source = _maybe_func(
    "cianfhoghlaim.dlt.british_isles.ireland.culture.local_education_documents",
    "local_education_documents_source",
)
local_documents_by_subject_source = _maybe_func(
    "cianfhoghlaim.dlt.british_isles.ireland.culture.local_documents_by_subject",
    "local_documents_by_subject_source",
)


__all__ = [
    "ainm_source",
    "canuint_audio_source",
    "canuint_dialect_summary_source",
    "canuint_search_source",
    "canuint_source",
    "canuint_word_alignment_source",
    "duchas_images_source",
    "duchas_source",
    "gaois_combined_source",
    "hidden_heritages_source",
    "ie_culture_heritage_source",
    "local_documents_by_subject_source",
    "local_education_documents_source",
    "logainm_source",
    "tearma_search_source",
    "tearma_source",
]
