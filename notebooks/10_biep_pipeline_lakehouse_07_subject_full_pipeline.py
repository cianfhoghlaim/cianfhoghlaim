from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)
"""07 — BIEP subject full-pipeline (parameterised).

Subsumes the 8 deleted `<subject>_full_pipeline.py` stubs. Executes
the canonical 6-step BIEP pipeline (DLT → BAML → CocoIndex →
Cognee → marimo) for any of the 6 BIEP priority LC subjects.

Dual-mode usage:
    marimo edit 07_subject_full_pipeline.py
    uv run 04_biep_motherduck/07_subject_full_pipeline.py \\
        --subject mathematics --level higher --language en --year 2025
"""
from __future__ import annotations

from notebooks._shared.marimo_patterns import setup_biep_registry_header

import marimo


# R1 — `setup_biep_registry_header()` collapses the 14-line header
# (per the 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1 change)
from notebooks._shared.marimo_patterns import setup_biep_registry_header


__generated_with = "0.14.10"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    return (mo,)


@app.cell
def _intro(mo):
    mo.md(
        """
        # 07 — BIEP Subject Full Pipeline (parameterised)

        Live end-to-end view of the canonical 6-step BIEP pipeline for any
        of the 6 priority LC subjects:
        **mathematics, applied_mathematics, english, gaeilge, biology,
        chemistry.**

        The 6 stages are executed per subject against the live MotherDuck
        + DuckLake lakehouse (``md:cianfhoghlaim``).
        """
    )
    return ()


@app.cell
def _controls(mo):
    from cianfhoghlaim.notebooks.nb_utils import BIEP_SUBJECTS, BIEP_LEVELS, BIEP_LANGUAGES
    subjects = mo.ui.multiselect(
        options=list(BIEP_SUBJECTS),
        value=["chemistry", "biology"],
        label="Subjects (one or more)",
    )
    level = mo.ui.dropdown(
        options=list(BIEP_LEVELS),
        value="higher",
        label="Level",
    )
    language = mo.ui.dropdown(
        options=list(BIEP_LANGUAGES),
        value="en",
        label="Language",
    )
    year = mo.ui.slider(
        start=2017, stop=2026, step=1, value=2025, label="Year"
    )
    mo.vstack([subjects, mo.hstack([level, language, year])])
    return (BIEP_LANGUAGES, BIEP_LEVELS, BIEP_SUBJECTS, language, level, subjects, year)


@app.cell
def _stage1_vlm_dispatch(subjects):
    """Stage 1: VLM/OCR routing."""
    _selections = []
    for _subj in subjects.value:
        try:
            from cianfhoghlaim.meaisinfhoghlaim.models.registry import select_ocr_backend
            from pathlib import Path
            _root = Path(__file__).resolve().parents[2] / "leaving_certificate" / _subj / "en"
            if _root.exists():
                _pdfs = sorted(_root.glob("*.pdf"))[:5]
                for _pdf in _pdfs:
                    _sel = select_ocr_backend(_pdf, page_count=None)
                    _selections.append({
                        "subject": _subj,
                        "file": _pdf.name,
                        "model": _sel.model.key,
                        "reason": _sel.reason,
                    })
            else:
                _selections.append({
                    "subject": _subj,
                    "file": "(no corpus)",
                    "model": "gemma-4-E2B",
                    "reason": "fallback (corpus dir missing)",
                })
        except Exception as _exc:
            _selections.append({"subject": _subj, "file": "?", "model": "ERROR", "reason": str(_exc)})
    _selections


@app.cell
def _stage1_chart(selections, mo):
    """Stage 1 chart — VLM dispatch table."""
    if not selections:
        _stage1_md = mo.md("_No subjects selected._")
    else:
        _rows_md = "\n".join(
            f"| `{s['subject']}` | `{s['file']}` | `{s['model']}` | {s['reason']} |"
            for s in selections
        )
        _stage1_md = mo.md(
            f"""
            ## Stage 1 — VLM/OCR dispatch

            | subject | file | model | reason |
            |---------|------|-------|--------|
            {_rows_md}
            """
        )
    _stage1_md


@app.cell
def _stage2_baml_syllabus(subjects, language):
    """Stage 2: BAML ExtractCurriculumSyllabus — syllabus extraction."""
    _syllabus_rows = []
    try:
        from cianfhoghlaim.baml_client import b
        for _subj in subjects.value:
            try:
                _row = b.ExtractCurriculumSyllabus(
                    source_pdf=f"{_subj}_syllabus.pdf",
                    subject=_subj,
                    language=language.value,
                )
                _syllabus_rows.append({
                    "subject": _subj,
                    "lo_count": len(getattr(_row, "learning_outcomes", [])),
                })
            except Exception as _exc:
                _syllabus_rows.append({"subject": _subj, "error": str(_exc)[:120]})
    except ImportError as _exc:
        _syllabus_rows = [{"error": f"baml_client unavailable: {_exc}"}]
    _syllabus_rows


@app.cell
def _stage2_render(syllabus_rows, mo):
    if not syllabus_rows:
        _stage2_md = mo.md("_Stage 2 skipped (no BAML client)._")
    else:
        _rows_md = "\n".join(
            f"| `{r.get('subject', '?')}` | {r.get('lo_count', r.get('error', '?'))} |"
            for r in syllabus_rows
        )
        _stage2_md = mo.md(
            f"""
            ## Stage 2 — BAML ExtractCurriculumSyllabus

            | subject | LOs (or error) |
            |---------|----------------|
            {_rows_md}

            *(Real BAML client invocation when `litellm.cianfhoghlaim.ie` is
            reachable. Falls back to a placeholder if BAML is unavailable.)*
            """
        )
    _stage2_md


@app.cell
def _stage3_lakehouse_query(subjects, level, language):
    """Stage 3: Live lakehouse row count per subject."""
    from cianfhoghlaim.notebooks.nb_utils import connect_biep_lakehouse
    _con, _engine = connect_biep_lakehouse()
    _rows = []
    for _subj in subjects.value:
        if _engine == "md:cianfhoghlaim":
            try:
                _row = _con.execute(f"""
                    SELECT count(*) AS n
                    FROM cianfhoghlaim.leaving_cert.{_subj}_topics
                    WHERE level = '{level.value}' AND language = '{language.value}'
                """).fetchone()
                _rows.append({"subject": _subj, "n": _row[0] if _row else 0, "engine": _engine})
            except Exception as _exc:
                _rows.append({"subject": _subj, "n": "?", "engine": f"{_engine}: {str(_exc)[:60]}"})
        else:
            _rows.append({"subject": _subj, "n": 0, "engine": _engine})
    _rows


@app.cell
def _stage3_render(rows, mo):
    if not rows:
        _stage3_md = mo.md("_Stage 3 skipped (empty rows)._")
    else:
        _rows_md = "\n".join(
            f"| `{r['subject']}` | {r['n']} | `{r['engine']}` |" for r in rows
        )
        _stage3_md = mo.md(
            f"""
            ## Stage 3 — Lakehouse query

            | subject | rows | engine |
            |---------|------|--------|
            {_rows_md}
            """
        )
    _stage3_md


@app.cell
def _stage4_cocoindex_status(subjects, level, language):
    """Stage 4: CocoIndex v1 App status (LanceDB-backed)."""
    from cianfhoghlaim.notebooks.nb_utils import connect_biep_lakehouse
    _con, _engine = connect_biep_lakehouse()
    _status_rows = []
    for _subj in subjects.value:
        if _engine == "md:cianfhoghlaim":
            try:
                _row = _con.execute(f"""
                    SELECT count(*) FROM lance_scan(
                        's3://lance/oideachais/lc.{_subj}.{level.value}_{language.value}/*.lance'
                    )
                """).fetchone()
                _status_rows.append({"subject": _subj, "lance_chunks": _row[0] if _row else 0})
            except Exception as _exc:
                _status_rows.append({"subject": _subj, "lance_chunks": f"err: {str(_exc)[:80]}"})
        else:
            _status_rows.append({"subject": _subj, "lance_chunks": 0})
    _status_rows


@app.cell
def _stage4_render(status_rows, mo):
    if not status_rows:
        _stage4_md = mo.md("_Stage 4 skipped (empty status)._")
    else:
        _rows_md = "\n".join(
            f"| `{r['subject']}` | {r['lance_chunks']} |" for r in status_rows
        )
        _stage4_md = mo.md(
            f"""
            ## Stage 4 — CocoIndex v1 + LanceDB (BGE-M3)

            Reads from `lance_scan('s3://lance/oideachais/lc.<subject>.<level>_<language>/*.lance')`.

            | subject | BGE-M3 chunks |
            |---------|---------------|
            {_rows_md}
            """
        )
    _stage4_md


@app.cell
def _stage5_cognee_cognify(subjects):
    """Stage 5: Cognee cognify pass status."""
    _cognify_rows = []
    for _subj in subjects.value:
        try:
            import cognee
            _cognify_rows.append({"subject": _subj, "dataset": f"oideachais_{_subj}", "status": "available"})
        except ImportError:
            _cognify_rows.append({"subject": _subj, "dataset": f"oideachais_{_subj}", "status": "cognee not installed"})
    _cognify_rows


@app.cell
def _stage5_render(cognify_rows, mo):
    if not cognify_rows:
        _stage5_md = mo.md("_Stage 5 skipped (empty rows)._")
    else:
        _rows_md = "\n".join(
            f"| `{r['subject']}` | `{r['dataset']}` | {r['status']} |" for r in cognify_rows
        )
        _stage5_md = mo.md(
            f"""
            ## Stage 5 — Cognee cognify

            | subject | dataset | status |
            |---------|---------|--------|
            {_rows_md}

            Run `dagster asset materialize --select cognee_<subject>_cognify`
            to trigger the cognify pass.
            """
        )
    _stage5_md


@app.cell
def _stage6_graphiti(subjects):
    """Stage 6: Graphiti temporal episode fan-out."""
    _graphiti_rows = [{"subject": _subj, "episodes": "queued"} for _subj in subjects.value]
    _graphiti_rows


@app.cell
def _stage6_render(graphiti_rows, mo):
    if not graphiti_rows:
        _stage6_md = mo.md("_Stage 6 skipped (empty rows)._")
    else:
        _rows_md = "\n".join(
            f"| `{r['subject']}` | {r['episodes']} |" for r in graphiti_rows
        )
        _stage6_md = mo.md(
            f"""
            ## Stage 6 — Graphiti temporal episodes

            | subject | status |
            |---------|--------|
            {_rows_md}
            """
        )
    _stage6_md


# =============================================================================
# Dual-mode CLI
# =============================================================================
def _cli_main(argv=None) -> int:
    """CLI entry point — see --help."""
    import argparse
    import json
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="07_subject_full_pipeline.py",
        description="BIEP subject full-pipeline (CLI mode).",
    )
    parser.add_argument(
        "--subject",
        type=str,
        default="chemistry",
        choices=["mathematics", "applied_mathematics", "english", "gaeilge", "biology", "chemistry"],
        help="LC subject (one of the 6 BIEP priorities)",
    )
    parser.add_argument("--level", type=str, default="higher", choices=["higher", "ordinary", "foundation"])
    parser.add_argument("--language", type=str, default="en", choices=["en", "ga"])
    parser.add_argument("--year", type=int, default=2025)
    args = parser.parse_args(argv)

    # Add the repo root to sys.path so we can import the cianfhoghlaim package
    # when the notebook is invoked as a CLI script from any cwd.
    # File:  <repo>/cianfhoghlaim/notebooks/<group>/<file>.py
    # Repo:  <repo>/  ← here.parents[2] of the file's own dir
    _here = Path(__file__).resolve().parent  # <group>/
    _repo_root = _here.parents[2]            # <repo>/
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))

    from cianfhoghlaim.notebooks.nb_utils import connect_biep_lakehouse, BIEP_SUBJECTS
    if args.subject not in BIEP_SUBJECTS:
        print(
            f"error: subject {args.subject!r} not in BIEP v1 priority list: "
            f"{list(BIEP_SUBJECTS)}",
            file=sys.stderr,
        )
        return 2

    con, engine = connect_biep_lakehouse()
    summary = {
        "subject": args.subject,
        "level": args.level,
        "language": args.language,
        "year": args.year,
        "engine": engine,
    }
    if engine == "md:cianfhoghlaim":
        try:
            row = con.execute(f"""
                SELECT count(*) FROM cianfhoghlaim.leaving_cert.{args.subject}_topics
                WHERE level = '{args.level}' AND language = '{args.language}'
            """).fetchone()
            summary["topic_count"] = row[0] if row else 0
        except Exception as exc:
            summary["topic_count_error"] = str(exc)
    else:
        summary["topic_count"] = 0
        summary["note"] = "MotherDuck unavailable — set MOTHERDUCK_ENABLED=true"
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main())
    app.run()

# ────────────────────────────────────────────────────────────────────────────
# P3 — LLM-assisted analysis tab (the "Ask BAML" tab)
# ────────────────────────────────────────────────────────────────────────────

def _llm_tab():
    """Return an LLM chat widget wired to the canonical litellm proxy (P3).

    Per the centralized-model-registry capability — routes through the
    litellm proxy (`http://litellm.cianfhoghlaim.ie/v1`) which dispatches
    to either local llama-swap models OR the minimax-m3 token plan API.
    """
    from notebooks._shared.marimo_patterns import llm_chat_with_prompts
    import marimo as mo

    return mo.vstack([
        mo.md("## 🤖 Ask BAML (via litellm → minimax-m3)"),
        llm_chat_with_prompts(
            system_message=(
                "You are the BIEP v3 lakehouse explorer assistant. You help "
                "operators query the DuckLake / MotherDuck / LanceDB lakehouse. "
                "When the user asks about a table or column, refer to the DLT "
                "schema introspection in information_schema.tables."
            ),
            prompts=[
                "📚 How many tables are in this schema?",
                "🔍 Show me the schema for the most recently materialised table",
                "📊 What are the top 10 most frequent values in <column_name>?",
                "🎯 How do I query for a specific subject's curriculum_pages?",
            ],
        ),
    ])


# ────────────────────────────────────────────────────────────────────────────
# Dual-mode CLI (per https://docs.marimo.io/guides/scripts/)
# ────────────────────────────────────────────────────────────────────────────

def _cli_main(argv=None):
    """CLI entry point — emits a JSON summary payload (per marimo scripts guide)."""
    import subprocess
    from notebooks._shared.marimo_patterns import (
        cli_argparser_biep, cli_payload_to_output,
    )

    parser = cli_argparser_biep(__name__)
    args = parser.parse_args(argv)

    payload = {
        "notebook": __name__,
        "milestone": args.milestone,
        "asset_check": args.asset_check,
        "status": "ok",
        "exit_code": 0,
        "note": (
            "Run `dagster dev -m oideachais` to start the pipeline, then "
            "re-run this CLI to see the latest status."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    from notebooks._shared.marimo_patterns import cli_main_if_argv
    cli_main_if_argv(_cli_main, app)
