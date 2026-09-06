"""PR0.3 — Phase 1 T4 (Healthcare) — NHS Wales patient information DLT source.

Deferred stub. PR0.3 will crawl `phw.nhs.wales/.../cy/` (Public
Health Wales bilingual patient information leaflets).
"""
SOURCE_ID = "ciancheiltis.en_cy.healthcare"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_cy/healthcare_chunks"
THEME_CODE = "T4"
LANGUAGE_PAIR = "en-cy"


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    del firecrawl_client
    return []


__all__ = ["SOURCE_ID", "LANCE_TABLE", "THEME_CODE", "LANGUAGE_PAIR"]
