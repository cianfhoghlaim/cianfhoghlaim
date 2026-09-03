# P2-26 — marimo (Phase 2, Data Plane)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** data-platform

## TL;DR

marimo is the **reactive notebook framework** that powers the 11 Cianfhoghlaim dashboards in `oideachais/notebooks/`. Unlike Jupyter, marimo's cells re-execute on dependency change (no hidden state), and notebooks are pure Python modules that can be exported to apps, scripts, or WASM.

The canonical Cianfhoghlaim pattern uses marimo's `@app.cell` decorator with **polars** DataFrames and **MotherDuck Dives** as the SQL backend.

## Code

| Path | Purpose |
|:--|:--|
| `oideachais/notebooks/curriculum_educator.py` | The canonical Phase 4 KPI dashboard (24 subjects × 4 material types) |
| `oideachais/notebooks/leabharlann_full_stack_demo.py` | 6-corpus leabharlann demo (aigne, gaeilge, gemini_deep_research, mata, ollscoil_na_gaillimhe, zotero) |
| `oideachais/notebooks/dives/` | MotherDuck-synced dashboards (4) |
| `oideachais/web/apps/oideachais-web/src/routes/notebooks.tsx` | TanStack Start route that renders marimo WASM |
| `stedding/dev/flows/crypteolas/taighde_crypteolas_tuath/notebooks/` | Crypteolas research notebooks |

**Canonical marimo cell** (`oideachais/notebooks/curriculum_educator.py`):

```python
import marimo
import polars as pl
from cianfhoghlaim.core.motherduck.init import get_motherduck_connection

app = marimo.App(width="medium")

@app.cell
def _():
    conn = get_motherduck_connection(read_only=True)
    df = pl.from_arrow(conn.execute("""
        SELECT subject, material_type, COUNT(*) AS row_count, SUM(n_pages) AS total_pages
        FROM lakehouse.oideachais.examinations_ie
        WHERE exam_year >= 2020
        GROUP BY 1, 2
    """).arrow())
    return df, conn
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `MOTHERDUCK_TOKEN` | `infisical://dev-baile/motherduck/token` | Locket |
| `MARIMO_OUTPUT_DIR` | `/tmp/marimo-renders` | compose default |
| `MARIMO_PORT` | `2718` | compose default |

## CCC anchors

`oideachais/notebooks/` (11 files) · `oideachais/web/apps/oideachais-web/src/routes/notebooks.tsx` · `docs/skills/marimo/SKILL.md`

Search terms: `"@app.cell"`, `"pl.from_arrow"`, `"mo.ui.table"`, `"marimo.App"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-Q3 | Initial Jupyter adoption |
| 2026-01 | Migrated all 11 notebooks to marimo (reactive, no hidden state) |
| 2026-04 | Added marimo WASM export (`marimo export wasm`) for browser rendering |
| 2026-06-04 | Archived `marimo-batch` + `marimo-notebook` skill changes |
| 2026-06-28 | v4 consolidation: `sruth/oideachais/notebooks/` → `oideachais/notebooks/` |

## Anti-patterns

1. Don't use Jupyter-style global state — marimo cells re-execute on dep change
2. Don't use `pandas` — use `polars` (10x faster, better MotherDuck interop)
3. Don't hardcode SQL strings — use `ATTACH 'md:lakehouse'` for shared queries
4. Don't skip `@app.cell` decorator — it's how marimo tracks dependencies
5. Don't use `print()` for output — use `mo.output.replace()` or `mo.md()`

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Framework | marimo (not Jupyter) | Reactive + no hidden state + WASM export |
| DataFrame lib | polars | 10x faster, native MotherDuck interop |
| SQL backend | MotherDuck (cross-host) | Lakehouse catalog |
| Export format | WASM + HTML + Python script | Multi-target (web, notebook, script) |
| Version control | Plain `.py` files | Diffable + reviewable in PRs |
| Local dev | `marimo edit notebooks/curriculum_educator.py` | Live reload |
| Production deploy | marimo WASM embedded in TanStack Start | Browser-rendered, no server |
| Secrets | Locket + Infisical | No plaintext |

## Files to read next

`oideachais/notebooks/curriculum_educator.py` · `docs/skills/marimo/SKILL.md` · `docs/skills/marimo-notebook/SKILL.md`
