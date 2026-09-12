"""PR0.8 — Phase 4 T1 (Legislation) — legislation.gov.uk /asp/ + /ssi/ + /sdsi/ DLT source.

This is the en-gd / Scotland theme T1 source: the bilingual
EN <-> GD pair of every Scottish Act (``/asp/<year>/<chapter>``),
Scottish Statutory Instrument (``/ssi/<year>/<num>``) and Scottish
Draft Statutory Instrument (``/sdsi/<year>/<num>``) — the three
devolved legislatures of the Scottish Parliament under the Scotland
Act 1998, plus the Gaelic Language (Scotland) Act 2005 (asp 7) which
is the founding statute of the modern Scottish Gaelic rights
framework (establishing Bòrd na Gàidhlig).

Canonical example: ``https://www.legislation.gov.uk/asp/2005/7/contents``
— the *Gaelic Language (Scotland) Act 2005*, the founding statute of
the modern Scottish Gaelic rights framework. The Act is published
in English only at ``/asp/2005/7/contents`` (the body is
English-dominant; the Scottish Gaelic mirror slug is not on
legislation.gov.uk).

PR0.8 will:

- ``firecrawl_map(base_url + "/asp")`` to enumerate the opaque
  ``/asp/<year>/<chapter>`` Scottish Act slugs.
- ``firecrawl_map(base_url + "/ssi")`` to enumerate the opaque
  ``/ssi/<year>/<num>`` Scottish Statutory Instrument slugs.
- ``firecrawl_map(base_url + "/sdsi")`` to enumerate the opaque
  ``/sdsi/<year>/<num>`` Scottish Draft Statutory Instrument slugs.
- ``firecrawl_scrape(...)`` with the bilingual page validator from
  ``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
  to assert the (en, gd) pair refer to the same article.
- ``dlt_sources/ciancheiltis/_shared/language_detector.metadata_mismatch(...)``
  to flag the rare case where the ``metadata.language`` tag disagrees
  with the body (e.g. some SSI explanatory notes ship
  ``metadata.language="en"`` while the body is Gaelic-only).
- ``dlt_sources/ciancheiltis/_shared/opaque_url_scanner.classify_url(...)``
  to filter the ``/asp/<year>/<chapter>`` /
  ``/ssi/<year>/<num>`` /
  ``/sdsi/<year>/<num>`` opaque slugs into the per-phase discovery
  checklist.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_gd.legislation"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_gd/legislation_chunks"
THEME_CODE = "T1"
LANGUAGE_PAIR = "en-gd"


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.8 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "SOURCE_ID",
    "THEME_CODE",
]