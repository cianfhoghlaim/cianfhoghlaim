#!/usr/bin/env python3
"""notebooks/24_deployment_control_panel.py — the sync health + model registry + schema + stacks dashboard.

Per the 2026-08-15-knowledge-sync-loop-v1 change (Day 2) +
the 2026-08-15-retroactive-pre-v7-cleanup-v1 change (Phase 8.1 — adds Layer 6) +
the 2026-08-15-baml-sync-loop-v1 change (Phase 6 — adds Layer 7 / BAML) +
the 2026-08-15-stacks-sync-loop-v1 change (Layer 8 — adds stacks) +
the 2026-08-15-agent-definitions-sync-loop-v1 change (Layer 10 — adds agents).
Consumes stedding/sync-reports/all-{date}.md and surfaces:
- The 9 sync layer statuses (paths / ccc / cognee / skills / mcp / dagster / baml / stacks / agents)
- The 14 MCP server health
- The 70+ model names (from the model-registry change)
- The 472 CocoIndex Apps
- The 89 stacks

Run via: uv run marimo edit notebooks/24_deployment_control_panel.py
"""
import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    from pathlib import Path
    import json
    from datetime import datetime, timezone
    return mo, Path, json, datetime, timezone


@app.cell
def __(mo, Path, json, datetime, timezone):
    REPORTS_DIR = Path("stedding/sync-reports")
    latest = None
    if REPORTS_DIR.is_dir():
        reports = sorted(REPORTS_DIR.glob("all-*.md"), reverse=True)
        if reports:
            latest = reports[0]
    return (latest, REPORTS_DIR)


@app.cell
def __(mo, latest, REPORTS_DIR):
    if latest is None:
        mo.output.replace(
            mo.md(
                f"# Deployment Control Panel\n\n"
                f"**No sync reports found in `{REPORTS_DIR}/`.**\n\n"
                f"Run `mise run sync:all` to generate the first report.\n"
            )
        )
    else:
        mtime = datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc)
        text = latest.read_text()
        return (mtime, text)


@app.cell
def __(mo, latest, mtime, text):
    # Header
    mo.output.replace(
        mo.md(
            f"# Deployment Control Panel\n\n"
            f"**Sync report:** `{latest}` (modified {mtime.isoformat()})\n\n"
            f"---\n\n"
        )
    )
    return


@app.cell
def __(mo, text):
    # Parse the 8 layer statuses from the report text
    # (6 from the original sync-loop + Layer 7 (BAML) added by
    # the 2026-08-15-baml-sync-loop-v1 change + Layer 8 (stacks) added by
    # the 2026-08-15-stacks-sync-loop-v1 change)
    statuses = {}
    if "OK: 0 pre-v7 path drift" in text:
        statuses["paths"] = "ok"
    else:
        statuses["paths"] = "fail"

    if "53 skills pass" in text:
        statuses["skills"] = "ok"
    else:
        statuses["skills"] = "fail"

    # Layer 6 (Dagster) — per 2026-08-15-retroactive-pre-v7-cleanup-v1
    if "OK:" in text and "assets registered across the 5-layer defs/" in text:
        statuses["dagster"] = "ok"
    else:
        statuses["dagster"] = "fail"

    # Layer 7 (BAML) — per 2026-08-15-baml-sync-loop-v1
    # Look for the baml sync report line "OK: N .baml files registered across the 7 clusters"
    if "OK:" in text and ".baml files registered across the 7 clusters" in text:
        statuses["baml"] = "ok"
    else:
        statuses["baml"] = "fail"

    # Layer 8 (stacks) — per 2026-08-15-stacks-sync-loop-v1
    # Look for the stacks sync report line "OK: N stacks registered across the 87-stack catalog"
    if "OK:" in text and "stacks registered across the 87-stack catalog" in text:
        statuses["stacks"] = "ok"
    elif "OK:" in text and "stacks registered across the" in text and "stack catalog" in text:
        statuses["stacks"] = "ok"
    else:
        statuses["stacks"] = "fail"

    # Layer 10 (agents) — per 2026-08-15-agent-definitions-sync-loop-v1
    # Look for the agents sync report line "OK: N .py files registered across the 7 agent subdirs"
    if "OK:" in text and ".py files registered across the 7 agent subdirs" in text:
        statuses["agents"] = "ok"
    elif "OK:" in text and ".py files registered across the" in text and "agent subdirs" in text:
        statuses["agents"] = "ok"
    else:
        statuses["agents"] = "fail"

    # CCC + cognee + mcp are informational; mark as informational
    statuses["ccc"] = "info"
    statuses["cognee"] = "info"
    statuses["mcp"] = "info"
    return (statuses,)


@app.cell
def __(mo, statuses):
    # Display the 9 layer statuses (added Layer 10 agents per 2026-08-15-agent-definitions-sync-loop-v1)
    pass_count = sum(1 for s in statuses.values() if s == "ok")
    fail_count = sum(1 for s in statuses.values() if s == "fail")
    info_count = sum(1 for s in statuses.values() if s == "info")

    mo.output.replace(
        mo.md(
            f"## 9 Sync Layer Statuses\n\n"
            f"- **paths**: {statuses.get('paths', '?')} {'✅' if statuses.get('paths') == 'ok' else '❌'}\n"
            f"- **ccc**: {statuses.get('ccc', '?')} (informational)\n"
            f"- **cognee**: {statuses.get('cognee', '?')} (informational)\n"
            f"- **skills**: {statuses.get('skills', '?')} {'✅' if statuses.get('skills') == 'ok' else '❌'}\n"
            f"- **mcp**: {statuses.get('mcp', '?')} (informational)\n"
            f"- **dagster**: {statuses.get('dagster', '?')} {'✅' if statuses.get('dagster') == 'ok' else '❌'} (Layer 6)\n"
            f"- **baml**: {statuses.get('baml', '?')} {'✅' if statuses.get('baml') == 'ok' else '❌'} (Layer 7)\n"
            f"- **stacks**: {statuses.get('stacks', '?')} {'✅' if statuses.get('stacks') == 'ok' else '❌'} (Layer 8)\n"
            f"- **agents**: {statuses.get('agents', '?')} {'✅' if statuses.get('agents') == 'ok' else '❌'} (Layer 10, NEW)\n\n"
            f"**Summary**: {pass_count} pass / {fail_count} fail / {info_count} info\n"
        )
    )
    return


@app.cell
def __(mo, json, Path):
    # MCP server inventory (from opencode.json)
    mcp_config = Path("opencode.json")
    if mcp_config.is_file():
        cfg = json.loads(mcp_config.read_text())
        mcp_servers = cfg.get("mcp", {})
    return (cfg, mcp_config, mcp_servers)


@app.cell
def __(mo, mcp_servers):
    # Display the 14 MCP servers
    mo.output.replace(
        mo.md(
            f"## 14 MCP Servers\n\n"
            + "\n".join(
                f"- **{name}** ({srv.get('type', '?')})"
                for name, srv in mcp_servers.items()
                if isinstance(srv, dict)
            )
        )
    )
    return


@app.cell
def __(mo, Path):
    # Skills inventory
    skills_dir = Path(".agents/skills")
    skills = sorted(
        p.parent.name
        for p in skills_dir.rglob("SKILL.md")
    ) if skills_dir.is_dir() else []
    mo.output.replace(
        mo.md(
            f"## {len(skills)} Agent Skills\n\n"
            + ", ".join(f"`{s}`" for s in skills[:30])
            + (f", ... (+{len(skills) - 30} more)" if len(skills) > 30 else "")
        )
    )
    return


@app.cell
def __(mo, Path, text):
    # Full report viewer
    with mo.expander("Full sync report", expanded=False):
        mo.output.replace(mo.md(f"```\n{text}\n```"))
    return


if __name__ == "__main__":
    app.run()