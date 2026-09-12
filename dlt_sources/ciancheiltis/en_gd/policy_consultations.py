"""PR0.8 — Phase 4 T2 (Policy / consultations) — gov.scot + Riaghaltas na h-Alba DLT source.

Deferred stub. PR0.8 will crawl the bilingual paired pages of:

- ``gov.scot`` — the Scottish government's public-facing portal
  (publishes policies, consultations, ministerial statements,
  statistical bulletins, service information). gov.scot ships an
  English default at the root ``/`` and a parallel Gaelic mirror
  under ``/gd/...`` subdirectories for the bilingual policy surface
  (e.g. ``gov.scot/gd/policies/...``).
- ``riaghaltas.gov.scot`` — the Gaelic-language native domain of the
  Scottish Government ("Riaghaltas na h-Alba"), the primary surface
  for Gaelic-first policy / consultation / news content published
  under the Gaelic Language (Scotland) Act 2005 statutory duties.

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
canonicalises the (en, gd) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_gd_embedding`` writes ONE LanceDB row per
consultation / policy page pair.

Phase 4 differs from Phase 2 (gov.ie) and Phase 3 (nidirect) in
that gov.scot's bilingual surface is narrower — only policy pages
with an explicit ``/gd/`` mirror are paired, and many consultations
ship English-only — the BAML coverage gap is expected to be wider
in Phase 4 than Phase 3 and the umbrella spec's content-based
language detector is the gate.
"""
SOURCE_ID = "ciancheiltis.en_gd.policy_consultations"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_gd/policy_consultations_chunks"
THEME_CODE = "T2"
LANGUAGE_PAIR = "en-gd"


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.8 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = ["LANCE_TABLE", "LANGUAGE_PAIR", "SOURCE_ID", "THEME_CODE"]