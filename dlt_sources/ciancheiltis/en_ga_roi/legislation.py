"""PR0.6 — Phase 2 T1 (Legislation) — Irish Statute Book (irishstatutebook.ie) DLT source.

This is the en-ga / Republic of Ireland theme T1 source: the Irish
Statute Book's bilingual EN <-> GA pair of every Act, Statutory
Instrument and Statutory Rule of the Oireachtas (1937-present).

Canonical example: `https://www.irishstatutebook.ie/eli/1937/act/0019/enacted/ga/html`
— the *Bunreacht na hÉireann* / *Constitution of Ireland* (1937, Act
No. 19) in Irish. The English mirror is at
`/eli/1937/act/0019/enacted/en/html`.

This is a deferred stub — the live crawler awaits the next
Firecrawl reset (keyless tier is exhausted today). PR0.6 will use:

- `firecrawl_map(base_url + "/eli")` to enumerate the opaque `/eli/
  <year>/<type>/<num>/enacted/{en,ga}/html` URLs.
- `firecrawl_scrape(...)` with the bilingual page validator from
  ``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
  to assert the (en, ga) pair refer to the same article.
- ``dlt_sources/ciancheiltis/_shared/language_detector.metadata_mismatch(...)``
  to flag the rare case where the ``metadata.language`` tag disagrees
  with the body (e.g. the 1948 *Republic of Ireland Act* whose
  Irish title-only revision historically mis-tagged itself ``en``).
- ``dlt_sources/ciancheiltis/_shared/opaque_url_scanner.classify_url(...)``
  to filter the ``/eli/<year>/<type>/<num>/enacted/{en,ga}/html``
  opaque slugs into the per-phase discovery checklist.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_ga_roi.legislation"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_roi/legislation_chunks"
THEME_CODE = "T1"
LANGUAGE_PAIR = "en-ga"


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.6 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "SOURCE_ID",
    "THEME_CODE",
]
