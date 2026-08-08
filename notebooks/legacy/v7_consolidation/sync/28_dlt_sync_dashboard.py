#!/usr/bin/env python3
"""notebooks/28_dlt_sync_dashboard.py - the DLT source sync dashboard.

Per the 2026-08-15-dlt-sync-loop-v1 change (Day 2).
Consumes stedding/sync-reports/dlt-{date}.md and shows:
- The per-subdir breakdown (13 jurisdiction subdirs)
- The 1903 .py files + 865 @dlt.source + 924 @dlt.resource
- The drift detection summary
- The canonical dlt_sources/common/ helpers

Run via: uv run marimo edit notebooks/28_dlt_sync_dashboard.py
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
        reports = sorted(REPORTS_DIR.glob("dlt-*.md"), reverse=True)
        if reports:
            latest = reports[0]
    return (latest, REPORTS_DIR)


@app.cell
def __(mo, latest, REPORTS_DIR):
    if latest is None:
        mo.output.replace(
            mo.md(
                f"# DLT Source Sync Dashboard (Layer 9)\n\n"
                f"**No dlt sync reports found in `{REPORTS_DIR}/`.**\n\n"
                f"Run `mise run sync:dlt` to generate the first report.\n"
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
            f"# DLT Source Sync Dashboard (Layer 9)\n\n"
            f"**Sync report:** `{latest}` (modified {mtime.isoformat()})\n\n"
            f"---\n\n"
        )
    )
    return


@app.cell
def __(mo, re, text):
    # Parse the DLT stats
    total_files = 0
    total_sources = 0
    total_resources = 0
    for line in text.splitlines():
        m_files = re.search(r"Total \.py files:\s*(\d+)", line)
        if m_files:
            total_files = int(m_files.group(1))
        m_sources = re.search(r"Total @dlt\.source:\s*(\d+)", line)
        if m_sources:
            total_sources = int(m_sources.group(1))
        m_resources = re.search(r"Total @dlt\.resource:\s*(\d+)", line)
        if m_resources:
            total_resources = int(m_resources.group(1))
    return (total_files, total_sources, total_resources)


@app.cell
def __(mo, total_files, total_sources, total_resources):
    if total_files > 0:
        mo.output.replace(
            mo.md(
                "## Summary\n\n"
                f"- **Total .py files**: {total_files}\n"
                f"- **Total @dlt.source**: {total_sources}\n"
                f"- **Total @dlt.resource**: {total_resources}\n"
            )
        )
    return


@app.cell
def __(mo, re, text):
    # Per-subdir stats
    subdirs = []
    for line in text.splitlines():
        m = re.match(r"\|\s+(\S+)\s+\|\s+(\d+)\s+\.py\s+\|\s+(\d+)\s+sources\s+\|\s+(\d+)\s+resources\s+\|\s*$", line)
        if m and m.group(1) not in ("american_nations", "Subdir", "subdir", "---"):
            subdirs.append({
                "name": m.group(1),
                "files": m.group(2),
                "sources": m.group(3),
                "resources": m.group(4),
            })
    return subdirs


@app.cell
def __(mo, subdirs):
    if subdirs:
        mo.output.replace(
            mo.md(
                "## Per-Jurisdiction Breakdown\n\n"
                "| Subdir | .py | Sources | Resources |\n"
                "|:--|--:|--:|--:|\n"
                + "\n".join(
                    f"| {d['name']} | {d['files']} | {d['sources']} | {d['resources']} |"
                    for d in subdirs
                )
            )
        )
    return


@app.cell
def __(mo):
    # The 13 Cognee clusters
    mo.output.replace(
        mo.md(
            "\n## The 13 Cognee Clusters\n\n"
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
            "13. `dlt_sources` (from this change)\n\n"
            "## DLT Evolution Feedback Loop\n\n"
            "When a .py file in `dlt_sources/` is modified, the next `sync:dlt-cognee` re-cognifies\n"
            "the modified source into the `dlt_sources` Cognee cluster + `sync:dlt-ccc` updates the 24th\n"
            "CCC concept guide + the deployment control panel surfaces the change.\n"
        )
    )
    return


if __name__ == "__main__":
    app.run()
