"""PR0.10 — Phase 6 T6 (Terminology) — IATE + Teanglann DLT source.

This is the en-ga / EU level theme T6 source: every bilingual
EN <-> GA term pair from the EU inter-institutional terminology
database IATE + the Irish-language terminology database Teanglann.

Phase 6 differs from the Phase 2 (en-ga / ROI) T6 in two important
ways:

1. **IATE** (Inter-Active Terminology for Europe,
   ``https://iate.europa.eu``) is the EU inter-institutional
   terminology database — the canonical Phase 6 entry point for
   EU-level terminology. Phase 6 includes IATE; Phase 2 (en-ga /
   ROI) does not (Phase 2 uses Téarma + Foclóir + Logainm.ie
   alone — the Republic of Ireland's national terminology stack).
2. **Teanglann** (``https://www.teanglann.ie``) — Foras na
   Gaeilge's Irish-language terminology database. Teanglann is the
   canonical en-ga term database for both Phase 2 (Republic of
   Ireland) and Phase 6 (EU level). It is included in both phases
   because Teanglann terms are used by EU institutions that
   translate into Irish.

The ``EU_TERMINOLOGY_DBS`` constant below enumerates the two
canonical Phase 6 entry points.

Canonical pair surface (per the umbrella spec's Phase 6 § T6 row):

- ``https://iate.europa.eu`` — the EU inter-institutional
  terminology database. The canonical EU-level EN <-> GA term
  database. Covers 24 official EU languages; Irish coverage is
  partial (selected high-frequency EU terms only).
- ``https://www.teanglann.ie`` — Foras na Gaeilge's Irish-language
  terminology database. The canonical Phase 2 + Phase 6 EN <-> GA
  term database for Irish-language content (general-purpose
  Irish-language terms).

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
canonicalises the (en, ga) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_ga_eu_embedding`` writes ONE LanceDB row per term
with both EN + GA embeddings.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_ga_eu.terminology"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu/terminology_chunks"
THEME_CODE = "T6"
LANGUAGE_PAIR = "en-ga"


# The two canonical Phase 6 terminology databases — the EU-level
# IATE database (canonical for EU institutions) + the Irish-language
# Teanglann database (canonical for Irish-language content broadly).
# Both databases surface bilingual EN <-> GA term pairs.
EU_TERMINOLOGY_DBS: tuple[str, ...] = (
    # IATE — the EU inter-institutional terminology database.
    # The canonical EU-level EN <-> GA term database; covers 24
    # official EU languages; Irish coverage is partial (selected
    # high-frequency EU terms only).
    "https://iate.europa.eu",
    # Teanglann — Foras na Gaeilge's Irish-language terminology
    # database. The canonical Phase 2 + Phase 6 EN <-> GA term
    # database for Irish-language content (general-purpose Irish-
    # language terms).
    "https://www.teanglann.ie",
)


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.10 wires Firecrawl.

    Phase 6 T6 surfaces every bilingual EN <-> GA term pair from
    IATE + Teanglann. Irish coverage in IATE is partial — selected
    high-frequency EU terms only — so PR0.10 will tag every term
    with its ``language_availability`` value.
    """
    del firecrawl_client
    return []


__all__ = [
    "EU_TERMINOLOGY_DBS",
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "SOURCE_ID",
    "THEME_CODE",
]
