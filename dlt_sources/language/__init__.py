"""dlt_sources.language — Ireland bilingual/cultural-heritage sub-package.

Per Phase 3D, each DLT source lives in its own file. The per-source
functions are re-exported at this package level for backward
compatibility with consumers that do
`from dlt_sources.language import duchas_source, ...`.

Modules that fail to import upstream are lazy-loaded to keep the
package import resilient (e.g. `duchas.py` references a missing
`shared.http` module — a pre-existing fragility flagged in
`oideachais/dagster_defs/definitions.py:74-87`).

NOTE: every import in this file previously pointed at
`dlt_sources.british_isles.ireland.culture.*` (and, for the lazy
re-exports, at the doubly-stale `cianfhoghlaim.dlt.british_isles.ireland.
culture.*`) — a package that does not exist anywhere in this repo. That
made the *whole* `dlt_sources.language` package unimportable (a package's
`__init__.py` always runs before any of its submodules can be reached),
even though every one of these 19 source files sits right here, as a
sibling of this file, and works. Same defect class as the documented
`dlt/`→`dlt_sources/` refactor stragglers (F4 in the KCG refactor
roadmap), just not previously catalogued for this specific package.
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
from dlt_sources.language.ainm import ainm_source
from dlt_sources.language.canuint import canuint_source
from dlt_sources.language.canuint_audio import canuint_audio_source
from dlt_sources.language.canuint_dialect_summary import (
    canuint_dialect_summary_source,
)
from dlt_sources.language.canuint_search import canuint_search_source
from dlt_sources.language.canuint_word_alignment import (
    canuint_word_alignment_source,
)
from dlt_sources.language.gaois_combined import gaois_combined_source
from dlt_sources.language.heritage import ie_culture_heritage_source
from dlt_sources.language.logainm import logainm_source
from dlt_sources.language.tearma import tearma_source
from dlt_sources.language.tearma_search import tearma_search_source

# Lazy re-exports (may be broken upstream).
duchas_source = _maybe_func("dlt_sources.language.duchas", "duchas_source")
duchas_images_source = _maybe_func(
    "dlt_sources.language.duchas_images", "duchas_images_source"
)
hidden_heritages_source = _maybe_func(
    "dlt_sources.language.hidden_heritages", "hidden_heritages_source"
)
local_education_documents_source = _maybe_func(
    "dlt_sources.language.local_education_documents",
    "local_education_documents_source",
)
local_documents_by_subject_source = _maybe_func(
    "dlt_sources.language.local_documents_by_subject",
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
