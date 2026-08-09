#!/usr/bin/env python3
"""notebooks/27_stacks_sync_dashboard.py — the IaC stacks sync dashboard.

Per the 2026-08-15-stacks-sync-loop-v1 change (Layer 8).
Consumes stedding/sync-reports/stacks-{date}.md and shows:
- The 89 stacks at bonneagar/stacks/ and their GOLD_STANDARD status
- The 4 known violators (browser, ludusavi, moonlight, storybook)
- The 5 stacks-sync sub-layers + their health
- The stacks evolution feedback loop

Run via: uv run marimo edit notebooks/27_stacks_sync_dashboard.py
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
        reports = sorted(REPORTS_DIR.glob("stacks-*.md"), reverse=True)
        if reports:
            latest = reports[0]
    return (latest, REPORTS_DIR)


@app.cell
def __(mo, latest, REPORTS_DIR):
    if latest is None:
        mo.output.replace(
            mo.md(
                f"# Stacks Sync Dashboard (Layer 8)\n\n"
                f"**No stacks sync reports found in `{REPORTS_DIR}/`.**\n\n"
                f"Run `mise run sync:stacks` to generate the first report.\n"
            )
        )
    else:
        text = latest.read_text()
        mtime = datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc)
        return (mtime, text)


@app.cell
def __(mo, latest, mtime, text):
    # Header
    mo.output.replace(
        mo.md(
            f"# Stacks Sync Dashboard (Layer 8)\n\n"
            f"**Sync report:** `{latest}` (modified {mtime.isoformat()})\n\n"
            f"---\n\n"
        )
    )
    return


@app.cell
def __(mo, re, text):
    # Parse per-stack GOLD_STANDARD status from the report table.
    # The table format is: "| <stack> | <status> |"
    stack_statuses: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s+(\S+)\s+\|\s+(OK|VIOLATOR[^|]*)\s+\|", line)
        if m:
            stack_statuses[m.group(1)] = m.group(2)
    return (stack_statuses,)


@app.cell
def __(mo, stack_statuses):
    # Display the per-stack GOLD_STANDARD status
    total = len(stack_statuses)
    clean = sum(1 for s in stack_statuses.values() if s == "OK (all 6 files)")
    violators = sum(1 for s in stack_statuses.values() if s.startswith("VIOLATOR"))

    if stack_statuses:
        mo.output.replace(
            mo.md(
                f"## Per-Stack GOLD_STANDARD Status\n\n"
                f"- Total stacks: **{total}**\n"
                f"- GOLD_STANDARD clean: **{clean}**\n"
                f"- GOLD_STANDARD violators: **{violators}**\n\n"
                "| Stack | Status |\n"
                "|:--|:--|\n"
                + "\n".join(
                    f"| {name} | {status} |"
                    for name, status in sorted(stack_statuses.items())
                )
            )
        )
    return clean, total, violators


@app.cell
def __(mo):
    # Display the 4 known violators + the 6-file GOLD_STANDARD pattern
    mo.output.replace(
        mo.md(
            "\n## The 6-File GOLD_STANDARD Pattern\n\n"
            "Every stack at `bonneagar/stacks/<name>/` MUST ship with:\n\n"
            "| File | Purpose |\n"
            "|:--|:--|\n"
            "| `compose.yaml` | Docker Compose definition (required — gates the rest) |\n"
            "| `sidecar.yaml` | Locket sidecar config (secrets injection at runtime) |\n"
            "| `secrets.env` | `infisical://dev-baile/...` secret references |\n"
            "| `pangolin.yaml` | Pangolin resource labels (the 6-label pattern) |\n"
            "| `blueprint.yaml` | Komodo blueprint (per-stack rollout config) |\n"
            "| `.env.example` | Documented env-var template (no real values) |\n\n"
            "## The 4 Known GOLD_STANDARD Violators (per Week 4 audit)\n\n"
            "- `browser` — missing 4/6 files (per Week 4 audit)\n"
            "- `ludusavi` — missing 4/6 files (per Week 4 audit)\n"
            "- `moonlight` — missing 4/6 files (per Week 4 audit)\n"
            "- `storybook` — missing 4/6 files (per Week 4 audit)\n\n"
            "Run `bash scripts/sync/stacks-drift.sh` for the live list.\n"
        )
    )
    return


@app.cell
def __(mo):
    # Display the 5 sub-layers + the orchestrator + the Cognee clusters
    mo.output.replace(
        mo.md(
            "\n## The 5 Sub-Layers (Layer 8)\n\n"
            "| Layer | Mise task | Purpose |\n"
            "|:--|:--|:--|\n"
            "| 1 | `mise run sync:stacks-drift` | Detect GOLD_STANDARD violations + name collisions |\n"
            "| 2 | `mise run sync:stacks-ccc` | Append the 23rd CCC concept guide (`stack-catalog-search`) |\n"
            "| 3 | `mise run sync:stacks-cognee` | Ingest the 89 stacks into Cognee cluster `stacks_catalog` |\n"
            "| 4 | `mise run sync:stacks-validate` | Run `stack-doctor.sh` + parse the output |\n"
            "| 5 | `mise run sync:stacks-health` | Per-stack health report |\n"
            "| orchestrator | `mise run sync:stacks` | Runs all 5 sub-layers + writes a unified report |\n\n"
            "## The 12 Cognee Clusters (post-Layer 8)\n\n"
            "1. `docs-cognee` — the canonical cognee docs\n"
            "2. `docs-platform` — platform overview docs\n"
            "3. `docs-data-platform` — data-platform docs\n"
            "4. `docs-agents` — agent docs\n"
            "5. `docs-models` — model docs\n"
            "6. `docs-web` — web docs\n"
            "7. `docs-ci` — CI docs\n"
            "8. `openspec_changes` — openspec changes\n"
            "9. `openspec_specs` — openspec specs\n"
            "10. `agent_skills` — 57 skills\n"
            "11. `baml_schemas` — 320 .baml files (Layer 7)\n"
            "12. `stacks_catalog` — **NEW**: 89 stacks (Layer 8)\n\n"
            "## Stacks Evolution Feedback Loop\n\n"
            "When a file under `bonneagar/stacks/<stack>/` is modified, the next `sync:stacks-cognee` "
            "detects the change (via file mtime comparison) + re-cognifies the modified stack into "
            "the `stacks_catalog` Cognee cluster + `sync:stacks-ccc` updates the 23rd CCC concept guide "
            "+ the deployment control panel (notebook 24) surfaces the change.\n"
        )
    )
    return


if __name__ == "__main__":
    app.run()
