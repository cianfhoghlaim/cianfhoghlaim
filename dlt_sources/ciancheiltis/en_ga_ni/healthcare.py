"""PR0.7 — Phase 3 T4 (Healthcare) — NI Health & Social Care (HSC) DLT source.

Deferred stub. PR0.7 will crawl the Health & Social Care (HSC) NI
bilingual EN <-> GA pair of every patient-information leaflet,
condition page and service description published by the 6 Health &
Social Care Trusts (Belfast, Northern, South Eastern, Southern, Western,
and the NI Ambulance Service).

Canonical example: ``https://online.hscni.net/`` — the HSC NI public
information portal hosts its patient-information library at
``online.hscni.net`` with parallel EN pages (default at the root) and
Irish-language mirrors under ``/ga/...`` (e.g.
``online.hscni.net/ga/...``).

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
canonicalises the (en, ga) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_ga_ni_embedding`` writes ONE LanceDB row per
patient-information page (with both EN + GA embeddings).

Phase 3 differs from Phase 2 (HSE — Ireland) in that the HSC NI
patient-information surface is smaller than the HSE equivalent and
ships fewer Irish-language mirrors — the BAML coverage gap is
expected to be wider in Phase 3 than Phase 2 and the umbrella spec's
content-based language detector is the gate.
"""
SOURCE_ID = "ciancheiltis.en_ga_ni.healthcare"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni/healthcare_chunks"
THEME_CODE = "T4"
LANGUAGE_PAIR = "en-ga"


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.7 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = ["LANCE_TABLE", "LANGUAGE_PAIR", "SOURCE_ID", "THEME_CODE"]
