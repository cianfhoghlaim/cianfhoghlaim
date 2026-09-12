"""PR0.8 — Phase 4 T5 (Language bodies) — Bòrd na Gàidhlig + sister bodies DLT source.

Deferred stub. PR0.8 will crawl the bilingual (or Gaelic-primary)
publications of the 6 canonical sister bodies that govern the
Scottish Gaelic language in Scotland under the **Gaelic Language
(Scotland) Act 2005** (the founding statute) + the **Scotland Act
1998** (the devolution constitutional basis) + the **European
Charter for Regional or Minority Languages** (UK ratification 2001,
extended to Scottish Gaelic in 2003).

The 6 sister bodies (``SCOTTISH_GAELIC_BODIES`` constant below) are
the canonical Phase 4 § T5 dataset: every body publishes bilingual or
Gaelic-only content required by statute, and every body is the
canonical ground truth for at least one subset of the en-gd
ground-truth pair.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_gd.language_bodies"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_gd/language_bodies_chunks"
THEME_CODE = "T5"
LANGUAGE_PAIR = "en-gd"


SCOTTISH_GAELIC_BODIES: tuple[str, ...] = (
    # Bòrd na Gàidhlig — the principal statutory body for the
    # promotion of Scottish Gaelic, established under section 2 of the
    # Gaelic Language (Scotland) Act 2005. Operates the Gaelic
    # Language Plans scheme (which requires public authorities in
    # Scotland to prepare + maintain a Gaelic Language Plan) and
    # publishes a substantial Gaelic-primary corpus at gaidhlig.scot.
    "gaidhlig.scot",
    # Stòrlann Nàiseanta na Gàidhlig — the National Gaelic
    # Heritage / Resources body, established under the same Act.
    # Maintains the Gaelic-medium educational resources corpus
    # (Stòrlann books + the Storlann curriculum portal) and the
    # Gaelic-only children's literature platform at learning.storlann.scot.
    "storlann.scot",
    # DASG (Dàta agus Sgeulachd Ghàidhlig / Dataset of the Gaelic
    # Story / Digitisation & Archive of Scottish Gaelic) — the
    # University of the Highlands and Islands (UHI) project that
    # maintains the canonical corpus + dictionary sources for
    # Scottish Gaelic at dasg.ac.uk.
    "dasg.ac.uk",
    # Sabhal Mòr Ostaig — the Gaelic-medium higher-education
    # institute on the Isle of Skye (part of UHI). Sole provider of
    # Gaelic-medium undergraduate + postgraduate degrees (BA / MA /
    # MSc in Gaelic + Gaelic-medium Education). Publishes both
    # Gaelic-primary and bilingual EN <-> GD content at smo.uhi.ac.uk.
    "smo.uhi.ac.uk",
    # BBC ALBA — the Scottish Gaelic-language television channel
    # (joint venture between BBC and MG ALBA / Seirbheis nam Meadhanan
    # Gàidhlig). Bilingual schedule + programme descriptions at
    # bbc.co.uk/alba (paired with the Gaelic-primary equivalent).
    "bbc.co.uk",
    # Comunn na Gàidhlig (CnG / The Gaelic Society) — the principal
    # Scottish Gaelic voluntary / membership organisation,
    # established 1891. Publishes a bilingual EN <-> GD corpus of
    # community events + educational resources + the annual Royal
    # National Mòd programme at cng.scot (formerly Gaelic
    # Society of Inverness + Comunn na Gàidhlig merged 2024).
    "cng.scot",
)


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.8 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "SCOTTISH_GAELIC_BODIES",
    "SOURCE_ID",
    "THEME_CODE",
]