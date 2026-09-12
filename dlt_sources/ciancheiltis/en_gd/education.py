"""PR0.8 — Phase 4 T3 (Education) — Education Scotland + SQA + Sabhal Mòr Ostaig DLT source.

Deferred stub. PR0.8 will pair the existing Education Scotland
(Foghlam Alba) and Scottish Qualifications Authority (SQA) +
Sabhal Mòr Ostaig (the Gaelic-medium higher education institute)
pipelines under the ciancheiltis bilingual-pair wrapper.

Note: the underlying DLT sources already exist at
``dlt_sources/british_isles/scotland/education/curriculum_for_excellence.py``
(plus its sibling helpers ``_curriculum_for_excellence_helpers.py``,
``gaelic_curriculum.py``, ``insight_benchmarking.py``,
``sqa_qualifications.py`` + the ``sqa/`` sub-tree — Phase 1 BIEP
substrate). This module is the **ciancheiltis-specific
bilingual-pair wrapper** that pairs every EN row with its GD mirror
under the Phase 4 language pair ``en-gd``.

Canonical pair surface (per the umbrella spec's Scotland Phase 4
row + the Gaelic Language (Scotland) Act 2005 which mandates
bilingual support for Gaelic-medium education):

- ``education.gov.scot/...`` (Education Scotland / Foghlam Alba
  Curriculum for Excellence benchmarks, experiences and outcomes,
  plus the Gaelic-medium education framework under
  ``education.gov.scot/.../gaelicmediumeducation``) paired with the
  Gaelic-medium equivalents where published under the ``gd/`` prefix.
- ``sqa.org.uk/...`` (SQA qualifications — National 5 / Higher /
  Advanced Higher / National Courses / Scottish Vocational
  Qualifications / SVQ specifications) paired with the Gaelic-medium
  equivalents where published.
- ``smo.uhi.ac.uk/...`` (Sabhal Mòr Ostaig — the Gaelic-medium
  higher-education institute on Skye; publishes Gaelic-primary
  degrees + the MSc in Gaelic-medium Education content) paired
  with the English equivalents.
- The Gaelic-medium curriculum portal at
  ``education.gov.scot/.../gaelicmediumeducation`` paired with its
  GD mirror.

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
is reused (per the Phase 1 § bilingual-page-validator section) to
canonicalise the (en, gd) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_gd_embedding`` can write ONE LanceDB row per
article (with both EN and GD embeddings).
"""
SOURCE_ID = "ciancheiltis.en_gd.education"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_gd/education_chunks"
THEME_CODE = "T3"
LANGUAGE_PAIR = "en-gd"


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.8 wires Firecrawl.

    PR0.8 will wrap the existing Education Scotland / Foghlam Alba +
    SQA + Sabhal Mòr Ostaig DLT sources from
    ``dlt_sources/british_isles/scotland/education/`` and pair every
    EN row with its GD mirror.
    """
    del firecrawl_client
    return []


__all__ = ["LANCE_TABLE", "LANGUAGE_PAIR", "SOURCE_ID", "THEME_CODE"]