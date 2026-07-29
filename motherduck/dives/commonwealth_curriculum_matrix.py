"""MotherDuck Dive: commonwealth_curriculum_matrix.

A read-only MotherDuck dashboard that surfaces the cross-nation
curriculum coverage matrix for the 5 Commonwealth pilot nations.
"""
from __future__ import annotations

from motherduck.dives import save_dive


DIVE_NAME = "commonwealth_curriculum_matrix"
DIVE_DESCRIPTION = (
    "Cross-nation curriculum coverage matrix for the 5 Commonwealth "
    "pilot nations (Australia / Canada / New Zealand / India / South Africa). "
    "Rows: country + domain. Columns: language. Cells: row count."
)


def build_commonwealth_curriculum_matrix_dive() -> None:
    """Persist the MotherDuck Dive for the Commonwealth pipeline."""
    save_dive(
        name=DIVE_NAME,
        sql="""
            SELECT country_code, domain, language, COUNT(*) AS row_count
            FROM oideachais.education.commonwealth.aus
            GROUP BY country_code, domain, language

            UNION ALL
            SELECT country_code, domain, language, COUNT(*) AS row_count
            FROM oideachais.education.commonwealth.can
            GROUP BY country_code, domain, language

            UNION ALL
            SELECT country_code, domain, language, COUNT(*) AS row_count
            FROM oideachais.education.commonwealth.nzl
            GROUP BY country_code, domain, language

            UNION ALL
            SELECT country_code, domain, language, COUNT(*) AS row_count
            FROM oideachais.education.commonwealth.ind
            GROUP BY country_code, domain, language

            UNION ALL
            SELECT country_code, domain, language, COUNT(*) AS row_count
            FROM oideachais.education.commonwealth.zaf
            GROUP BY country_code, domain, language
        """,
    )


__all__ = [
    "DIVE_DESCRIPTION",
    "DIVE_NAME",
    "build_commonwealth_curriculum_matrix_dive",
]
