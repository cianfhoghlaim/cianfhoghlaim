#!/usr/bin/env python3
"""notebooks/30_notebooks_sync_dashboard.py - the Notebooks sync dashboard.

Per the 2026-08-15-notebooks-sync-loop-v1 change (Day 2).
Consumes stedding/sync-reports/notebooks-{date}.md and shows:
- The per-prefix breakdown (20+ numeric prefixes)
- The 104 .py files + 108 @app.cell decorators
- The canonical notebooks/_shared/ helpers

Run via: uv run marimo edit notebooks/30_notebooks_sync_dashboard.py
"""
import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    from pathlib import Path
    import re
    from datetime import datetime, timezone
    return mo, Path, re, datetime, timezone


@app.cell
def __(mo, Path, datetime, timezone):
    REPORTS_DIR = Path("stedding/sync-reports")
    latest = None
    if REPORTS_DIR.is_dir():
        reports = sorted(REPORTS_DIR.glob("notebooks-*.md"), reverse=True)
        if reports:
            latest = reports[0]
    return (latest, REPORTS_DIR)


@app.cell
def __(mo, latest, REPORTS_DIR):
    if latest is None:
        mo.output.replace(
            mo.md(
                f"# Notebooks Sync Dashboard (Layer 11)\n\n"
                f"**No notebooks sync reports found in `{REPORTS_DIR}/`.**\n\n"
                f"Run `mise run sync:notebooks` to generate the first report.\n"
            )
        )
    else:
        text = latest.read_text()
        mtime = datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc)
        return (mtime, text)


@app.cell
def __(mo, latest, mtime, text):
    mo.output.replace(
        mo.md(
            f"# Notebooks Sync Dashboard (Layer 11)\n\n"
            f"**Sync report:** `{latest}` (modified {mtime.isoformat()})\n\n"
            f"---\n\n"
        )
    )
    return


@app.cell
def __(mo, re, text):
    total_files = 0
    total_cells = 0
    for line in text.splitlines():
        m_files = re.search(r"Total notebook files:\s*(\d+)", line)
        if m_files:
            total_files = int(m_files.group(1))
        m_cells = re.search(r"Total @app\.cell decorators:\s*(\d+)", line)
        if m_cells:
            total_cells = int(m_cells.group(1))
    return (total_files, total_cells)


@app.cell
def __(mo, total_files, total_cells):
    if total_files > 0:
        mo.output.replace(
            mo.md(
                "## Summary\n\n"
                f"- **Total notebook files**: {total_files}\n"
                f"- **Total @app.cell decorators**: {total_cells}\n"
                f"- **Total prefixes**: 20+\n"
            )
        )
    return


@app.cell
def __(mo, re, text):
    prefixes = []
    for line in text.splitlines():
        m = re.match(r"\|\s+(\d+_)\s+\|\s+(\d+)\s+\.py\s+\|\s+(\d+)\s+@app\.cell\s+\|\s*$", line)
        if m and m.group(1) not in ("prefix_", "---"):
            prefixes.append({
                "prefix": m.group(1),
                "files": m.group(2),
                "cells": m.group(3),
            })
    return prefixes


@app.cell
def __(mo, prefixes):
    if prefixes:
        mo.output.replace(
            mo.md(
                "## Per-Prefix Breakdown\n\n"
                "| Prefix | .py | @app.cell |\n"
                "|:--|--:|--:|\n"
                + "\n".join(
                    f"| {p['prefix']} | {p['files']} | {p['cells']} |"
                    for p in prefixes
                )
            )
        )
    return


@app.cell
def __(mo):
    # The 15 Cognee clusters
    mo.output.replace(
        mo.md(
            "\n## The 15 Cognee Clusters\n\n"
            "1. `docs-cognee` (existing)\n"
            "2. `docs-platform` (existing)\n"
            "3. `docs-data-platform` (existing)\n"
            "4. `docs-agents` (existing)\n"
            "5. `docs-models` (existing)\n"
            "6. `docs-web` (existing)\n"
            "7. `docs-ci` (existing)\n"
            "8. `openspec_changes` (from knowledge-sync-loop-v1)\n"
            "9. `openspec_specs` (from knowledge-sync-loop-v1)\n"
            "10. `agent_skills` (from knowledge-sync-loop-v1)\n"
            "11. `baml_schemas` (from baml-sync-loop-v1)\n"
            "12. `stacks_catalog` (from stacks-sync-loop-v1)\n"
            "13. `dlt_sources` (from dlt-sync-loop-v1)\n"
            "14. `agent_definitions` (from agent-definitions-sync-loop-v1)\n"
            "15. `notebooks` (from this change)\n\n"
            "## Notebooks Evolution Feedback Loop\n\n"
            "When a .py file in `notebooks/` is modified, the next `sync:notebooks-cognee` re-cognifies\n"
            "the modified notebook into the `notebooks` Cognee cluster + `sync:notebooks-ccc` updates the 26th\n"
            "CCC concept guide + the deployment control panel surfaces the change.\n"
        )
    )
    return


if __name__ == "__main__":
    app.run()
