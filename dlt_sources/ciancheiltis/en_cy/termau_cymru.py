"""PR0.3 — Phase 1 T6 (Terminology) — Coleg Cymraeg Cenedlaethol Termau DLT source.

Coleg Cymraeg Cenedlaethol publishes a Welsh terminology database at
`colegcymraeg.ac.uk/termau/`. The en-cy term pairs are the canonical
Welsh-side ground truth for the bilingual concept registry.
"""
SOURCE_ID = "ciancheiltis.en_cy.termau_cymru"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_cy/termau_cymru_chunks"
THEME_CODE = "T6"
LANGUAGE_PAIR = "en-cy"


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    del firecrawl_client
    return []


__all__ = ["SOURCE_ID", "LANCE_TABLE", "THEME_CODE", "LANGUAGE_PAIR"]
