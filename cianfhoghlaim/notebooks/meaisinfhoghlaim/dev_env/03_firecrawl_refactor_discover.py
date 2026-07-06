# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.13.0",
# ]
# ///
"""03 — Firecrawl refactor discovery for `dlt`.

Demonstrates `firecrawl_refactor_discover` from
`cianfhoghlaim.agents.adk.tools.dev_env` — fetches the upstream
breaking-change notes for a package via the Firecrawl MCP server.

By default, the tool reads from the curated
`stedding/ingest_queue/<package>.json` snapshot when
`USE_LOCAL_SCRAPES=true` is set, so it never burns Firecrawl credits
during routine dev-env demos.

See also:
- `.agents/skills/firecrawl/SKILL.md`
- `.agents/skills/browser-tools/SKILL.md`
- `openspec/changes/upstream-package-monitoring/`
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
        # 03 — firecrawl_refactor_discover (upstream breaking changes)

        Live demo of `firecrawl_refactor_discover` from
        `cianfhoghlaim.agents.adk.tools.dev_env`. Fetches the latest
        breaking-change notes from the canonical upstream sources
        (PyPI changelog, GitHub Releases, official blog) for the
        package you select below.

        **Behaviour:**
        - If `USE_LOCAL_SCRAPES=true` (the default for this notebook),
          reads from `stedding/ingest_queue/<pkg>.json`
        - Otherwise, calls the Firecrawl MCP server (`firecrawl_research_search_papers`
          + `firecrawl_scrape`)
        - Never raises on network failure — returns a graceful
          `error: firecrawl_unavailable: ...`
        """
    )
    return


@app.cell
def _package_picker(mo):
    """Multi-select widget for the package to investigate."""
    DEFAULT = ["dlt"]
    picker = mo.ui.multiselect(
        options=[
            "dlt", "dagster", "motherduck", "lancedb", "cognee",
            "marimo", "duckdb", "pydantic",
        ],
        value=DEFAULT,
        label="Package to investigate",
    )
    picker
    return DEFAULT, picker


@app.cell
def _run_discover(picker):
    """Call `firecrawl_refactor_discover` for the selected package."""
    import asyncio
    import importlib.util
    import os
    from pathlib import Path

    # Honour the canonical local-scrape fallback flag
    os.environ.setdefault("USE_LOCAL_SCRAPES", "true")

    _tool_path = Path("cianfhoghlaim/agents/adk/tools/dev_env.py")
    _spec = importlib.util.spec_from_file_location("dev_env", _tool_path)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)

    if not picker.value:
        result = {"package": None, "breaking_changes": [], "source_urls": []}
    else:
        # Run sequentially — each call may take ~1-3s for the snapshot read
        result = asyncio.run(
            _mod.firecrawl_refactor_discover(picker.value[0])
        )
    return Path, result


@app.cell
def _render(result, mo):
    """Render the refactor discovery report."""
    pkg = result.get("package", "?")
    changes = result.get("breaking_changes", [])
    urls = result.get("source_urls", [])
    source = result.get("source", "live")
    error = result.get("error")

    if error:
        mo.md(
            f"""
            ## Error fetching `{pkg}` breaking changes

            `{error}`

            **Try next:**
            - Set `USE_LOCAL_SCRAPES=true` to use the curated snapshot
            - Or add a snapshot at `stedding/ingest_queue/{pkg}.json`
            - Or run with `FIRECRAWL_API_KEY` set for a live fetch
            """
        )

    if not changes:
        mo.md(
            f"""
            ## No breaking changes detected for `{pkg}` (last 90 days)

            Source: `{source}`

            Source URLs:
            {chr(10).join(f"- {u}" for u in urls) if urls else "_none_"}

            The curated snapshot may be empty. Either:
            1. The package has been stable for the past 90 days
            2. The snapshot needs to be refreshed — file an issue to
               have the firecrawl-monitor scheduler pick it up
            """
        )

    rows = []
    for ch in changes:
        version = ch.get("version", "?")
        desc = ch.get("description", "").replace("|", "\\|")
        step = ch.get("migration_step", "").replace("|", "\\|")
        src = ch.get("source_url", "")
        rows.append(
            f"| `{version}` | {desc[:200]} | {step[:200]} | [link]({src}) |"
        )

    mo.md(
        f"""
        ## {len(changes)} breaking change(s) for `{pkg}` (last 90 days)

        Source: `{source}`

        | version | description | migration_step | source |
        |---------|-------------|----------------|--------|
        {chr(10).join(rows)}

        **Source URLs:**
        {chr(10).join(f"- {u}" for u in urls) if urls else "_none_"}

        **Try next:** chain with `drift_detect` (notebook 02) to see
        whether the breaking change has been pinned in
        `pyproject.toml`, then chain with `openspec_validate` (notebook
        06) to draft the migration change.
        """
    )
    return changes, error, pkg, rows, source, urls


if __name__ == "__main__":
    app.run()
