"""PR0.10 — Phase 6 T3 (Education) — Eurydice + Cedefop DLT source.

This is the en-ga / EU level theme T3 source: the bilingual
EN <-> GA pair of every Eurydice + Cedefop publication surfaced
by the canonical EU education agency portals.

Canonical example: the Eurydice ``eurydice.europa.eu`` portal (the
EU-wide education information network that publishes comparative
reports on European education systems in all 24 official EU
languages, including Irish) paired with its Irish-language
equivalents where published — the EU Irish-language education
presence is partial (most publications are English-only with
selected Irish summaries).

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
is reused (per the Phase 1 § bilingual-page-validator section) to
canonicalise the (en, ga) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_ga_eu_embedding`` can write ONE LanceDB row per
article (with both EN and GA embeddings where the GA side exists;
the BAML coverage gate + ``language_availability`` tag flag the
partial rows but does not drop them).

The underlying single-language DLT source already exists at
``dlt_sources/european_union/education/eurydice.py`` +
``dlt_sources/european_union/education/cedefop.py`` (the canonical
EU education agency pipelines). This module is the
**ciancheiltis-specific bilingual-pair wrapper** that pairs every
EN row with its GA mirror under the Phase 6 language pair
``en-ga``.

Canonical pair surface (per the umbrella spec's Phase 6 § T3 row):

- ``eurydice.europa.eu`` — the EU-wide education information
  network; comparative reports on European education systems
  in all 24 official EU languages, including Irish.
- ``cedefop.europa.eu`` — the European Centre for the Development
  of Vocational Training; publishes skills + vocational training
  reports; selected Irish-language editions where published.

The EU Irish-language education surface is partial — most
publications are English-only with selected Irish summaries. The
umbrella spec acknowledges Phase 6 § T3 as a "partial" theme —
the BAML coverage gate will flag most rows as English-only.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_ga_eu.education"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu/education_chunks"
THEME_CODE = "T3"
LANGUAGE_PAIR = "en-ga"


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.10 wires Firecrawl.

    EU-level coverage is **partial** for Irish — most EU education
    publications are English-only with selected Irish summaries.
    PR0.10 will pair every English Eurydice / Cedefop publication
    with whatever Irish content exists and surface the
    ``language_availability`` tag.
    """
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "SOURCE_ID",
    "THEME_CODE",
]
