# Spec Delta: oideachais-marimo-dashboards

## ADDED Requirements

### Requirement: Marimo on Cloudflare Workers + Container (WASM)

The system SHALL support deploying a marimo notebook as a
Cloudflare Worker wrapping a marimo Container via a Durable Object,
exposed over TCP 8080.

#### Scenario: Worker serves the marimo WASM bundle

- **GIVEN** a `Dockerfile` at `infrastructure/stacks/<surface>/marimo/`
  that pins `python:3.12-slim` + `marimo[server]` + a `marimo edit
  --headless` entry point on port 8080
- **WHEN** the user runs `wrangler deploy` against the
  `wrangler.jsonc` (with a `durable_object_namespace` for the
  marimo singleton)
- **THEN** the Worker SHALL serve the marimo UI on a `*.workers.dev`
  URL
- **AND** the `src/index.ts` Durable Object SHALL proxy
  `fetch()` to the marimo Container

### Requirement: PEP 723 inline dependency blocks in notebooks

The system SHALL ship all shareable marimo notebooks with the
PEP 723 inline dependency header (so `uv run notebook.py` works
without a `pyproject.toml`).

#### Scenario: Notebook runs with `uv run`

- **GIVEN** a notebook `sruth/oideachais/notebooks/<name>.py` with a
  PEP 723 header (`# /// script ... #`) declaring
  `requires-python = ">=3.12"` and `dependencies = ["marimo", ...]`
- **WHEN** the user runs `uv run <name>.py`
- **THEN** the notebook SHALL execute without a `pyproject.toml`
  in the working directory
- **AND** `uv` SHALL resolve the declared dependencies into an
  isolated cache

### Requirement: Multi-column layout via `@app.cell(column=N)`

The system SHALL use `@app.cell(column=N)` plus
`layout_file=".../grid.json"` to persist multi-column dashboard
layouts.

#### Scenario: Grid layout persists across runs

- **GIVEN** a notebook with 3 cells in columns 0, 1, 1 respectively
  and a `layout_file="grid.json"`
- **WHEN** the user drags a cell from column 1 to column 0 in
  the marimo editor
- **THEN** the `grid.json` SHALL be updated
- **AND** the next `uv run <name>.py` SHALL preserve the new layout

### Requirement: DLT + LanceDB pipeline pattern in notebooks

The system SHALL use the DLT `lancedb_adapter(source, embed=[...])`
pattern in marimo notebooks to build vector + full-text + hybrid
search demos end-to-end.

#### Scenario: Pipeline completes in a notebook cell

- **GIVEN** a marimo cell that calls
  `pipeline.run(lancedb_adapter(source, embed=["text"]))`
- **WHEN** the cell runs
- **THEN** the DLT pipeline SHALL materialise the source rows
  into the LanceDB table at `lancedb_data/<table>.lance`
- **AND** a follow-up cell SHALL be able to run
  `table.search(q, query_type="hybrid").rerank(RRFReranker())`
  without re-running the pipeline

## REMOVED Requirements

(None. All existing 3 requirements are preserved.)
