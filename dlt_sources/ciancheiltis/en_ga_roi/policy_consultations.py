"""PR0.6 — Phase 2 T2 (Policy / consultations) — gov.ie EN <-> GA DLT source.

Deferred stub. PR0.6 will crawl the bilingual paired pages of every
gov.ie department — each department publishes both an English
landing page (e.g. `gov.ie/en/department-of-education/...`) and an
Irish landing page (e.g. `gov.ie/ga/an-roinn-oideachais/...`).

The gov.ie content surface is the canonical Republic of Ireland
policy / consultation corpus. Mirrors the Phase 1 en-cy
``policy_consultations`` pattern that uses the gov.wales WAF bypass
fallback; PR0.6 will use the simpler
``firecrawl_scrape`` + ``firecrawl_map`` flow because gov.ie does
not impose a CloudFront + WAF + CAPTCHA challenge (per the
umbrella spec § Phase-2 — gov.wales WAF bypass is en-cy only).
"""
SOURCE_ID = "ciancheiltis.en_ga_roi.policy_consultations"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_roi/policy_consultations_chunks"
THEME_CODE = "T2"
LANGUAGE_PAIR = "en-ga"


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.6 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = ["LANCE_TABLE", "LANGUAGE_PAIR", "SOURCE_ID", "THEME_CODE"]
