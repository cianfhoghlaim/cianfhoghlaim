"""PR0.3 — Phase 1 T2 (Policy / consultations) — gov.wales consultations DLT source.

Deferred stub. PR0.3 will use
`dlt_sources.ciancheiltis._shared.gov_wales_waf_bypass.fetch` to
engage the WAF fallback chain (firecrawl_interact profile →
hwb.gov.wales mirror).
"""
SOURCE_ID = "ciancheiltis.en_cy.policy_consultations"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_cy/policy_consultations_chunks"
THEME_CODE = "T2"
LANGUAGE_PAIR = "en-cy"


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    del firecrawl_client
    return []


__all__ = ["SOURCE_ID", "LANCE_TABLE", "THEME_CODE", "LANGUAGE_PAIR"]
