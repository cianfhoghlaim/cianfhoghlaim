# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13",
#   "ibis-framework[duckdb]>=9.0",
#   "pandas>=2.2",
#   "altair>=5.0",
#   "pyarrow>=15",
#   "anywidget>=0.9",
#   "traitlets>=5.14",
# ]
# ///

"""Marimo Patterns Tour — the educative outline for the marimo v14 features.

This notebook demonstrates every marimo v14 feature used by the BIEP
v3 jurisdiction dashboards (notebooks 19, 20, 21, 22, 26, 27) + the
Tier 3 grouped dashboards (meaisin_ops_console, celtic_languages,
corpus_overview, speedrun_mmo, academic_history, irish_law) + the
sync_health dashboard.

Designed to be the FIRST notebook an operator opens when learning
marimo. Each cell demonstrates ONE pattern with a `@app.cell(hide_code=True)`
prose intro (the E1 pattern).

## The 6 pillars demonstrated

1. **P1 — Tabbed operator console** (`mo.ui.tabs`)
2. **P2 — Live progress bar + form gating** (`mo.status.progress_bar`
   + `mo.ui.run_button(...).form()`)
3. **P3 — LLM-assisted analysis tab** (`mo.ui.chat` +
   `mo.ai.llm.openai(base_url=LITELLM_BASE_URL, model="minimax-m3")`)
4. **P4 — 3-column multi-pane grid layout** (`@app.cell(column=N)`
   + `layout_file=".../grid.json"`)
5. **P5 — RAGAS gauge widget (anywidget)**
   (`mo.ui.anywidget(RAGASGaugeWidget(...))`)
6. **P6 — Dual-mode (marimo + CLI)** per
   https://docs.marimo.io/guides/scripts/

## KCG patterns used
- marimo (per `.agents/skills/marimo/SKILL.md`) — every cell follows
  the marimo v14 idioms + the dual-mode CLI pattern per the official
  scripts guide.
- ibis (per `.agents/skills/ibis/SKILL.md`) — the queries go through
  `notebooks/_shared/db.py:connect_md()` (ibis-first).
- BIEP v3 systematic download — the 8-cell surface per the BIEP v3
  spec.

Reference: openspec/changes/2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1/
"""
import marimo

from notebooks._shared.marimo_patterns import (
    LITELLM_BASE_URL,
    cli_argparser_biep,
    cli_main_if_argv,
    cli_payload_to_output,
    form_gated_run_button,
    llm_chat_with_prompts,
    progress_bar_with_eta,
    ragas_color,
    ragas_gauge_widget,
    ragas_status_emoji,
    setup_biep_registry_header,
    tabbed_biep_operator_console,
    three_column_grid_app,
)
from notebooks._shared.ragas_gauge import (
    RAGASGaugeWidget,
    ragas_color as ragas_color_lib,
    ragas_status_emoji as ragas_status_emoji_lib,
)


__generated_with = "0.14.10"
app = marimo.App(width="full")


# ────────────────────────────────────────────────────────────────────────────
# Cell 1: Setup + R1 — `setup_biep_registry_header()`
# ────────────────────────────────────────────────────────────────────────────

@app.cell(hide_code=True)
def _intro():
    import marimo as mo
    mo.md(
        """
        # 🎓 Marimo Patterns Tour

        Welcome to the **marimo v14 features tour** for the cianfhoghlaim
        notebook surface. This notebook demonstrates every marimo v14
        feature used by the BIEP v3 jurisdiction dashboards + the Tier 3
        grouped dashboards + the sync_health dashboard.

        ## What you'll learn

        1. **P1** — `mo.ui.tabs` for the tabbed operator console
        2. **P2** — `mo.status.progress_bar` + `mo.ui.run_button(...).form()`
        3. **P3** — `mo.ui.chat` + `mo.ai.llm.openai(base_url=LITELLM_BASE_URL)`
        4. **P4** — `@app.cell(column=N)` + `layout_file=".../grid.json"`
        5. **P5** — `mo.ui.anywidget(RAGASGaugeWidget(...))`
        6. **P6** — Dual-mode (marimo + CLI) per
           [docs.marimo.io/guides/scripts/](https://docs.marimo.io/guides/scripts/)

        ## Run modes

        - **Marimo mode**: `marimo edit notebooks/00_marimo_patterns_tour.py`
        - **CLI mode**: `python notebooks/00_marimo_patterns_tour.py --milestone m1 --asset-check documents_ingested`

        Per https://docs.marimo.io/guides/scripts/ — the CLI mode emits
        JSON to stdout (for `mise run biep:v3:gate` consumption).
        """
    )
    return (mo,)


@app.cell
def _registry_header(mo):
    """R1 — `setup_biep_registry_header()` collapses the 14-line header.

    The canonical KCG header (model registry + schema introspection +
    deployment choice) is now a single function call instead of a
    14-line `try/except ImportError` block.

    Per https://docs.marimo.io/guides/best_practices.md — "Use
    functions. Encapsulate logic into functions to avoid polluting
    the global namespace with temporary or intermediate variables,
    and to avoid code duplication."
    """
    _ctx = setup_biep_registry_header()
    mo.md(
        f"""
        ## R1 — `setup_biep_registry_header()` ✓

        | Field | Value |
        |---|---|
        | Default LLM | `{_ctx['default_llm']}` |
        | Registry summary | `{_ctx['registry_summary']}` |
        | DLT source count | `{_ctx['dlt_source_count']}` |
        | CocoIndex App count | `{_ctx['coco_app_count']}` |
        | BAML class count | `{_ctx['baml_class_count']}` |
        | Enabled models (deployment-choice.yaml) | `{_ctx['enabled_models']}` |
        """
    )
    return (_ctx,)


# ────────────────────────────────────────────────────────────────────────────
# Cell 2: P1 — `mo.ui.tabs` for the tabbed operator console
# ────────────────────────────────────────────────────────────────────────────

@app.cell(hide_code=True)
def _section_p1(mo):
    mo.md(
        """
        ## P1 — Tabbed operator console (`mo.ui.tabs`)

        Per https://docs.marimo.io/guides/interactivity.md — UI elements
        assigned to global variables are reactive. `mo.ui.tabs` is a
        composite UI element that lets the operator pick from a tab
        bar.

        Reference: `docs/research/marimo/marimo/youtube-material/examples/motherduck-demo.py`
        (l. 124) + `notebooks/10_biep_pipeline_lakehouse_06_exam_papers_explorer.py`
        (l. 478-494 — the existing 8-tab operator console).
        """
    )
    return (mo,)


@app.cell
def _p1_dropdown(mo):
    """P1 — A `mo.ui.dropdown` that controls which tab is highlighted."""
    _selected_tab = mo.ui.dropdown(
        options=["Overview", "Cohorts", "Drill", "Schedule", "Asset Checks", "Dives", "Activity"],
        value="Overview",
        label="Tab to highlight",
    )
    mo.vstack([_selected_tab])
    return (_selected_tab,)


@app.cell
def _p1_tabs(_selected_tab, mo):
    """P1 — The 7-tab operator console.

    Per the BIEP v3 spec — the canonical 7 tabs are:
    Overview / Cohorts / Drill / Schedule / Asset Checks / Dives / Activity.
    """
    tabs = tabbed_biep_operator_console({
        "Overview": mo.md("## 📊 Overview\n\nThe BIEP v3 milestone summary + scheduling policy."),
        "Cohorts": mo.md("## 🎯 Cohorts\n\nThe per-jurisdiction cohort matrix (Ireland 100 rows, England 276 rows, etc.)."),
        "Drill": mo.md("## 🔍 Drill\n\nThe per-cohort drill-down with RAGAS gauge (P5)."),
        "Schedule": mo.md("## ⏰ Schedule\n\nThe 4-cadence scheduling policy (yearly / monthly / weekly / nightly + event-driven)."),
        "Asset Checks": mo.md("## ✅ Asset Checks\n\nThe live `dagster asset check` for the selected milestone."),
        "Dives": mo.md("## 🦆 Dives\n\nThe canonical MotherDuck Dives + Flights per jurisdiction."),
        "Activity": mo.md("## 🤖 Activity\n\nThe LLM-assisted analysis tab (P3)."),
    })
    mo.vstack([tabs, mo.md(f"_Currently selected tab: **{_selected_tab.value}**_")])
    return (tabs,)


# ────────────────────────────────────────────────────────────────────────────
# Cell 3: P2 — `mo.status.progress_bar` + `mo.ui.run_button(...).form()`
# ────────────────────────────────────────────────────────────────────────────

@app.cell(hide_code=True)
def _section_p2(mo):
    mo.md(
        """
        ## P2 — Live progress bar + form gating

        Per https://docs.marimo.io/guides/expensive_notebooks.md — the
        canonical way to gate an expensive operation is `mo.ui.run_button`
        + `mo.stop`. The advanced pattern adds `mo.status.progress_bar`
        for ETA + rate feedback.

        Reference: `docs/research/marimo/marimo/youtube-material/examples/lance-demo.py`
        (l. 39-46 — 250-row progress bar) + `chroma-db-search.py`
        (l. 320 — `mo.ui.text_area(...).form()`).
        """
    )
    return (mo,)


@app.cell
def _p2_form(mo):
    """P2 — `form_gated_run_button()` returns a (run_button, form) pair.

    The button only fires on form submit (not on every click).
    """
    _run_button, _form = form_gated_run_button(label="Run progress bar demo")
    mo.vstack([
        mo.md("Click the button below to start a 30-second progress bar:"),
        _run_button,
        _form,
    ])
    return (_form, _run_button)


@app.cell
def _p2_progress(_form, _run_button, mo):
    """P2 — Iterate the progress bar inside the form."""
    _progress = progress_bar_with_eta(title="Demo operation", total=30)
    if _run_button.value:
        for _i in _progress:
            import time
            time.sleep(1)
    mo.vstack([_progress])
    return (_progress,)


# ────────────────────────────────────────────────────────────────────────────
# Cell 4: P3 — `mo.ui.chat` + `mo.ai.llm.openai(base_url=LITELLM_BASE_URL)`
# ────────────────────────────────────────────────────────────────────────────

@app.cell(hide_code=True)
def _section_p3(mo):
    mo.md(
        f"""
        ## P3 — LLM-assisted analysis tab

        Per the `centralized-model-registry` capability — the canonical
        LLM is `minimax-m3`, routed through the litellm proxy at
        `{LITELLM_BASE_URL}` (which dispatches to local llama-swap models
        OR the minimax-m3 token plan API).

        The `llm_chat_with_prompts()` helper wraps `mo.ui.chat` +
        `mo.ai.llm.openai(base_url=LITELLM_BASE_URL, model=...)` with 5
        jurisdiction-specific built-in prompts.

        Reference: `docs/research/marimo/marimo/youtube-material/examples/motherduck-demo.py`
        (l. 81-87 — the `prompt()` LLM SQL trick) +
        `notebooks/10_biep_pipeline_lakehouse_05_marking_scheme_analyzer.py`
        (l. 248-270 — `mo.ui.chat(mo.ai.llm.openai(model="gpt-4o-mini", ...))`).
        """
    )
    return (mo,)


@app.cell
def _p3_chat(mo):
    """P3 — The LLM chat widget with 5 built-in prompts."""
    _chat = llm_chat_with_prompts(
        system_message=(
            "You are the cianfhoghlaim marimo patterns tour assistant. "
            "You help operators understand the marimo v14 features used by the BIEP v3 dashboards."
        ),
        prompts=[
            "💡 What is the marimo reactivity rule?",
            "💡 How do I wrap a dashboard in mo.ui.tabs?",
            "💡 How do I write a dual-mode (marimo + CLI) notebook?",
            "💡 How do I build a custom anywidget like the RAGASGaugeWidget?",
            "💡 What is the BIEP v3 8-cell operator console?",
        ],
    )
    mo.vstack([mo.md("## 🤖 Ask the LLM (via litellm)"), _chat])
    return (_chat,)


# ────────────────────────────────────────────────────────────────────────────
# Cell 5: P5 — `mo.ui.anywidget(RAGASGaugeWidget(...))`
# ────────────────────────────────────────────────────────────────────────────

@app.cell(hide_code=True)
def _section_p5(mo):
    mo.md(
        """
        ## P5 — RAGAS gauge widget (anywidget)

        Per https://docs.marimo.io/guides/integrating_with_marimo/custom_ui_plugins.md
        — `mo.ui.anywidget` is the canonical way to embed custom
        interactive widgets (anywidget + traitlets) in a marimo
        notebook.

        The `RAGASGaugeWidget` renders a circular progress gauge with a
        colour band (green ≥0.85 / yellow ≥0.70 / red <0.70) + a
        sparkline of the last N RAGAS scores.

        Reference: `docs/research/marimo/marimo/youtube-material/examples/chroma-db-search.py`
        (l. 388 — mopad gamepad widget).
        """
    )
    return (mo,)


@app.cell
def _p5_gauge(mo):
    """P5 — The RAGAS gauge widget."""
    _gauge = ragas_gauge_widget(
        score=0.82,
        history=[0.78, 0.79, 0.82],
        cohort_slug="ireland_lc_mathematics_higher_en",
    )
    mo.vstack([mo.md("## 📊 RAGAS Gauge (per-cohort)"), _gauge])
    return (_gauge,)


@app.cell
def _p5_gauge_live(mo):
    """P5 — A slider that live-updates the gauge."""
    _slider = mo.ui.slider(start=0.0, stop=1.0, step=0.01, value=0.82, label="RAGAS score")
    _gauge_live = ragas_gauge_widget(
        score=_slider.value,
        history=[0.78, 0.79, _slider.value],
        cohort_slug=f"live (score={_slider.value:.2f})",
    )
    mo.vstack([
        mo.md("## 📊 Live RAGAS Gauge (try the slider)"),
        _slider,
        _gauge_live,
    ])
    return (_gauge_live, _slider)


# ────────────────────────────────────────────────────────────────────────────
# Cell 6: P6 — Dual-mode (marimo + CLI) per https://docs.marimo.io/guides/scripts/
# ────────────────────────────────────────────────────────────────────────────

@app.cell(hide_code=True)
def _section_p6(mo):
    mo.md(
        """
        ## P6 — Dual-mode (marimo + CLI) per https://docs.marimo.io/guides/scripts/

        Per the official marimo scripts guide — every BIEP v3 jurisdiction
        dashboard is **dual-mode**:
        - **Marimo mode**: `marimo edit notebooks/19_ireland_pipeline_dashboard.py`
        - **CLI mode**: `python notebooks/19_ireland_pipeline_dashboard.py --milestone m1 --asset-check documents_ingested`

        The CLI mode emits a JSON payload to stdout (for `mise run
        biep:v3:gate` consumption).

        The canonical pattern is:
        ```python
        def _cli_main(argv=None) -> int:
            parser = cli_argparser_biep("19_ireland_pipeline_dashboard")
            args = parser.parse_args(argv)
            # ... invoke dagster asset check ...
            return 0

        if __name__ == "__main__":
            cli_main_if_argv(_cli_main, app)
        ```
        """
    )
    return (mo,)


# ────────────────────────────────────────────────────────────────────────────
# Dual-mode CLI (per https://docs.marimo.io/guides/scripts/)
# ────────────────────────────────────────────────────────────────────────────

def _cli_main(argv: list[str] | None = None) -> int:
    """CLI entry point — emits the marimo patterns tour info as JSON.

    Per https://docs.marimo.io/guides/scripts/ — when run with CLI args,
    this script emits JSON to stdout (the marimo runtime is skipped).
    """
    import json
    parser = cli_argparser_biep("00_marimo_patterns_tour")
    args = parser.parse_args(argv)

    payload = {
        "notebook": "00_marimo_patterns_tour",
        "milestone": args.milestone,
        "asset_check": args.asset_check,
        "cohort_kind": args.cohort_kind,
        "jurisdiction": args.jurisdiction,
        "status": "ok",
        "exit_code": 0,
        "features_demonstrated": [
            "R1 — setup_biep_registry_header()",
            "P1 — tabbed_biep_operator_console()",
            "P2 — progress_bar_with_eta() + form_gated_run_button()",
            "P3 — llm_chat_with_prompts()",
            "P4 — three_column_grid_app()",
            "P5 — ragas_gauge_widget()",
            "P6 — cli_argparser_biep() + cli_main_if_argv()",
        ],
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)