# British Isles Education Pipeline v2 (BIEP v2) Capability

## Purpose

`british-isles-education-pipeline-v2` (BIEP v2) is the v2 umbrella that
extends the BIEP v1 flagship (`british-isles-education-pipeline`) to cover
the full set of secondary-school curricula in the Republic of Ireland and
England:

- **Leaving Certificate (Ireland, EN+GA)** — the 6 LC priority subjects
  from BIEP v1, now extended with the Change 3 4-path OCR/VLM ensemble
- **Junior Cycle (Ireland, EN+GA)** — 18 NCCA subjects + 16 short courses +
  36 CBAs (the Change 1 promotion from DLT-only to full extraction)
- **A-Level (England, EN)** — 9 priority subjects × 3 awarding bodies
  (AQA + OCR + Edexcel) (the Change 2 England pipeline)
- **GCSE (England, EN)** — the same 9 subjects × 3 awarding bodies, at
  GCSE level (also Change 2)

The corresponding source code lives at:

- `baml_src/british_isles/ireland/education/lc_extraction/`
  + `baml_src/british_isles/ireland/education/junior_cycle/`
  + `baml_src/british_isles/england/education/`
- `dlt/british_isles/ireland/education/{leaving_cert,junior_cycle,lc_extraction,...}.py`
  + `dlt/british_isles/ireland/education/junior_cycle_subjects/`
  + `dlt/british_isles/england/education/subjects/`
- `cocoindex/subjects/*.py` (the 7 BIEP-v1 subject flows + 1 new JC flow)
  + `cocoindex/british_isles/england/{aqa,ocr,edexcel}_education_embedding.py`
- `orchestration/defs/2_materials/lc_extraction/`
  + `orchestration/defs/2_materials/junior_cycle/`
  + `orchestration/defs/2_materials/england_education/`
  + `orchestration/defs/2_materials/ocr_comparison/ensemble_comparison/`
- `notebooks/04_biep_v2/{00,01,02,03}_*.py` (the 4 new BIEP v2 notebooks)
- `bonneagar/stacks/unstract/workflow_data/{aqa_gcse_spec,ncca_jc_cba,sec_lc_marking}.json`
- `bonneagar/stacks/changedetection/monitors/{aqa,ocr,edexcel}_monitor.yaml`

## Background

The BIEP v1 flagship (`british-isles-education-pipeline/spec.md`) covers 6
LC subjects × 2 languages + gov.ie circulars — the v1 floor. The BIEP v2
extends to:

- The full 18-subject Junior Cycle (was DLT-only, becomes full BIEP)
- The 3 awarding bodies of England (was a thin scaffold, becomes full BIEP)
- The 4-path OCR/VLM ensemble with RAGAS voting (was single-path BAML,
  becomes ensemble of BAML + Unstract + qwen3-vl-8b + gemma-4-26B-A4B)
- The full audit trail marimo portal (was just the 6 BIEP subject
  notebooks, becomes 10 ibis-first notebooks across 4 jurisdictions)

The 5 sequential openspec changes that landed this v2 umbrella:

| Change | Status | Scope |
|:--|:--|:--|
| `2026-07-20-biep-v2-junior-cycle-extraction-v1` | ✅ archived | Junior Cycle full extraction |
| `2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1` | ✅ archived | England AQA + OCR + Edexcel |
| `2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1` | ✅ archived | OCR/VLM ensemble + RAGAS vote |
| `2026-07-23-biep-v2-marimo-portal-v1` | ✅ archived | 4 cross-jurisdiction notebooks |
| `2026-07-24-biep-v2-gov-uk-change-detection-v1` | ✅ archived | AQA/OCR/Edexcel change sensors |

## Requirements

### Requirement: 4-jurisdiction BIEP coverage

The system SHALL provide a full BIEP-grade pipeline for **4 jurisdictions**:

- Republic of Ireland Leaving Certificate (EN + GA) — 6 LC priority subjects
- Republic of Ireland Junior Cycle (EN + GA) — 18 subjects + 16 short courses + 36 CBAs
- England A-Level (EN, AQA + OCR + Edexcel) — 9 priority subjects × 3 boards
- England GCSE (EN, AQA + OCR + Edexcel) — 9 priority subjects × 3 boards

The corresponding source code SHALL be at:

- `baml_src/british_isles/<jurisdiction>/education/` per jurisdiction
- `dlt/british_isles/<jurisdiction>/education/` per jurisdiction
- `cocoindex/<jurisdiction>/<subject>_embedding.py` per subject
- `orchestration/defs/2_materials/<jurisdiction>/` per jurisdiction
- `notebooks/04_biep_v2/` for the cross-jurisdiction portal

#### Scenario: 4-jurisdiction mise run dagster:oideachais

- **WHEN** a teacher clicks "Materialize all" in the Dagster UI for the
  4-jurisdiction BIEP v2 pipeline
- **THEN** the L1 ingest + L2 BAML + L3 embed assets for all 4
  jurisdictions materialise within minutes
- **AND** the 4 MotherDuck Dives surface the topic coverage per jurisdiction
- **AND** the daily Flight re-runs BAML extraction on any new PDFs
- **AND** the 4 marimo notebooks at `notebooks/04_biep_v2/` render the
  cross-jurisdiction cohort

### Requirement: 4-path OCR/VLM ensemble with RAGAS voting

The system SHALL provide the canonical ensemble extractor at
`meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py` that runs **4 paths
in parallel** for any incoming PDF, lands each path's output in a
separate per-path DuckLake table, and votes the canonical row via the
RAGAS `biiep_extraction_consensus` metric:

- **Path 1** (BAML) — `Docling-serve` → text → BAML function
- **Path 2** (Unstract) — `Docling-serve` → Unstract workflow → JSON
- **Path 3** (qwen3-vl-8b) — page-level image → qwen3-vl-8b raw response
- **Path 4** (gemma-4-26B-A4B) — page-level image → gemma-4-26B-A4B raw response

Per-path DuckLake tables follow the convention
`cianfhoghlaim.education.british_isles.<jurisdiction>.<scope>.<subject>.<path>`:

- `.baml_canonical` (Path 1)
- `.unstract_json` (Path 2)
- `.qwen3_vl` (Path 3)
- `.gemma4` (Path 4)
- `.voted_canonical` (the RAGAS-voted result)

#### Scenario: 4-path ensemble on any of the 4 jurisdictions

- **GIVEN** any of the 4 jurisdiction pipelines (LC / JC / A-Level / GCSE)
  has a new PDF
- **WHEN** the `biiep_ocr_ensemble` Dagster asset materialises the row
- **THEN** all 4 paths run in parallel
- **AND** all 4 path outputs land in the per-jurisdiction per-path DuckLake
  table
- **AND** the RAGAS `biiep_extraction_consensus` metric ranks the 4 outputs
- **AND** the highest-scoring output lands in `...voted_canonical`
- **AND** the asset check `ragas_score >= 0.70` passes

### Requirement: Cross-jurisdiction marimo portal

The system SHALL provide 4 marimo notebooks at `notebooks/04_biep_v2/`:

- `00_biep_v2_overview.py` — single-pane view across LC + JC + A-Level + GCSE
- `01_junior_cycle_explorer.py` — JC drill-down
- `02_england_explorer.py` — AQA/OCR/Edexcel comparison
- `03_ocr_ensemble_audit.py` — the full audit trail for any BAML-extracted record

All 4 notebooks SHALL:

- Use the **ibis-first contract** (no raw `duckdb.connect()`)
- Render against the live lakehouse (`ibis.duckdb.connect("md:oideachais")` +
  `ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")`)
- Have a `## KCG patterns used` docstring referencing the `ibis` and
  `marimo` skills
- Run on `marimo run <path> --headless`

The system SHALL also provide:

- **3 Hono API endpoints** at `web/hono-api/src/routes/biep-v2/{lc,jc,england}.ts`
- **1 TanStack Start public page** at `web/apps/cianfhoghlaim-web/src/routes/biep-v2/index.tsx`

#### Scenario: Full audit trail in 03_ocr_ensemble_audit.py

- **WHEN** a researcher selects any BAML-extracted record in
  `03_ocr_ensemble_audit.py`
- **THEN** all 8 panels render:
  1. Source PDF page
  2. Docling DocTags XML
  3. Unstract JSON output
  4. qwen3-vl-8b raw response
  5. gemma-4-26B-A4B raw response
  6. RAGAS `biiep_extraction_consensus` score bar chart
  7. Final BAML Pydantic object
  8. Langfuse trace link

### Requirement: England ChangeDetection freshness guarantee

The system SHALL provide 3 ChangeDetection.io monitors (one per awarding
body) and 1 Dagster sensor that re-runs the BAML extraction on any
changed AQA / OCR / Edexcel specification.

The sensor MUST:

- Subscribe to the 3 ChangeDetection.io webhook endpoints
- Resolve to the per-board DAG asset key
- Trigger the `england_england_re_extraction_job`
- Emit a Langfuse trace event
- Write an audit row to `cianfhoghlaim.education.british_isles.england.changes`
- Fire Slack + email alerts

#### Scenario: AQA GCSE mathematics spec change re-runs the ensemble

- **WHEN** AQA publishes a new version of the GCSE Mathematics specification
- **THEN** the ChangeDetection.io `aqa_monitor.yaml` fires the webhook
- **AND** the Dagster sensor triggers the `england_england_re_extraction_job`
- **AND** the Change 3 4-path ensemble re-runs + RAGAS votes
- **AND** a Slack alert posts to `#kcg-biep-v2`
- **AND** an email alert posts to `kcg-curriculum@cianfhoghlaim.ie`

## Cross-references

- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the BIEP v1 flagship that this v2 umbrella subsumes
- [`ireland-primary-jc-dlt-baml`](../ireland-primary-jc-dlt-baml/spec.md) —
  the JC capability that v2 extends to full extraction
- [`cross-region-pipeline`](../cross-region-pipeline/spec.md) —
  the umbrella contract (DuckLake namespace, DLT path contract, partition contract)
- [`meaisinfhoghlaim-ocr-htr`](../meaisinfhoghlaim-ocr-htr/spec.md) —
  the 26-model 6-backend OCR/VLM registry that v2 extends (adds Docling +
  Unstract backends + ensemble consensus requirement)
- [`cianfhoghlaim-marimo-dashboards`](../cianfhoghlaim-marimo-dashboards/spec.md) —
  the marimo dashboard capability that v2 extends (adds 4 BIEP v2 notebooks)
- [`cianfhoghlaim-baml-schemas`](../cianfhoghlaim-baml-schemas/spec.md) —
  the BAML extraction library that v2 extends with 9 new BAML files
  (4 JC + 5 England)
- [`cianfhoghlaim-cocoindex-v1-migration`](../cianfhoghlaim-cocoindex-v1-migration/spec.md) —
  the R1–R4 v1 conformance contract the 4 new CocoIndex Apps obey
- [`dagster-5-layer-component-architecture`](../dagster-5-layer-component-architecture/spec.md) —
  the 5-layer Dagster component architecture that all 154 BIEP v2 assets obey
- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) —
  the 94 Docker Compose stacks catalogue that v2 extends (adds 3
  ChangeDetection monitors for England)
- [`upstream-package-monitoring`](../upstream-package-monitoring/spec.md) —
  the upstream-monitoring spec that v2 extends (adds BIEP v2 England sibling
  sensor)
- [`agent-observability`](../agent-observability/spec.md) —
  the observability stack (Langfuse + MLflow + RAGAS + Logfire) that v2
  wires the Slack/email alerts + RAGAS voting through
- [`agentic-frontend-frameworks`](../agentic-frontend-frameworks/spec.md) —
  the TanStack Start + CopilotKit + Hono + oRPC umbrella that v2 uses for
  the public web view
- `archive/2026-07-20-biep-v2-junior-cycle-extraction-v1/` — the Change 1 archive
- `archive/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/` — the Change 2 archive
- `archive/2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1/` — the Change 3 archive
- `archive/2026-07-23-biep-v2-marimo-portal-v1/` — the Change 4 archive
- `archive/2026-07-24-biep-v2-gov-uk-change-detection-v1/` — the Change 5 archive
- `docs/research/biiep_v2_umbrella_audit.md` *(authoritative cross-jurisdiction audit)*
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
- `.agents/skills/dagster/SKILL.md` — the 5-layer component architecture
- `.agents/skills/motherduck/SKILL.md` — MotherDuck Dives + Flights
- `.agents/skills/marimo/SKILL.md` — marimo notebook patterns
- `.agents/skills/ibis/SKILL.md` — the ibis-first contract
- `.agents/skills/tanstack-start/SKILL.md` — TanStack Start patterns
- `.agents/skills/hono/SKILL.md` — Hono API patterns
- `.agents/skills/change-detection/SKILL.md` — ChangeDetection.io patterns
- `.agents/skills/agent-observability/SKILL.md` — Langfuse + RAGAS observability
- `.agents/skills/ragas/SKILL.md` — RAGAS trace-based metrics
- `.agents/skills/mlflow/SKILL.md` — MLflow experiment tracking

## Migrated from

This v2 umbrella subsumes the v1 BIEP spec
([`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md))
for the 4 jurisdictions it covers. The v1 spec remains canonical for the
6-subject LC + gov.ie circulars floor; v2 is the umbrella on top.
