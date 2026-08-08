"""Canonical marimo pattern helpers for the Cianfhoghlaim notebook surface.

This module hoists the high-impact marimo v14 patterns (P1-P6) +
the 4 refactor patterns (R1-R4) into reusable functions. Every BIEP v3
jurisdiction dashboard + BIEP lakehouse explorer + Tier 3 grouped
dashboard + sync_health dashboard imports from here.

The 8 pillars of improvement delivered:

R1 — Hoist the centralized-registry header
    `setup_biep_registry_header()` — collapses the 14-line
    `try: from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for;
    from notebooks._shared.schema import ... except ImportError: ...
    _DEFAULT_LLM = "minimax-m3"` block that was duplicated across 18
    notebooks.

P1 — Tabbed operator console
    `tabbed_biep_operator_console(tabs, label)` — wraps the 8-cell
    BIEP v3 surface in `mo.ui.tabs` so the operator picks from a
    single tab bar (Overview / Cohorts / Drill / Schedule / Asset
    Checks / Dives / Activity).

P2 — Live progress bar + form gating
    `progress_bar_with_eta(title, total)` — wraps
    `mo.status.progress_bar(range(total), show_eta=True, show_rate=True)`.
    `form_gated_run_button(label)` — wraps `mo.ui.run_button(label).form()`.

P3 — LLM-assisted analysis tab
    `llm_chat_with_prompts(system_message, prompts, **kwargs)` —
    wraps `mo.ui.chat(mo.ai.llm.openai(base_url=LITELLM_BASE_URL, ...), prompts=[...])`.
    Routes through the litellm proxy (which dispatches to local
    llama-swap models OR the minimax-m3 token plan API per the
    `centralized-model-registry` capability).

P4 — 3-column multi-pane grid layout
    `three_column_grid_app(title, layout_filename)` — returns a
    `marimo.App(width="full", layout_file=...)` configured for the
    3-column BIEP v3 operator console.

P5 — RAGAS gauge widget (anywidget)
    `ragas_gauge_widget(score, history)` — wraps
    `mo.ui.anywidget(RAGASGaugeWidget(...))` from
    `notebooks/_shared/ragas_gauge.py`.

P6 — Dual-mode (marimo + CLI) per https://docs.marimo.io/guides/scripts/
    `cli_argparser_biep(notebook_name)` — the canonical argparse for
    the BIEP v3 dashboards (--milestone, --asset-check, --cohort-kind,
    --jurisdiction, --output flags).

## KCG patterns used
- marimo (per `.agents/skills/marimo/SKILL.md`) — every helper follows
  the marimo v14 idioms (`mo.ui.tabs`, `mo.status.progress_bar`,
  `mo.ui.chat`, `mo.ui.anywidget`, dual-mode CLI).
- ibis (per `.agents/skills/ibis/SKILL.md`) — the helpers are
  marimo-agnostic (pure functions, returning widgets).
- centralized-model-registry (per
  `.agents/skills/centralized-registry/SKILL.md`) — the LLM helper
  uses `model_for("text_llm", "default")` to resolve the canonical
  text LLM.

Reference: openspec/changes/2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1/
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# ────────────────────────────────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────────────────────────────────

# The canonical LiteLLM OpenAI-compatible base URL.
# Per the centralized-model-registry capability — the canonical LLM
# gateway. All `mo.ai.llm.openai()` calls route through here so the
# operator can swap between local llama-swap models and the minimax-m3
# token plan API via `deployment-choice.yaml`.
LITELLM_BASE_URL = os.environ.get(
    "CIANFHOGHLAIM_LITELLM_BASE_URL",
    "http://litellm.cianfhoghlaim.ie/v1",
)
"""The canonical LiteLLM OpenAI-compatible base URL.

Honours `CIANFHOGHLAIM_LITELLM_BASE_URL`; defaults to
`http://litellm.cianfhoghlaim.ie/v1` (the production litellm endpoint).
"""


# The canonical RAGAS threshold (per the BIEP v3 spec).
RAGAS_PASS_THRESHOLD = 0.70
"""The canonical RAGAS pass threshold for the BIEP v3 4-path OCR ensemble."""


def ragas_color(score: float) -> str:
    """Return the colour band for a RAGAS score.

    - Green ≥0.85 (excellent)
    - Yellow ≥0.70 (pass)
    - Red <0.70 (fail)

    Used by both the `RAGASGaugeWidget` and the markdown cells.
    """
    if score >= 0.85:
        return "#22c55e"  # green
    elif score >= RAGAS_PASS_THRESHOLD:
        return "#eab308"  # yellow
    else:
        return "#ef4444"  # red


def ragas_status_emoji(score: float) -> str:
    """Return the status emoji for a RAGAS score."""
    if score >= 0.85:
        return "✅"
    elif score >= RAGAS_PASS_THRESHOLD:
        return "⚠️"
    else:
        return "❌"


# ────────────────────────────────────────────────────────────────────────────
# R1 — Hoist the centralized-registry header
# ────────────────────────────────────────────────────────────────────────────

def setup_biep_registry_header() -> dict[str, Any]:
    """Hoist the canonical 14-line `try/except ImportError` header (R1).

    Replaces the 14-line block that was duplicated across 18 notebooks:

    ```python
    try:
        from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for
        from notebooks._shared.schema import (
            list_dlt_sources, list_cocoindex_apps, list_baml_classes,
            read_deployment_choice,
        )
        _DEFAULT_LLM = model_for("text_llm", "default")
        _REGISTRY_SUMMARY = MODEL_REGISTRY.summary()
        _DLT_SOURCE_COUNT = len(list_dlt_sources())
        _COCO_APP_COUNT = len(list_cocoindex_apps())
        _BAML_CLASS_COUNT = len(list_baml_classes())
        _ENABLED_MODELS = sum(
            1 for v in read_deployment_choice().get("enabled_models", {}).values() if v
        )
    except ImportError:
        _DEFAULT_LLM = "minimax-m3"
        _REGISTRY_SUMMARY = {"total": 0, "by_family": {}, "available": 0, "deprecated": 0}
        _DLT_SOURCE_COUNT = _COCO_APP_COUNT = _BAML_CLASS_COUNT = 0
        _ENABLED_MODELS = 0
    ```

    Returns a dict with the 6 registry fields. The caller unpacks with:

    ```python
    from notebooks._shared.marimo_patterns import setup_biep_registry_header
    _ctx = setup_biep_registry_header()
    # Then use _ctx["default_llm"], _ctx["registry_summary"], etc.
    ```

    The dict keys are:
    - `default_llm` — the canonical text LLM alias (default: "minimax-m3")
    - `registry_summary` — the MODEL_REGISTRY.summary() dict
    - `dlt_source_count` — the count of `@dlt.source` decorated functions
    - `coco_app_count` — the count of CocoIndex v1 Apps
    - `baml_class_count` — the count of BAML classes
    - `enabled_models` — the count of enabled models in
      `deployment-choice.yaml`
    """
    try:
        from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for  # noqa: E402
        from notebooks._shared.schema import (  # noqa: E402
            list_dlt_sources, list_cocoindex_apps, list_baml_classes,
            read_deployment_choice,
        )
        return {
            "default_llm": model_for("text_llm", "default"),
            "registry_summary": MODEL_REGISTRY.summary(),
            "dlt_source_count": len(list_dlt_sources()),
            "coco_app_count": len(list_cocoindex_apps()),
            "baml_class_count": len(list_baml_classes()),
            "enabled_models": sum(
                1 for v in read_deployment_choice().get("enabled_models", {}).values() if v
            ),
        }
    except ImportError:
        # Fallback for minimal container builds where the registry is unavailable
        return {
            "default_llm": "minimax-m3",  # canonical M3 alias (the legacy hardcoded value)
            "registry_summary": {"total": 0, "by_family": {}, "available": 0, "deprecated": 0},
            "dlt_source_count": 0,
            "coco_app_count": 0,
            "baml_class_count": 0,
            "enabled_models": 0,
        }


# ────────────────────────────────────────────────────────────────────────────
# P1 — Tabbed operator console
# ────────────────────────────────────────────────────────────────────────────

def tabbed_biep_operator_console(
    tabs: dict[str, Any],
    label: str = "BIEP v3 operator console",
) -> Any:
    """Wrap the BIEP v3 operator console tabs in `mo.ui.tabs` (P1).

    Per https://docs.marimo.io/guides/interactivity.md — `mo.ui.tabs`
    is a composite UI element that lets the operator pick from a tab
    bar. The argument `tabs` is a dict mapping tab label → child
    widget (typically a `mo.vstack([...])` or `mo.md(...)`).

    The 7 canonical tabs for the BIEP v3 dashboards are:
    - Overview
    - Cohorts
    - Drill
    - Schedule
    - Asset Checks
    - Dives
    - Activity

    Usage:
    ```python
    tabs = tabbed_biep_operator_console({
        "Overview": overview_ui,
        "Cohorts": cohort_matrix_ui,
        "Drill": drill_down_ui,
        "Schedule": schedule_ui,
        "Asset Checks": asset_check_ui,
        "Dives": dive_link_ui,
        "Activity": activity_ui,
    })
    tabs
    ```
    """
    try:
        import marimo as mo
    except ImportError:
        return tabs  # Graceful fallback for non-marimo contexts (tests, etc.)
    return mo.ui.tabs(tabs, label=label)


# ────────────────────────────────────────────────────────────────────────────
# P2 — Live progress bar + form gating
# ────────────────────────────────────────────────────────────────────────────

def progress_bar_with_eta(title: str, total: int, subtitle: str = "Working!") -> Any:
    """Return a `mo.status.progress_bar` with ETA + rate (P2).

    Per the upstream `lance-demo.py` pattern (l. 39-46) — the progress
    bar shows ETA + rate so the operator sees feedback during
    long-running operations.

    Usage:
    ```python
    progress = progress_bar_with_eta(title="Polling dagster asset check", total=120)
    for i in progress:
        time.sleep(1)
        # ... poll ...
    ```
    """
    try:
        import marimo as mo
    except ImportError:
        return range(total)  # Graceful fallback
    return mo.status.progress_bar(
        range(total),
        title=title,
        subtitle=subtitle,
        show_eta=True,
        show_rate=True,
    )


def form_gated_run_button(label: str, **kwargs: Any) -> tuple[Any, Any]:
    """Return a `(run_button, form)` pair where the button only fires on form submit (P2).

    Per the upstream `chroma-db-search.py` pattern (l. 320) — wraps
    `mo.ui.run_button(label).form()` so the button only fires when
    the form is submitted (not on every click).

    Usage:
    ```python
    run_button, form = form_gated_run_button(label="Run dagster asset check")
    mo.vstack([run_button, form])
    ```
    """
    try:
        import marimo as mo
    except ImportError:
        return None, None
    run_button = mo.ui.run_button(label=label, **kwargs)
    return run_button, run_button.form()


def run_dagster_asset_check(
    checks: str,
    *,
    timeout: int = 120,
    module: str = "orchestration.definitions",
) -> dict[str, Any]:
    """Run the canonical `dagster asset check` and return the result (P2).

    Per the BIEP v3 spec — every BIEP jurisdiction dashboard's
    `_asset_check_status` cell calls this to invoke the live asset
    check via `subprocess.run` and surface the result as JSON.

    Parameters
    ----------
    checks : str
        The comma-separated list of check names (e.g.
        "ireland_lc_documents_ingested_check,ireland_lc_extractions_ragas_check")
    timeout : int
        The subprocess timeout in seconds (default: 120)
    module : str
        The Dagster module to load (default:
        "orchestration.definitions")

    Returns
    -------
    dict
        - `checks`: the input checks string
        - `exit_code`: the subprocess return code
        - `status`: "passed" / "failed" / "error"
        - `stdout_tail`: the last 1000 chars of stdout
        - `stderr_tail`: the last 500 chars of stderr
        - `error`: the error message (if any)
    """
    try:
        result = subprocess.run(
            [
                "uv", "run", "dagster", "asset", "check",
                "--select", checks,
                "-m", module,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "checks": checks,
            "exit_code": result.returncode,
            "status": "passed" if result.returncode == 0 else "failed",
            "stdout_tail": result.stdout[-1000:],
            "stderr_tail": result.stderr[-500:],
        }
    except subprocess.TimeoutExpired:
        return {
            "checks": checks,
            "exit_code": -1,
            "status": "timeout",
            "stdout_tail": "",
            "stderr_tail": f"Subprocess timed out after {timeout}s",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "checks": checks,
            "exit_code": -1,
            "status": "error",
            "error": str(exc),
            "stdout_tail": "",
            "stderr_tail": "",
        }


# ────────────────────────────────────────────────────────────────────────────
# P3 — LLM-assisted analysis tab
# ────────────────────────────────────────────────────────────────────────────

def llm_chat_with_prompts(
    system_message: str,
    prompts: list[str],
    *,
    model: str | None = None,
    base_url: str | None = None,
    show_configuration_controls: bool = False,
) -> Any:
    """Return an LLM chat widget wired to the litellm proxy (P3).

    Per the upstream `motherduck-demo.py` + `10_biep_05_marking_scheme_analyzer.py`
    patterns — wraps `mo.ui.chat(mo.ai.llm.openai(base_url=..., model=...,
    system_message=...), prompts=[...])`.

    The litellm proxy dispatches to either local llama-swap models OR
    the minimax-m3 token plan API per the `centralized-model-registry`
    capability.

    Parameters
    ----------
    system_message : str
        The system message that primes the LLM (e.g. "You are the
        BIEP v3 Ireland education assistant...")
    prompts : list[str]
        The 4-5 built-in prompts that appear in the chat widget
        (e.g. "Summarise the marking scheme")
    model : str, optional
        The canonical model alias. If None, resolves via
        `model_for("text_llm", "default")` (returns "minimax-m3")
    base_url : str, optional
        The OpenAI-compatible base URL. If None, uses
        `LITELLM_BASE_URL` (`http://litellm.cianfhoghlaim.ie/v1`)
    show_configuration_controls : bool
        Whether to show the marimo LLM configuration controls in the
        chat widget (default: False for a cleaner UI)

    Usage:
    ```python
    chat = llm_chat_with_prompts(
        system_message="You are the BIEP v3 Ireland education assistant...",
        prompts=[
            "📚 Summarise the Ireland LC Mathematics Higher EN 2024 syllabus",
            "🔍 Find the Irish-language equivalent for the LC Chemistry topic 'atomic structure'",
            "📊 Compare the marking scheme distribution between 2024 and 2023",
        ],
    )
    mo.vstack([mo.md("## 🤖 Ask BAML (via litellm → minimax-m3)"), chat])
    ```
    """
    if model is None:
        try:
            from meaisinfhoghlaim.models import model_for
            model = model_for("text_llm", "default")
        except ImportError:
            model = "minimax-m3"  # canonical fallback

    if base_url is None:
        base_url = LITELLM_BASE_URL

    try:
        import marimo as mo
    except ImportError:
        return None

    llm = mo.ai.llm.openai(
        base_url=base_url,
        model=model,
        system_message=system_message,
    )
    return mo.ui.chat(
        llm,
        prompts=prompts,
        show_configuration_controls=show_configuration_controls,
    )


# ────────────────────────────────────────────────────────────────────────────
# P4 — 3-column multi-pane grid layout
# ────────────────────────────────────────────────────────────────────────────

def three_column_grid_app(
    title: str,
    layout_filename: str | None = None,
    width: str = "full",
) -> Any:
    """Return a `marimo.App` configured for the 3-column BIEP v3 operator console (P4).

    Per the upstream `lance-demo.py` pattern (l. 24/39/110/147/320) +
    the `youtube-material/examples/layouts/*.grid.json` files — uses
    `@app.cell(column=N)` + `layout_file=.../grid.json` to persist
    the multi-column dashboard layout.

    Parameters
    ----------
    title : str
        The notebook title (for documentation, not used in the app)
    layout_filename : str, optional
        The grid.json filename (saved next to the notebook). If None,
        the operator can drag cells to set the layout and marimo will
        persist it.
    width : str
        The marimo app width (default: "full" for operator consoles)

    Usage:
    ```python
    app = three_column_grid_app(
        title="BIEP v3 — Ireland Pipeline Dashboard",
        layout_filename="19_ireland_pipeline_dashboard.grid.json",
    )

    @app.cell(column=0, hide_code=True)
    def _overview(mo): ...
    ```
    """
    try:
        import marimo as mo
    except ImportError:
        return None

    kwargs: dict[str, Any] = {"width": width}
    if layout_filename:
        # The layout file is expected to live next to the notebook
        # (the marimo runtime resolves the path relative to the
        # notebook file at edit time).
        kwargs["layout_file"] = layout_filename

    app = mo.App(**kwargs)
    return app


# ────────────────────────────────────────────────────────────────────────────
# P5 — RAGAS gauge widget (anywidget)
# ────────────────────────────────────────────────────────────────────────────

def ragas_gauge_widget(
    score: float,
    history: list[float] | None = None,
    cohort_slug: str = "",
) -> Any:
    """Return a `mo.ui.anywidget` RAGAS gauge for the given cohort (P5).

    Wraps `RAGASGaugeWidget` from `notebooks/_shared/ragas_gauge.py`.
    Renders a circular progress gauge with a colour band (green
    ≥0.85 / yellow ≥0.70 / red <0.70) + a sparkline of the last N
    RAGAS scores.

    Parameters
    ----------
    score : float
        The current RAGAS score (0.0 to 1.0)
    history : list[float], optional
        The last N RAGAS scores (for the sparkline). Default: empty
        list (no sparkline)
    cohort_slug : str
        The cohort slug (for the title)

    Usage:
    ```python
    gauge = ragas_gauge_widget(score=0.82, history=[0.78, 0.79, 0.82], cohort_slug="ireland_lc_mathematics_higher_en")
    mo.vstack([mo.md("## RAGAS Gauge"), gauge])
    ```
    """
    try:
        import marimo as mo
        from notebooks._shared.ragas_gauge import RAGASGaugeWidget
    except ImportError:
        return None

    return mo.ui.anywidget(
        RAGASGaugeWidget(
            score=score,
            history=history or [],
            cohort_slug=cohort_slug,
        )
    )


# ────────────────────────────────────────────────────────────────────────────
# P6 — Dual-mode (marimo + CLI) per https://docs.marimo.io/guides/scripts/
# ────────────────────────────────────────────────────────────────────────────

def cli_argparser_biep(notebook_name: str) -> argparse.ArgumentParser:
    """Return the canonical argparse for the BIEP v3 dashboards (P6).

    Per https://docs.marimo.io/guides/scripts/ — every BIEP v3
    jurisdiction dashboard gets the same 5 canonical CLI flags:

    - `--milestone`: which BIEP milestone to materialise (M0-M4)
    - `--asset-check`: which asset check to run
    - `--cohort-kind`: which cohort kind (lc_spec / jc_spec / etc.)
    - `--jurisdiction`: which jurisdiction
    - `--output`: output format (json / table / markdown)

    Parameters
    ----------
    notebook_name : str
        The notebook's name (used as the `prog` for argparse)

    Usage:
    ```python
    def _cli_main(argv=None) -> int:
        parser = cli_argparser_biep("19_ireland_pipeline_dashboard")
        args = parser.parse_args(argv)
        # ... use args.milestone, args.asset_check, etc. ...
    ```
    """
    parser = argparse.ArgumentParser(
        prog=notebook_name,
        description=(
            f"{notebook_name} — BIEP v3 jurisdiction dashboard — "
            "dual-mode (marimo + CLI) per https://docs.marimo.io/guides/scripts/."
        ),
    )
    parser.add_argument(
        "--milestone",
        type=str,
        default="m1",
        choices=["m0", "m1", "m2", "m3", "m4"],
        help="BIEP v3 milestone (M0=foundation, M1=Ireland LC, M2=Ireland JC, "
             "M3=England A-Level, M4=England GCSE). Default: m1.",
    )
    parser.add_argument(
        "--asset-check",
        type=str,
        default="documents_ingested",
        choices=["documents_ingested", "extractions_ragas", "lance_chunks"],
        help="The asset check to run. Default: documents_ingested.",
    )
    parser.add_argument(
        "--cohort-kind",
        type=str,
        default="lc_spec",
        choices=["lc_spec", "jc_spec", "jc_short_course", "jc_cba",
                 "a_level", "gcse"],
        help="The cohort kind for the RAGAS drill-down. Default: lc_spec.",
    )
    parser.add_argument(
        "--jurisdiction",
        type=str,
        default="ireland",
        choices=["ireland", "england", "scotland+wales+ni", "crown"],
        help="The jurisdiction. Default: ireland.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="json",
        choices=["json", "table", "markdown"],
        help="Output format. Default: json (for CI consumption).",
    )
    return parser


def cli_payload_to_output(payload: dict[str, Any], output: str) -> str:
    """Render the CLI payload in the requested output format (P6 helper).

    Per https://docs.marimo.io/guides/scripts/ — the CLI mode emits
    the asset-check JSON payload in 1 of 3 formats: `json` (for CI),
    `table` (for humans reading the terminal), `markdown` (for
    pasting into a marimo cell).
    """
    import json

    if output == "json":
        return json.dumps(payload, indent=2)
    elif output == "table":
        lines = ["| Field | Value |", "|---|---|"]
        for k, v in payload.items():
            v_str = str(v).replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {k} | `{v_str[:200]}` |")
        return "\n".join(lines)
    else:  # markdown
        lines = [f"## {payload.get('notebook', '?')} — "
                 f"{payload.get('milestone', '?')}/{payload.get('asset_check', '?')}", ""]
        lines.append(f"**Status**: `{payload.get('status', '?')}` "
                     f"(exit code {payload.get('exit_code', '?')})")
        if payload.get("stdout_tail"):
            lines += ["", "```", payload["stdout_tail"][-1000:], "```"]
        return "\n".join(lines)


def cli_main_if_argv(_cli_main_fn: Any, app: Any) -> None:
    """The canonical `if __name__ == "__main__":` pattern (P6).

    Per https://docs.marimo.io/guides/scripts/ — if the script is
    invoked with CLI args (other than the `marimo edit/run` defaults),
    run the CLI; otherwise start the marimo runtime.

    Parameters
    ----------
    _cli_main_fn : callable
        The `_cli_main(argv) -> int` function (per the official
        marimo scripts guide pattern)
    app : marimo.App
        The marimo app instance (for the `app.run()` fallback)

    Usage at the bottom of every BIEP v3 dashboard:
    ```python
    if __name__ == "__main__":
        cli_main_if_argv(_cli_main, app)
    ```
    """
    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main_fn())
    app.run()


# ────────────────────────────────────────────────────────────────────────────
# Convenience: __all__ + module API
# ────────────────────────────────────────────────────────────────────────────

__all__ = [
    # R1
    "setup_biep_registry_header",
    # P1
    "tabbed_biep_operator_console",
    # P2
    "progress_bar_with_eta",
    "form_gated_run_button",
    "run_dagster_asset_check",
    # P3
    "llm_chat_with_prompts",
    "LITELLM_BASE_URL",
    # P4
    "three_column_grid_app",
    # P5
    "ragas_gauge_widget",
    "RAGAS_PASS_THRESHOLD",
    "ragas_color",
    "ragas_status_emoji",
    # P6
    "cli_argparser_biep",
    "cli_payload_to_output",
    "cli_main_if_argv",
]