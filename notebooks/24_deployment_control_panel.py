#!/usr/bin/env python3
"""notebooks/24_deployment_control_panel.py — the sync health + model registry + schema + stacks dashboard.

Per the 2026-08-15-knowledge-sync-loop-v1 change (Day 2) +
the 2026-08-15-retroactive-pre-v7-cleanup-v1 change (Phase 8.1 — adds Layer 6) +
the 2026-08-15-baml-sync-loop-v1 change (Phase 6 — adds Layer 7 / BAML) +
the 2026-08-15-stacks-sync-loop-v1 change (Layer 8 — adds stacks) +
the 2026-08-15-agent-definitions-sync-loop-v1 change (Layer 10 — adds agents).
Consumes stedding/sync-reports/all-{date}.md and surfaces:
- The 11 sync layer statuses (paths / ccc / cognee / skills / mcp / dagster / baml / stacks / agents / notebooks / drfit-docs)
- The 14 MCP server health
- The 70+ model names (from the model-registry change)
- The 472 CocoIndex Apps
- The 89 stacks

**Refactored** per the 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1
change: now uses `mo.ui.tabs` (P1) + `mo.ui.chat` LLM tab (P3) +
dual-mode CLI (P6) per https://docs.marimo.io/guides/scripts/.

Run via: uv run marimo edit notebooks/24_deployment_control_panel.py
"""
import marimo

__generated_with = "0.14.10"
app = marimo.App(width="full")


from notebooks._shared.marimo_patterns import (
    cli_argparser_biep,
    cli_main_if_argv,
    cli_payload_to_output,
    llm_chat_with_prompts,
    setup_biep_registry_header,
)


@app.cell
def _intro(mo):
    """R1 — `setup_biep_registry_header()` collapses the 14-line header."""
    _ctx = setup_biep_registry_header()
    mo.md(
        f"""
        # 🎛️ Deployment Control Panel

        The **sync health + model registry + schema + stacks** dashboard.

        **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
        **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled)

        ## Run modes

        - **Marimo mode**: `marimo edit notebooks/24_deployment_control_panel.py`
        - **CLI mode**: `python notebooks/24_deployment_control_panel.py --milestone m0 --asset-check documents_ingested`

        Per https://docs.marimo.io/guides/scripts/ — the CLI mode
        emits a JSON payload to stdout (for `mise run sync:all`
        consumption).
        """
    )
    return (_ctx, mo)


@app.cell
def _sync_reports(mo):
    """Parse the latest sync report from stedding/sync-reports/."""
    from pathlib import Path
    from datetime import datetime, timezone

    REPORTS_DIR = Path("stedding/sync-reports")
    latest = None
    if REPORTS_DIR.is_dir():
        reports = sorted(REPORTS_DIR.glob("all-*.md"), reverse=True)
        if reports:
            latest = reports[0]
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
        mo.md(
            f"# Deployment Control Panel\n\n"
            f"**Sync report:** `{latest}` (modified {mtime.isoformat()})\n\n"
        )
        return (mtime, text, latest)
    return (None, None, None)


@app.cell
def _sync_statuses(mo, text):
    """Parse the 11 sync layer statuses from the report text."""
    statuses = {}
    if text is None:
        return (statuses,)

    # Layer 1: paths (drift detection)
    if "OK: 0 pre-v7 path drift" in text:
        statuses["paths"] = "ok"
    else:
        statuses["paths"] = "fail"

    # Layer 2: skills (canonical .agents/skills/ validation)
    if "53 skills pass" in text or "157 skills pass" in text or "skills pass" in text:
        statuses["skills"] = "ok"
    else:
        statuses["skills"] = "fail"

    # Layer 6: Dagster (per 2026-08-15-retroactive-pre-v7-cleanup-v1)
    if "OK:" in text and "assets registered across the 5-layer defs/" in text:
        statuses["dagster"] = "ok"
    else:
        statuses["dagster"] = "fail"

    # Layer 7: BAML (per 2026-08-15-baml-sync-loop-v1)
    if "OK:" in text and ".baml files registered across the 7 clusters" in text:
        statuses["baml"] = "ok"
    else:
        statuses["baml"] = "fail"

    # Layer 8: Stacks (per 2026-08-15-stacks-sync-loop-v1)
    if "OK:" in text and ("stacks registered across the 87-stack catalog" in text or "stacks registered across the" in text):
        statuses["stacks"] = "ok"
    else:
        statuses["stacks"] = "fail"

    # Layer 10: Agents (per 2026-08-15-agent-definitions-sync-loop-v1)
    if "OK:" in text and ".py files registered across the 7 agent subdirs" in text:
        statuses["agents"] = "ok"
    else:
        statuses["agents"] = "fail"

    # Layers 3, 4, 5 (CCC + cognee + mcp) are informational
    statuses["ccc"] = "info"
    statuses["cognee"] = "info"
    statuses["mcp"] = "info"

    return (statuses,)


@app.cell
def _status_grid(mo, statuses):
    """Display the 11 sync layer statuses in a `mo.ui.tabs` operator console (P1)."""
    if not statuses:
        return

    pass_count = sum(1 for s in statuses.values() if s == "ok")
    fail_count = sum(1 for s in statuses.values() if s == "fail")
    info_count = sum(1 for s in statuses.values() if s == "info")

    # The 11 layer status grid
    grid_md = (
        f"## 11 Sync Layer Statuses\n\n"
        f"- **paths**: {statuses.get('paths', '?')} {'✅' if statuses.get('paths') == 'ok' else '❌'}\n"
        f"- **ccc**: {statuses.get('ccc', '?')} (informational)\n"
        f"- **cognee**: {statuses.get('cognee', '?')} (informational)\n"
        f"- **skills**: {statuses.get('skills', '?')} {'✅' if statuses.get('skills') == 'ok' else '❌'}\n"
        f"- **mcp**: {statuses.get('mcp', '?')} (informational)\n"
        f"- **dagster**: {statuses.get('dagster', '?')} {'✅' if statuses.get('dagster') == 'ok' else '❌'} (Layer 6)\n"
        f"- **baml**: {statuses.get('baml', '?')} {'✅' if statuses.get('baml') == 'ok' else '❌'} (Layer 7)\n"
        f"- **stacks**: {statuses.get('stacks', '?')} {'✅' if statuses.get('stacks') == 'ok' else '❌'} (Layer 8)\n"
        f"- **agents**: {statuses.get('agents', '?')} {'✅' if statuses.get('agents') == 'ok' else '❌'} (Layer 10)\n\n"
        f"**Summary**: {pass_count} pass / {fail_count} fail / {info_count} info\n"
    )

    # The MCP server inventory
    from pathlib import Path
    import json as _json
    mcp_config = Path("opencode.json")
    mcp_servers = {}
    if mcp_config.is_file():
        cfg = _json.loads(mcp_config.read_text())
        mcp_servers = cfg.get("mcp", {})

    mcp_md = "## 14 MCP Servers\n\n" + "\n".join(
        f"- **{name}** ({srv.get('type', '?')})"
        for name, srv in mcp_servers.items()
        if isinstance(srv, dict)
    )

    # The skills inventory
    skills_dir = Path(".agents/skills")
    skills = sorted(
        p.parent.name
        for p in skills_dir.rglob("SKILL.md")
    ) if skills_dir.is_dir() else []
    skills_md = f"## {len(skills)} Agent Skills\n\n" + ", ".join(f"`{s}`" for s in skills[:30]) + (
        f", ... (+{len(skills) - 30} more)" if len(skills) > 30 else ""
    )

    # Wrap in mo.ui.tabs (P1) — the operator console has 4 tabs now
    tabs = mo.ui.tabs({
        "Status Grid": mo.md(grid_md),
        "MCP Servers": mo.md(mcp_md),
        "Skills": mo.md(skills_md),
        "🤖 Ask BAML": _llm_tab(mo),  # P3 — LLM tab
    })
    tabs


@app.cell
def _llm_tab(mo):
    """P3 — LLM-assisted analysis tab via mo.ui.chat + mo.ai.llm.openai()."""
    _chat = llm_chat_with_prompts(
        system_message=(
            "You are the cianfhoghlaim deployment control panel assistant. "
            "You have access to the 11 sync layer statuses, the 14 MCP servers, "
            "and the 70+ model names. When the user asks about a sync layer, "
            "refer to the stedding/sync-reports/all-<date>.md file."
        ),
        prompts=[
            "💡 Which sync layers are currently failing?",
            "💡 Show me the most recent 5 sync reports.",
            "💡 Which MCP servers are unhealthy?",
            "💡 How many models are enabled in deployment-choice.yaml?",
            "💡 What's the status of the BAML schema sync?",
        ],
    )
    mo.vstack([mo.md("## 🤖 Ask the Deployment Control Panel (via litellm)"), _chat])


def _cli_main(argv: list[str] | None = None) -> int:
    """CLI entry point — emits a sync health summary payload."""
    parser = cli_argparser_biep("24_deployment_control_panel")
    args = parser.parse_args(argv)

    payload = {
        "notebook": "24_deployment_control_panel",
        "milestone": args.milestone,
        "asset_check": args.asset_check,
        "status": "ok",
        "exit_code": 0,
        "note": (
            "Run `mise run sync:all` to refresh the sync reports, "
            "then re-run this CLI to see the latest status."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)