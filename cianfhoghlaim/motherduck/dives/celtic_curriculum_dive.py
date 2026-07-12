"""Celtic curriculum MotherDuck Dive — 6 Celtic languages coverage.

Added 2026-07-17. Reads from `oideachais.celtic.curriculum.*` via
the local DuckDB destination.
"""

from __future__ import annotations


def build_celtic_curriculum_dive() -> str:
    """Return the SQL DDL for the Celtic curriculum Dive."""
    return """
    CREATE OR REPLACE VIEW md:oideachais.dives.celtic_curriculum AS
    SELECT
        language,
        nation_code,
        education_level,
        year_levels,
        curriculum_body,
        framework_name,
        framework_name_native,
        content_text
    FROM (
        SELECT 'irish' AS language, * FROM md:oideachais.celtic.curriculum.irish
        UNION ALL SELECT 'scottish_gaelic', * FROM md:oideachais.celtic.curriculum.scottish_gaelic
        UNION ALL SELECT 'welsh', * FROM md:oideachais.celtic.curriculum.welsh
        UNION ALL SELECT 'breton', * FROM md:oideachais.celtic.curriculum.breton
        UNION ALL SELECT 'manx', * FROM md:oideachais.celtic.curriculum.manx
        UNION ALL SELECT 'cornish', * FROM md:oideachais.celtic.curriculum.cornish
    );
    """


CELTIC_CURRICULUM_KPI_QUERIES = {
    "per_language_coverage": """
        SELECT language, COUNT(*) AS n_specs, COUNT(DISTINCT education_level) AS n_levels
        FROM md:oideachais.dives.celtic_curriculum
        GROUP BY language
        ORDER BY n_specs DESC;
    """,
    "per_education_level": """
        SELECT education_level, language, COUNT(*) AS n_specs
        FROM md:oideachais.dives.celtic_curriculum
        GROUP BY education_level, language
        ORDER BY n_specs DESC;
    """,
    "curriculum_body_breakdown": """
        SELECT curriculum_body, COUNT(*) AS n_specs
        FROM md:oideachais.dives.celtic_curriculum
        WHERE curriculum_body IS NOT NULL
        GROUP BY curriculum_body
        ORDER BY n_specs DESC;
    """,
    "year_level_distribution": """
        SELECT year_levels, COUNT(*) AS n_specs
        FROM md:oideachais.dives.celtic_curriculum
        WHERE year_levels IS NOT NULL
        GROUP BY year_levels
        ORDER BY n_specs DESC
        LIMIT 30;
    """,
}


__all__ = [
    "build_celtic_curriculum_dive",
    "CELTIC_CURRICULUM_KPI_QUERIES",
]