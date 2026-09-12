"""PR0.8 — Phase 4 T7 (Courts & Tribunals) — Scottish Courts + SPA DLT source.

Deferred stub. PR0.8 will crawl the Scottish Courts and Tribunals
Service (SCTS) public-facing content at ``scotcourts.gov.uk`` —
the catalogue of court forms, the Court of Session + High Court +
Sheriff Court + Justice of the Peace Court rules, and the published
judgments of the superior courts — plus the Scottish Police
Authority (SPA) at ``spa.police.uk``.

**Partial Phase 4**: The SCTS publishes an English-only corpus with
extremely limited Gaelic-language material (court forms + the Court
of Session gowning protocol ship with optional Gaelic-language
glossaries only). The SCTS bilingual surface is the smallest of the
Phase 1-4 sister-court corpora and the umbrella spec acknowledges
Phase 4 § T7 as a "partial" theme — the BAML coverage gate is
expected to flag most rows as English-only.

The SCTS is established under the Courts Reform (Scotland) Act 2014
+ the Judiciary and Courts (Scotland) Act 2008 + the Courts of
Scotland Act 1672 (the primary historic statute). The SPA is
established under the Police and Fire Reform (Scotland) Act 2012.

PR0.8 will pair the EN form (e.g. ``scotcourts.gov.uk/forms/<court>/.../en/``)
with its GD mirror (e.g. ``scotcourts.gov.uk/forms/<court>/.../gd/``)
where published and write one LanceDB row per bilingual form pair
via the ``ciancheiltis_en_gd_embedding`` App.

The underlying single-language pipeline is NOT yet seeded in
``dlt_sources/british_isles/scotland/law/`` — Phase 4 § T7 is the
first Phase to populate that sub-tree.
"""
SOURCE_ID = "ciancheiltis.en_gd.courts"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_gd/courts_chunks"
THEME_CODE = "T7"
LANGUAGE_PAIR = "en-gd"


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.8 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = ["LANCE_TABLE", "LANGUAGE_PAIR", "SOURCE_ID", "THEME_CODE"]