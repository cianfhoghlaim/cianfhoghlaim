# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.13.0",
#     "altair>=5.0.0",
# ]
# ///
"""02 — Drift detection across the 6 known-drift packages.

Demonstrates `drift_detect` from
`cianfhoghlaim.agents.adk.tools.dev_env` — compares the pinned version
in `pyproject.toml` against the latest PyPI release for a curated list
of packages known to drift frequently in the Cianfhoghlaim stack.

See also:
- `openspec/changes/2026-07-04-dev-env-setup-latest-packages-and-wire-25-notebooks/`
- `.agents/skills/change-detection/SKILL.md`
"""

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
        # 02 — drift_detect (PyPI version drift)

        Live demo of `drift_detect` from
        `cianfhoghlaim.agents.adk.tools.dev_env`. Inspects the
        `pyproject.toml` pin for each package below and compares it
        against the latest PyPI release.

        **Severity legend:**
        - 🟢 **current** — pin matches latest
        - 🟡 **patch** — pin behind on patch only (safe bump)
        - 🟠 **minor** — pin behind on minor (review changelog)
        - 🔴 **major** — pin behind on major (migration guide required)
        - ⚪ **unknown** — package not found on PyPI
        """
    )
    return


@app.cell
def _package_picker(mo):
    """Multi-select widget for the packages to inspect."""
    DEFAULT = [
        "dlt", "dagster", "motherduck", "lancedb", "cognee", "marimo",
    ]
    picker = mo.ui.multiselect(
        options=DEFAULT + ["duckdb", "baml", "pydantic", "fastapi", "huggingface-hub"],
        value=DEFAULT,
        label="Packages to inspect (default = 6 known-drift packages)",
    )
    picker
    return DEFAULT, picker


@app.cell
def _run_drift(picker):
    """Call `drift_detect` for the user-selected packages."""
    import asyncio
    import importlib.util
    from pathlib import Path

    # Phase 1 fix: compute absolute path from __file__ so the
    # notebook loads the dev_env tool module from any cwd.
    #   <repo>/cianfhoghlaim/notebooks/01_dev_env/0X.py
    # Tool:  <repo>/cianfhoghlaim/agents/adk/tools/dev_env.py
    # Path:  notebooks.parents[1] = cianfhoghlaim (package root)
    _HERE = Path(__file__).resolve().parent
    _TOOL = (
        _HERE.parents[1] / "agents" / "adk" / "tools" / "dev_env.py"
    )
    _spec = importlib.util.spec_from_file_location("dev_env", _TOOL)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)

    if not picker.value:
        result = {"packages": [], "summary": {"total": 0}, "checked_at": "n/a"}
    else:
        result = asyncio.run(_mod.drift_detect(picker.value))

    return Path, result


@app.cell
def _render(result, mo):
    """Render the drift report as a colour-coded table."""
    SEVERITY_BADGE = {
        "current": "🟢",
        "patch": "🟡",
        "minor": "🟠",
        "major": "🔴",
        "unknown": "⚪",
    }

    if not result["packages"]:
        mo.md("_No packages selected._")

    rows = []
    for pkg in result["packages"]:
        sev = pkg["severity"]
        badge = SEVERITY_BADGE.get(sev, "❓")
        rows.append(
            f"| {badge} `{pkg['tool_name']}` | "
            f"`{pkg['current_version'] or 'n/a'}` | "
            f"`{pkg['latest_version']}` | "
            f"**{sev}** | "
            f"{pkg['recommendation']} |"
        )

    summary = result["summary"]
    mo.md(
        f"""
        ## Drift report — {summary['total']} packages checked at {result['checked_at']}

        | severity | package | pinned | latest | severity | recommendation |
        |----------|---------|--------|--------|----------|----------------|
        {chr(10).join(rows)}

        **Summary:** {summary.get('current', 0)} current · {summary.get('patch', 0)} patch ·
        {summary.get('minor', 0)} minor · {summary.get('major', 0)} major ·
        {summary.get('unknown', 0)} unknown

        **Next steps:**
        - For **patch** bumps: run `uv pip install ".[all]"` and re-run
          `mise run py:typecheck`
        - For **minor** bumps: review the package's CHANGELOG, then bump
        - For **major** bumps: file an openspec change first (see
          `openspec/changes/`)
        """
    )
    return SEVERITY_BADGE, rows, summary


# =============================================================================
# Dual-mode entry: marimo app OR standalone CLI script
# =============================================================================
def _cli_main(argv=None) -> int:
    """Run 02_drift_detect.py as a CLI script from any cwd.

    Usage from any directory:
        python 02_drift_detect.py --help
        uv run notebooks/01_dev_env/02_drift_detect.py <flags>

    The marimo entry point is unchanged:
        marimo edit 02_drift_detect.py
        marimo run  02_drift_detect.py
    """
    import argparse
    import asyncio
    import importlib.util
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(prog='02_drift_detect.py', description=__doc__)
    parser.add_argument("--packages", action="append", default=None, help="Repeatable. e.g. --packages dlt --packages dagster (default: 6 known-drift packages)")
    args = parser.parse_args(argv)

    # Load dev_env tool module (same absolute-path fix as Phase 1 cell above)
    _HERE = Path(__file__).resolve().parent
    _TOOL = _HERE.parents[1] / 'agents' / 'adk' / 'tools' / 'dev_env.py'
    _spec = importlib.util.spec_from_file_location('dev_env', _TOOL)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)

    pkgs = args.packages if args.packages is not None else [
        'dlt', 'dagster', 'motherduck', 'lancedb', 'cognee', 'marimo',
    ]
    results = asyncio.run(_mod.drift_detect(pkgs))
    print(json.dumps(results, indent=2, default=str))
    return 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main())
    app.run()
