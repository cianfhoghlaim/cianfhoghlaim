"""dlt_sources/breton_cornish/british_isles — Breton + Cornish DLT sources.

Per the **2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1**
openspec change (Phase 14 of the cianfhoghlaim-nua v6 era plan).

Brittany (Breizh) + Cornwall historically share a Brythonic Celtic
linguistic continuum. The two languages (Brezhoneg + Kernewek) are
sister-repo lift targets for ``ciancheiltis``, hence they live in
their own top-level ``breton_cornish/`` package (rather than under
the country-specific education DLT sub-packages).

The ``__init__.py`` re-exports the local source modules.
"""
from __future__ import annotations

from . import breton_vernacular  # Phase 14 — vernacular BR DLT source
from . import cornish_vernacular  # Phase 14 — vernacular KW DLT source

__all__ = ['breton_vernacular', 'cornish_vernacular']
