"""PR0.7 — Phase 3 T6 (Terminology) — IATE DLT source.

Deferred stub. PR0.7 will crawl the 1 canonical en-ga terminology
database for Phase 3:

- ``iate.europa.eu`` — the EU inter-institutional terminology database
  (covers Irish as a treaty language). Phase 3 shares this resource
  with Phase 2 (Republic of Ireland) — there is no separate NI-specific
  term DB because NI follows the same Irish-language standard as the
  Republic under the *Caighdeán Oifigiúil* (the Official Standard for
  Modern Irish).

The ``NI_TERMINOLOGY_DBS`` constant below enumerates the canonical
Phase 3 entry points. Note: Téarma + Teanglann (the Republic of
Ireland-specific term DBs at Phase 2 § T6) are NOT duplicated here —
they are already covered by the Phase 2 en_ga_roi/terminology.py stub
and re-exposed via the umbrella spec's bilingual-concept registry
(``stedding/education/bilingual_concepts/ciancheiltis_en_ga_roi__T6.jsonl``).
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_ga_ni.terminology"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni/terminology_chunks"
THEME_CODE = "T6"
LANGUAGE_PAIR = "en-ga"


NI_TERMINOLOGY_DBS: tuple[str, ...] = (
    # IATE — the EU inter-institutional terminology database (covers
    # Irish as a treaty language; relevant for both Phase 2 ROI and
    # Phase 3 NI because both jurisdictions share the same official
    # Irish-language standard).
    "https://iate.europa.eu",
)


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.7 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "NI_TERMINOLOGY_DBS",
    "SOURCE_ID",
    "THEME_CODE",
]
