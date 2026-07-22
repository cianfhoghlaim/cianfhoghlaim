# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13",
#   "ibis-framework[duckdb]>=9.0",
#   "pandas>=2.2",
#   "altair>=5.0",
#   "pyarrow>=15",
# ]
#
# [tool.uv]
# package = "biep-v2-leaving-cert-subject-panel"
# ///

"""Leaving Cert Subject Panel — the 7-tab grouped marimo (BIEP v2).

Per the 2026-07-25-flatten-notebooks-v1 change. This single notebook
replaces the 7 per-subject files that previously lived at
``notebooks/leaving_cert/<subject>.py`` + ``06_en_vs_ga_comparison.py``
(chem/cs/eng/ga/geo/math + EN/GA comparison, 2,657 LOC total).

The 7 tabs render side-by-side:
  1. Mathematics
  2. Chemistry
  3. Geography
  4. Gaeilge (bilingual EN/GA)
  5. English (bilingual EN/GA)
  6. Computer Science
  7. EN/GA Comparison (the old `06_en_vs_ga_comparison.py`)

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query goes through
  ``notebooks._shared.db:connect_md()`` (NO raw ``duckdb.connect``).
- marimo (per `.agents/skills/marimo/SKILL.md`) — `mo.ui.tabs` for the
  7 per-subject views; `mo.ui.multiselect` for the filter UI.

TABLES:
  cianfhoghlaim.lc.<subject>.<level>_<lang>  (per-subject LanceDB tables)

Reference: openspec/changes/2026-07-25-flatten-notebooks-v1/
"""

import marimo

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _intro():
    import marimo as mo
    mo.md(
        """
        # Leaving Cert Subject Panel — 7-tab grouped marimo (BIEP v2)

        Browse the 6 priority LC subjects side-by-side, plus an
        EN/GA comparison view. Replaces the 7 per-subject
        `notebooks/leaving_cert/<subject>.py` + `06_en_vs_ga_comparison.py`
        files (~2,657 LOC).
        """
    )
    return (mo,)


@app.cell
def _filter_ui(mo):
    subject_filter = mo.ui.multiselect(
        options=["mathematics", "chemistry", "geography", "english", "gaeilge", "computer_science"],
        value=["mathematics", "english"],
        label="LC subject",
    )
    level_filter = mo.ui.multiselect(
        options=["hl", "ol", "fl"],
        value=["hl", "ol"],
        label="Level",
    )
    language_filter = mo.ui.multiselect(
        options=["en", "ga"],
        value=["en", "ga"],
        label="Language",
    )
    mo.vstack([subject_filter, level_filter, language_filter])
    return subject_filter, level_filter, language_filter


@app.cell
def _ibis_first_conn(mo):
    """The ibis-first contract per the BIEP v2 spec + 2026-07-25 refactor."""
    from notebooks._shared.db import connect_md
    conn = connect_md()
    lance_table_suffix = "cianfhoghlaim.lc.<subject>.<level>_<lang>"
    mo.md(
        f"✓ ibis-first wired — per-subject LanceDB tables: `{lance_table_suffix}`"
    )
    return conn, lance_table_suffix


@app.cell
def _tabs(conn, subject_filter, level_filter, language_filter, mo):
    """The 7-tab grouped view.

    Each tab queries the per-subject LC LanceDB table via ibis.
    """
    subject_tabs = mo.ui.tabs(
        {
            "1. Mathematics": _math_tab(conn, subject_filter, level_filter, language_filter),
            "2. Chemistry": _chem_tab(conn, subject_filter, level_filter, language_filter),
            "3. Geography": _geo_tab(conn, subject_filter, level_filter, language_filter),
            "4. Gaeilge (EN/GA)": _ga_tab(conn, subject_filter, level_filter, language_filter),
            "5. English (EN/GA)": _en_tab(conn, subject_filter, level_filter, language_filter),
            "6. Computer Science": _cs_tab(conn, subject_filter, level_filter, language_filter),
            "7. EN/GA Comparison": _en_vs_ga_tab(conn, subject_filter, level_filter, language_filter),
        }
    )
    subject_tabs
    return (subject_tabs,)


@app.cell
def _math_tab(conn, subject_filter, level_filter, language_filter):
    """Mathematics tab — per-level topic coverage."""
    rows = _lc_query(conn, "mathematics", subject_filter, level_filter, language_filter)
    return rows


@app.cell
def _chem_tab(conn, subject_filter, level_filter, language_filter):
    """Chemistry tab — per-level topic coverage."""
    return _lc_query(conn, "chemistry", subject_filter, level_filter, language_filter)


@app.cell
def _geo_tab(conn, subject_filter, level_filter, language_filter):
    """Geography tab — per-level topic coverage."""
    return _lc_query(conn, "geography", subject_filter, level_filter, language_filter)


@app.cell
def _ga_tab(conn, subject_filter, level_filter, language_filter):
    """Gaeilge tab (bilingual EN/GA)."""
    return _lc_query(conn, "gaeilge", subject_filter, level_filter, language_filter)


@app.cell
def _en_tab(conn, subject_filter, level_filter, language_filter):
    """English tab (bilingual EN/GA)."""
    return _lc_query(conn, "english", subject_filter, level_filter, language_filter)


@app.cell
def _cs_tab(conn, subject_filter, level_filter, language_filter):
    """Computer Science tab."""
    return _lc_query(conn, "computer_science", subject_filter, level_filter, language_filter)


@app.cell
def _en_vs_ga_tab(conn, subject_filter, level_filter, language_filter):
    """EN/GA comparison tab — the old `06_en_vs_ga_comparison.py` content."""
    return conn.sql(
        """
        SELECT
            topic,
            SUM(CASE WHEN language = 'en' THEN n ELSE 0 END) AS en_count,
            SUM(CASE WHEN language = 'ga' THEN n ELSE 0 END) AS ga_count,
            SUM(CASE WHEN language = 'en' THEN n ELSE 0 END) -
                SUM(CASE WHEN language = 'ga' THEN n ELSE 0 END) AS diff
        FROM cianfhoghlaim.lc._all_subjects_topics
        WHERE subject IN %(subjects)s
          AND level IN %(levels)s
        GROUP BY topic
        ORDER BY ABS(diff) DESC
        LIMIT 50
        """,
        params={
            "subjects": tuple(subject_filter.value),
            "levels": tuple(level_filter.value),
        },
    ).execute()


@app.cell
def _lc_query(conn, subject, subject_filter, level_filter, language_filter):
    """Canonical ibis query: per-subject topic counts for the given filters.

    Returns a pandas DataFrame for marimo's table rendering.
    """
    return conn.sql(
        """
        SELECT level, language, topic, COUNT(*) AS n
        FROM cianfhoghlaim.lc.{subject}_topics
        WHERE subject = %(subject)s
          AND level IN %(levels)s
          AND language IN %(languages)s
        GROUP BY level, language, topic
        ORDER BY n DESC
        LIMIT 100
        """,
        params={
            "subject": subject,
            "levels": tuple(level_filter.value),
            "languages": tuple(language_filter.value),
        },
    ).execute()


if __name__ == "__main__":
    app.run()