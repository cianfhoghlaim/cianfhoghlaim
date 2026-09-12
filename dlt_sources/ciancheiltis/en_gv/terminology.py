"""PR0.9 — Phase 5 T6 (Terminology) — Gaelg Corpus ONLY DLT source.

Deferred stub. PR0.9 will crawl the single canonical en-gv
terminology database for Phase 5:

- ``corpus.gaelg.im`` — the Gaelg Corpus (the University of
  Cambridge + Culture Vannin joint Manx-language corpus project).
  Hosts the canonical Manx-language text + audio corpus +
  terminology database, including the historical archive of the
  Manx Bible translation + the Llunyschtal Manx newspaper
  archive + the modern Manx-language curriculum vocabulary.

Phase 5 differs from Phase 4 in two important ways:

1. **No shared IATE**: IATE (the EU inter-institutional
   terminology database used in Phase 2 + Phase 3 § T6) is NOT
   duplicated here — Gaelic falls outside the EU treaty language
   regime and Manx falls outside the post-Brexit UK-EU Trade and
   Cooperation Agreement 2020 entirely (the Isle of Man is a
   Crown Dependency, not part of the UK for treaty purposes).
2. **Single corpus DB**: Manx has only ONE canonical terminology
   corpus — ``corpus.gaelg.im`` — versus Phase 4's two (Faclair
   + DASG) and Phase 1 / Phase 2 / Phase 3's several (TermOnom +
   Porth Termau + logainm.ie etc.). The ``MANX_TERMINOLOGY_DBS``
   constant below enumerates the single canonical Phase 5 entry
   point.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_gv.terminology"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_gv/terminology_chunks"
THEME_CODE = "T6"
LANGUAGE_PAIR = "en-gv"


MANX_TERMINOLOGY_DBS: tuple[str, ...] = (
    # Gaelg Corpus — the University of Cambridge + Culture Vannin
    # joint Manx-language corpus project. The single canonical
    # en-gv terminology database for Phase 5 (no Faclair-equivalent
    # + no DASG-equivalent exist for Manx — only this single
    # corpus).
    "https://corpus.gaelg.im",
)


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.9 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "MANX_TERMINOLOGY_DBS",
    "SOURCE_ID",
    "THEME_CODE",
]
