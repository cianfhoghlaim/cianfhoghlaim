"""PR0.3 — Phase 1 T1 (Legislation) — legislation.gov.uk Welsh-content DLT source.

This is the en-cy / Wales theme T1 source: the legislation.gov.uk
Welsh-language statutory instruments (`/wsi/`) and the UK SIs
that are predominantly Welsh (`/uksi/<year>/<num>/made/welsh`).

Canonical example: `legislation.gov.uk/wsi/2007/2044/made/welsh` —
the *Gorchymyn Ffurfiau Cymraeg Llwon a Chadarnhadau (Deddf
Llywodraeth Leol (Cymru) 2012)*.

This is a deferred stub — the live crawler awaits the next
Firecrawl reset (keyless tier is exhausted today). PR0.3 will
use:

- `firecrawl_map(base_url + "/wsi")` to enumerate the opaque-URL
  Welsh SIs.
- `firecrawl_scrape(...)` with `jsonOptions.schema=BilingualPageSpec`
  to extract the en/cy parallel blocks.
- `_shared.language_detector.metadata_mismatch(...)` to flag the
  metadata `language: "eng"` failure mode (per SI 2007/1484).
- `_shared.opaque_url_scanner.classify_url(...)` to filter.
"""
from __future__ import annotations


SOURCE_ID = "ciancheiltis.en_cy.legislation"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_cy/legislation_chunks"
THEME_CODE = "T1"
LANGUAGE_PAIR = "en-cy"


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.3 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = [
    "SOURCE_ID",
    "LANCE_TABLE",
    "THEME_CODE",
    "LANGUAGE_PAIR",
]
