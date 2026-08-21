## ADDED Requirements

### Requirement: 4-stage BAML template architecture

The system SHALL provide 5 BAML templates under
`baml_src/british_isles/_shared/` that parameterise extraction
across the 4 education stages (Leaving Cycle + Junior Cycle +
A-Level + GCSE) plus the cross-stage qpack generator:

| Template | Stages | Replaces |
|:--|:--|:--|
| `lc_extraction_template.baml` | Leaving Cycle (14 subjects × EN + GA) | 6 `lc_extraction/*.baml` files |
| `junior_cycle_template.baml` | Junior Cycle (8 subjects × EN + GA) | 6 `junior_cycle/*.baml` files |
| `alevel_extraction_template.baml` | A-Level (15 subjects × 3 boards × EN) | 15 `a_level_extraction/*.baml` files |
| `gcse_extraction_template.baml` | GCSE (9 subjects × 3 boards × EN) | 9 `gcse_extraction/*.baml` files |
| `qpack_template.baml` | All 4 stages | 8 `qpack_*.baml` files |

Each template uses a `subject` parameter + `{% if subject == "x" %}`
conditional blocks to cover the per-subject variations.

#### Scenario: Each template covers its stage's subjects via {% if %} conditionals

- **GIVEN** the 14 LC subjects (mathematics, applied_mathematics, chemistry, physics, biology, geography, english, gaeilge, french, history, business, accounting, art, music, computer_science)
- **WHEN** the operator runs `baml-cli generate --from baml_src`
- **THEN** the 5 templates generate without errors
- **AND** each `Extract*` function in the templates handles every
  subject via `{% if %}` conditionals
- **AND** the `baml_client` module exposes the union of all template
  functions as `b.Extract<Stage>Subject(subject="<slug>", text=...)`

#### Scenario: 4-stage plane parity across BAML + CocoIndex + Marimo + ADK

- **GIVEN** the 4-stage plane architecture from
  `2026-08-18-mega-3-roadmap-v1`
- **WHEN** the operator runs `ccc:search "stage_template"` or
  inspects `baml_src/british_isles/_shared/`
- **THEN** the system shows 5 BAML templates
- **AND** (per Mega-3b) 4 CocoIndex factory files
- **AND** (per Mega-3c) 4 Marimo dashboard files
- **AND** (per Phase 7 of this change) 4 ADK agent files

### Requirement: BAML `spawn` + `await` for the 4-path OCR ensemble

The system SHALL use BAML `spawn` (BEP-034) and `await` to parallelise
the 4 paths in the OCR ensemble (`ensembled_extraction.baml`):
BAML + Unstract + qwen3-vl-8b + gemma-4.

The reason: per the BEP-034 spec, `spawn` runs the 4 paths
concurrently as green threads. The current sequential implementation
takes ~350s; the parallel implementation takes ~120s (3× speedup).

#### Scenario: The 4 paths run concurrently with graceful degradation

- **GIVEN** the `Run4PathEnsemble` BAML function with 4 `spawn` blocks
- **WHEN** the operator runs
  `python -c "from baml_client.async_client import b; out = await b.Run4PathEnsemble(pdf)"`
- **THEN** the 4 paths run concurrently as `spawn` blocks
- **AND** any path that fails is caught by `catch_all` and returns a
  `PathOutput { path: "<name>", schema_valid: false }`
- **AND** the wall-clock latency is < 130s (down from 350s sequential)

### Requirement: BAML `host.callable` for `run_lct6_query`

The system SHALL use BAML host callables (BEP-3571) to allow the
`run_lct6_query` function to accept typed Python closures for the
MotherDuck credentials + the chart-render surface.

The reason: per the baml-text-to-sql-demo pattern, host callables
let BAML own the SQL chart logic while Python owns the database
connection + the secrets in the connection string.

#### Scenario: run_lct6_query accepts host callables

- **GIVEN** the `run_lct6_query(introspect, execute, render_chart)` BAML function
- **WHEN** the operator passes
  `introspect=lambda: duckdb_conn.execute("SHOW TABLES").fetchall()`,
  `execute=lambda sql: duckdb_conn.execute(sql).fetchall()`,
  `render_chart=lambda df: altair.Chart(df).mark_bar().encode(...)`
- **THEN** the BAML function calls each closure mid-workflow and
  gets back typed values
- **AND** the secrets stay in Python (never in BAML)

### Requirement: BAML `catch` / `catch_all` for the 6 LC extractors

The system SHALL use BAML `catch` / `catch_all` in every `Extract*`
function in the 6 `lc_extraction/*.baml` files so that a single
malformed field degrades gracefully rather than aborting the
extraction.

The reason: per the baml-deep-research-demo pattern, `catch_all`
returns a fallback value instead of aborting the workflow.

#### Scenario: Every Extract* function has catch_all

- **WHEN** `mise run lint:baml-catch-coverage` runs
- **THEN** every `Extract*` function in
  `baml_src/british_isles/ireland/education/lc_extraction/*.baml`
  MUST have a `catch_all (_) { <fallback> }` block
- **AND** the lint returns `OK: 6/6 extractors covered`

### Requirement: BAML `render_null_as` for missing fields

The system SHALL use the BAML 0.223.0 `render_null_as` output format
option for the `source_pages`, `year`, `total_marks` fields across
the 6 LC extractor return types.

The reason: per the BAML 0.223.0 changelog, `render_null_as="-1"`
serialises missing fields as `-1` instead of `null`, which fixes the
schema-tearing issue when a PDF doesn't state page count.

#### Scenario: Missing fields render as -1

- **GIVEN** a `SyllabusDocument` with `source_pages=null` (the PDF
  doesn't state page count)
- **WHEN** the operator runs `baml-cli generate` and inspects the
  rendered output
- **THEN** the `source_pages` field renders as `-1` (per
  `render_null_as="-1"`)
- **AND** the DuckLake ingestion accepts the value without rejection

### Requirement: BAML intersection bounds for cross-jurisdiction types

The system SHALL use BAML intersection bounds `T extends Document +
Bilingual + HasMetadata` in `baml_src/british_isles/_cross/
multi_nation_curriculum.baml` to replace the 4 near-identical
extraction functions with 1 generic.

#### Scenario: Generic extraction function covers 4 jurisdictions

- **GIVEN** the 8 BI nations (Ireland + England + Scotland + Wales +
  Northern Ireland + Jersey + Guernsey + Isle of Man)
- **WHEN** the operator runs `b.ExtractNationCurriculum[T extends Document + Bilingual + HasMetadata](text="...")`
- **THEN** the generic function enforces all 3 bounds at compile
  time (per the 2026-08-01 intersection bounds feature)
- **AND** the function dispatches to the per-jurisdiction extractor
  based on the `T` parameter

### Requirement: BAML `image` / `pdf` multimodal inputs

The system SHALL use BAML `image` and `pdf` types as direct inputs
to the extraction functions in the 6-stage PDF pipeline (Stages 1-3)
instead of the embed→string→BAML handoff.

#### Scenario: Direct PDF input replaces text handoff

- **GIVEN** the BAML function `ExtractCurriculumSyllabus(intake_form: pdf)` at `baml_src/british_isles/ireland/education/pdfs/root_pdf_extraction.baml`
- **WHEN** the operator runs
  `pdf = baml_py.Pdf.from_base64(base64.b64encode(content).decode())`
- **THEN** the function accepts the direct PDF input
- **AND** no embed→string→BAML handoff is required (per the
  `patient_intake_baml/main.py` pattern)

### Requirement: BAML `@assert` test blocks for the qpack generators

The system SHALL use BAML `assert` statements in the qpack template
to validate that every generated NCCA LO code matches the canonical
pattern `LC-...-LO-\d+` (or the JC / A-Level / GCSE equivalent).

#### Scenario: Every generated qpack passes the LO code assertion

- **GIVEN** the qpack template with `assert.baml_lo_code matches /<stage>-<subject>-LO-\d+/`
- **WHEN** `baml-cli test` runs
- **THEN** the 8 NCCA JC qpack generators each have at least 1
  assertion that validates the LO code pattern
- **AND** a malformed LO code triggers a test failure