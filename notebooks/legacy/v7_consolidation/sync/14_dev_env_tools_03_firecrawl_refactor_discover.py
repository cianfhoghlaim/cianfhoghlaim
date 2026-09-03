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

    # Phase 1 fix: compute absolute path from __file__ so the
    # notebook loads the dev_env tool module from any cwd.
    #   <repo>/cianfhoghlaim/notebooks/01_dev_env/0X.py
    # Tool:  <repo>/cianfhoghlaim/agents/adk/tools/dev_env.py
    # Path:  notebooks.parents[1] = cianfhoghlaim (package root)
    _HERE = Path(__file__).resolve().parent
    _TOOL = (
        _HERE.parents[1] / "agents" / "adk" / "tools" / "dev_env.py"
    )
    _spec = importlib.util.spec_from_file_location("dev_env", _TOOL)
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


# =============================================================================
# Dual-mode entry: marimo app OR standalone CLI script
# =============================================================================
def _cli_main(argv=None) -> int:
    """Run 03_firecrawl_refactor_discover.py as a CLI script from any cwd.

    Usage from any directory:
        python 03_firecrawl_refactor_discover.py --help
        uv run notebooks/01_dev_env/03_firecrawl_refactor_discover.py <flags>

    The marimo entry point is unchanged:
        marimo edit 03_firecrawl_refactor_discover.py
        marimo run  03_firecrawl_refactor_discover.py
    """
    import argparse
    import asyncio
    import importlib.util
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(prog='03_firecrawl_refactor_discover.py', description=__doc__)
    parser.add_argument("--package", type=str, default="dlt", help="PyPI / GitHub package name")
    parser.add_argument("--use-local-scrapes", action="store_true", default=False, help="Read from stedding/ingest_queue/<pkg>.json snapshot")
    parser.add_argument("--version-target", type=str, default=None, help="Optional specific version to inspect")
    args = parser.parse_args(argv)

    # Load dev_env tool module (same absolute-path fix as Phase 1 cell above)
    _HERE = Path(__file__).resolve().parent
    _TOOL = _HERE.parents[1] / 'agents' / 'adk' / 'tools' / 'dev_env.py'
    _spec = importlib.util.spec_from_file_location('dev_env', _TOOL)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)

    kwargs = {
        'use_local_scrapes': args.use_local_scrapes or None,
        'version_target': args.version_target,
    }
    results = asyncio.run(_mod.firecrawl_refactor_discover(args.package, **kwargs))
    print(json.dumps(results, indent=2, default=str))
    return 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main())
    app.run()
