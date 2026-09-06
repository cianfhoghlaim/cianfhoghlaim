"""Per-phase lifespan re-export for the ciancheiltis Phase 1 (en-cy / Wales) App.

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


__all__ = [
    "COCOINDEX_AVAILABLE",
    "EMBEDDER",
    "EMBED_DIM",
    "EMBED_MODEL",
    "LANCEDB_URI",
    "LANCE_DB",
    "PHASE_LANGUAGE_PAIR",
    "PHASE_TABLE_URL",
    "RESOLVED_FILE_REGISTRY",
    "shared_lifespan",
]
