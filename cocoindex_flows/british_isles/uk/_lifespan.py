"""Per-phase lifespan re-export for the ciancheiltis Phase 1 (en-cy / Wales) + Phase 2 (en-ga / ROI) + Phase 3 (en-ga / NI) + Phase 4 (en-gd / Scotland) + Phase 5 (en-gv / Isle of Man) + Phase 6 (en-ga / EU level) Apps.

This is a thin per-phase shim over the canonical shared lifespan at
``cocoindex_flows._shared._lifespan``. The R1 conformance contract
(per the ``oideachais-cocoindex-v1`` skill + the
``openspec/specs/ciancheiltis/spec.md`` R1-R4 section) requires:

> R1: MUST import ``from ._lifespan import shared_lifespan``

Every ciancheiltis phase App (en-cy, en-ga-roi, en-ga-ni, en-gd, en-gv,
en-ga-eu) ships its own sibling ``_lifespan.py`` that re-exports the
canonical shared lifespan + ContextKeys, so each phase is a self-contained
module subtree that can be moved (or vendored) without breaking the
R1 import path.

Phase 5 (en-gv / Isle of Man, language pair ``en-gv``) was added by
PR0.9. Manx (Gaelg) is in revival status — there is no statutory
bilingual publication duty. The Phase 5 corpus is therefore expected
to be smaller than the Phase 1 / Phase 4 sister corpora. The Phase 5
App lives at ``ciancheiltis_en_gv_embedding.py`` (sibling of the
Phase 1 / Phase 2 / Phase 3 / Phase 4 Apps) and re-exports
``PHASE_TABLE_URL_GV`` + ``PHASE_LANGUAGE_PAIR_GV`` from this shim.

The canonical home for the underlying implementations is
``cocoindex_flows/_shared/_lifespan.py`` (one of the 14 module-scope
``app = coco.App(...)`` declarations that share the
``shared_lifespan`` per REFACTORING.md item 12). DO NOT duplicate the
``@coco.lifespan`` body here — re-export only.

Public surface (the umbrella spec's R1 contract):

- ``shared_lifespan`` — the canonical async lifespan provider
- ``LANCE_DB`` — the canonical ``coco.ContextKey[coco_lancedb.LanceAsyncConnection]``
- ``EMBEDDER`` — the canonical ``BAAI/bge-m3`` embedder ContextKey
  (``detect_change=True`` so a model swap auto-re-embeds)
- ``RESOLVED_FILE_REGISTRY`` — the in-memory file cache used by
  ``localfs.walk_dir`` (not used by ciancheiltis, but re-exported for
  symmetry with the canonical module)
- ``LANCEDB_URI`` — the canonical dev default
  (``rest://lakehouse-lance-namespace:8182``)
- ``EMBED_MODEL`` — ``"BAAI/bge-m3"`` (1024-d, multilingual incl.
  CY/GA/GD/GV per the umbrella spec § R2)
- ``EMBED_DIM`` — ``1024``
- ``COCOINDEX_AVAILABLE`` — graceful-degradation flag (mirrors the
  canonical module's optional-dependency handling)
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

# The canonical ``_shared._lifespan`` module exports ``shared_lifespan``
# only inside its ``if COCOINDEX_AVAILABLE:`` block (see
# ``cocoindex_flows/_shared/_lifespan.py:112-138``). When CocoIndex is
# not installed the symbol is absent, so we import it conditionally and
# fall back to a no-op async-generator stub.
from cocoindex_flows._shared._lifespan import (
    COCOINDEX_AVAILABLE,
    EMBED_DIM,
    EMBED_MODEL,
    EMBEDDER,
    LANCE_DB,
    LANCEDB_URI,
    RESOLVED_FILE_REGISTRY,
)

try:
    from cocoindex_flows._shared._lifespan import shared_lifespan
except ImportError:  # pragma: no cover - cocoindex not installed

    async def shared_lifespan(  # type: ignore[no-redef]
        builder: Any = None,
    ) -> AsyncIterator[None]:
        """No-op fallback shared lifespan when CocoIndex is not installed."""
        if builder is not None:
            # Best-effort: provide the canonical ContextKeys as None so
            # downstream ``await coco.use_context(KEY)`` calls degrade
            # to a clear AttributeError rather than a confusing NoneType.
            for key in (LANCE_DB, EMBEDDER, RESOLVED_FILE_REGISTRY):
                try:
                    builder.provide(key, None)  # type: ignore[arg-type]
                except Exception:  # pragma: no cover - defensive
                    pass
        yield

# Phase 1 (en-cy / Wales) is bilingual EN <-> CY. The shared
# ``BAAI/bge-m3`` embedder covers both natively (1024-d, multilingual),
# so no per-phase ContextKey overrides are required. The constants below
# are documentation-only; if the phase later needs a phase-specific
# regex, dialect normaliser, or token-level override, declare it here
# with a sibling ``# R2-exempt: <reason>`` comment so the
# ``_check_module_r1_to_r4`` linter doesn't flag it.
PHASE_LANGUAGE_PAIR: str = "en-cy"
PHASE_TABLE_URL: str = "lancedb://md:cianfhoghlaim/ciancheiltis/en_cy_chunks"

# Phase 2 (en-ga / Republic of Ireland) is bilingual EN <-> GA. The
# shared ``BAAI/bge-m3`` embedder covers both natively (1024-d,
# multilingual), so no per-phase ContextKey overrides are required
# here either. The Phase 2 App lives at
# ``ciancheiltis_en_ga_roi_embedding.py`` (sibling of the Phase 1 App
# ``ciancheiltis_en_cy_embedding.py``) and re-exports the constants
# below via ``from ._lifespan import PHASE_TABLE_URL_GA_ROI,
# PHASE_LANGUAGE_PAIR_GA_ROI`` so the R1 import line in the App is
# unambiguous about which phase it targets.
PHASE_LANGUAGE_PAIR_GA_ROI: str = "en-ga"
PHASE_TABLE_URL_GA_ROI: str = (
    "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_roi_chunks"
)

# Phase 3 (en-ga / Northern Ireland) is bilingual EN <-> GA. The
# shared ``BAAI/bge-m3`` embedder covers both natively (1024-d,
# multilingual), so no per-phase ContextKey overrides are required
# here either. The Phase 3 App lives at
# ``ciancheiltis_en_ga_ni_embedding.py`` (sibling of the Phase 1 App
# ``ciancheiltis_en_cy_embedding.py`` + the Phase 2 App
# ``ciancheiltis_en_ga_roi_embedding.py``) and re-exports the constants
# below via ``from ._lifespan import PHASE_TABLE_URL_GA_NI,
# PHASE_LANGUAGE_PAIR_GA_NI`` so the R1 import line in the App is
# unambiguous about which phase it targets.
PHASE_LANGUAGE_PAIR_GA_NI: str = "en-ga"
PHASE_TABLE_URL_GA_NI: str = (
    "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni_chunks"
)

# Phase 4 (en-gd / Scotland) is bilingual EN <-> GD. The
# shared ``BAAI/bge-m3`` embedder covers both natively (1024-d,
# multilingual), so no per-phase ContextKey overrides are required
# here either. The Phase 4 App lives at
# ``ciancheiltis_en_gd_embedding.py`` (sibling of the Phase 1 App
# ``ciancheiltis_en_cy_embedding.py`` + the Phase 2 App
# ``ciancheiltis_en_ga_roi_embedding.py`` + the Phase 3 App
# ``ciancheiltis_en_ga_ni_embedding.py``) and re-exports the constants
# below via ``from ._lifespan import PHASE_TABLE_URL_GD,
# PHASE_LANGUAGE_PAIR_GD`` so the R1 import line in the App is
# unambiguous about which phase it targets.
PHASE_LANGUAGE_PAIR_GD: str = "en-gd"
PHASE_TABLE_URL_GD: str = (
    "lancedb://md:cianfhoghlaim/ciancheiltis/en_gd_chunks"
)

# Phase 5 (en-gv / Isle of Man) is bilingual EN <-> GV. The
# shared ``BAAI/bge-m3`` embedder covers Manx (Gaelg) natively
# (1024-d, multilingual, partial coverage — Manx is a smaller
# corpus than CY/GA/GD so coverage is partial), so no per-phase
# ContextKey overrides are required here either. The Phase 5 App
# lives at ``ciancheiltis_en_gv_embedding.py`` (sibling of the
# Phase 1 App ``ciancheiltis_en_cy_embedding.py`` + the Phase 2
# App ``ciancheiltis_en_ga_roi_embedding.py`` + the Phase 3 App
# ``ciancheiltis_en_ga_ni_embedding.py`` + the Phase 4 App
# ``ciancheiltis_en_gd_embedding.py``) and re-exports the
# constants below via ``from ._lifespan import PHASE_TABLE_URL_GV,
# PHASE_LANGUAGE_PAIR_GV`` so the R1 import line in the App is
# unambiguous about which phase it targets.
#
# Note: Manx (Gaelg) is in **revival** status — there is no
# statutory bilingual publication duty and no statutory
# commissioner. The Phase 5 strict-gate (per
# ``dlt_sources/ciancheiltis/en_gv/__init__.py``) is "capture what
# bilingual content exists and surface it faithfully". The
# Phase 5 corpus is therefore expected to be smaller than the
# Phase 1 / Phase 4 sister corpora and the umbrella spec's
# content-based language detector is the gate.
PHASE_LANGUAGE_PAIR_GV: str = "en-gv"
PHASE_TABLE_URL_GV: str = (
    "lancedb://md:cianfhoghlaim/ciancheiltis/en_gv_chunks"
)

# Phase 6 (en-ga / EU level) is bilingual EN <-> GA. Irish is an
# official language and treaty language of the European Union under
# Article 55 of the Treaty on European Union (TEU) + Council
# Regulation No 1/1958. EU institutions translate selectively into
# Irish — the shared ``BAAI/bge-m3`` embedder covers GA natively
# (1024-d, multilingual). The Phase 6 App lives at
# ``ciancheiltis_en_ga_eu_embedding.py`` (sibling of the Phase 1
# ``ciancheiltis_en_cy_embedding.py`` + the Phase 2 App
# ``ciancheiltis_en_ga_roi_embedding.py`` + the Phase 3 App
# ``ciancheiltis_en_ga_ni_embedding.py`` + the Phase 4 App
# ``ciancheiltis_en_gd_embedding.py`` + the Phase 5 App
# ``ciancheiltis_en_gv_embedding.py``) and re-exports the constants
# below via ``from ._lifespan import PHASE_TABLE_URL_GA_EU,
# PHASE_LANGUAGE_PAIR_GA_EU`` so the R1 import line in the App is
# unambiguous about which phase it targets.
#
# Note: EU-level coverage is **partial** for Irish — many EU
# documents exist only in English plus a "summary in Irish" rather
# than a full Irish translation. The Phase 6 schema MUST capture
# the ``language_availability`` ∈ ``{"full", "partial",
# "summary_only"}`` as a first-class column (the constant
# ``PHASE_LANGUAGE_AVAILABILITY`` below); the BAML coverage gate
# flags the partial rows but does not drop them.
PHASE_LANGUAGE_PAIR_GA_EU: str = "en-ga"
PHASE_TABLE_URL_GA_EU: str = (
    "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu_chunks"
)
# The Phase 6 schema column for ``language_availability`` ∈
# ``{"full", "partial", "summary_only"}`` (the umbrella spec's
# Phase 6 § first-class-column rule). The Phase 6 App
# (``ciancheiltis_en_ga_eu_embedding.py``) reads this constant via
# the R1 import line so the BAML extraction client
# (``CiancheiltisGaEuExtract``) can populate the column without
# re-declaring the value at every call site.
PHASE_LANGUAGE_AVAILABILITY: str = "language_availability"


__all__ = [
    "COCOINDEX_AVAILABLE",
    "EMBEDDER",
    "EMBED_DIM",
    "EMBED_MODEL",
    "LANCEDB_URI",
    "LANCE_DB",
    "PHASE_LANGUAGE_PAIR",
    "PHASE_LANGUAGE_AVAILABILITY",
    "PHASE_LANGUAGE_PAIR_GA_EU",
    "PHASE_LANGUAGE_PAIR_GA_NI",
    "PHASE_LANGUAGE_PAIR_GA_ROI",
    "PHASE_LANGUAGE_PAIR_GD",
    "PHASE_LANGUAGE_PAIR_GV",
    "PHASE_TABLE_URL",
    "PHASE_TABLE_URL_GA_EU",
    "PHASE_TABLE_URL_GA_NI",
    "PHASE_TABLE_URL_GA_ROI",
    "PHASE_TABLE_URL_GD",
    "PHASE_TABLE_URL_GV",
    "RESOLVED_FILE_REGISTRY",
    "shared_lifespan",
]
