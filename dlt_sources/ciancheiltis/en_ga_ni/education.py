"""PR0.7 — Phase 3 T3 (Education) — CCEA + Education Authority NI DLT source.

Deferred stub. PR0.7 will pair the existing CCEA (Council for the
Curriculum, Examinations & Assessment — the NI statutory curriculum
body) and Education Authority NI (EANI / Education NI) pipelines
under the ciancheiltis bilingual-pair wrapper.

Note: the underlying DLT source already exists at
``dlt_sources/british_isles/northern_ireland/education/ccea_qualifications.py``
(plus its sibling helpers ``_ccea_curriculum_helpers.py``,
``education_ni.py``, ``etini.py``, ``irish_medium_ni.py``,
``ni_curriculum.py`` — Phase 1 BIEP substrate). This module is the
**ciancheiltis-specific bilingual-pair wrapper** that pairs every EN
row with its GA mirror under the Phase 3 language pair ``en-ga``.

Canonical pair surface (per the umbrella spec's Northern Ireland
Phase 3 row + the Identity and Language (Northern Ireland) Act 2022
which mandates bilingual support for Irish-medium schools):

- ``ccea.org.uk/...`` (CCEA qualifications, GCSE / A-level /
  AS-level specifications) paired with the
  Irish-medium Irish-language equivalents under the Irish-medium
  syllabus where published.
- ``eani.org.uk/...`` (Education Authority NI parents + pupils +
  schools service pages) paired with the Irish-medium equivalents
  where published.
- The Irish-medium Aonad / Gaelscoil / Meánscoil portal at
  ``ccea.org.uk/irish-medium`` paired with its GA mirror.
- The CCEA primary + post-primary curriculum for Irish-medium
  schools under
  ``ccea.org.uk/curriculum/irish-medium-overview``.

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
is reused (per the Phase 1 § bilingual-page-validator section) to
canonicalise the (en, ga) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_ga_ni_embedding`` can write ONE LanceDB row per
article (with both EN and GA embeddings).
"""
SOURCE_ID = "ciancheiltis.en_ga_ni.education"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni/education_chunks"
THEME_CODE = "T3"
LANGUAGE_PAIR = "en-ga"


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.7 wires Firecrawl.

    PR0.7 will wrap the existing CCEA + Education Authority NI DLT
    sources from ``dlt_sources/british_isles/northern_ireland/education/``
    and pair every EN row with its GA mirror.
    """
    del firecrawl_client
    return []


__all__ = ["LANCE_TABLE", "LANGUAGE_PAIR", "SOURCE_ID", "THEME_CODE"]
