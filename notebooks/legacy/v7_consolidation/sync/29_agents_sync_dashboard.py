#!/usr/bin/env python3
"""notebooks/29_agents_sync_dashboard.py - the Agent Definitions sync dashboard.

Per the 2026-08-15-agent-definitions-sync-loop-v1 change (Day 2).
Consumes stedding/sync-reports/agents-{date}.md and shows:
- The per-subdir breakdown (7 agent subdirs)
- The 353 .py files + the 5 AGENTS.md
- The 8 NCCA subject specialists
- The 12-agent fleet coverage

Run via: uv run marimo edit notebooks/29_agents_sync_dashboard.py
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
        reports = sorted(REPORTS_DIR.glob("agents-*.md"), reverse=True)
        if reports:
            latest = reports[0]
    return (latest, REPORTS_DIR)


@app.cell
def __(mo, latest, REPORTS_DIR):
    if latest is None:
        mo.output.replace(
            mo.md(
                f"# Agent Definitions Sync Dashboard (Layer 10)\n\n"
                f"**No agents sync reports found in `{REPORTS_DIR}/`.**\n\n"
                f"Run `mise run sync:agents` to generate the first report.\n"
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
            f"# Agent Definitions Sync Dashboard (Layer 10)\n\n"
            f"**Sync report:** `{latest}` (modified {mtime.isoformat()})\n\n"
            f"---\n\n"
        )
    )
    return


@app.cell
def __(mo, re, text):
    total_files = 0
    for line in text.splitlines():
        m = re.search(r"Total \.py files:\s*(\d+)", line)
        if m:
            total_files = int(m.group(1))
    return total_files


@app.cell
def __(mo, total_files):
    if total_files > 0:
        mo.output.replace(
            mo.md(
                "## Summary\n\n"
                f"- **Total .py files**: {total_files}\n"
                f"- **Total AGENTS.md**: 5\n"
                f"- **Total NCCA subject specialists**: 8 (in agents/tuatha/agents/)\n"
            )
        )
    return


@app.cell
def __(mo, re, text):
    subdirs = []
    for line in text.splitlines():
        m = re.match(r"\|\s+(\S+)\s+\|\s+(\d+)\s+\.py\s+\|\s+(\d+)\s+AGENTS\.md\s+\|\s*$", line)
        if m and m.group(1) not in ("agents", "Subdir", "subdir", "---"):
            subdirs.append({
                "name": m.group(1),
                "files": m.group(2),
                "agents_md": m.group(3),
            })
    return subdirs


@app.cell
def __(mo, subdirs):
    if subdirs:
        mo.output.replace(
            mo.md(
                "## Per-Subdir Breakdown\n\n"
                "| Subdir | .py | AGENTS.md |\n"
                "|:--|--:|--:|\n"
                + "\n".join(
                    f"| {d['name']} | {d['files']} | {d['agents_md']} |"
                    for d in subdirs
                )
            )
        )
    return


@app.cell
def __(mo):
    # The 14 Cognee clusters
    mo.output.replace(
        mo.md(
            "\n## The 14 Cognee Clusters\n\n"
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
            "14. `agent_definitions` (from this change)\n\n"
            "## Agent Definitions Evolution Feedback Loop\n\n"
            "When a .py file in `agents/` is modified, the next `sync:agents-cognee` re-cognifies\n"
            "the modified agent into the `agent_definitions` Cognee cluster + `sync:agents-ccc` updates the 25th\n"
            "CCC concept guide + the deployment control panel surfaces the change.\n"
        )
    )
    return


if __name__ == "__main__":
    app.run()
