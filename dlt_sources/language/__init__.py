"""dlt_sources.language — DEPRECATION SHIM.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (§1.3, master plan §3.2, §7.1), `dlt_sources/language/` is
**deprecated**. The grab-bag has been split into 3 themed sub-trees:

- `dlt_sources.lexicographic/` (11 source files + 3 helpers)
- `dlt_sources.cultural_heritage/` (6 source files + 2 helpers)
- `dlt_sources.language_models/` (1 source file)

Every legacy import path continues to work via the deprecation shims
below. New code SHOULD import from the canonical themed sub-tree:

    from dlt_sources.lexicographic import ainm, canuint, tearma, duchas, logainm
    from dlt_sources.cultural_heritage import celtic_mythology, duchas_corpus, heritage
    from dlt_sources.language_models import universal_dependencies

The `mise run lint:dlt-paths` CI gate (per master plan §1.10) fails
the build if any source `.py` file is added back to this directory
(other than `__init__.py` shims).

Reference:
- Master plan §3.2 ("Themed sub-trees")
- Master plan §7.1 ("dlt_sources/ migrations — language/ split")
"""
from __future__ import annotations

import importlib
import logging as _logging
from types import ModuleType as _ModuleType
from typing import Any as _Any

_logger = _logging.getLogger(__name__)


def _safe_module_attr(parent_pkg: str, module_name: str, attr_name: str) -> _Any:
    """Best-effort import of `parent_pkg.module_name` and return its `attr_name`.

    Returns `None` (and logs a warning) if the module is unavailable
    (e.g. missing transitive deps like `shared.utils`). This shim
    MUST never raise — it is a deprecation compatibility layer.
    """
    fqmn = f"{parent_pkg}.{module_name}"
    try:
        mod = importlib.import_module(fqmn)
        return getattr(mod, attr_name, None)
    except Exception as e:
        _logger.warning(
            "dlt_sources.language deprecation shim: %s.%s unavailable: %s",
            parent_pkg, module_name, e,
        )
        return None


def _safe_module(parent_pkg: str, module_name: str) -> _ModuleType | None:
    """Best-effort import of `parent_pkg.module_name` itself."""
    fqmn = f"{parent_pkg}.{module_name}"
    try:
        return importlib.import_module(fqmn)
    except Exception as e:
        _logger.warning(
            "dlt_sources.language deprecation shim: %s.%s unavailable: %s",
            parent_pkg, module_name, e,
        )
        return None


# ─── Lexicographic sub-tree (re-exports the source FUNCTION from each module) ─
# Each module exposes a single source function with the same name as the
# module (e.g. `ainm.py` defines `ainm_source`). We import the source
# FUNCTION directly via `_safe_module_attr`.
ainm = _safe_module_attr("dlt_sources.lexicographic", "ainm", "ainm_source")
canuint = _safe_module_attr("dlt_sources.lexicographic", "canuint", "canuint_source")
canuint_audio = _safe_module_attr("dlt_sources.lexicographic", "canuint_audio", "canuint_audio_source")
canuint_dialect_summary = _safe_module_attr("dlt_sources.lexicographic", "canuint_dialect_summary", "canuint_dialect_summary_source")
canuint_search = _safe_module_attr("dlt_sources.lexicographic", "canuint_search", "canuint_search_source")
canuint_word_alignment = _safe_module_attr("dlt_sources.lexicographic", "canuint_word_alignment", "canuint_word_alignment_source")
duchas = _safe_module_attr("dlt_sources.lexicographic", "duchas", "duchas_source")
gaois = _safe_module_attr("dlt_sources.lexicographic", "gaois", "gaois_source")
gaois_combined = _safe_module_attr("dlt_sources.lexicographic", "gaois_combined", "gaois_combined_source")
logainm = _safe_module_attr("dlt_sources.lexicographic", "logainm", "logainm_source")
tearma = _safe_module_attr("dlt_sources.lexicographic", "tearma", "tearma_source")
tearma_search = _safe_module_attr("dlt_sources.lexicographic", "tearma_search", "tearma_search_source")

# ─── Cultural heritage sub-tree ────────────────────────────────────────────
celtic_mythology = _safe_module_attr("dlt_sources.cultural_heritage", "celtic_mythology", "celtic_mythology_source")
duchas_corpus = _safe_module_attr("dlt_sources.cultural_heritage", "duchas_corpus", "duchas_images_source")
heritage = _safe_module_attr("dlt_sources.cultural_heritage", "heritage", "heritage_source")
hidden_heritages = _safe_module_attr("dlt_sources.cultural_heritage", "hidden_heritages", "hidden_heritages_source")
local_documents_by_subject = _safe_module_attr("dlt_sources.cultural_heritage", "local_documents_by_subject", "local_documents_by_subject_source")
local_education_documents = _safe_module_attr("dlt_sources.cultural_heritage", "local_education_documents", "local_education_documents_source")

# ─── Language models sub-tree ──────────────────────────────────────────────
universal_dependencies = _safe_module_attr("dlt_sources.language_models", "universal_dependencies", "ud_source")


# ─── Legacy aliases (per master plan §7.1) ─────────────────────────────────
# The original `language.duchas_images` module was renamed to
# `cultural_heritage.duchas_corpus`. Re-export it under the old name
# for backwards compatibility.
duchas_images = _safe_module("dlt_sources.cultural_heritage", "duchas_corpus")


__all__ = [
    # Lexicographic
    "ainm", "canuint", "canuint_audio", "canuint_dialect_summary",
    "canuint_search", "canuint_word_alignment", "duchas", "gaois",
    "gaois_combined", "logainm", "tearma", "tearma_search",
    # Cultural heritage
    "celtic_mythology", "duchas_corpus", "heritage", "hidden_heritages",
    "local_documents_by_subject", "local_education_documents",
    # Language models
    "universal_dependencies",
    # Legacy aliases
    "duchas_images",
]
