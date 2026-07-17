"""MotherDuck Dive: eu_nation_curriculum_matrix.

A read-only MotherDuck dashboard that surfaces the cross-nation
curriculum coverage matrix for the 6 EU nations + Ukraine pilot
countries. Backed by
``cianfhoghlaim.<domain>.european_nations.<iso3>`` DuckLake tables.
"""
from __future__ import annotations

from motherduck.dives import save_dive


DIVE_NAME = "eu_nation_curriculum_matrix"
DIVE_DESCRIPTION = (
    "Cross-nation curriculum coverage matrix for the 6 EU nations + "
    "Ukraine pilot countries (Ukraine / France / Germany / Poland / Spain / Italy). "
    "Rows: country + domain. Columns: language. Cells: row count."
)


def build_eu_nation_curriculum_matrix_dive() -> None:
    """Persist the MotherDuck Dive for the EU nations + Ukraine pipeline."""
    save_dive(
        name=DIVE_NAME,
        sql="""
            SELECT country_code, domain, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.education.european_nations.ukr
            GROUP BY country_code, domain, language

            UNION ALL
            SELECT country_code, domain, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.law.european_nations.ukr
            GROUP BY country_code, domain, language

            UNION ALL
            SELECT country_code, domain, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.education.european_nations.fra
            GROUP BY country_code, domain, language

            UNION ALL
            SELECT country_code, domain, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.law.european_nations.fra
            GROUP BY country_code, domain, language

            UNION ALL
            SELECT country_code, domain, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.education.european_nations.deu
            GROUP BY country_code, domain, language

            UNION ALL
            SELECT country_code, domain, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.education.european_nations.pol
            GROUP BY country_code, domain, language

            UNION ALL
            SELECT country_code, domain, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.education.european_nations.esp
            GROUP BY country_code, domain, language

            UNION ALL
            SELECT country_code, domain, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.education.european_nations.ita
            GROUP BY country_code, domain, language
        """,
    )


__all__ = [
    "DIVE_DESCRIPTION",
    "DIVE_NAME",
    "build_eu_nation_curriculum_matrix_dive",
]
