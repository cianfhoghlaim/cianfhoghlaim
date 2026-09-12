"""PR0.7 — Phase 3 T2 (Policy / consultations) — nidirect + NI Executive DLT source.

Deferred stub. PR0.7 will crawl the bilingual paired pages of:

- ``nidirect.gov.uk`` — the Northern Ireland government's public-facing
  information portal (publishes policies, consultations, service
  information, statistics). nidirect ships both an English mirror
  (default at the root ``/``) and an Irish-language mirror under the
  ``/ga/`` subdirectory (e.g. ``nidirect.gov.uk/ga/...``).
- The Northern Ireland Executive (``northernireland.gov.uk``) and the
  nine NI Departments (Education, Health, Infrastructure, Justice,
  Finance, Economy, Communities, Agriculture/Environment/Rural
  Affairs, and The Executive Office). Each department publishes a
  bilingual EN + GA landing page under
  ``northernireland.gov.uk/<dept>`` paired with the Irish mirror.

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
canonicalises the (en, ga) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_ga_ni_embedding`` writes ONE LanceDB row per
consultation / policy page pair.

Phase 3 differs from Phase 2 (gov.ie) in that the nidirect WAF is
looser — Firecrawl's standard ``firecrawl_scrape`` + ``firecrawl_map``
flow is sufficient (no CloudFront + WAF + CAPTCHA challenge analogous
to the Phase 1 ``gov.wales`` surface; the Phase 1 WAF bypass is not
needed here).
"""
SOURCE_ID = "ciancheiltis.en_ga_ni.policy_consultations"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni/policy_consultations_chunks"
THEME_CODE = "T2"
LANGUAGE_PAIR = "en-ga"


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.7 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = ["LANCE_TABLE", "LANGUAGE_PAIR", "SOURCE_ID", "THEME_CODE"]
