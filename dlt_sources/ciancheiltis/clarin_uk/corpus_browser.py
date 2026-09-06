"""PR0.1 — CLARIN-UK Celtic corpus catalogue.

Lands curated CLARIN-UK Celtic-language corpora into
`lancedb://md:cianfhoghlaim/clarin_uk_corpora` as ground truth for
the six ciancheiltis phases.

CLARIN-UK catalogue URL:
    https://www.clarin.ac.uk/resource-families/celtic-languages/

This is a deferred stub — PR0.3 will wire it up to the Firecrawl
`firecrawl_agent` (autonomous research) + `firecrawl_map` (URL
discovery) + `firecrawl_parse` (PDF ingestion) tool surface.

Schema columns (per Requirement §CLARIN-UK):
    corpus_name         str
    iso_language_pair   list[str]
    corpus_size_mb      float
    license             str  ("CC-BY" / "CC-BY-NC" / "research-only" / etc.)
    download_url        str
    has_bilingual_text  bool
    languages           list[str]
"""
from __future__ import annotations

from typing import Any

from dlt_sources.ciancheiltis.clarin_uk import CLARIN_UK_CELTIC_FAMILY_URL


SOURCE_ID = "ciancheiltis.clarin_uk.corpus_browser"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/clarin_uk_corpora"


def collect(*, firecrawl_client: Any | None = None) -> list[dict[str, Any]]:
    """Return the discovered CLARIN-UK Celtic corpus rows.

    Returns an empty list until Firecrawl is reachable and PR0.3 lands
    the live crawler.
    """
    del firecrawl_client  # wired in PR0.3
    return [
        {
            "corpus_name": "CLARIN-UK Celtic resource family",
            "iso_language_pair": ["en-cy", "en-ga", "en-gd", "en-gv", "en-br", "en-cornish"],
            "corpus_size_mb": 0.0,
            "license": "varies-by-resource",
            "download_url": CLARIN_UK_CELTIC_FAMILY_URL,
            "has_bilingual_text": True,
            "languages": ["en", "cy", "ga", "gd", "gv", "br", "cor"],
            "_seed_only": True,
        }
    ]


__all__ = ["collect", "SOURCE_ID", "LANCE_TABLE"]
