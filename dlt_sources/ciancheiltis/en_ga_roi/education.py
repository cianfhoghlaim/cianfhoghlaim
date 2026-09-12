"""PR0.6 — Phase 2 T3 (Education) — NCCA + curriculumonline.ie EN <-> GA DLT source.

Deferred stub. PR0.6 will pair the existing bilingual coverage
(NCCA + curriculumonline.ie ship EN + GA mirrors for every
Leaving Certificate syllabus) under the ciancheiltis bilingual-pair
wrapper.

Note: the underlying DLT source already exists at
``dlt_sources/british_isles/ireland/education/ncca.py`` +
``dlt_sources/british_isles/ireland/education/curriculumonline_syllabi.py``
(those are the canonical English-side pipelines + the Phase 1
BIEP substrate). This module is the **ciancheiltis-specific
bilingual-pair wrapper** that pairs every EN row with its GA mirror
under the Phase 2 language pair ``en-ga``.

Canonical pair surface (per the umbrella spec's Republic-of-Ireland
Phase 2 row):

- `ncca.ie/en/resources/...` paired with `ncca.ie/ga/acmhainni/...`
- `curriculumonline.ie/en/...` paired with `curriculumonline.ie/ga/...`
- `ncca.ie/en/curriculum-and-assessment-framework` paired with the
  GA slug (typically `/ga/cur-chreatam agus measúnaithe`)

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
is reused (per the Phase 1 § bilingual-page-validator section) to
canonicalise the (en, ga) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_ga_roi_embedding`` can write ONE LanceDB row per
article (with both EN and GA embeddings).
"""
SOURCE_ID = "ciancheiltis.en_ga_roi.education"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_roi/education_chunks"
THEME_CODE = "T3"
LANGUAGE_PAIR = "en-ga"


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.6 wires Firecrawl.

    PR0.6 will wrap the existing NCCA + curriculumonline.ie DLT
    sources from ``dlt_sources/british_isles/ireland/education/``
    and pair every EN row with its GA mirror.
    """
    del firecrawl_client
    return []


__all__ = ["LANCE_TABLE", "LANGUAGE_PAIR", "SOURCE_ID", "THEME_CODE"]
