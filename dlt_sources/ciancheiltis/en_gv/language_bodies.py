"""PR0.9 — Phase 5 T5 (Language bodies) — Culture Vannin + sister Manx bodies DLT source.

Deferred stub. PR0.9 will crawl the bilingual or Manx-primary
publications of the 5 canonical sister bodies that govern the
revival of the Manx (Gaelg) language on the Isle of Man.

Unlike Phase 4 (Scotland / en-gd) — which has a founding statute
(the **Gaelic Language (Scotland) Act 2005**) and a statutory
principal body (Bòrd na Gàidhlig) — Manx has **no statutory
commissioner** and **no statutory bilingual publication duty**.
The 5 sister bodies below are voluntary / charitable / academic
institutions that curate the Manx revival corpus.

The 5 sister bodies (``MANX_LANGUAGE_BODIES`` constant below) are
the canonical Phase 5 § T5 dataset: every body publishes bilingual
or Manx-primary content on a voluntary basis, and every body is
the canonical ground truth for at least one subset of the en-gv
ground-truth pair.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_gv.language_bodies"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_gv/language_bodies_chunks"
THEME_CODE = "T5"
LANGUAGE_PAIR = "en-gv"


MANX_LANGUAGE_BODIES: tuple[str, ...] = (
    # Culture Vannin — the Manx cultural foundation, established
    # 1985 as the Manx Heritage Foundation, renamed Culture Vannin
    # 2010. The principal body for Manx cultural + linguistic
    # revival on the Isle of Man. Funds the Manx Language Project,
    # Bunscoill Ghaelgagh, the Learn Manx platform, and the Manx
    # Music + Dance development agency. Publishes both English +
    # Manx-primary content at culturevannin.im.
    "culturevannin.im",
    # Learn Manx — the online Manx-language learning platform,
    # launched 2016 by Culture Vannin under the Manx Language
    # Project. Hosts the canonical Manx-language course at
    # learngaelg.im with audio + grammar + vocabulary resources
    # in both English + Manx.
    "learngaelg.im",
    # Bunscoill Ghaelgagh — the Manx-medium primary school,
    # established 2001 at St John's (the only Manx-medium school
    # on the Isle of Man). Operates under DESC with Culture Vannin
    # co-funding. Publishes Manx-primary + bilingual EN <-> GV
    # content at bunscoill.gaelg.im.
    "bunscoill.gaelg.im",
    # Manx Language Service — the Isle of Man Government's Manx
    # language service (operated jointly by the Cabinet Office +
    # Culture Vannin). Provides Manx-language translation +
    # interpretation for the Isle of Man Government + publishes
    # the Manx-language equivalents of official notices + forms
    # under the revival mandate.
    "manxlanguage.im",
    # Gaelg Corpus — the University of Cambridge + Culture Vannin
    # joint Manx-language corpus project. Hosts the canonical
    # Manx-language text + audio corpus at corpus.gaelg.im,
    # including the historical archive of the Manx Bible
    # translation + the Llunyschtal Manx newspaper archive.
    "corpus.gaelg.im",
)


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.9 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "MANX_LANGUAGE_BODIES",
    "SOURCE_ID",
    "THEME_CODE",
]
