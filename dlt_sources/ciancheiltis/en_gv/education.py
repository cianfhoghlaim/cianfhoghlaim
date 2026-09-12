"""PR0.9 — Phase 5 T3 (Education) — desc.gov.im + Bunscoill Ghaelgagh + Learn Manx DLT source.

Deferred stub. PR0.9 will pair the existing Isle of Man Department
of Education, Sport and Culture (DESC) + Bunscoill Ghaelgagh +
Learn Manx pipelines under the ciancheiltis bilingual-pair wrapper.

Note: the underlying DLT source already exists at
``dlt_sources/british_isles/isle_of_man/education/isle_of_man.py``
(plus its sibling helper
``dlt_sources/british_isles/isle_of_man/education/island/isle_of_man_education.py``
— Phase 1 BIEP substrate). This module is the **ciancheiltis-specific
bilingual-pair wrapper** that pairs every EN row with its GV mirror
under the Phase 5 language pair ``en-gv``.

Canonical pair surface (per the umbrella spec's Isle of Man Phase 5
row):

- ``desc.gov.im/...`` (Department of Education, Sport and Culture
  + the 32 Manx primary + 5 secondary schools + the University
  College Isle of Man + the Isle of Man College of Further
  Education + the Manx curriculum framework) paired with the
  Manx-language equivalents where published.
- ``bunscoill.gaelg.im`` (Bunscoill Ghaelgagh — the Manx-medium
  primary school established 2001 at St John's, the only
  Manx-medium school on the Isle of Man; operates under DESC with
  Culture Vannin co-funding) paired with its EN sister-school
  equivalents.
- ``learngaelg.im`` (Learn Manx — the online Manx-language
  learning platform run by Culture Vannin under the Manx
  Language Project) paired with its English-language sister
  resources.

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
is reused (per the Phase 1 § bilingual-page-validator section) to
canonicalise the (en, gv) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_gv_embedding`` can write ONE LanceDB row per
article (with both EN and GV embeddings).
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_gv.education"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_gv/education_chunks"
THEME_CODE = "T3"
LANGUAGE_PAIR = "en-gv"


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.9 wires Firecrawl.

    PR0.9 will wrap the existing DESC + Bunscoill Ghaelgagh +
    Learn Manx DLT source from
    ``dlt_sources/british_isles/isle_of_man/education/`` and pair
    every EN row with its GV mirror.

    Manx (Gaelg) is in revival status — the Manx-medium education
    surface is much smaller than the Welsh-medium (Phase 1) or
    Scottish-Gaelic-medium (Phase 4) equivalents; Bunscoill
    Ghaelgagh is the only Manx-medium primary school.
    """
    del firecrawl_client
    return []


__all__ = ["LANCE_TABLE", "LANGUAGE_PAIR", "SOURCE_ID", "THEME_CODE"]
