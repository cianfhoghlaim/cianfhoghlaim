"""Dúchas folklore MotherDuck Dive — page-level summaries only.

Added 2026-07-17 by the
`openspec/changes/2026-07-17-gaois-celtic-language-pipeline-v1/`
change. Reads from the Dúchas DuckLake tables via the local DuckDB
destination and emits 4 KPI breakdowns:

1. Per-collection breakdown (CBE / CBES / CBEG / CBEF)
2. Per-county distribution
3. Per-decade coverage
4. Per-topic classification (HandbookTopicCode A-N)

**Important**: page-level summaries only. NOT 74M row word-level data
(the 5-level bbox child table lives separately at
`oideachais.language.duchas_bboxes` for the marimo bbox notebook).
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def build_duchas_folklore_dive() -> str:
    """Return the SQL DDL for the Dúchas folklore Dive.

    The Dive aggregates to the page level (NOT word level).
    """
    return """
    CREATE OR REPLACE VIEW md:oideachais.dives.duchas_folklore AS
    SELECT
        page_id,
        collection,
        volume_id,
        page_number,
        primary_language,
        county,
        transcription_confidence,
        human_verified,
        topic_codes,
        school_name,
        collector,
        teacher,
        created_at,
        modified_at
    FROM md:oideachais.celtic.duchas.manuscripts
    WHERE page_id IS NOT NULL;
    """


# Pre-built KPI queries (consumed by the marimo notebook + the
# MotherDuck workspace)

DUCHAS_KPI_QUERIES = {
    "collection_breakdown": """
        SELECT
            collection,
            COUNT(*) AS n_pages,
            COUNT(DISTINCT volume_id) AS n_volumes,
            COUNT(DISTINCT county) AS n_counties,
            AVG(transcription_confidence) AS avg_confidence
        FROM md:oideachais.dives.duchas_folklore
        GROUP BY collection
        ORDER BY n_pages DESC;
    """,
    "county_distribution": """
        SELECT
            county,
            COUNT(*) AS n_pages,
            COUNT(DISTINCT collection) AS n_collections
        FROM md:oideachais.dives.duchas_folklore
        WHERE county IS NOT NULL
        GROUP BY county
        ORDER BY n_pages DESC
        LIMIT 32;
    """,
    "decade_coverage": """
        SELECT
            SUBSTR(CAST(created_at AS VARCHAR), 1, 4) AS decade,
            collection,
            COUNT(*) AS n_pages
        FROM md:oideachais.dives.duchas_folklore
        WHERE created_at IS NOT NULL
        GROUP BY decade, collection
        ORDER BY decade DESC, n_pages DESC;
    """,
    "topic_classification": """
        SELECT
            topic_code,
            COUNT(*) AS n_pages
        FROM (
            SELECT UNNEST(STRING_SPLIT(topic_codes, ',')) AS topic_code
            FROM md:oideachais.dives.duchas_folklore
            WHERE topic_codes IS NOT NULL
        )
        WHERE topic_code != ''
        GROUP BY topic_code
        ORDER BY n_pages DESC;
    """,
    "page_level_summary": """
        SELECT
            page_id,
            collection,
            county,
            primary_language,
            transcription_confidence,
            topic_codes
        FROM md:oideachais.dives.duchas_folklore
        ORDER BY transcription_confidence DESC
        LIMIT 200;
    """,
}


__all__ = [
    "build_duchas_folklore_dive",
    "DUCHAS_KPI_QUERIES",
]