## ADDED Requirements

### Requirement: BIEP v2 cross-jurisdiction notebooks

The system SHALL provide 4 marimo notebooks at `notebooks/04_biep_v2/`:

- `00_biep_v2_overview.py` — single-pane view across LC + JC + A-Level + GCSE
  with cross-jurisdiction filter
- `01_junior_cycle_explorer.py` — drill into JC learning outcomes by strand
  + the 36 CBAs
- `02_england_explorer.py` — side-by-side AQA / OCR / Edexcel comparison
  for the same subject
- `03_ocr_ensemble_audit.py` — the full audit trail for any BAML-extracted
  record (PDF + Docling + Unstract + 2 VLM responses + RAGAS score + final
  BAML Pydantic + Langfuse trace link)

All 4 notebooks MUST:

- Use the **ibis-first contract** (`ibis.duckdb.connect("md:oideachais")` +
  `ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")`) — no raw
  `duckdb.connect()` per `british-isles-education-pipeline/spec.md` Requirement 5
- Have a `## KCG patterns used` docstring referencing the `ibis` and
  `marimo` skills
- Be PEP 723 inline-dependency notebooks (`@app.setup` + `@app.function`)
- Run on `marimo run <path> --headless` against the dev lakehouse

The system SHALL also provide:

- **3 Hono API endpoints** at `web/hono-api/src/routes/biep-v2/{lc,jc,england}.ts`
  that back the marimo notebooks with paginated JSON
- **1 TanStack Start public page** at `web/apps/cianfhoghlaim-web/src/routes/biep-v2/index.tsx`
  that embeds all 4 notebooks + 4 BIEP MotherDuck Dives as iframes

#### Scenario: 4 notebooks render against the live lakehouse

- **GIVEN** the lakehouse stack is up
  (`docker compose -f bonneagar/stacks/lakehouse/compose.yaml -f sidecar.yaml up -d`)
- **AND** the BIEP v2 LanceDB tables are populated from Changes 1 + 2 + 3
- **WHEN** the operator runs
  `marimo run notebooks/04_biep_v2/00_biep_v2_overview.py --headless`
- **THEN** the first 2 data cells execute the ibis-first contract
- **AND** the cross-jurisdiction filter UI shows the LC + JC + A-Level + GCSE
  cohorts
- **AND** every data query is expressed as an ibis expression

#### Scenario: Full audit trail in 03_ocr_ensemble_audit.py

- **GIVEN** the BIEP v2 ensemble asset `biiep_ocr_ensemble` has materialised
  a row with `record_id = "ireland.junior_cycle.english.en.2026.Q1.q1"`
- **WHEN** the operator opens `03_ocr_ensemble_audit.py` and selects that record
- **THEN** all 8 panels render:
  1. Source PDF page (from `s3://garage/cianfhoghlaim/junior_cycle/english/en/2026/Q1.pdf#page=1`)
  2. Docling DocTags XML (from `.docling_doctags`)
  3. Unstract JSON (from `.unstract_json`)
  4. qwen3-vl-8b raw response (from `.qwen3_vl`)
  5. gemma-4-26B-A4B raw response (from `.gemma4`)
  6. RAGAS `biiep_extraction_consensus` score bar chart
  7. Final BAML Pydantic object (the `.voted_canonical` row)
  8. Langfuse trace link (deep-link to the trace)
- **AND** the audit trail matches the user's chosen view surface strategy

#### Scenario: ibis is the canonical entrypoint, not raw duckdb

- **WHEN** the 4 BIEP v2 notebooks are grepped for `import duckdb` or
  `duckdb.connect`
- **THEN** 0 matches — every `duckdb.connect(uri)` is replaced by
  `ibis.duckdb.connect(uri)`
- **AND** every query is expressed as an ibis expression rather than raw
  SQL strings
