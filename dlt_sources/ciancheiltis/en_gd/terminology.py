"""PR0.8 — Phase 4 T6 (Terminology) — Faclair + DASG terminology DLT source.

Deferred stub. PR0.8 will crawl the 2 canonical en-gd terminology
databases for Phase 4:

- ``faclair.ac.uk`` — the Faclair Gàidhlig / Scottish Gaelic
  Dictionary project (the University of Aberdeen + Sabhal Mòr Ostaig
  + DASG / UHI joint project). The canonical Phase 4 § T6 dataset
  for Scottish Gaelic, hosted by the University of Aberdeen
  (formerly the historical Dwelly's Dictionary at
  ``faclair.com``).
- ``dasg.ac.uk`` — the DASG (Dàta agus Sgeulachd Ghàidhlig)
  terminology database — the University of the Highlands and
  Islands project that maintains the canonical terminology +
  corpus + dictionary sources for Scottish Gaelic at dasg.ac.uk.
  DASG's terminology layer is paired with the Faclair as the two
  canonical en-gd term DBs for Phase 4.

The ``SCOTTISH_TERMINOLOGY_DBS`` constant below enumerates the
canonical Phase 4 entry points. Note: IATE (the EU inter-institutional
terminology database at Phase 2 + Phase 3 § T6) is NOT duplicated
here — Gaelic falls outside the EU treaty language regime and IATE
carries only a partial Scottish Gaelic term set under the EU-UK
Trade and Cooperation Agreement 2020.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_gd.terminology"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_gd/terminology_chunks"
THEME_CODE = "T6"
LANGUAGE_PAIR = "en-gd"


SCOTTISH_TERMINOLOGY_DBS: tuple[str, ...] = (
    # Faclair Gàidhlig — the canonical Scottish Gaelic dictionary
    # project (University of Aberdeen + Sabhal Mòr Ostaig joint).
    # Hosted at faclair.ac.uk; supersedes the historical Dwelly's
    # Dictionary.
    "https://www.faclair.ac.uk",
    # DASG (Dàta agus Sgeulachd Ghàidhlig) — the UHI terminology
    # + corpus database. Paired with Faclair as the second
    # canonical en-gd term DB.
    "https://www.dasg.ac.uk",
)


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.8 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "SCOTTISH_TERMINOLOGY_DBS",
    "SOURCE_ID",
    "THEME_CODE",
]