# docs/marimo/ — Marimo Reference Library

Marimo is a reactive Python notebook framework — git-friendly, deterministic, and deployable as a static WASM app. The `docs/marimo/` library is consolidated to **2.6MB of curated content** (the upstream full source-code mirror moved to `../08-mirrors/marimo/`).

Last consolidated: 2026-06-14

---

## Strategic docs (4 at root)

| Document | Description |
|----------|-------------|
| [marimo.md](marimo.md) | The "Marimo Notebook Assistant" skill — expertise in reactive dataflow, UI components, layouts, AI integration |
| [marimo-reference.md](marimo-reference.md) | Merged reference — synthesized from 41 source files (skill + cloudflare + examples + patterns) |
| [marimo_cloudflare.md](marimo_cloudflare.md) | "Building an Interactive Learning Platform for Irish Mathematics" — Marimo WASM + Cloudflare Durable Objects + Coder + TanStack Start architecture |
| [README.md](README.md) | (Upstream-marimo example index) |

## Curated .py demos (16 at root, by topic)

**Data engineering:**

- `chunking.py` — chunking-strategy comparison
- `cloudflare_data_ops.py` — Cloudflare R2/D1 operations
- `cocoindex_flows.py` — CocoIndex flow patterns
- `crawl4ai_extraction.py` — crawl4ai extraction examples
- `dlt_lancedb demo.py` — DLT → LanceDB pipeline
- `document_indexing_comparison.py` — indexing-strategy comparison
- `ducklake-demo.py` — DuckLake (DuckDB + Iceberg + lakehouse)
- `ibis_example.py` — Ibis backend-agnostic dataframe API
- `iceberg-demo.py` — Apache Iceberg integration
- `lance-demo.py` — LanceDB vector store
- `motherduck-demo.py` — MotherDuck serverless DuckDB
- `neo4j-demo.py` — Neo4j graph database
- `sqlmesh_duckdb_ibis.py` — SQLMesh + DuckDB + Ibis
- `my-mcp.py` — MCP server example
- `ocr_comparison_enhanced.py` — OCR pipeline comparison
- `typer-demo.py` — Typer CLI demo

## Topic subdirs (15 dirs, ~200 files)

| Subdir | Topic | Files |
|---|---|---|
| [ai/](ai/) | AI integration examples (LLM cells, chat, generative UI) | 26 |
| [cloud/](cloud/) | Cloud provider deployments | 9 |
| [cloudflare/](cloudflare/) | Cloudflare-specific patterns | 14 |
| [control_flow/](control_flow/) | Cell execution control | 2 |
| [frameworks/](frameworks/) | Integration with web frameworks (FastAPI, etc.) | 21 |
| [layouts/](layouts/) | Slide layouts, sidebars, multi-column | 7 |
| [markdown/](markdown/) | Markdown rendering, dynamic markdown | 6 |
| [maths_examples/](maths_examples/) | Math notebooks (SymPy, etc.) | 8 |
| [misc/](misc/) | Miscellaneous demos | 19 |
| [outputs/](outputs/) | Output-format examples | 13 |
| [running_as_a_script/](running_as_a_script/) | Running as a CLI script | 4 |
| [running_cells/](running_cells/) | Cell execution models | 6 |
| [sql/](sql/) | SQL cells + DataFrame integration | 16 |
| [testing/](testing/) | Testing patterns | 3 |
| [third_party/](third_party/) | Third-party library integrations | 56 |
| [ui/](ui/) | UI component examples | 38 |

## Upstream mirrors (in `../08-mirrors/`)

- `../08-mirrors/marimo/` — full upstream source-code mirror (1,492 .py + 9 .md, 169MB, 3,641 files). Use when you need to read the actual marimo internals.
- `../08-mirrors/marimo-docs/` — partial upstream docs mirror (462 .py, 6.2MB). The Sphinx docs source.

## Note on consolidation

The **upstream `marimo/marimo/` (3,641 files, 169MB) and `marimo/docs/` (462 .py, 6.2MB)** were moved to `docs/08-mirrors/marimo/` and `docs/08-mirrors/marimo-docs/`. Curated content stays here at 2.6MB, ~200 files, easier to navigate. The `marimo/__marimo__/session/` runtime session files (3 JSON) and `.claude`/`.cursor`/`.vscode` were dropped.
