"""Gaois terminology MotherDuck Dive — Téarma + Logainm + Ainm coverage.

Added 2026-07-17 by the
`openspec/changes/2026-07-17-gaois-celtic-language-pipeline-v1/`
change. Reads from the 3 Gaois DuckLake tables via the local DuckDB
destination and emits 4 KPI breakdowns:

1. Per-language term coverage (ga vs en vs both)
2. Per-domain breakdown (LAW, MED, IT, EDU, ENV, Finland, SCI, etc.)
3. Top 50 most-used terms across the 3 sources
4. A summary stat table

Connection via `nb_utils.connect_biep_lakehouse()` (the canonical
MotherDuck helper).
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def build_gaois_terminology_dive() -> str:
    """Return the SQL DDL for the Gaois terminology Dive.

    The Dive is a virtual view over the 3 Gaois DuckLake tables that
    exposes a unified Gaois terminology fact table.
    """
    return """
    CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.gaois_terminology AS
    SELECT
        'tearma' AS source_kind,
        term_en,
        term_ga,
        domain,
        language,
        NULL AS category,
        description,
        NULL AS county,
        NULL AS place_name,
        NULL AS full_name,
        NULL AS profession,
        NULL AS birth_year,
        NULL AS death_year,
        NULL AS latitude,
        NULL AS longitude
    FROM md:cianfhoghlaim.celtic.gaois.tearma_terms
    UNION ALL
    SELECT
        'logainm' AS source_kind,
        NULL AS term_en,
        place_name_ga AS term_ga,
        NULL AS domain,
        'ga' AS language,
        category,
        NULL AS description,
        county,
        place_name,
        NULL AS full_name,
        NULL AS profession,
        NULL AS birth_year,
        NULL AS death_year,
        latitude,
        longitude
    FROM md:cianfhoghlaim.celtic.gaois.logainm_places
    UNION ALL
    SELECT
        'ainm' AS source_kind,
        NULL AS term_en,
        NULL AS term_ga,
        NULL AS domain,
        language,
        NULL AS category,
        biography AS description,
        NULL AS county,
        NULL AS place_name,
        full_name,
        profession,
        birth_year,
        death_year,
        NULL AS latitude,
        NULL AS longitude
    FROM md:cianfhoghlaim.celtic.gaois.ainm_biographies;
    """


# Pre-built KPI queries (consumed by the marimo notebook + the
# MotherDuck workspace)

GAOIS_KPI_QUERIES = {
    "language_coverage": """
        SELECT
            language,
            source_kind,
            COUNT(*) AS n_terms
        FROM md:cianfhoghlaim.dives.gaois_terminology
        GROUP BY language, source_kind
        ORDER BY n_terms DESC;
    """,
    "domain_breakdown": """
        SELECT
            domain,
            COUNT(*) AS n_terms,
            COUNT(DISTINCT language) AS n_languages
        FROM md:cianfhoghlaim.dives.gaois_terminology
        WHERE domain IS NOT NULL
        GROUP BY domain
        ORDER BY n_terms DESC
        LIMIT 30;
    """,
    "top_50_terms": """
        SELECT
            source_kind,
            COALESCE(term_en, place_name, full_name) AS term_en,
            term_ga,
            domain,
            language
        FROM md:cianfhoghlaim.dives.gaois_terminology
        WHERE term_ga IS NOT NULL OR term_en IS NOT NULL
        LIMIT 50;
    """,
    "summary_stats": """
        SELECT
            source_kind,
            COUNT(*) AS n_terms,
            COUNT(DISTINCT domain) AS n_domains,
            COUNT(DISTINCT language) AS n_languages,
            MIN(created_at) AS earliest,
            MAX(modified_at) AS latest
        FROM md:cianfhoghlaim.dives.gaois_terminology
        GROUP BY source_kind
        ORDER BY n_terms DESC;
    """,
}


__all__ = [
    "build_gaois_terminology_dive",
    "GAOIS_KPI_QUERIES",
]