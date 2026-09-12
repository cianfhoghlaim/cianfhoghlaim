"""PR0.7 — Phase 3 T1 (Legislation) — legislation.gov.uk UKSI/NISI/NID/NIA DLT source.

This is the en-ga / Northern Ireland theme T1 source: the bilingual
EN <-> GA pair of every Northern Ireland Statutory Instrument (NISI),
Northern Ireland Department publication (NID), Northern Ireland
Assembly Act (NIA), and the smaller subset of UK-wide Statutory
Instruments (UKSI) that apply to Northern Ireland under the
constitutional settlement.

Canonical example: ``https://www.legislation.gov.uk/uksi/2022/15/contents/made``
— the *Identity and Language (Northern Ireland) Act 2022*. This is the
founding statute of the modern Irish-language rights framework in NI
(establishing the Irish Language Commissioner + the Commissioner for
Ulster Scots and the Ulster Scots Academy). The Act is published in
English only at ``/uksi/2022/15/contents/made`` (the body is
English-dominant; the Irish-mirror slug is not on legislation.gov.uk).

PR0.7 will:

- ``firecrawl_map(base_url + "/nisi")`` to enumerate the opaque
  ``/nisi/<year>/<num>`` Northern Ireland Statutory Instrument slugs.
- ``firecrawl_map(base_url + "/nid")`` to enumerate the opaque
  ``/nid/<year>/<num>`` Northern Ireland Department publications.
- ``firecrawl_map(base_url + "/nia")`` to enumerate the opaque
  ``/nia/<year>/<chapter>`` Northern Ireland Assembly Acts.
- ``firecrawl_map(base_url + "/uksi")`` to enumerate the opaque
  ``/uksi/<year>/<num>`` UK-wide SIs that are NI-applicable.
- ``firecrawl_scrape(...)`` with the bilingual page validator from
  ``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
  to assert the (en, ga) pair refer to the same article.
- ``dlt_sources/ciancheiltis/_shared/language_detector.metadata_mismatch(...)``
  to flag the rare case where the ``metadata.language`` tag disagrees
  with the body (e.g. some NI Department circulars ship
  ``metadata.language="en"`` while the body is Irish-only).
- ``dlt_sources/ciancheiltis/_shared/opaque_url_scanner.classify_url(...)``
  to filter the ``/nisi/<year>/<num>`` /
  ``/nid/<year>/<num>`` / ``/nia/<year>/<chapter>`` /
  ``/uksi/<year>/<num>`` opaque slugs into the per-phase discovery
  checklist.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_ga_ni.legislation"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni/legislation_chunks"
THEME_CODE = "T1"
LANGUAGE_PAIR = "en-ga"


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.7 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "SOURCE_ID",
    "THEME_CODE",
]
