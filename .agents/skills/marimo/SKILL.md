---
name: marimo
description: Expert assistant for marimo reactive Python notebooks. Use when building reactive dashboards with multi-column layout, PEP 723 inline dependency blocks, `@app.setup` + `@app.function` lifecycle modes, `mo.sql(engine=)` for federated SQL against DuckLake/MotherDuck, DLT + LanceDB + RRF hybrid search patterns, or marimo-on-Cloudflare Workers + Container deployment. Powers the 6 per-subject BIEP notebooks (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science) at `notebooks/`.
---

# Marimo Notebook Assistant

Marimo is the reactive Python notebook framework that ships
as the canonical lakehouse-dashboard surface for the
Cianfhoghlaim platform. Every notebook is a **pure-Python
file** (no JSON, no `.ipynb` format) with reactive cells
(like Excel cells — changing one cell automatically updates
all cells that depend on it).

## When to use this skill

Use when you need to:

- "Build a reactive dashboard for the lakehouse"
- "Add PEP 723 inline dependency blocks to a notebook"
- "Use `@app.setup` / `@app.function` / `mo.app_meta().mode`"
- "Run `mo.sql(f"...", engine=conn)` against DuckLake or
  MotherDuck"
- "Build a multi-column layout with `@app.cell(column=N)`"
- "Add `mo.status.spinner` or `mo.status.progress_bar` for
  long-running operations"
- "DLT → LanceDB pipeline in a notebook (with `RRFReranker`)"
- "Deploy a marimo notebook to Cloudflare Workers + Container"
- "Wire a marimo chat to Pydantic AI / Agno / OpenAI"
- "Add a `mo.ui.chat` with `allow_attachments=[...]`"

## Mental model

- **`@app.cell`** — a reactive cell. Re-runs when its
  dependencies (referenced variables) change.
- **`@app.function`** — a regular Python function (no
  reactivity). Use for helpers.
- **`@app.setup`** — a one-time init cell. Runs once at
  notebook load. Use for `load_dotenv()`, opening DB
  connections, registering MCP tools.
- **`mo.app_meta().mode`** — `edit`, `run`, or `script`.
  Branch on it for notebook-vs-CLI dual mode.
- **`mo.running_in_notebook()`** — True when running in the
  marimo editor, False when running as a script.

## PEP 723 inline dependency blocks

Every shareable marimo notebook in the repo uses PEP 723
inline dependency headers, so `uv run <name>.py` works
without a `pyproject.toml` in the working directory:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "polars",
#     "duckdb",
#     "lancedb",
#     "pyarrow",
#     "dlt[lancedb]",
# ]
# ///
```

The `# /// script` block is **mandatory** for any notebook
that is checked into `notebooks/` (or any
subdirectory). `uv` resolves the declared dependencies into
an isolated cache.

## `@app.cell` basics

```python
import marimo as mo

app = marimo.App(width="full", layout_file="grid.json")


@app.cell
def __():
    import polars as pl
    return pl


@app.cell
def __():
    df = pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    mo.ui.table(df)
    return (df,)


if __name__ == "__main__":
    app.run()
```

Every cell returns a tuple of the variables it defines
(no return → no exposed variables).

## Multi-column layout

Use `@app.cell(column=N)` and `app = marimo.App(width="full")`
to build side-by-side dashboards:

```python
app = marimo.App(width="full")


@app.cell
def header():
    mo.md("# My Dashboard")
    return


@app.cell
def left_panel():
    selector = mo.ui.dropdown(options=[...])
    selector
    return (selector,)


@app.cell
def right_panel():
    chart = mo.ui.altair_chart(...)
    chart
    return (chart,)


@app.cell(column=1)  # ← column 1 (right side)
def _():
    mo.md("Right panel content")
    return
```

`mo.sidebar([...], footer=[...])` provides a full sidebar
chrome (with optional icons via `mo.icon("lucide:database")`).

## Persistent layouts

`layout_file=".../grid.json"` saves the user's custom layout
(arranged via drag-and-drop in the editor) to disk:

```python
app = marimo.App(width="full", layout_file="grid.json")
```

Next time the notebook loads, the saved layout is restored.
Use this for any dashboard that the user customises.

## `mo.app_meta().mode` and `mo.running_in_notebook()`

For notebooks that double as CLI tools:

```python
import sys

@app.cell
def _():
    mode = mo.app_meta().mode
    if mode == "script":
        # Run as a script (e.g. `uv run notebook.py --query "..."`)
        sys.argv  # parse CLI args here
    return (mode,)


@app.cell
def _():
    if not mo.running_in_notebook():
        # Don't show UI components when running headless
        print("Running as script")
```

The canonical example: `running_as_a_script/with_argparse.py`
parses `argparse` arguments when the notebook is run as a
script and shows the UI when it's edited in the browser.

## `mo.status.spinner` and `mo.status.progress_bar`

For long-running operations:

```python
@app.cell
def _():
    with mo.status.spinner(title="Loading 10k rows..."):
        df = pl.scan_parquet("data.parquet").collect()
    df
    return (df,)


@app.cell
def _():
    for i in mo.status.progress_bar(range(100), show_eta=True, show_rate=True):
        do_slow_thing(i)
    return
```

`spinner` is a context manager. `progress_bar` is an iterable
wrapper. Both render real-time UI feedback in the notebook.

## `mo.sql(f"...", engine=conn, output=False)`

For SQL queries against an explicit DuckDB / MotherDuck
connection (the canonical way to read from DuckLake):

```python
@app.cell
def _():
    import duckdb
    con = duckdb.connect("md:cianfhoghlaim")
    return (con,)


@app.cell
def _():
    con = _
    df = mo.sql(
        f"SELECT subject, COUNT(*) AS n FROM curriculum GROUP BY subject",
        engine=con,
        output=False,  # don't auto-display, we'll show it
    )
    mo.ui.table(df)
    return
```

`engine=conn` passes an explicit connection (DuckDB, MotherDuck,
or any DB-API 2.0). `output=False` prevents auto-display so you
can wrap the result in a custom UI component.

## DLT → LanceDB pipeline pattern

The canonical "ETL into a vector store" pattern, demonstrated
end-to-end:

```python
import dlt
from lancedb import lancedb_adapter
from lancedb.rerankers import RRFReranker


@dlt.resource
def curriculum_pages():
    for page in fetch_pages():
        yield {"text": page["text"], "filename": page["filename"]}


@app.cell
def _():
    pipeline = dlt.pipeline(
        destination="duckdb",
        dataset_name="curriculum",
    )
    load_info = pipeline.run(lancedb_adapter(curriculum_pages(), embed=["text"]))
    load_info
    return (load_info,)


@app.cell
def _():
    import lancedb
    db = lancedb.connect("./lancedb_data")
    table = db.open_table("curriculum_pages")
    results = (table
        .search("handwriting recognition for Irish", query_type="hybrid")
        .rerank(RRFReranker())
        .limit(10)
        .to_pandas())
    mo.ui.table(results)
    return
```

`lancedb_adapter(source, embed=["text"])` automatically
embeds the `text` column (using the configured model) and
writes the vectors + metadata to a LanceDB table. The
follow-up cell runs hybrid search with RRF reranking.

## `@app.setup` — one-time init

```python
@app.setup
def setup_dotenv():
    from dotenv import load_dotenv
    load_dotenv()
    return  # no exposed variables


@app.setup
def register_mcp_tool():
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("cianfhoghlaim-curriculum")
    # Register the tool globally so all cells can use it
    return (mcp,)
```

`@app.setup` runs once at notebook load. Use it for `load_dotenv()`,
DB connection setup, MCP tool registration, etc.

## `mo.ui.chat` with Pydantic AI / Agno

```python
@app.cell
def _():
    import os
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        mo.stop(not api_key, mo.md("Set OPENAI_API_KEY to use the chat."))
    return (api_key,)


@app.cell
def _():
    chat = mo.ui.chat(
        mo.ai.llm.openai(
            model="gpt-4o-mini",
            system_message="You are a curriculum assistant.",
        ),
        allow_attachments=["image/png", "image/jpeg", "application/pdf"],
        max_messages=20,
    )
    chat
    return (chat,)


@app.cell
def _():
    chat = _
    mo.md(f"**You:** {chat.value[-1].content if chat.value else ''}")
    return
```

`mo.ui.chat` works with any OpenAI-compatible API (set
`OPENAI_API_BASE` for vLLM / llama.cpp / Ollama).

## Cloudflare Workers + Container deployment

The KCG production pattern: a Cloudflare Worker proxies
requests to a marimo Container via a Durable Object. See
`references/deployment-cloudflare.md` for the full setup
(Dockerfile + wrangler.jsonc + src/index.ts).

## KCG conventions

- Every shareable notebook in `notebooks/` MUST
  have a PEP 723 `# /// script` header
- The FastAPI app serves notebooks at `/dashboards/<name>`
- Each dashboard has an asset check in
  `orchestration/defs/4_asset_generation/marimo_dashboards.py` that
  verifies the notebook renders without errors
- Live mode (`marimo edit --watch`) is supported via the
  `marimo-watch` Dagster sensor

## When to use a marimo notebook vs. a marimo app

- **Notebook** — single-author, exploratory data analysis
- **App** (`@app.cell` + `marimo.App` + FastAPI mount) —
  multi-author, production dashboard, multi-cell reactive
  layout, deployable to Cloudflare

The KCG convention: start as a notebook, promote to an app
once the analysis is stable.

## Anti-patterns

- **Don't use marimo for batch / scheduled jobs** — use a
  Dagster asset instead. Marimo is for interactive dashboards.
- **Don't fetch data in `@app.cell` without memoisation** —
  use `@app.setup` to load the data once, then reference it
  from the cells.
- **Don't use `print()` for output** — use `mo.md()`,
  `mo.ui.table()`, `mo.ui.altair_chart()`, etc.
- **Don't store secrets in cells** — use `@app.setup` +
  `load_dotenv()`.

## Resources

- Marimo docs: <https://docs.marimo.io/>
- PEP 723: <https://peps.python.org/pep-0723/>
- KCG notebooks: `notebooks/`
- KCG dashboard assets:
  `orchestration/defs/4_asset_generation/marimo_dashboards.py`
- Reference files in this skill:
  - `references/deployment-cloudflare.md` — Cloudflare Workers
    + Container deployment
  - `references/data-pipelines.md` — DLT + LanceDB + Iceberg +
    DuckLake patterns
  - `references/vector-search.md` — LanceDB hybrid + RRF
    rerankers
  - `references/layouts.md` — multi-column + sidebar + grid
  - `references/lifecycle-modes.md` — `edit` / `run` / `script`
  - `references/ai-chat.md` — `mo.ui.chat` patterns
  - `references/sql-cells.md` — `mo.sql(engine=conn)` patterns
- Related skills: `.agents/skills/dlt/`, `.agents/skills/lancedb/`,
  `.agents/skills/ducklake/`, `.agents/skills/motherduck/`,
  `.agents/skills/cocoindex/`

## British-Isles Education pipeline — Canonical KCG pattern (post-v4)

The post-v4 BIEP (`openspec/changes/lc6-biep/`) ships **6
per-subject marimo notebooks** (Mathematics, Chemistry, Geography,
Gaeilge, English, Computer Science) at
`notebooks/lc_<subject>_dashboard.py`. Each
notebook is a federated SQL front-end over the DuckLake +
LanceDB combination, reading via `mo.sql(engine=md:cianfhoghlaim)`:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "duckdb", "ibis-framework"]
# ///
import marimo as mo
app = mo.App(width="medium")


@app.cell
def _():
    import duckdb
    con = duckdb.connect("md:cianfhoghlaim")  # MotherDuck + DuckLake
    return (con,)


@app.cell
def _(con):
    # Federated SQL: DuckLake + LanceDB via lance_scan()
    result = con.sql("""
        SELECT s.subject, s.year, s.topic, count(*) AS n
        FROM cianfhoghlaim.leaving_cert.mathematics_topics s
        GROUP BY s.subject, s.year, s.topic
        ORDER BY s.year, n DESC
    """).df()
    return (result,)


@app.cell
def _(result):
    import altair as alt
    chart = alt.Chart(result).mark_line().encode(
        x="year:O", y="n:Q", color="topic:N"
    )
    return (chart,)
```

**British-Isles Education pipeline use case:**

- **6 per-subject notebooks** — `lc_mathematics_dashboard.py`,
  `lc_chemistry_dashboard.py`, `lc_geography_dashboard.py`,
  `lc_gaeilge_dashboard.py`, `lc_english_dashboard.py`,
  `lc_computer_science_dashboard.py` at
  `notebooks/`.
- **Federated SQL** — `duckdb.connect("md:cianfhoghlaim")` reads
  DuckLake tables AND LanceDB tables via `lance_scan()` in the
  same SQL query (so a single notebook joins BAML-extracted
  syllabus topics with vector-search retrieval).
- **Bilingual UI** — the Gaeilge dashboard uses Gaeilge
  strings for the `mo.ui.dropdown` labels and the cell output
  (the `ExtractCrossLinguisticConcept` BAML function aligns
  terminology across the two languages).
- **42 lc5/lc6 assets → 6 notebooks** — each notebook reads
  from 7 DuckLake tables (one per BAML stage × subject);
  the 7th per-subject table is `gov_circulars_archive` for
  the `government_circulars` partition.
- **Asset checks** — each notebook has a Dagster asset
  check in
  `orchestration/defs/4_asset_generation/marimo_dashboards.py`
  that re-runs the notebook with `--headless` and asserts no
  cell errors.

## v14 Helper Modules

The v14 notebook surface centralises reusable behaviour in three helper modules:

- `notebooks/_shared/marimo_patterns.py` — canonical dashboard patterns,
  including registry headers, dual-mode execution, and shared layout helpers.
- `notebooks/_shared/area_shims/biiep_v3_dashboard.py` — shared BIEP v3
  jurisdiction dashboard cells and the eight-cell dashboard surface.
- `notebooks/_shared/ragas_gauge.py` — reusable RAGAS quality gauge rendering
  for notebook evaluation panels.

LLM routing uses the `LITELLM_BASE_URL` constant from the shared helpers rather
than hardcoding a gateway URL. These helpers are used by the 17 BIEP v3
jurisdiction dashboards, the 7 grouped dashboards, and the consolidated
`notebooks/sync_health.py` dashboard.

Cross-references:
- [`.agents/skills/dlt/SKILL.md`](../dlt/SKILL.md) — the
  `cianfhoghlaim.leaving_cert.<subject>_<lang>` tables
- [`.agents/skills/cocoindex/SKILL.md`](../cocoindex/SKILL.md) —
  the LanceDB tables joined via `lance_scan()`
- [`.agents/skills/motherduck/SKILL.md`](../motherduck/SKILL.md) —
  the `md:cianfhoghlaim` connection string
- [`.agents/skills/duckdb/SKILL.md`](../duckdb/SKILL.md) —
  the `lance_scan()` integration
- [`.agents/skills/ducklake/SKILL.md`](../ducklake/SKILL.md) —
  the DuckLake `ATTACH` for the same `md:cianfhoghlaim` database

## Examples

See [`./examples/`](./examples/) for upstream `.ipynb` ↔ `.py`
conversion test fixtures (9 total). These are marimo's own
internal test cases for the `mo convert` CLI — useful when
debugging an unexpected conversion result:

- `marimo_docs_marimo_tests__convert_ipynb_data_*.ipynb` —
  edge cases (duplicate definitions, syntax errors, hidden
  markdown cells, pip commands, aug-assign semantics)
- `marimo_docs_marimo_tests__convert_ipynb_data_cell_metadata.ipynb`
  — cell metadata round-trip
- `marimo_docs_marimo_tests__convert_ipynb_data_comments_preservation.ipynb`
  — Python comment preservation across conversion
