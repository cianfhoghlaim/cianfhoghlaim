"""PR0.6 — Phase 2 T5 (Language bodies) — Foras na Gaeilge + Gaois DLT source.

Deferred stub. PR0.6 will crawl the bilingual (or Irish-primary)
publications of the 6 cross-border language bodies that govern the
Irish language under the **Official Languages Act 2003** + the
**20-Year Strategy for the Irish Language 2010-2030** + the
**Gaeltacht Act 2012**.

The 6 sister bodies (``IRISH_LANGUAGE_BODIES`` constant below) are
the canonical Phase 2 Phase 2 § T5 dataset: every body publishes
bilingual or Irish-only content required by statute, and every
body is the canonical ground truth for at least one subset of the
en-ga ground-truth pair.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_ga_roi.language_bodies"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_roi/language_bodies_chunks"
THEME_CODE = "T5"
LANGUAGE_PAIR = "en-ga"


IRISH_LANGUAGE_BODIES: tuple[str, ...] = (
    # The cross-border North/South body responsible for the promotion
    # of the Irish language across the island of Ireland (the successor
    # to Bord na Gaeilge, est. 1999 per the Good Friday Agreement).
    "forasnagaeilge.ie",
    # The linguistic research + lexicographic publisher (host of
    # Gaois, the national Irish-language terminology database,
    # Foclóirí Stairiúla, and the Irish-language newspaper archive).
    "gaois.ie",
    # The regulator of Irish-medium schools (Gaelscoileanna) and the
    # Irish-medium Aonad support network across the Republic.
    "cna.ie",
    # The regional authority for the Gaeltacht regions (the Irish-
    # speaking districts of the Republic); publishes the Gaeltacht
    # development plans + the Irish-medium placename database.
    "udaras.ie",
    # The Irish-language public-service broadcaster (TG4 + TG4 Player);
    # publishes bilingual subtitles + programme catalogues.
    "tg4.ie",
    # The Gaeltacht radio service of RTÉ; publishes bilingual podcasts
    # + script archives for the Raidió na Gaeltachta programming strand.
    "rte.ie/rnag",
)


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.6 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = [
    "IRISH_LANGUAGE_BODIES",
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "SOURCE_ID",
    "THEME_CODE",
]
