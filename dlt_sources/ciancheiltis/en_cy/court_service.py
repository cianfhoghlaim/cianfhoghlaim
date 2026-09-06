"""PR0.3 — Phase 1 T7 (Courts & Tribunals) — HMCTS Welsh DLT source.

Deferred stub. PR0.3 will crawl HMCTS Welsh pages via the
Welsh Courts Service bilingual content.
"""
SOURCE_ID = "ciancheiltis.en_cy.court_service"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_cy/court_service_chunks"
THEME_CODE = "T7"
LANGUAGE_PAIR = "en-cy"


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    del firecrawl_client
    return []


__all__ = ["SOURCE_ID", "LANCE_TABLE", "THEME_CODE", "LANGUAGE_PAIR"]
