"""MotherDuck Dive: eu_official_language_coverage.

A read-only MotherDuck dashboard that surfaces the cross-language
coverage of every EU institutional source. Backed by
``oideachais.<domain>.europeanunion.<institution>`` DuckLake tables.
"""
from __future__ import annotations

from motherduck.dives import save_dive


DIVE_NAME = "eu_official_language_coverage"
DIVE_DESCRIPTION = (
    "Cross-language coverage matrix of the EU institutional pipeline. "
    "Rows: institution (eur_lex, ema, ecdc, eurostat, ...). "
    "Columns: language (the 24 EU official languages). "
    "Cells: row count for the (institution, language) partition."
)


def build_eu_official_language_coverage_dive() -> None:
    """Persist the MotherDuck Dive for the EU institutional pipeline."""
    save_dive(
        name=DIVE_NAME,
        sql="""
            SELECT
                institution,
                language,
                COUNT(*) AS row_count
            FROM oideachais.law.europeanunion.eur_lex
            GROUP BY institution, language

            UNION ALL

            SELECT
                institution,
                language,
                COUNT(*) AS row_count
            FROM oideachais.medicine.europeanunion.ema
            GROUP BY institution, language

            UNION ALL

            SELECT
                institution,
                language,
                COUNT(*) AS row_count
            FROM oideachais.medicine.europeanunion.ecdc
            GROUP BY institution, language

            UNION ALL

            SELECT
                institution,
                language,
                COUNT(*) AS row_count
            FROM oideachais.statistics.europeanunion.eurostat
            GROUP BY institution, language

            UNION ALL

            SELECT
                institution,
                language,
                COUNT(*) AS row_count
            FROM oideachais.education.europeanunion.eurydice
            GROUP BY institution, language

            UNION ALL

            SELECT
                institution,
                language,
                COUNT(*) AS row_count
            FROM oideachais.government.europeanunion.commission
            GROUP BY institution, language

            UNION ALL

            SELECT
                institution,
                language,
                COUNT(*) AS row_count
            FROM oideachais.government.europeanunion.parliament
            GROUP BY institution, language

            UNION ALL

            SELECT
                institution,
                language,
                COUNT(*) AS row_count
            FROM oideachais.government.europeanunion.council
            GROUP BY institution, language
        """,
    )


__all__ = [
    "DIVE_DESCRIPTION",
    "DIVE_NAME",
    "build_eu_official_language_coverage_dive",
]
