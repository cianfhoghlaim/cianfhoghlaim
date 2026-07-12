# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
# ]
# ///
"""07 — Analysis-plan viewer (5 NCCA educational stages).

Tabbed marimo dashboard that renders the 5 ``analysis_plan/<stage>.md``
artifacts (Aistear / Primary / Junior Cycle / Senior Cycle / Tertiary)
as their original Markdown — so a teacher / agent can scan all 5
plans at once.

Dual-mode usage:

    # Interactive — see all 5 tabs
    marimo edit 07_analysis_plan_viewer.py

    # CLI — print one stage's plan to stdout
    uv run 07_educational_stages/07_analysis_plan_viewer.py --cycle senior_cycle
"""
from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    return (mo,)


@app.cell
def _intro(mo):
    mo.md(
        """
        # 07 — Analysis-plan viewer (5 NCCA educational stages)

        Renders the 5 ``analysis_plan/<stage>.md`` artifacts at the
        top of the ``notebooks/`` tree. Each tab shows the original
        markdown for one stage: **Aistear**, **Primary**, **Junior
        Cycle**, **Senior Cycle**, **Tertiary**.

        The plans are the planning artifacts written during the
        ``ireland-primary-jc-dlt-baml-and-full-stack-demo`` openspec
        change — they scope the questions each dashboard answers
        + the upstream data sources it pulls from.
        """
    )
    return  # (no-op; marimo-safe)


@app.cell
def _cycle_picker(mo):
    cycle = mo.ui.dropdown(
        options=["all", "aistear", "primary", "junior_cycle", "senior_cycle", "tertiary"],
        value="all",
        label="Cycle (blank = all 5 tabs)",
    )
    cycle
    return (cycle,)


@app.cell
def _render(cycle, mo):
    """Read and render the 5 plan files as one marimo tab."""
    from pathlib import Path

    _plans_dir = Path(__file__).resolve().parent.parent / "analysis_plan"
    _cycle_to_file = {
        "aistear": "aistear.md",
        "primary": "primary.md",
        "junior_cycle": "junior_cycle.md",
        "senior_cycle": "senior_cycle.md",
        "tertiary": "tertiary.md",
    }
    if cycle.value == "all":
        _tabs = {}
        for _c, _fname in _cycle_to_file.items():
            _fp = _plans_dir / _fname
            _content = _fp.read_text() if _fp.exists() else f"_no plan file at `{_fp}`_"
            _tabs[_c.replace("_", " ").title()] = mo.md(_content)
        _rendered = mo.ui.tabs(_tabs)
    else:
        _fp = _plans_dir / _cycle_to_file[cycle.value]
        _rendered = mo.md(_fp.read_text() if _fp.exists() else f"_no plan file at `{_fp}`_")
    _rendered


# =============================================================================
# Dual-mode CLI
# =============================================================================
def _cli_main(argv=None) -> int:
    """Print one (or all) of the analysis_plan/<stage>.md files to stdout."""
    import argparse
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="07_analysis_plan_viewer.py",
        description="Render the 5 NCCA analysis-plan Markdown files.",
    )
    parser.add_argument(
        "--cycle",
        type=str,
        default="all",
        choices=["all", "aistear", "primary", "junior_cycle", "senior_cycle", "tertiary"],
    )
    args = parser.parse_args(argv)

    plans_dir = Path(__file__).resolve().parent.parent / "analysis_plan"
    cycle_to_file = {
        "aistear": "aistear.md",
        "primary": "primary.md",
        "junior_cycle": "junior_cycle.md",
        "senior_cycle": "senior_cycle.md",
        "tertiary": "tertiary.md",
    }
    if args.cycle == "all":
        for fname in cycle_to_file.values():
            fp = plans_dir / fname
            if fp.exists():
                print(fp.read_text())
                print("\n---\n")
        return 0
    fp = plans_dir / cycle_to_file[args.cycle]
    if not fp.exists():
        print(f"error: plan file missing: {fp}", file=sys.stderr)
        return 2
    print(fp.read_text())
    return 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main())
    app.run()