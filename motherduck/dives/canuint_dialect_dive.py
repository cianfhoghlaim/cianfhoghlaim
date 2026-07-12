"""Canuint dialect MotherDuck Dive — pronunciation + word alignment.

Added 2026-07-17 by the
`openspec/changes/2026-07-17-gaois-celtic-language-pipeline-v1/`
change. Reads from `oideachais.celtic.canuint.*` via the local DuckDB
destination.
"""

from __future__ import annotations


def build_canuint_dialect_dive() -> str:
    """Return the SQL DDL for the Canuint dialect Dive."""
    return """
    CREATE OR REPLACE VIEW md:oideachais.dives.canuint_dialect AS
    SELECT
        word_id,
        recording_id,
        location_id,
        location_name,
        province,
        dialectal_text,
        standardized_text,
        speaker,
        start_seconds,
        end_seconds,
        confidence,
        duration_ms,
        language
    FROM md:oideachais.celtic.canuint.word_alignments
    WHERE word_id IS NOT NULL;
    """


CANUINT_KPI_QUERIES = {
    "province_breakdown": """
        SELECT
            province,
            COUNT(*) AS n_words,
            COUNT(DISTINCT location_id) AS n_locations,
            COUNT(DISTINCT speaker) AS n_speakers,
            AVG(duration_ms) AS avg_duration_ms
        FROM md:oideachais.dives.canuint_dialect
        GROUP BY province
        ORDER BY n_words DESC;
    """,
    "word_alignment_stats": """
        SELECT
            recording_id,
            location_name,
            province,
            COUNT(*) AS n_words,
            MIN(start_seconds) AS first_word_start,
            MAX(end_seconds) AS last_word_end,
            AVG(confidence) AS avg_confidence
        FROM md:oideachais.dives.canuint_dialect
        GROUP BY recording_id, location_name, province
        ORDER BY n_words DESC
        LIMIT 30;
    """,
    "dialect_comparison": """
        SELECT
            province,
            dialectal_text,
            standardized_text,
            COUNT(*) AS n_occurrences
        FROM md:oideachais.dives.canuint_dialect
        WHERE dialectal_text != standardized_text
        GROUP BY province, dialectal_text, standardized_text
        ORDER BY n_occurrences DESC
        LIMIT 50;
    """,
    "top_50_words": """
        SELECT
            standardized_text,
            COUNT(*) AS n_occurrences,
            COUNT(DISTINCT province) AS n_provinces
        FROM md:oideachais.dives.canuint_dialect
        GROUP BY standardized_text
        ORDER BY n_occurrences DESC
        LIMIT 50;
    """,
}


__all__ = [
    "build_canuint_dialect_dive",
    "CANUINT_KPI_QUERIES",
]