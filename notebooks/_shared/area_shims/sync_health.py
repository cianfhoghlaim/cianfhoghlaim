"""Sync health per-tab overview helpers.

Per the 2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1
change — this module provides the 11 per-tab overview helpers for the
`notebooks/sync_health.py` grouped dashboard, which consolidates:
- `14_dev_env_tools_*.py` (6 sub-notebooks)
- `15_observability_*.py` (3 sub-notebooks)
- `25_dagster_sync_dashboard.py`
- `26_baml_sync_dashboard.py`
- `27_stacks_sync_dashboard.py`
- `28_dlt_sync_dashboard.py`
- `29_agents_sync_dashboard.py`
- `30_notebooks_sync_dashboard.py`

The 11 sync layers (per the `knowledge-sync-loop` spec):
- paths (drift detection on repo paths)
- ccc (CocoIndex code semantic search)
- cognee (knowledge graph sync)
- skills (.agents/skills/ validation)
- mcp (14 MCP servers health)
- dagster (Dagster asset sync)
- baml (BAML schema sync)
- stacks (89 Docker Compose stacks)
- agents (12-agent fleet sync)
- notebooks (60+ marimo notebooks sync)
- drift-docs (drift detection on docs)
"""
from __future__ import annotations


def paths_sync_overview() -> str:
    """Paths sync overview."""
    return """
    ## 📁 Paths Sync

    Drift detection on repo paths — verifies the 0 pre-v7 path drift
    invariant per the `repo-hygiene-agent-routing` spec.

    Run `mise run sync:paths` to refresh.
    """


def ccc_sync_overview() -> str:
    """CCC (CocoIndex Code) sync overview."""
    return """
    ## 🔍 CCC Sync (CocoIndex Code)

    The CocoIndex code semantic search index — verifies every Python
    function is indexed and searchable.

    Run `mise run sync:ccc` to refresh the ccc index.
    """


def cognee_sync_overview() -> str:
    """Cognee sync overview."""
    return """
    ## 🧠 Cognee Sync (Knowledge Graph)

    The 11-cluster Cognee knowledge graph — verifies every cluster has
    the expected entity count.

    Run `mise run sync:cognee` to refresh the cognee clusters.
    """


def skills_sync_overview() -> str:
    """Skills sync overview."""
    return """
    ## 🎓 Skills Sync (.agents/skills/ validation)

    Validates every SKILL.md file in `.agents/skills/` has the correct
    frontmatter + structure. Target: 61+ skills pass.

    Run `mise run lint:skills` to refresh.
    """


def mcp_sync_overview() -> str:
    """MCP sync overview."""
    return """
    ## 🔌 MCP Sync (14 MCP servers health)

    The 14 MCP servers (filesystem, brave-search, exa, firecrawl,
    motherduck, notion, cognee, github, gitlab, marimo, dagster,
    playwright, huggingface, obsidian) — health check status.

    Run `mise run sync:mcp` to refresh.
    """


def dagster_sync_overview() -> str:
    """Dagster sync overview."""
    return """
    ## ⚙️ Dagster Sync (Asset sync)

    The ~833 Dagster assets across the 5-layer defs/ tree. Verifies all
    assets are registered + the 5-layer group_name convention is
    followed.

    Per the `dagster-asset-sync` spec.

    Run `mise run sync:dagster` to refresh.
    """


def baml_sync_overview() -> str:
    """BAML sync overview."""
    return """
    ## 📐 BAML Sync (Schema sync)

    The 838 BAML classes across 7 clusters + the 3 BIEPV3 clients. Verifies
    every .baml file has the expected functions + clients.

    Per the `baml-sync-loop` spec.

    Run `mise run sync:baml` to refresh.
    """


def stacks_sync_overview() -> str:
    """Stacks sync overview."""
    return """
    ## 🐳 Stacks Sync (89 Docker Compose stacks)

    The 89 Docker Compose stacks validated against the GOLD_STANDARD
    pattern (compose.yaml + sidecar.yaml + secrets.env + pangolin.yaml +
    blueprint.yaml + .env.example).

    Per the `stacks-sync-loop` spec.

    Run `mise run sync:stacks` to refresh.
    """


def agents_sync_overview() -> str:
    """Agents sync overview."""
    return """
    ## 🤖 Agents Sync (12-agent fleet)

    The 12-agent fleet (root + curriculum + translation + corpus +
    research + education_research + bunchloch_research + geospatial +
    statistics + curriculum_comparison + agui_curriculum + mcp_curriculum).

    Per the `agent-definitions-sync-loop` spec.

    Run `mise run sync:agents` to refresh.
    """


def notebooks_sync_overview() -> str:
    """Notebooks sync overview."""
    return """
    ## 📓 Notebooks Sync (60+ marimo notebooks)

    The 60+ marimo notebooks validated for syntax + ibis-first contract +
    PEP 723 dependency blocks + dual-mode CLI.

    Per the `notebooks-sync-loop` spec.

    Run `mise run sync:notebooks` to refresh.
    """


def drift_docs_overview() -> str:
    """Drift-docs sync overview."""
    return """
    ## 📚 Drift Docs Sync (Number drift detection)

    Detects number drift in the 16 AGENTS.md files (e.g. claimed 89
    specs vs actual 90 specs). Validates every number claim against
    ground truth.

    Run `mise run lint:drift-docs` to refresh.
    """


SYNC_HEALTH_TABS = [
    ("Paths", paths_sync_overview),
    ("CCC", ccc_sync_overview),
    ("Cognee", cognee_sync_overview),
    ("Skills", skills_sync_overview),
    ("MCP", mcp_sync_overview),
    ("Dagster", dagster_sync_overview),
    ("BAML", baml_sync_overview),
    ("Stacks", stacks_sync_overview),
    ("Agents", agents_sync_overview),
    ("Notebooks", notebooks_sync_overview),
    ("Drift Docs", drift_docs_overview),
]


def build_sync_status_grid() -> str:
    """Build the canonical 11-sync-layer status grid (parses stedding/sync-reports/all-*.md)."""
    from pathlib import Path
    from datetime import datetime, timezone

    reports_dir = Path("stedding/sync-reports")
    latest = None
    if reports_dir.is_dir():
        reports = sorted(reports_dir.glob("all-*.md"), reverse=True)
        if reports:
            latest = reports[0]

    if latest is None:
        return "No sync reports found. Run `mise run sync:all` to generate the first report."

    mtime = datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc)
    text = latest.read_text()

    statuses = {}
    if "OK: 0 pre-v7 path drift" in text:
        statuses["paths"] = "ok"
    elif "skills pass" in text:
        statuses["skills"] = "ok"
    if "assets registered across the 5-layer defs/" in text:
        statuses["dagster"] = "ok"
    if ".baml files registered across the 7 clusters" in text:
        statuses["baml"] = "ok"
    if "stacks registered across" in text:
        statuses["stacks"] = "ok"
    if ".py files registered across the 7 agent subdirs" in text:
        statuses["agents"] = "ok"
    if ".ipynb files registered" in text or "notebooks" in text.lower():
        statuses["notebooks"] = "ok"
    statuses["ccc"] = "info"
    statuses["cognee"] = "info"
    statuses["mcp"] = "info"
    statuses["drift-docs"] = "ok" if "0 number drift claims" in text else "fail"

    pass_count = sum(1 for s in statuses.values() if s == "ok")
    fail_count = sum(1 for s in statuses.values() if s == "fail")
    info_count = sum(1 for s in statuses.values() if s == "info")

    md = f"## 11 Sync Layer Statuses (latest: `{latest.name}`, {mtime.isoformat()})\n\n"
    for layer, status in statuses.items():
        emoji = "✅" if status == "ok" else ("❌" if status == "fail" else "ℹ️")
        md += f"- **{layer}**: {status} {emoji}\n"
    md += f"\n**Summary**: {pass_count} pass / {fail_count} fail / {info_count} info\n"
    return md


__all__ = [
    "paths_sync_overview",
    "ccc_sync_overview",
    "cognee_sync_overview",
    "skills_sync_overview",
    "mcp_sync_overview",
    "dagster_sync_overview",
    "baml_sync_overview",
    "stacks_sync_overview",
    "agents_sync_overview",
    "notebooks_sync_overview",
    "drift_docs_overview",
    "build_sync_status_grid",
    "SYNC_HEALTH_TABS",
]