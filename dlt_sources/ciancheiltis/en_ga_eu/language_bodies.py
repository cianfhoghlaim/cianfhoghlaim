"""PR0.10 — Phase 6 T5 (Language bodies) — EU Council Irish Language Unit + Oifig an Choimisinéara Teanga DLT source.

This is the en-ga / EU level theme T5 source: every canonical EU
language body that governs the use of Irish within the EU
institutions + the Irish-language commissioner who oversees the
implementation of the Official Languages Act 2003 in the Republic
of Ireland.

The umbrella spec's Phase 6 § T5 row enumerates two distinct
categories:

1. **EU-side language bodies** (``EU_LANGUAGE_BODIES`` constant
   below) — the EU institutions' own Irish-language services + the
   Irish Language Commissioner (Coimisinéir Teanga) who monitors
   the Irish-language regime across the EU institutions.
2. **National-language oversight** — Oifig an Choimisinéara Teanga
   (the Office of the Irish Language Commissioner) is the
   independent statutory office under the Official Languages Act
   2003 — included here as a Phase 6 cross-reference because its
   scope extends to EU institutions operating in Ireland.

Canonical example: the EU Council Irish Language Unit
(``https://www.consilium.europa.eu/ga/``) — the dedicated Irish-
language team within the General Secretariat of the Council of
the EU that translates + interprets high-level Council documents
into Irish.

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
is reused (per the Phase 1 § bilingual-page-validator section) to
canonicalise the (en, ga) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_ga_eu_embedding`` can write ONE LanceDB row per
language-body publication (with both EN and GA embeddings where
the GA side exists; the BAML coverage gate + ``language_availability``
tag flag the partial rows but does not drop them).
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_ga_eu.language_bodies"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu/language_bodies_chunks"
THEME_CODE = "T5"
LANGUAGE_PAIR = "en-ga"


# The EU-side sister bodies that govern the use of Irish within the
# EU institutions + the Irish Language Commissioner (Coimisinéir
# Teanga) who monitors the Irish-language regime across the EU
# institutions. Every body is the canonical ground truth for at
# least one subset of the en-ga Phase 6 ground-truth pair.
EU_LANGUAGE_BODIES: tuple[str, ...] = (
    # EU Council Irish Language Unit — the dedicated Irish-language
    # team within the General Secretariat of the Council of the EU
    # that translates + interprets high-level Council documents
    # into Irish. Publishes a small Irish-language presence on the
    # Council's web (the ``/ga/`` switch under
    # ``consilium.europa.eu``).
    "consilium.europa.eu/ga",
    # Coimisinéir Teanga — the Irish Language Commissioner, the
    # independent statutory office under the Official Languages Act
    # 2003 (``https://www.coimisineir.ie``). Monitors the Irish-
    # language regime across public bodies in the Republic of
    # Ireland and (selectively) EU institutions operating in
    # Ireland. Publishes annual reports + investigations in
    # bilingual EN <-> GA.
    "coimisineir.ie",
    # Aonad na Gaeilge / Irish Language Unit (European Parliament)
    # — the European Parliament's dedicated Irish-language team
    # that provides interpretation + translation for the
    # Parliament's Irish-language plenary sessions. Publishes
    # bilingual EN <-> GA press releases for plenary debates.
    "europarl.europa.eu/ga",
    # Oifig an Choimisinéara Teanga — the Office of the Irish
    # Language Commissioner (the support office for the
    # Commissioner). Hosts the bilingual EN <-> GA investigation
    # archive + the statutory compliance reports.
    "oifigcoimisineara.ie",
    # Irish Language Translation Centre (European Commission) —
    # the European Commission's Irish-language translation service
    # within DG Translation. Provides the Irish-language
    # translations of selected Commission publications (the
    # Commission Irish-language presence is partial — selected
    # press materials + selected legislative summaries).
    "ec.europa.eu/info/ga",
)


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.10 wires Firecrawl.

    EU-level Irish-language coverage is partial — the EU Council +
    Parliament + Commission each maintain a dedicated Irish-
    language team but publish selectively. PR0.10 will surface
    every bilingual language-body publication with its
    ``language_availability`` tag.
    """
    del firecrawl_client
    return []


__all__ = [
    "EU_LANGUAGE_BODIES",
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "SOURCE_ID",
    "THEME_CODE",
]
