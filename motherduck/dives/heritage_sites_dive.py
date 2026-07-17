"""Heritage sites MotherDuck Dive — heritage + hidden heritages coverage.

Added 2026-07-17 by the
`openspec/changes/2026-07-17-gaois-celtic-language-pipeline-v1/`
change. Reads from the heritage DuckLake tables via the local DuckDB
destination and emits 4 KPI breakdowns:

1. Per-county heritage site coverage
2. Per-type breakdown (monument / castle / ringfort / church / etc.)
3. Map of all heritage sites (lat/lon)
4. Hidden heritages vs main heritages comparison
"""

from __future__ import annotations


def build_heritage_sites_dive() -> str:
    """Return the SQL DDL for the heritage sites Dive."""
    return """
    CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.heritage_sites AS
    SELECT
        'main' AS heritage_kind,
        site_id,
        site_name,
        site_name_ga,
        site_type,
        county,
        latitude,
        longitude,
        description,
        created_at,
        modified_at
    FROM md:cianfhoghlaim.celtic.heritage.sites
    UNION ALL
    SELECT
        'hidden' AS heritage_kind,
        site_id,
        site_name,
        site_name_ga,
        'hidden' AS site_type,
        county,
        latitude,
        longitude,
        description,
        created_at,
        modified_at
    FROM md:cianfhoghlaim.celtic.heritage.hidden_sites;
    """


HERITAGE_KPI_QUERIES = {
    "county_coverage": """
        SELECT
            county,
            heritage_kind,
            COUNT(*) AS n_sites
        FROM md:cianfhoghlaim.dives.heritage_sites
        WHERE county IS NOT NULL
        GROUP BY county, heritage_kind
        ORDER BY n_sites DESC
        LIMIT 50;
    """,
    "type_breakdown": """
        SELECT
            site_type,
            heritage_kind,
            COUNT(*) AS n_sites
        FROM md:cianfhoghlaim.dives.heritage_sites
        WHERE site_type IS NOT NULL
        GROUP BY site_type, heritage_kind
        ORDER BY n_sites DESC;
    """,
    "all_sites_map": """
        SELECT
            site_id,
            site_name,
            site_name_ga,
            county,
            site_type,
            heritage_kind,
            latitude,
            longitude
        FROM md:cianfhoghlaim.dives.heritage_sites
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        LIMIT 10000;
    """,
    "hidden_vs_main": """
        SELECT
            heritage_kind,
            COUNT(*) AS n_sites,
            COUNT(DISTINCT county) AS n_counties,
            COUNT(DISTINCT site_type) AS n_types
        FROM md:cianfhoghlaim.dives.heritage_sites
        GROUP BY heritage_kind
        ORDER BY n_sites DESC;
    """,
}


__all__ = [
    "build_heritage_sites_dive",
    "HERITAGE_KPI_QUERIES",
]