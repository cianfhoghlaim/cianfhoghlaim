"""PR0.8 — Phase 4 T4 (Healthcare) — NHS Scotland + Gaelic patient info DLT source.

Deferred stub. PR0.8 will crawl the NHS Scotland bilingual EN <-> GD
pair of every patient-information leaflet, condition page and
service description published by the 14 territorial Health Boards
(NHS Ayrshire and Arran, NHS Borders, NHS Dumfries and Galloway,
NHS Fife, NHS Forth Valley, NHS Grampian, NHS Greater Glasgow and
Clyde, NHS Highland, NHS Lanarkshire, NHS Lothian, NHS Orkney,
NHS Shetland, NHS Tayside, NHS Western Isles) plus NHS24
(``nhsinform.scot``) and the Scottish Ambulance Service.

Canonical example: ``https://www.nhsinform.scot/`` — NHS Scotland's
public information portal hosts its patient-information library at
``nhsinform.scot`` with parallel EN pages (default at the root) and
Gaelic-language mirrors under ``/gd/...`` (e.g.
``nhsinform.scot/gd/...``).

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
canonicalises the (en, gd) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_gd_embedding`` writes ONE LanceDB row per
patient-information page (with both EN + GD embeddings).

Phase 4 differs from Phase 3 (HSC NI) in that NHS Scotland's
patient-information surface is larger than HSC NI but ships fewer
Gaelic-language mirrors — the BAML coverage gap is expected to be
wider in Phase 4 than Phase 3 and the umbrella spec's content-based
language detector is the gate.
"""
SOURCE_ID = "ciancheiltis.en_gd.healthcare"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_gd/healthcare_chunks"
THEME_CODE = "T4"
LANGUAGE_PAIR = "en-gd"


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.8 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = ["LANCE_TABLE", "LANGUAGE_PAIR", "SOURCE_ID", "THEME_CODE"]