"""MotherDuck Dive: eu_multilingual_coverage.

A read-only MotherDuck dashboard that surfaces the EU institutional
multilingual (en + ga) coverage matrix for cross-jurisdiction
alignment with the British Isles Ireland + Northern Ireland corpus.
"""
from __future__ import annotations

from motherduck.dives import save_dive


DIVE_NAME = "eu_multilingual_coverage"
DIVE_DESCRIPTION = (
    "EU institutional multilingual (English + Irish) coverage matrix "
    "for cross-jurisdiction alignment with the British Isles corpus."
)


def build_eu_multilingual_coverage_dive() -> None:
    """Persist the MotherDuck Dive for EU multilingual coverage."""
    save_dive(
        name=DIVE_NAME,
        sql="""
            SELECT institution, language, coverage_level
            FROM cianfhoghlaim.multilingual.eu_english_coverage
            UNION ALL
            SELECT institution, language, coverage_level
            FROM cianfhoghlaim.multilingual.eu_irish_coverage
        """,
    )


__all__ = [
    "DIVE_DESCRIPTION",
    "DIVE_NAME",
    "build_eu_multilingual_coverage_dive",
]
