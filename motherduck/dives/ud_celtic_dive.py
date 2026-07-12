"""Universal Dependencies Celtic treebanks MotherDuck Dive.

Added 2026-07-17. Reads from `oideachais.celtic.ud_celtic.*` via
the local DuckDB destination.
"""

from __future__ import annotations


def build_ud_celtic_dive() -> str:
    """Return the SQL DDL for the UD Celtic Dive."""
    return """
    CREATE OR REPLACE VIEW md:oideachais.dives.ud_celtic AS
    SELECT
        sent_id,
        treebank,
        language,
        variety,
        text,
        split,
        tokens_count
    FROM md:oideachais.celtic.ud_celtic.sentences
    WHERE sent_id IS NOT NULL;
    """


UD_CELTIC_KPI_QUERIES = {
    "treebank_breakdown": """
        SELECT
            treebank,
            language,
            variety,
            COUNT(*) AS n_sentences,
            SUM(tokens_count) AS n_tokens
        FROM md:oideachais.dives.ud_celtic
        GROUP BY treebank, language, variety
        ORDER BY n_sentences DESC;
    """,
    "language_coverage": """
        SELECT
            language,
            COUNT(DISTINCT treebank) AS n_treebanks,
            COUNT(*) AS n_sentences
        FROM md:oideachais.dives.ud_celtic
        GROUP BY language
        ORDER BY n_sentences DESC;
    """,
    "top_20_lemmas": """
        SELECT lemma, COUNT(*) AS n_occurrences
        FROM md:oideachais.celtic.ud_celtic.tokens
        WHERE lemma IS NOT NULL
        GROUP BY lemma
        ORDER BY n_occurrences DESC
        LIMIT 20;
    """,
    "pos_distribution": """
        SELECT upos, COUNT(*) AS n_tokens
        FROM md:oideachais.celtic.ud_celtic.tokens
        WHERE upos IS NOT NULL
        GROUP BY upos
        ORDER BY n_tokens DESC;
    """,
}


__all__ = [
    "build_ud_celtic_dive",
    "UD_CELTIC_KPI_QUERIES",
]