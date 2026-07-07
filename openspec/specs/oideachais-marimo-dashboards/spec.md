# Oideachais Marimo Dashboards Capability

## Purpose

`oideachais-marimo-dashboards` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at
`cianfhoghlaim/notebooks/` and `cianfhoghlaim/notebooks/dashboards/`. See
`docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for
the project identity.

This spec was consolidated from the 51-line
`leabharlann-full-stack-demo` spec and now covers the full Marimo
notebook surface.

## Background

Marimo reactive Python notebooks for the oideachais lakehouse. The
notebooks are served as dashboards (mounted at `/dashboards/*` on the
FastAPI app) and cover the 5 educational stages (Aistear, Primary,
Junior Cycle, Senior Cycle, Tertiary), the cross-domain analysis, the
ducklake explorer, the lakehouse inspector, and the leabharlann
full-stack demo.
## Requirements
### Requirement: 5-stage education dashboards

The system SHALL provide Marimo notebooks for each of the 5 educational
stages (Aistear, Primary, Junior Cycle, Senior Cycle, Tertiary).

#### Scenario: Aistear dashboard renders

- **GIVEN** the `cianfhoghlaim/notebooks/dashboards/aistear.py` notebook
- **WHEN** the user navigates to `/dashboards/aistear`
- **THEN** the notebook renders with the Aistear theme data from
  DuckLake

### Requirement: Leabharlann full-stack demo

The system SHALL provide a Marimo notebook that visualises the
end-to-end leabharlann pipeline (1 UoG + 1 Zotero sample PDF →
BAML extraction → CocoIndex update → LanceDB insert → Cognee add →
DuckDB metadata write).

#### Scenario: Full-stack demo renders

- **GIVEN** the `cianfhoghlaim/notebooks/dashboards/leabharlann_full_stack_demo.py`
  notebook
- **WHEN** the user navigates to `/dashboards/leabharlann-full-stack-demo`
- **THEN** the notebook renders with the 5-step pipeline visualisation
  + the DuckDB result table for the last demo run

### Requirement: Cross-domain + lakehouse + ducklake dashboards

The system SHALL provide cross-domain, lakehouse, and ducklake
explorer notebooks.

#### Scenario: DuckLake explorer renders

- **GIVEN** the `cianfhoghlaim/notebooks/ducklake_explorer.py` notebook
- **WHEN** the user navigates to `/dashboards/ducklake`
- **THEN** the notebook renders with the table list from DuckLake
  and an interactive SQL query interface

### Requirement: Marimo on Cloudflare Workers + Container (WASM)

The system SHALL support deploying a marimo notebook as a
Cloudflare Worker wrapping a marimo Container via a Durable Object,
exposed over TCP 8080.

#### Scenario: Worker serves the marimo WASM bundle

- **GIVEN** a `Dockerfile` at `bonneagar/stacks/<surface>/marimo/`
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

- **GIVEN** a notebook `cianfhoghlaim/notebooks/<name>.py` with a
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

### Requirement: University courses dashboard

The system SHALL provide a marimo notebook at
`cianfhoghlaim/notebooks/_oideachais/university_courses.py`
served at `/dashboards/university-courses`. The notebook SHALL have
4 tabs (per the `oideachais-university-deep-extraction` spec):

1. **M.Sc. AI 25/26 modules** — pre-filtered to the user's upcoming programme
2. **All UoG courses** — searchable, filterable by school / NFQ level / ECTS
3. **Reading lists** — every reading-list item, with "Group by module" + "Group by ISBN-13" toggles
4. **Cross-archive** — the user's personal UoG artefacts joined to the matching scraped `CourseDescriptor` rows via the new Cognee edge

The notebook SHALL use `mo.sql(engine=md:oideachais)` (the MotherDuck
Postgres endpoint) for the underlying queries.

#### Scenario: User opens the M.Sc. AI 25/26 tab

- **WHEN** the user navigates to `/dashboards/university-courses` and clicks the "M.Sc. AI 25/26" tab
- **THEN** the notebook SHALL display a table of all 12+ modules in the M.Sc. AI 2025-26 programme
- **AND** each row SHALL show `module_code`, `module_title`, `ects`, `semester`, `lecturers[]`, `assessment_breakdown`, and a clickable `source_url`

#### Scenario: Cross-archive join renders

- **GIVEN** the `university_cross_archive` cognify pass has emitted the `CT511 → HDSD` and `MA335 → BScMS` edges
- **WHEN** the user opens the "Cross-archive" tab
- **THEN** the table SHALL show the user's CT511 + MA335 assignments on the left, the matching course descriptors on the right, and the `match_confidence` between them
- **AND** clicking a `course_descriptor.url` SHALL open the UoG programme page in a new tab

#### Scenario: Reading lists grouped by ISBN-13

- **WHEN** the user opens the "Reading lists" tab and selects the "Group by ISBN-13" radio button
- **THEN** the table SHALL be grouped by `isbn_13` (rows with the same ISBN are combined)
- **AND** each group SHALL show the count of modules referencing that book
- **AND** books appearing in ≥ 2 modules SHALL be highlighted (e.g. with a `📚` emoji prefix in the title)

### Requirement: BIEP Notebooks Wire to Local Lakehouse (ibis-first)

The system SHALL provide marimo notebooks for each of the 6 LC subjects
(Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science)
that default to the local `bunchloch-infra` lakehouse — not to
PlanetScale or Lance Cloud — and that prefer the ibis DataFrame API
over raw `duckdb` SQL, per the canonical KCG pattern documented in
`.agents/skills/ibis/SKILL.md` (entrypoint `ibis.duckdb.connect(uri)`).

#### Scenario: Math notebook reads from local Lakekeeper via ibis

- **GIVEN** the lakehouse stack (Garage + Lakekeeper + Lance) is up
  per Change 2
- **WHEN** the operator runs
  `marimo run cianfhoghlaim/notebooks/biep/mathematics.py`
- **THEN** the notebook's first data cell SHALL execute
      `conn = ibis.duckdb.connect("ducklake:postgres:host=lakehouse-postgres port=5432 user=lakekeeper password=… dbname=ducklake_oideachais")`
- **AND** it SHALL resolve
      `lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")`
- **AND** every data query SHALL be expressed as an ibis expression
      (`conn.table(...).filter(...).mutate(...).execute()`) rather
      than raw SQL strings
- **AND** the operation SHALL complete within 10 seconds against the
      empty Lakekeeper (returns 0-row DataFrames, not errors)
- **AND** the notebook SHALL be reproducible when the same operator
      swaps the URI to `md:oideachais` for the cloud-remote path
      (only one env var difference; no code change)

#### Scenario: ibis is the canonical entrypoint, not raw duckdb

- **WHEN** the 7 BIEP + lakehouse notebooks are grepped
- **THEN** every `import duckdb` is replaced by `import ibis`
- **AND** every `duckdb.connect(uri)` call is replaced by
  `ibis.duckdb.connect(uri)`
- **AND** zero raw `duckdb.connect(` calls remain in the notebooks
- **AND** the `ibis` skill is referenced in the per-notebook
      `## KCG patterns used` docstring

#### Scenario: All 6 BIEP subject notebooks pass the per-subject smoke

- **GIVEN** the lakehouse stack from Change 2 is healthy
- **WHEN** `opencode/scripts/run-biep-notebooks.sh` is run for all 6
  subjects
- **THEN** each notebook's first data cell completes within 2 seconds
  (no Lakekeeper timeouts)
- **AND** each notebook's first Lance cell lists the expected
  `oideachais.lc.<subject>.<level>_<lang>` tables
- **AND** zero notebooks leave "Pending" cells after 5 seconds

### Requirement: BIEP Notebooks — ibis-first refactor of all 11 files

All 11 BIEP subject + leabharlann notebooks under
`cianfhoghlaim/notebooks/04_biep_motherduck/` MUST use
`ibis.duckdb.connect()` as the canonical KCG entrypoint (per the
`wire-biep-notebooks-to-lakehouse` change spec). The system SHALL
reject any raw `duckdb.connect()` call or any `.fetchdf()` call
in these notebooks.

#### Scenario: ibis is the canonical entrypoint in all 11 BIEP notebooks

- **WHEN** the 11 BIEP notebooks are grepped
- **THEN** every `duckdb.connect(uri)` call SHALL be replaced by
  `ibis.duckdb.connect(uri)` (was 0; now ≥ 20 across 11 files)
- **AND** every `.fetchdf()` call SHALL be replaced by
  `.to_pandas()` (was 3; now 0)
- **AND** every `duckdb.sql("SET motherduck_token=...")` SHALL be
  removed (the ibis.duckdb.connect() URL form picks up the token
  automatically)
- **AND** the `ibis` skill SHALL be referenced in each notebook's
  `## KCG patterns used` docstring

#### Scenario: All 11 BIEP notebooks boot against the live lakehouse

- **WHEN** the lakehouse stack is up (per the upgrade-4-stacks-with-infisical
  change) AND the 11 BIEP notebooks are launched via `marimo run`
- **THEN** the ibis.duckdb.connect() connection SHALL succeed (or
  fall back to MotherDuck if the local lakehouse is unreachable)
- **AND** the first data cell SHALL complete within 10 seconds
  (returns 0-row DataFrames, not errors)
- **AND** the marimo reactive graph SHALL resolve without "Pending"
  cells after 5 seconds

## Cross-references

- [`cianfhoghlaim/notebooks/`](../../cianfhoghlaim/notebooks/) (the 11 Marimo notebooks)
- [`cianfhoghlaim/notebooks/dashboards/`](../../cianfhoghlaim/notebooks/dashboards/) (the dashboard subdir)
- [`.agents/skills/marimo/SKILL.md`](../../.agents/skills/marimo/SKILL.md)
- [`.agents/skills/build-notebook/SKILL.md`](../../.agents/skills/build-notebook/SKILL.md)
- [`openspec/specs/oideachais-leabharlann/spec.md`](oideachais-leabharlann/spec.md) (the upstream pipeline)
