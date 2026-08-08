#!/usr/bin/env python3
"""notebooks/26_baml_sync_dashboard.py — the BAML schema sync dashboard.

Per the 2026-08-15-baml-sync-loop-v1 change (Day 2).
Consumes stedding/sync-reports/baml-{date}.md and shows:
- The per-cluster breakdown (american_nations, british_isles, celtic,
  commonwealth, european_nations, european_union, processing)
- The BAML client inventory (clients.baml, clients_llama_swap.baml,
  clients_ocr_ensemble.baml)
- The 4 BAML sync metrics (baml_file_count, function_count,
  class_count, client_count)

Run via: uv run marimo edit notebooks/26_baml_sync_dashboard.py
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
        reports = sorted(REPORTS_DIR.glob("baml-*.md"), reverse=True)
        if reports:
            latest = reports[0]
    return (latest, REPORTS_DIR)


@app.cell
def __(mo, latest, REPORTS_DIR):
    if latest is None:
        mo.output.replace(
            mo.md(
                f"# BAML Schema Sync Dashboard (Layer 7)\n\n"
                f"**No baml sync reports found in `{REPORTS_DIR}/`.**\n\n"
                f"Run `mise run sync:baml` to generate the first report.\n"
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
            f"# BAML Schema Sync Dashboard (Layer 7)\n\n"
            f"**Sync report:** `{latest}` (modified {mtime.isoformat()})\n\n"
            f"---\n\n"
        )
    )
    return


@app.cell
def __(mo, re, text):
    # Parse per-cluster counts
    cluster_counts = {}
    current_cluster = None
    for line in text.splitlines():
        m_cluster = re.match(r"^### (\S+)$", line)
        if m_cluster:
            current_cluster = m_cluster.group(1)
            cluster_counts[current_cluster] = {}
        m_count = re.match(r"^- (\S+):\s+(\d+)$", line)
        if m_count and current_cluster:
            cluster_counts[current_cluster][m_count.group(1)] = int(m_count.group(2))
    return cluster_counts


@app.cell
def __(mo, cluster_counts):
    # Display the per-cluster breakdown
    if cluster_counts:
        mo.output.replace(
            mo.md(
                "## Per-Cluster Breakdown\n\n"
                "| Cluster | .baml files | function | class | enum | client<llm> | test |\n"
                "|:--|--:|--:|--:|--:|--:|--:|\n"
                + "\n".join(
                    f"| {cluster} | {counts.get('.baml', 0)} | {counts.get('function', 0)} | "
                    f"{counts.get('class', 0)} | {counts.get('enum', 0)} | "
                    f"{counts.get('client<llm>', 0)} | {counts.get('test', 0)} |"
                    for cluster, counts in cluster_counts.items()
                )
            )
        )
    return


@app.cell
def __(mo):
    # Display the canonical BAML clients
    mo.output.replace(
        mo.md(
            "\n## The 33 LLM Clients (3 files)\n\n"
            "- `baml_src/clients.baml` — the canonical 23 clients (ExtractEn + LitellmClient + 11 BIEPSubject + ...)\n"
            "- `baml_src/clients_llama_swap.baml` — the 4 llama-swap clients (LlamaSwapClient + ...)\n"
            "- `baml_src/clients_ocr_ensemble.baml` — the 2 OCR ensemble clients (Docling + Unstract)\n"
            "\n## BAML Evolution Feedback Loop\n\n"
            "When a `.baml` file in `baml_src/` is modified, the next `sync:baml-cognee` re-cognifies "
            "the modified file into the `baml_schemas` Cognee cluster + `sync:baml-ccc` updates the 22nd "
            "CCC concept guide + the deployment control panel surfaces the change.\n"
        )
    )
    return


if __name__ == "__main__":
    app.run()