# centralized-schema-registry Specification

## Purpose
TBD - created by archiving change 2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1. Update Purpose after archive.
## Requirements
### Requirement: BAML is the single source of truth for all structured data shapes

The system SHALL treat BAML (`baml_src/**/*.baml`) as the single
source of truth for all structured data shapes (Pydantic classes,
Zod schemas, DuckDB tables). No Python file SHALL declare a Pydantic
class that mirrors a BAML class with the same field names.

#### Scenario: BAML class declarations are the canonical types

- **GIVEN** the 838 BAML class definitions across 320 `.baml` files
- **WHEN** the operator runs `python3 -c "from cianfhoghlaim.baml_client.types import *; print(len(dir()))"`
- **THEN** the output is `>= 819` (819 generated Pydantic classes +
  some dunders)
- **AND** the 96 hand-written Pydantic duplicates in
  `dlt_sources/british_isles/ireland/education/subjects/<subject>/schema.py`
  have been deleted or replaced with `from cianfhoghlaim.baml_client.types import ...`

#### Scenario: Pydantic classes match BAML classes field-by-field

- **GIVEN** the BAML class `MathFormativeItem` at
  `baml_src/british_isles/ireland/education/subjects/qpack_mathematics.baml`
- **WHEN** the operator runs
  `python3 -c "from cianfhoghlaim.baml_client.types import MathFormativeItem; m = MathFormativeItem(...); print(m.model_dump())"`
- **THEN** the output matches the BAML schema field-by-field
- **AND** no Python file in `dlt_sources/` declares a `MathFormativeItem`
  class that mirrors the BAML class

#### Scenario: 96 hand-written Pydantic duplicates are removed

- **GIVEN** the 8 `dlt_sources/.../subjects/<subject>/schema.py` files
  (mathematics, chemistry, computer_science, gaeilge, english,
  geography, history, applied_mathematics) each declaring 12 Pydantic
  classes
- **WHEN** the operator runs
  `grep -r "class.*BaseModel" dlt_sources/british_isles/ireland/education/subjects/`
- **THEN** the output contains zero `BaseModel` declarations
- **AND** the `schema.py` files are either deleted or contain only
  re-export statements (`from cianfhoghlaim.baml_client.types import ...`)

### Requirement: BAML TypeScript codegen activated; baml_client_ts/ is generated on every `mise run baml:generate`

The system SHALL enable BAML TypeScript codegen so that web apps can
`import { z } from "@baml/..."` (or path-relative) and consume
Zod-compatible schemas generated from BAML. The TypeScript codegen
output directory SHALL be `baml_client_ts/` at the repo root.

#### Scenario: mise run baml:generate populates both clients

- **GIVEN** `baml_src/baml.toml` declares
  `[generators.lang_ts] output_type = "typescript" output_dir = "../baml_client_ts"`
- **WHEN** the operator runs `mise run baml:generate`
- **THEN** `baml_client_ts/` is populated with at minimum `index.ts`,
  `types.ts`, `async_client.ts` (~3 MB total)
- **AND** `baml_client/` is also populated (Python Pydantic)

#### Scenario: Web apps import from baml_client_ts

- **GIVEN** the `baml_client_ts/` directory populated
- **WHEN** the operator updates
  `web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/bi-ep.gen.ts`
  to `export * from "../../../../../../baml_client_ts"`
- **THEN** the web app builds green (`bun run build` in
  `web/apps/cianfhoghlaim-leaving-cert/`)
- **AND** the bi-ep.gen.ts file becomes a ~10-line re-export
  (was 671 LOC of DuckDB-introspection-derived Zod)

#### Scenario: Zod schemas match BAML classes field-by-field

- **GIVEN** the BAML class `MathFormativeItem` and the generated
  TypeScript Zod schema `MathFormativeItem` at `baml_client_ts/types.ts`
- **WHEN** the operator imports both in a TypeScript file and runs
  `MathFormativeItem.parse({...})` with valid data
- **THEN** the parse succeeds
- **AND** the schema matches the BAML class field-by-field

### Requirement: 96 hand-written Pydantic duplicates are removed

The system SHALL replace the 8 `dlt_sources/.../subjects/<subject>/schema.py`
files with `from cianfhoghlaim.baml_client.types import ...` imports.
The 96 hand-written Pydantic classes (8 subjects × 12 classes) are
removed.

#### Scenario: Per-subject schema.py replaced with BAML imports

- **GIVEN** the 8 `dlt_sources/.../subjects/<subject>/schema.py` files
  (mathematics, chemistry, computer_science, gaeilge, english,
  geography, history, applied_mathematics)
- **WHEN** the operator reads any of the 8 files
- **THEN** the file is either deleted OR contains only re-export
  statements like:
  ```python
  from cianfhoghlaim.baml_client.types import (
      MathBilingualText, MathEvidenceLink, MathNCCALearningOutcome,
      MathTopicArea, MathNCCALevel, MathFormativeItemType,
      MathFeedbackChannel, MathFormativeItem, MathFormativeItemAttempt,
      MathScoreBreakdown, MathQuestPack, MathQuestPackValidation,
  )
  ```
- **AND** the file does NOT contain any `class X(BaseModel):` declarations
  for the 12 mirrored BAML classes

#### Scenario: Downstream consumers use the generated Pydantic

- **GIVEN** any Dagster asset or DLT resource that previously imported
  from `dlt_sources.british_isles.ireland.education.subjects.<subject>.schema`
- **WHEN** the operator runs `mise run py:typecheck`
- **THEN** the imports resolve through the canonical
  `from cianfhoghlaim.baml_client.types import ...` path
- **AND** the exit code is `0`

### Requirement: Central DuckDB schema introspection view

The system SHALL provide a `notebooks/_shared/schema.py` module with
5 helpers:

1. `schema_introspect(conn) -> list[dict]` — every BIEP DuckDB table
   + every LanceDB table + every BAML class as `{table_name,
   schema_name, column_name, column_type, source: "duckdb" | "lance"
   | "baml"}`
2. `schema_introspect_table(conn, table_name) -> list[dict]` — the
   canonical column metadata for any BIEP table
3. `list_dlt_sources() -> list[dict]` — all 920 `@dlt.source`
   decorated functions + their primary keys + their destinations
4. `list_cocoindex_apps() -> list[dict]` — all 472 CocoIndex Apps +
   their LanceDB mount targets + their embedders
5. `list_baml_classes() -> list[dict]` — all 838 BAML classes + their
   parent BAML files + their clients

#### Scenario: schema_introspect returns every BIEP table

- **GIVEN** the BIEP MotherDuck + DuckLake lakehouse at
  `md:cianfhoghlaim` populated with the 24 BIEP tables + the per-
  jurisdiction cohort tables + the leabharlann tables
- **WHEN** the operator runs
  `python3 -c "from notebooks._shared.schema import schema_introspect; from notebooks._shared.db import connect_md; print(len(schema_introspect(connect_md())))"`
- **THEN** the output is `>= 200` (24 BIEP tables × ~8 columns + 40+
  per-jurisdiction cohort tables + LanceDB + BAML)

#### Scenario: list_dlt_sources returns every DLT source

- **GIVEN** the `dlt_sources/` directory with 920 `@dlt.source`
  decorated functions
- **WHEN** the operator runs
  `python3 -c "from notebooks._shared.schema import list_dlt_sources; print(len(list_dlt_sources()))"`
- **THEN** the output is `>= 920`

#### Scenario: list_cocoindex_apps returns every CocoIndex App

- **GIVEN** the `cocoindex/` directory with 472 Apps (94 explicit +
  378 factory-generated)
- **WHEN** the operator runs
  `python3 -c "from notebooks._shared.schema import list_cocoindex_apps; print(len(list_cocoindex_apps()))"`
- **THEN** the output is `>= 472`

#### Scenario: list_baml_classes returns every BAML class

- **GIVEN** the 838 BAML class definitions across 320 `.baml` files
- **WHEN** the operator runs
  `python3 -c "from notebooks._shared.schema import list_baml_classes; print(len(list_baml_classes()))"`
- **THEN** the output is `>= 838`

### Requirement: Auto-derive Pydantic from BAML via baml_client.b

The system SHALL provide an auto-derive hook that emits the Pydantic
v2 models from the canonical BAML `class` declarations at
`baml_src/`. The hook SHALL be invoked via `mise run baml:derive-pydantic`
and SHALL produce the Pydantic models in `baml_client/baml_client/basalt/`.

#### Scenario: Pydantic models are auto-derived from BAML

- **GIVEN** a new BAML `class Foo { ... }` is added to `baml_src/`
- **WHEN** the operator runs `mise run baml:derive-pydantic`
- **THEN** the corresponding Pydantic `class Foo(BaseModel): ...` SHALL
  appear in `baml_client/baml_client/basalt/`
- **AND** the Pydantic model SHALL have the same field names + types
  as the BAML class

