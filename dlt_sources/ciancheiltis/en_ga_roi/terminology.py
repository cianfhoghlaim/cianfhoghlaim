"""PR0.6 — Phase 2 T6 (Terminology) — Téarma + Teanglann + IATE DLT source.

Deferred stub. PR0.6 will crawl the 3 canonical en-ga terminology
databases:

- `tearma.ie` — the Foras na Gaeilge national terminology database
  (the canonical Irish-language side of the en-ga ground-truth pair).
- `teanglann.ie` — the NUI Maynooth Irish-English / English-Irish
  dictionary (also hosts Foclóir Gaeilge-Gaeilge and the older
  Foclóir Béarla-Gaeilge / Foclóir Gaeilge-Béarla dictionaries).
- `iate.europa.eu` — the EU inter-institutional terminology database
  (covers Irish as a treaty language; relevant for both Phase 2
  ROI and Phase 6 EU).

These three are the canonical Phase 2 § T6 surface. The
``IRISH_TERMINOLOGY_DBS`` constant below enumerates the canonical
entry points.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_ga_roi.terminology"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_roi/terminology_chunks"
THEME_CODE = "T6"
LANGUAGE_PAIR = "en-ga"


IRISH_TERMINOLOGY_DBS: tuple[str, ...] = (
    "https://www.tearma.ie",
    "https://www.teanglann.ie",
    "https://iate.europa.eu",
)


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.6 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = [
    "IRISH_TERMINOLOGY_DBS",
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "SOURCE_ID",
    "THEME_CODE",
]
