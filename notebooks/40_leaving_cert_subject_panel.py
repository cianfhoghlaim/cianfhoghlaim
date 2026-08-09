# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
# ]
# [tool.uv]
# package = "biep-v2-leaving-cert-subject-panel"
# ///

"""Leaving Cert Subject Panel — the 7-tab grouped marimo (BIEP v2).

Per the 2026-07-25-flatten-notebooks-v1 change + the
2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1 change
(which adds P1 + P3 + P6 marimo v14 features).

This single notebook replaces the 7 per-subject files that previously
lived at `notebooks/leaving_cert/<subject>.py` + `06_en_vs_ga_comparison.py`
(chem/cs/eng/ga/geo/math + EN/GA comparison, 2,657 LOC total).

The 7 tabs render side-by-side:
  1. Mathematics
  2. Chemistry
  3. Geography
  4. Gaeilge (bilingual EN/GA)
  5. English (bilingual EN/GA)
  6. Computer Science
  7. EN/GA Comparison (the old `06_en_vs_ga_comparison.py`)
+ An 8th "Ask BAML" tab (P3 — LLM chat)

## KCG patterns used
- marimo (per `.agents/skills/marimo/SKILL.md`) — `mo.ui.tabs` for the
  7 per-subject views; `mo.ui.multiselect` for the filter UI; +
  `mo.ui.chat` for the LLM tab (P3); + dual-mode CLI (P6) per
  https://docs.marimo.io/guides/scripts/.
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query goes
  through `notebooks._shared.db:connect_md()` (ibis-first).

TABLES:
  cianfhoghlaim.lc.<subject>.<level>_<lang>  (per-subject LanceDB tables)

Reference: openspec/changes/2026-07-25-flatten-notebooks-v1/
Reference: openspec/changes/2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1/
"""

import marimo

__generated_with = "0.14.10"
app = marimo.App(width="full")


from notebooks._shared.marimo_patterns import (
    cli_argparser_biep,
    cli_main_if_argv,
    cli_payload_to_output,
    llm_chat_with_prompts,
    setup_biep_registry_header,
)


@app.cell
def _intro(mo):
    """R1 — `setup_biep_registry_header()` collapses the 14-line header."""
    _ctx = setup_biep_registry_header()
    mo.md(
        f"""
        # 📚 Leaving Cert Subject Panel — 7-tab grouped marimo (BIEP v2)

        Browse the 6 priority LC subjects side-by-side, plus an
        EN/GA comparison view. Replaces the 7 per-subject
        `notebooks/leaving_cert/<subject>.py` + `06_en_vs_ga_comparison.py`
        files (~2,657 LOC).

        **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
        **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled)
        """
    )
    return (_ctx, mo)


@app.cell
def _filter_ui(mo):
    """The filter UI — subject + level + language multiselects."""
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
def _ibis_conn(mo):
    """The ibis-first connection (per the BIEP v2 spec)."""
    from notebooks._shared.db import connect_md
    conn = connect_md()
    mo.md("✓ ibis-first wired — per-subject LanceDB tables: `cianhoghlaim.lc.<subject>.<level>_<lang>`")
    return (conn,)


@app.cell
def _tabs(conn, subject_filter, level_filter, language_filter, mo):
    """The 8-tab grouped view (P1 — `mo.ui.tabs`).

    Each per-subject tab queries the per-subject LC LanceDB table via ibis.
    The 8th tab is the LLM "Ask the Syllabus" chat (P3).
    """
    subject_tabs = mo.ui.tabs({
        "1. Mathematics": _lc_query(conn, "mathematics", subject_filter, level_filter, language_filter, mo),
        "2. Chemistry": _lc_query(conn, "chemistry", subject_filter, level_filter, language_filter, mo),
        "3. Geography": _lc_query(conn, "geography", subject_filter, level_filter, language_filter, mo),
        "4. Gaeilge (EN/GA)": _lc_query(conn, "gaeilge", subject_filter, level_filter, language_filter, mo),
        "5. English (EN/GA)": _lc_query(conn, "english", subject_filter, level_filter, language_filter, mo),
        "6. Computer Science": _lc_query(conn, "computer_science", subject_filter, level_filter, language_filter, mo),
        "7. EN/GA Comparison": _en_vs_ga_query(conn, subject_filter, level_filter, mo),
        "8. 🤖 Ask BAML": _llm_tab(mo),  # P3 — LLM-assisted analysis tab
    })
    subject_tabs


@app.cell
def _lc_query(conn, subject, subject_filter, level_filter, language_filter, mo):
    """Canonical ibis query: per-subject topic counts for the given filters.

    Returns a pandas DataFrame for marimo's table rendering.
    """
    return conn.sql(
        f"""
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


@app.cell
def _en_vs_ga_query(conn, subject_filter, level_filter, mo):
    """EN/GA comparison query — the old `06_en_vs_ga_comparison.py` content."""
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
def _llm_tab(mo):
    """P3 — LLM-assisted analysis tab via mo.ui.chat + mo.ai.llm.openai()."""
    _chat = llm_chat_with_prompts(
        system_message=(
            "You are the BIEP v2 Leaving Cert Subject Panel assistant. "
            "You have access to the 6 priority LC subjects (Mathematics, "
            "Chemistry, Geography, English, Gaeilge, Computer Science) across "
            "Higher/Ordinary/Foundation levels and EN/GA languages. When the "
            "user asks about a specific topic, refer to the cianfhoghlaim.lc."
            "<subject>_topics tables."
        ),
        prompts=[
            "📚 Summarise the Mathematics Higher EN learning outcomes for 'algebra'",
            "🔍 Find the Irish-language equivalent for the Chemistry topic 'atomic structure'",
            "📊 Compare EN vs GA topic frequency for English Higher",
            "🎯 What are the 5 most-tested topics on the Gaeilge Higher exam?",
            "🌐 Translate the Computer Science HL topic 'algorithms' into Irish",
        ],
    )
    mo.vstack([mo.md("## 🤖 Ask the LC Subject Panel (via litellm)"), _chat])


def _cli_main(argv: list[str] | None = None) -> int:
    """CLI entry point — emits an LC panel summary payload."""
    parser = cli_argparser_biep("40_leaving_cert_subject_panel")
    args = parser.parse_args(argv)

    payload = {
        "notebook": "40_leaving_cert_subject_panel",
        "milestone": args.milestone,
        "asset_check": args.asset_check,
        "status": "ok",
        "exit_code": 0,
        "subjects": ["mathematics", "chemistry", "geography", "english", "gaeilge", "computer_science"],
        "note": (
            "The LC Subject Panel renders 7 per-subject tabs + 1 LLM tab. "
            "Run via `marimo edit notebooks/40_leaving_cert_subject_panel.py`."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)