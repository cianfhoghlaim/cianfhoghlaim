"""PR0.1 — Foclóir Gàidhlig-Gaeilge (Kevin Scannell) cross-Celtic dictionary.

`https://kevinscannell.com/files/gd2ga.pdf` is the canonical
Scottish Gaelic → Irish cross-Celtic dictionary. It supports the
ciancheiltis cross-Celtic concept graph by giving a direct
mapping from `gd` terms to their `ga` equivalents — useful for the
Phase 4 → Phase 2 cross-walk and for the bilingual concept registry
seed.

This is a deferred stub — `firecrawl_parse` on the PDF will yield
the structured term pairs in PR0.3.
"""
from __future__ import annotations

from dlt_sources.ciancheiltis.clarin_uk import FOCLOIR_GD_GA_URL


SOURCE_ID = "ciancheiltis.clarin_uk.focloir_gd_ga"


__all__ = ["SOURCE_ID", "FOCLOIR_GD_GA_URL"]
