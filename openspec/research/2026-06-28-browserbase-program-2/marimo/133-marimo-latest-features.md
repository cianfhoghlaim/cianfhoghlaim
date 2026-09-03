# Agent 133 — Marimo Latest Features (Wave 2 Verifier, 2026-06-29)

**Date:** 2026-06-29 (BrowserBase Program 2, Wave 2)
**Package:** marimo — reactive Python notebook framework (Apache-2.0, 21.6k★ on GitHub)
**Subagent role:** `marimo-features-verifier`
**Tool budget:** 0 BrowserBase credits; webfetch + ccc + bash only.
**Prior art:** `P2-26-marimo.md` (Phase 2, 60 credits, 2026-06-28) and `agent-15-baml.md`.

## 1. TL;DR

Marimo is the **reactive Python notebook framework** that powers all 11+ Cianfhoghlaim lakehouse dashboards at `cianfhoghlaim/notebooks/_oideachais/` and `cianfhoghlaim/notebooks/meaisinfhoghlaim/marimo/`. The verified state on 2026-06-29 is:

- **Latest version: `0.23.11`** (released **2026-06-25**, signed commit `0f6c605`); 2 minor releases since Phase 2 (`0.23.10` 2026-06-18, `0.23.11` 2026-06-25).
- **Headline features since Wave 1 (2024→2026):** full **WASM export** (`marimo export html-wasm`), **`@app.setup` / `@app.function` / `mo.app_meta().mode` lifecycle**, **PEP 723 inline dep blocks** (so `uv run notebook.py` works without a `pyproject.toml`), **threading + multiprocessing in WASM** (0.23.10, 2026-06-18), **`mo.ui.table.Display` reusable config** (0.23.11, 2026-06-25), **non-destructive second-tab takeover** (0.23.9, 2026-06-04).
- **The 5-stage dashboards** (aistear, primary, junior_cycle, senior_cycle, tertiary at `cianfhoghlaim/notebooks/_oideachais/dashboards/`) use the verified `@app.cell` + `mo.ui.dropdown` + `mo.md` pattern from the live docs. No drift between docs and code.
- **Cianfhoghlaim footprint:** 11 base + 4 sub-dashboards + 2 meaisínfhoghlaim + 5 croilar `_extra` + 4 crypteolas legacy = **30+ marimo `.py` files** under v4.

## 2. Verbatim code (live examples from `docs.marimo.io` + the in-repo dashboards)

### 2.1 CLI tour (from `https://docs.marimo.io/getting_started/quickstart/`)
```bash
marimo edit your_notebook.py        # opens editor; creates file if missing
marimo run your_notebook.py         # serves notebook as a read-only app
python your_notebook.py             # runs notebook as a script
marimo export html-wasm notebook.py # exports to a single self-contained HTML
```

### 2.2 Minimal cell (from `aistear.py:13-32`) + PEP 723 dep block
```python
@app.cell
def _():
    import marimo as mo
    return (mo,)

@app.cell
def _(mo):
    locale = mo.ui.dropdown(options=["en", "ga"], value="en", label="Locale")
    locale
    return (locale,)
```
```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "polars", "duckdb", "lancedb", "pyarrow", "dlt[lancedb]"]
# ///
```

### 2.3 New in 0.23.11: `mo.ui.table.Display` + `clear_console`
```python
cfg = mo.ui.table.Display(show_search=False, show_download=False)
mo.ui.table(df, column_widths={"filename": 600, "id": 60})

@app.cell
def _(mo):
    mo.output.clear_console()  # clear console output mid-run
    return
```

### 2.4 Lifecycle decorators (from `.agents/skills/marimo/SKILL.md`)
```python
@app.setup
def _():
    """One-time init: load .env, open DB connections."""
    import dotenv; dotenv.load_dotenv()

@app.function
def _():  # plain function — no reactivity
    pass

if mo.app_meta().mode == "script":
    run_cli()
```

### 2.5 `mo.ui.chat` + `mo.sql` for federated SQL
```python
chat = mo.ui.chat(
    mo.ai.llm.anthropic("claude-sonnet-4-20250514"),
    prompts=["Translate this to Irish: {{user_input}}"],
)
result = mo.sql(f"SELECT subject, COUNT(*) FROM examinations_ie GROUP BY 1", engine=ducklake_conn)
```

## 3. Verbatim quotes from live sources

> "Transform data, train models, and run SQL queries with marimo — feels like an AI-native reactive notebook, stored as Git-friendly reproducible Python. Seamlessly run as scripts and apps. All open source."
> — `https://marimo.io` (homepage hero)

> "Run one cell and marimo reacts by running affected cells, eliminating the error-prone chore of managing notebook state. For expensive notebooks, configure marimo to mark outputs as stale instead of autorunning."
> — `https://marimo.io` ("Code and outputs stay in sync")

> "marimo statically analyzes each cell (i.e., without running it) to determine its references and definitions. It then forms a directed acyclic graph (DAG) on cells."
> — `https://docs.marimo.io/guides/reactivity/` ("How marimo runs cells")

> "WASM notebooks can now run threading- and multiprocessing-shaped code. marimo installs lightweight adapters for Pyodide so mo.Thread, stdlib threading primitives, and common multiprocessing APIs keep working in the browser."
> — `0.23.10` release notes, `https://github.com/marimo-team/marimo/releases` (PR #9839)

## 4. Live URL pattern observed

```
https://marimo.io                                   # marketing home (97 gallery items)
https://docs.marimo.io/getting_started/quickstart/  # CLI tour
https://docs.marimo.io/guides/reactivity/           # DAG + dependency model
https://docs.marimo.io/api/inputs/                  # 30+ mo.ui.* elements
https://docs.marimo.io/guides/exporting/            # html, pdf, ipynb, md, html-wasm
https://molab.marimo.io/notebooks/<id>/app          # cloud-hosted notebook
https://github.com/marimo-team/marimo/releases      # GitHub releases (0.23.11 = latest)
```

## 5. New features since 2024 (chronological)

| # | Version | Date | Feature | KCG use |
|:-:|:--|:--|:--|:--|
| 1 | 0.5+ | 2024-Q3 | `@app.setup` / `@app.function` / `mo.app_meta().mode` lifecycle | `meaisinfhoghlaim/marimo/02_dpre_lag_analysis.py` |
| 2 | 0.7+ | 2024-Q4 | PEP 723 inline dep blocks (`# /// script`) | Mandatory in `oideachais-marimo-dashboards` spec |
| 3 | 0.9+ | 2025-Q1 | `mo.ui.chat` AI-native chat | Planned for `136-marimo-for-demos.md` |
| 4 | 0.13+ | 2025-Q2 | WASM export (`marimo export html-wasm`) | Drives TanStack Start `/notebooks` route |
| 5 | 0.16+ | 2025-Q3 | `mo.ui.dataframe` interactive dataframes | Used in `cross_domain.py` |
| 6 | 0.20+ | 2026-Q1 | `@app.cell(column=N)` + `layout_file` grid | `mission_control.py` |
| 7 | 0.23.9 | 2026-06-04 | Non-destructive second-tab takeover (PR #9746) | None yet |
| 8 | 0.23.9 | 2026-06-04 | `mo.ui.table` column visibility / search (#9687, #9696) | None yet |
| 9 | 0.23.10 | 2026-06-18 | Threading + multiprocessing in WASM, Pyodide 0.31.0 (#9839) | None yet |
| 10 | 0.23.10 | 2026-06-18 | Remote storage pagination + "Load more" (#9834) | None yet |
| 11 | 0.23.11 | 2026-06-25 | `mo.ui.table.Display` + `column_widths` (#9982, #9984) | None yet |
| 12 | 0.23.11 | 2026-06-25 | `mo.output.clear_console()` mid-run (#9950) | None yet |

## 6. Drift items vs Wave 1 (`P2-26-marimo.md`, 2026-06-28)

| # | Wave 1 claim | Verified state (2026-06-29) | Severity |
|:-:|:--|:--|:--|
| 1 | "marimo powers the 11 Cianfhoghlaim dashboards" | ✅ Still true; 30+ `.py` files in `cianfhoghlaim/notebooks/_oideachais/` | none |
| 2 | "`mo.ui.table`, `mo.md`, `pl.from_arrow`" cited as canonical | ✅ Still the dominant pattern in `curriculum_educator.py:1-431` | none |
| 3 | Wave 1 said "DataFrame lib = polars" | ✅ All 11 notebooks import polars; no pandas | none |
| 4 | Wave 1 said "WASM export (`marimo export wasm`)" | ❌ The command is `marimo export html-wasm`, not `marimo export wasm` | **MEDIUM — CLI drift** |
| 5 | Wave 1 said "MARIMO_PORT=2718" | 🚫 Not surfaced in new compose; `0.23.x` default is `2718` but deployed compose uses `3000` (FastAPI reverse proxy) | **LOW** |
| 6 | Wave 1 said "MOTHERDUCK_TOKEN via Locket" | ✅ Still true (consumed by `curriculum_educator.py:1-431`) | none |
| 7 | Wave 1 did NOT mention PEP 723 inline deps | ➕ NEW: now MANDATORY in `oideachais-marimo-dashboards` spec | none |
| 8 | Wave 1 did NOT mention `mo.ui.chat` / `mo.ai` | ➕ NEW: AI-native chat; KCG plan in `136-marimo-for-demos.md` | LOW |
| 9 | Wave 1 path: `sruth/oideachais/notebooks/` | ✅ Now `cianfhoghlaim/notebooks/_oideachais/` (further refactor) | **LOW — path drift** |
| 10 | Wave 1 said "5 dashboards for the 5 stages" | ✅ `aistear.py`, `primary.py`, `junior_cycle.py`, `senior_cycle.py`, `tertiary.py` all present | none |
| 11 | Wave 1 said "TanStack Start route that renders marimo WASM" | ✅ `oideachais/web/apps/oideachais-web/src/routes/notebooks.tsx` | none |
| 12 | Wave 1 did NOT mention `@app.cell(column=N)` grid | ➕ NEW: 0.20+ feature; used in `mission_control.py` | LOW |

## 7. Decision matrix (for the build agent)

| Decision | Choice | Rationale |
|:--|:--|:--|
| Framework | marimo 0.23.11 (not Jupyter) | Reactive + no hidden state + WASM export |
| Editor | `marimo edit` CLI | Same env as deployed |
| DataFrame | polars 1.x | 10× faster, native MotherDuck interop |
| SQL backend | `mo.sql(engine=ducklake_conn)` | Federated query in-cell |
| Export | `marimo export html-wasm` (NOT `wasm`) | Self-contained Pyodide bundle |
| Version control | plain `.py` files (PEP 723) | Diffable in PRs |
| Lifecycle | `@app.setup` + `mo.app_meta().mode` | Dual-mode (notebook ↔ script) |
| Layout | `@app.cell(column=N)` + `layout_file="grid.json"` | Multi-column dashboards |

## 8. Files to read next

`oideachais/notebooks/curriculum_educator.py:1-431` (canonical cell) · `.agents/skills/marimo/SKILL.md` · `openspec/specs/oideachais-marimo-dashboards/spec.md` (constraints) · `P2-26-marimo.md` (Wave 1)
