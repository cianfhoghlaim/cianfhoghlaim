"""PR0.3 — Phase 1 T5 (Language body) — Welsh Language Commissioner DLT source.

Crawls `welshlanguagecommissioner.wales/.../cy/standards/` for the
Commissioner's bilingual Welsh-language standards (the regulator's
own publications are bilingual by statute).
"""
SOURCE_ID = "ciancheiltis.en_cy.language_commissioner"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_cy/language_commissioner_chunks"
THEME_CODE = "T5"
LANGUAGE_PAIR = "en-cy"


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    del firecrawl_client
    return []


__all__ = ["SOURCE_ID", "LANCE_TABLE", "THEME_CODE", "LANGUAGE_PAIR"]
