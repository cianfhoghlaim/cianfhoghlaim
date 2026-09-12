"""PR0.6 — Phase 2 T4 (Healthcare) — HSE (Health Service Executive) DLT source.

Deferred stub. PR0.6 will crawl the HSE's bilingual EN <-> GA pair
of every patient-information leaflet, condition page and service
description.

Canonical example: `https://www2.hse.ie/conditions/<slug>/` — the HSE
hosts its public-facing condition library at ``www2.hse.ie`` (a
WordPress-driven CMS) with parallel IR + EN pages under
``/ga/.../`` (Irish) and ``/en/.../`` (English) slug patterns.

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
canonicalises the (en, ga) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_ga_roi_embedding`` writes ONE LanceDB row per
patient-information page (with both EN + GA embeddings).
"""
SOURCE_ID = "ciancheiltis.en_ga_roi.healthcare"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_roi/healthcare_chunks"
THEME_CODE = "T4"
LANGUAGE_PAIR = "en-ga"


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.6 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = ["LANCE_TABLE", "LANGUAGE_PAIR", "SOURCE_ID", "THEME_CODE"]
