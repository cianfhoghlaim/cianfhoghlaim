"""PR0.10 — Phase 6 T1 (Legislation) — EUR-Lex CELEX + Treaties + Regulations + Directives + Decisions + International Agreements DLT source.

This is the en-ga / EU level theme T1 source: every CELEX-numbered
document published on EUR-Lex
(``https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:<num>``
+ the Irish-language switch
``https://eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:<num>``).

Irish is an **official language and treaty language** of the European
Union under Article 55 of the Treaty on European Union (TEU) and
Council Regulation No 1/1958. EU institutions translate
**selectively** into Irish — every EU treaty (TEU, TFEU, Charter) is
fully available in Irish, but many Regulations + Directives + Decisions
+ International Agreements exist only in English plus a "summary in
Irish" rather than a full Irish translation.

The canonical example (per the umbrella spec's Phase 6 row): the
Treaty on European Union, Irish-language edition, at
``https://eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:12012E``
— the canonical proof-of-existence for Irish-language EU primary law.

The schema MUST capture the ``language_availability`` ∈
``{"full", "partial", "summary_only"}`` as a first-class column (per
the umbrella spec's Phase 6 § `language_availability` requirement):

- ``full`` — full Irish translation published (Treaties, some
  Regulations + Decisions).
- ``partial`` — selected chapters / articles in Irish; remainder in
  English only.
- ``summary_only`` — only a "summary in Irish" exists alongside the
  English body.

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
canonicalises the (en, ga) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_ga_eu_embedding`` writes ONE LanceDB row per
CELEX-numbered document with both EN + GA embeddings + the
``language_availability`` tag.

The underlying single-language EUR-Lex pipeline already exists at
``dlt_sources/european_union/eur_lex/`` (the canonical CELEX
sub-tree — treaties + regulations + directives + decisions + CJEU
case law). This module is the **ciancheiltis-specific bilingual-pair
wrapper** that pairs every EN row with its GA mirror under the
Phase 6 language pair ``en-ga``.

PR0.10 will:

- ``firecrawl_map`` the EUR-Lex CELEX catalogue (the 6 sub-trees at
  ``eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:`` — Treaties,
  Regulations, Directives, Decisions, International Agreements, CJEU
  case law).
- For each CELEX number, request the Irish switch
  ``?uri=CELEX:<num>`` via ``firecrawl_scrape`` with the
  ``/GA/TXT/`` path; surface the
  ``language_availability ∈ {"full", "partial", "summary_only"}``
  per the umbrella spec's Phase 6 § schema-first-class-column rule.
- ``dlt_sources/ciancheiltis/_shared/language_detector.metadata_mismatch(...)``
  to flag the rare case where the ``metadata.language`` tag
  disagrees with the body (EUR-Lex typically ships
  ``metadata.language="EN"`` even for the Irish switch — the
  content-based detector is the gate).
- ``dlt_sources/ciancheiltis/_shared/opaque_url_scanner.classify_url(...)``
  to filter the ``CELEX:<num>`` opaque slugs into the per-phase
  discovery checklist.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_ga_eu.legislation"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu/legislation_chunks"
THEME_CODE = "T1"
LANGUAGE_PAIR = "en-ga"


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.10 wires Firecrawl.

    EU-level coverage is **partial** for Irish — many EU documents
    exist only in English plus a "summary in Irish" rather than a
    full Irish translation. PR0.10 will surface every CELEX-numbered
    document on EUR-Lex with its ``language_availability`` tag
    (``full`` / ``partial`` / ``summary_only``) per the umbrella
    spec's Phase 6 § first-class-column rule.
    """
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "SOURCE_ID",
    "THEME_CODE",
]
