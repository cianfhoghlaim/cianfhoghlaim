"""PR0.10 — Phase 6 T7 (Courts & Tribunals) — CJEU case law DLT source.

This is the en-ga / EU level theme T7 source: every CJEU (Court of
Justice of the European Union) judgment + opinion + order at
``curia.europa.eu`` paired with its Irish-language equivalent where
published.

**Partial Phase 6 T7 (caveat prominently documented)**: CJEU case
law exists primarily in **English only**. The CJEU publishes every
judgment + opinion + order in the language of the case (the
"language of the case" is the official EU language chosen by the
parties), and historically the overwhelming majority of cases are
heard in English. Irish-language CJEU case law is **rare** —
typically limited to cases where the Irish Government is a party
or where the language of the case was explicitly Irish. Most
CJEU case law is therefore English-only.

The umbrella spec acknowledges Phase 6 § T7 as a "partial" theme
— the BAML coverage gate will flag most rows as English-only or
summary_only.

Canonical example: a CJEU judgment at
``https://curia.europa.eu/juris/liste.jsf?language=en&num=<case_no>``
paired with its Irish-language equivalent at
``https://curia.europa.eu/juris/liste.jsf?language=ga&num=<case_no>``
where published.

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
canonicalises the (en, ga) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_ga_eu_embedding`` writes ONE LanceDB row per
CJEU judgment with both EN + GA embeddings where the GA side
exists. The ``language_availability`` tag is the critical signal
here — most rows will be tagged ``summary_only`` or English-only.

The underlying single-language CJEU pipeline already exists at
``dlt_sources/european_union/eur_lex/cjeu_case_law.py`` (the
canonical CJEU case law DLT source). This module is the
**ciancheiltis-specific bilingual-pair wrapper** that pairs every
EN row with its GA mirror under the Phase 6 language pair
``en-ga``.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_ga_eu.courts"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu/courts_chunks"
THEME_CODE = "T7"
LANGUAGE_PAIR = "en-ga"

# Phase 6 T7 is partial coverage — most CJEU case law exists in
# English only. The umbrella spec acknowledges Phase 6 § T7 as a
# "partial" theme — the BAML coverage gate will flag most rows
# as English-only or summary_only. Subagent 3 picks this up for
# the MotherDuck Dive caveat.
PARTIAL_COVERAGE = True


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.10 wires Firecrawl.

    Most CJEU case law exists in English only. PR0.10 will pair
    every CJEU judgment with its Irish-language equivalent where
    published and surface the ``language_availability`` tag
    (``full`` / ``partial`` / ``summary_only``).
    """
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "PARTIAL_COVERAGE",
    "SOURCE_ID",
    "THEME_CODE",
]
