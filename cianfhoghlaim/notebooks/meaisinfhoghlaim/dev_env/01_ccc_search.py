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

See also:
- `.agents/skills/ccc/SKILL.md`
- `openspec/changes/2026-07-06-add-dev-env-demo-tools-to-adk-agents/`
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
        # 01 — ccc_search (semantic code search)

        Live demo of `ccc_search` from
        `cianfhoghlaim.agents.adk.tools.dev_env`. The query runs against
        the v1 LanceDB index at
        `.cocoindex_code/lancedb/codebase_chunks.lance` (4820+ chunks
        indexed across the Cianfhoghlaim monorepo).

        **Why ccc before grep?** Semantic search surfaces contextually
        relevant code even when the exact keyword isn't present. Use
        this BEFORE `rg` / `grep` to ground your investigation.
        """
    )
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
def _run_search(query, limit):
    """Call `ccc_search` and capture the structured chunks."""
    import asyncio
    import importlib.util
    from pathlib import Path

    # Import the tool module directly (the package __init__ has a
    # pre-existing pydantic-v2.13 incompat in research_agent.py that
    # is unrelated to this change).
    _tool_path = Path("cianfhoghlaim/agents/adk/tools/dev_env.py")
    _spec = importlib.util.spec_from_file_location("dev_env", _tool_path)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)

    results = asyncio.run(
        _mod.ccc_search(query.value, limit=limit.value)
    )
    return Path, results


@app.cell
def _render(results, mo, query):
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
    return header, rows


if __name__ == "__main__":
    app.run()
