# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.13.0",
#     "lancedb>=0.34.0",
#     "pyarrow>=15.0.0",
# ]
# ///
"""01 — Semantic code search via `ccc_search`.

Demonstrates the `ccc_search` tool from
`cianfhoghlaim.agents.adk.tools.dev_env` — the ADK-friendly wrapper
around the v1 CocoIndex Code LanceDB index at
`.cocoindex_code/lancedb/codebase_chunks.lance`.

Pattern: "ccc before grep" — always run semantic code search BEFORE
`rg` / `grep` to surface contextually relevant chunks.

Post-2026-08-15, this notebook adds a `centralized_registry` preset
that searches the 4 canonical artifacts (MODEL_REGISTRY +
notebooks/_shared/schema.py + 00_control_panel + deployment-choice.yaml)
+ the 3 openspec specs + the lint:registry helper. Use this preset to
discover what's currently registered, what was recently changed, and
what the canonical API surface looks like.

See also:
- `.agents/skills/ccc/SKILL.md`
- `.agents/skills/centralized-registry/SKILL.md`
- `openspec/changes/2026-07-06-add-dev-env-demo-tools-to-adk-agents/`
- `openspec/changes/archive/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/`
"""

import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo

    return (mo,)


@app.cell
def _intro(mo):
    mo.md("""
    # 01 — ccc_search (semantic code search)

    Live demo of `ccc_search` from
    `cianfhoghlaim.agents.adk.tools.dev_env`. The query runs against
    the v1 LanceDB index at
    `.cocoindex_code/lancedb/codebase_chunks.lance` (4820+ chunks
    indexed across the Cianfhoghlaim monorepo).

    **Why ccc before grep?** Semantic search surfaces contextually
    relevant code even when the exact keyword isn't present. Use
    this BEFORE `rg` / `grep` to ground your investigation.
    """)
    return


@app.cell
def _query_input(mo):
    query = mo.ui.text(
        value="LANCE_DB shared lifespan pattern",
        label="Search query",
        full_width=True,
    )
    limit = mo.ui.slider(
        start=1, stop=20, step=1, value=5, label="Result limit"
    )
    mo.vstack([query, limit])
    return limit, query


@app.cell
def _run_search(limit, query):
    """Call `ccc_search` and capture the structured chunks."""
    import asyncio
    import importlib.util
    from pathlib import Path

    # Import the tool module directly (the package __init__ has a
    # pre-existing pydantic-v2.13 incompat in research_agent.py that
    # is unrelated to this change).
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

    results = asyncio.run(
        _mod.ccc_search(query.value, limit=limit.value)
    )
    return (results,)


@app.cell
def _render(mo, query, results):
    """Render the search results as a marimo table."""
    if not results:
        mo.md(
            f"""
            **No results for `{query.value}`**

            Either the index is empty or the query doesn't match any
            indexed chunk. Try:
            - Run `bun run ccc:v1:index` to rebuild the index
            - Use a different query (e.g. `BAML extraction`, `Dagster asset`)
            """
        )

    # Build a markdown table from the structured results
    header = (
        "| relevance | file_path | line_no | snippet |\n"
        "|-----------|-----------|---------|---------|\n"
    )
    rows = []
    for r in results:
        if "error" in r:
            rows.append(f"| ❌ | `{r.get('error')}` | 0 | `{r.get('stderr', '')[:120]}` |")
            continue
        rel = r.get("relevance", 0)
        path = r.get("file_path", "")
        line = r.get("line_no", 0)
        snippet = (r.get("snippet") or "").replace("|", "\\|").replace("\n", " ")[:120]
        rows.append(f"| {rel:.2f} | `{path}` | {line} | {snippet} |")

    mo.md(
        f"""
        ## Results for `{query.value}` ({len(results)} found)

        {header}{chr(10).join(rows)}

        **How to read this table:**
        - `relevance` is a 0..1 score (higher = better)
        - `file_path` is repo-relative (or absolute, depending on the
          indexer config)
        - `snippet` is the first line of the matched chunk, truncated
          to 120 chars
        - ❌ rows indicate tool errors (missing index, missing deps, etc.)

        **Try next:** open one of the `file_path`s in your editor, or
        chain with `drift_detect` (notebook 02) to also check the
        pinned version of any imported package.
        """
    )
    return


# =============================================================================
# Dual-mode entry: marimo app OR standalone CLI script
# =============================================================================
def _cli_main(argv=None) -> int:
    """Run 01_ccc_search.py as a CLI script from any cwd.

    Usage from any directory:
        python 01_ccc_search.py --help
        uv run notebooks/01_dev_env/01_ccc_search.py <flags>

    The marimo entry point is unchanged:
        marimo edit 01_ccc_search.py
        marimo run  01_ccc_search.py
    """
    import argparse
    import asyncio
    import importlib.util
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(prog='01_ccc_search.py', description=__doc__)
    parser.add_argument("--query", type=str, default="LANCE_DB shared lifespan pattern", help="Natural-language search query")
    parser.add_argument("--limit", type=int, default=5, help="Result limit (1..100)")
    parser.add_argument("--semantic", action="store_true", default=False, help="Use BGE-M3 semantic search (slower first call)")
    args = parser.parse_args(argv)

    # Load dev_env tool module (same absolute-path fix as Phase 1 cell above)
    _HERE = Path(__file__).resolve().parent
    _TOOL = _HERE.parents[1] / 'agents' / 'adk' / 'tools' / 'dev_env.py'
    _spec = importlib.util.spec_from_file_location('dev_env', _TOOL)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)

    kwargs = {'limit': args.limit, 'semantic': args.semantic}
    results = asyncio.run(_mod.ccc_search(args.query, **kwargs))
    print(json.dumps(results, indent=2, default=str))
    return 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main())
    app.run()
