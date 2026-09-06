"""PR0.3 — Phase 1 T3 (Education) — Hwb Cymraeg + WJEC/CBAC DLT source.

Deferred stub. PR0.3 will crawl:
- `hwb.gov.wales/cy/curriculum-for-wales/...` (Cymraeg curriculum content)
- `cbac.co.uk/cymwysterau/...` (WJEC Welsh-medium qualifications)
- `qualificationswales.org/.../cy/` (Qualifications Wales bilingual pages)
"""
SOURCE_ID = "ciancheiltis.en_cy.education"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_cy/education_chunks"
THEME_CODE = "T3"
LANGUAGE_PAIR = "en-cy"


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    del firecrawl_client
    return []


__all__ = ["SOURCE_ID", "LANCE_TABLE", "THEME_CODE", "LANGUAGE_PAIR"]
