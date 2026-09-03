#!/usr/bin/env python3
"""notebooks/25_dagster_sync_dashboard.py — the Dagster asset sync dashboard.

Per the 2026-08-15-retroactive-pre-v7-cleanup-v1 change (Day 2).
Consumes stedding/sync-reports/dagster-{date}.md and shows:
- The per-layer breakdown (1_ingestion, 2_materials, 3_model_lifecycle,
  4_asset_generation, 5_agent_ops)
- The 5 KCG Components + 4 derived Components inventory
- The @asset / @asset_check / @sensor / YAML defs counts
- The overall Layer 6 health status

Run via: uv run marimo edit notebooks/25_dagster_sync_dashboard.py
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
        reports = sorted(REPORTS_DIR.glob("dagster-*.md"), reverse=True)
        if reports:
            latest = reports[0]
    return (latest, REPORTS_DIR)


@app.cell
def __(mo, latest, REPORTS_DIR):
    if latest is None:
        mo.output.replace(
            mo.md(
                f"# Dagster Sync Dashboard (Layer 6)\n\n"
                f"**No dagster sync reports found in `{REPORTS_DIR}/`.**\n\n"
                f"Run `mise run sync:dagster` to generate the first report.\n"
            )
        )
    else:
        text = latest.read_text()
        mtime = datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc)
        return (text, mtime)


@app.cell
def __(mo, latest, mtime, text):
    # Header
    mo.output.replace(
        mo.md(
            f"# Dagster Sync Dashboard (Layer 6)\n\n"
            f"**Sync report:** `{latest}` (modified {mtime.isoformat()})\n\n"
            f"---\n\n"
        )
    )
    return


@app.cell
def __(mo, re, text):
    # Parse per-layer counts
    layer_counts = {}
    current_layer = None
    for line in text.splitlines():
        m_layer = re.match(r"^### (\S+)$", line)
        if m_layer:
            current_layer = m_layer.group(1)
            layer_counts[current_layer] = {}
        m_count = re.match(r"^- (@\w+):\s+(\d+)$", line)
        if m_count and current_layer:
            layer_counts[current_layer][m_count.group(1)] = int(m_count.group(2))

    # Build the markdown table
    rows = []
    for layer, counts in layer_counts.items():
        rows.append(
            f"| {layer} | {counts.get('@asset', 0)} | {counts.get('@asset_check', 0)} | {counts.get('@sensor', 0)} |"
        )
    return rows


@app.cell
def __(mo, rows):
    # Display the per-layer breakdown
    if rows:
        mo.output.replace(
            mo.md(
                "## Per-Layer Dagster Asset Breakdown\n\n"
                "| Layer | @asset | @asset_check | @sensor |\n"
                "|:--|--:|--:|--:|\n"
                + "\n".join(rows)
            )
        )
    return


@app.cell
def __(mo):
    # Display the KCG Components
    mo.output.replace(
        mo.md(
            "\n## The 5 KCG Components (orchestration/components/)\n\n"
            "- `CelticIngestionComponent` (layer1_ingestion.py)\n"
            "- `CelticMaterialsComponent` (layer2_materials.py)\n"
            "- `CelticModelLifecycleComponent` (layer3_model_lifecycle.py)\n"
            "- `CelticAssetGenerationComponent` (layer4_asset_generation.py)\n"
            "- `CelticAgentOpsComponent` (layer5_agent_ops.py)\n\n"
            "## The 4 Derived Components (orchestration/components/)\n\n"
            "- `BIEPSubjectComponent` (biep_subject_component.py)\n"
            "- `JuniorCycleSubjectComponent` (junior_cycle_subject_component.py)\n"
            "- `EnglandBoardSubjectComponent` (england_board_subject_component.py)\n"
            "- `EnglandCrossBoardComparatorComponent` (england_cross_board_comparator_component.py)\n"
        )
    )
    return


if __name__ == "__main__":
    app.run()