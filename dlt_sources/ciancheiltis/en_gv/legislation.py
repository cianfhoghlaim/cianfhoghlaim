"""PR0.9 — Phase 5 T1 (Legislation) — legislation.gov.im + Tynwald Acts DLT source.

This is the en-gv / Isle of Man theme T1 source: the bilingual
EN <-> GV pair of every Manx Act (Tynwald Acts) and Statutory
Document published on ``legislation.gov.im`` (the consolidated
legislation portal of the Isle of Man Government).

Canonical example: ``https://legislation.gov.im/cms/legislation/`` —
the Isle of Man legislation portal hosted by the Office of the
Legislative Counsel. Tynwald is the bicameral parliament of the
Isle of Man (the Legislative Council + the House of Keys) and is
the longest continuously functioning parliament in the world (AD
979, established by the Norse-Gaelic Tynwald ceremony).

Manx (Gaelg) is in **revival status** — there is **no statutory
requirement** to publish Manx-language versions of Acts (the
Gaelic Language (Scotland) Act 2005 equivalent does not exist for
the Isle of Man). Where Manx-language content exists it is
typically limited to the long titles of pre-1900 Acts in the
historical archive at the Manx Museum / Manx National Heritage
(curated by ``Culture Vannin`` — the Phase 5 § T5 canonical body).

PR0.9 will:

- ``firecrawl_map(base_url + "/cms/legislation")`` to enumerate the
  Acts + Statutory Documents hosted on legislation.gov.im.
- ``firecrawl_scrape(...)`` with the bilingual page validator from
  ``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
  to assert the (en, gv) pair refer to the same article.
- ``dlt_sources/ciancheiltis/_shared/language_detector.metadata_mismatch(...)``
  to flag the rare case where the ``metadata.language`` tag disagrees
  with the body (e.g. some Manx historical archive pages ship
  ``metadata.language="en"`` while the long title is Gaelic-only).
- ``dlt_sources/ciancheiltis/_shared/opaque_url_scanner.classify_url(...)``
  to filter the ``/cms/legislation/acts/<year>/<chapter>`` opaque
  slugs into the per-phase discovery checklist.

Phase 5 differs from Phases 1-4 in that the Isle of Man has **no
statutory bilingual publication duty** for legislation — the
Phase 5 strict-gate (per ``dlt_sources/ciancheiltis/en_gv/__init__.py``)
is "capture what bilingual content exists and surface it
faithfully".
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_gv.legislation"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_gv/legislation_chunks"
THEME_CODE = "T1"
LANGUAGE_PAIR = "en-gv"


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.9 wires Firecrawl.

    Manx (Gaelg) is in revival status — there is no statutory
    bilingual publication duty for Acts on legislation.gov.im.
    PR0.9 will surface whatever bilingual content exists in the
    Tynwald archive (typically limited to the long titles of
    pre-1900 Acts in the historical Manx-language archive curated
    by Culture Vannin + the Manx National Heritage).
    """
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "SOURCE_ID",
    "THEME_CODE",
]
