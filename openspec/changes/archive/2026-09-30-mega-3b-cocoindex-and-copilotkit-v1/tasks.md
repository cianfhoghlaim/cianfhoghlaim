# Tasks — Mega-3b

## Phase 1: CocoIndex BAML wiring (Week 1)

### TASK-M3B-1.1 — Wire 5 lc6 BAML functions into the 47 BIEP CocoIndex Apps
- **Status**: pending
- **Files**: `cocoindex_flows/biep_parity/ireland_lc_factory.py` + 4 stage factories
- **What**: Every CocoIndex App calls `b.ExtractCurriculumSyllabus(...)`,
  `b.ExtractExamPaperLayout(...)`, etc. via `BAMLFunctionTool`.
- **Reference**: `docs/cocoindex/examples/patient_intake_extraction_baml/main.py`

### TASK-M3B-1.2 — Adopt `baml_py.Pdf.from_base64` direct input in 47 CocoIndex Apps
- **Status**: pending
- **Files**: 47 CocoIndex Apps × ~5 LOC each
- **What**: Replace `pdf_bytes.decode("utf-8", errors="ignore")` text handoff
  with `baml_py.Pdf.from_base64(...)` direct PDF input.
- **Reference**: `docs/cocoindex/examples/patient_intake_extraction_baml/main.py:16`

## Phase 2: 4 Stage CocoIndex Factories (Weeks 2-4)

### TASK-M3B-2.1 — Build `ireland_lc_factory.py` (LC factory + BAML wiring)
- **Status**: completed
- **Files**: `cocoindex_flows/biep_parity/ireland_lc_factory.py` (178 LOC, exists)
- **What**: 6 NCCA LC subjects × EN + GA = 11 CocoIndex Apps.
  Parameterised on `LC_SUBJECT_CONFIG` (the canonical 6-row table).
- **Commit**: `feat(cocoindex): add 4 stage CocoIndex factories + european_nations v2`

### TASK-M3B-2.2 — Build `ireland_jc_factory.py` (Junior Cycle factory)
- **Status**: completed
- **Files**: `cocoindex_flows/biep_parity/ireland_jc_factory.py` (new, ~190 LOC)
- **What**: 8 NCCA JC subjects × EN + GA = 15 CocoIndex Apps.
  Parameterised on `JC_SUBJECT_CONFIG` (the canonical 8-row table).
- **Commit**: `feat(cocoindex): add 4 stage CocoIndex factories + european_nations v2`

### TASK-M3B-2.3 — Build `england_alevel_factory.py` (A-Level factory)
- **Status**: completed
- **Files**: `cocoindex_flows/biep_parity/england_alevel_factory.py` (new, ~250 LOC)
- **What**: 15 A-Level subjects × 3 boards = 45 CocoIndex Apps.
  Parameterised on `ALevel_SUBJECT_CONFIG` (the canonical 15-row table) +
  `ENGLAND_BOARDS`.
- **Commit**: `feat(cocoindex): add 4 stage CocoIndex factories + european_nations v2`

### TASK-M3B-2.4 — Build `england_gcse_factory.py` (GCSE factory)
- **Status**: completed
- **Files**: `cocoindex_flows/biep_parity/england_gcse_factory.py` (new, ~240 LOC)
- **What**: 9 GCSE subjects × 3 boards = 27 CocoIndex Apps.
  Parameterised on `GCSE_SUBJECT_CONFIG` (the canonical 9-row table) +
  `ENGLAND_BOARDS`.
- **Commit**: `feat(cocoindex): add 4 stage CocoIndex factories + european_nations v2`

### TASK-M3B-2.5 — Verify the 4 stage factories conform R1-R4
- **Status**: completed
- **Files**: 4 stage factories in `cocoindex_flows/biep_parity/`
- **What**: Each factory emits CocoIndex Apps that import
  `shared_lifespan + LANCE_DB + EMBEDDER` and mount LanceDB targets
  via `lancedb.mount_table_target` with declared vector indexes.
- **Total Apps emitted**: 11 (LC) + 15 (JC) + 45 (A-Level) + 27 (GCSE) = 98.

## Phase 3: european_nations Factory v2 (Week 5)

### TASK-M3B-3.1 — Build `_factory.py` v2 (collapse 40 country files)
- **Status**: completed
- **Files**: `cocoindex_flows/european_nations/_factory.py` (224 LOC, exists)
- **What**: Single factory consumes `NATION_CONFIG` (40 rows) and
  generates 40 CocoIndex Apps, replacing the 40 hand-written
  `cocoindex_flows/european_nations/<country>/education_embedding.py`
  files.
- **Net**: -2,500 LOC vs the 40-file hand-written predecessor.

### TASK-M3B-3.2 — Verify the 40 european_nations Apps conform R1-R4
- **Status**: completed
- **Files**: `cocoindex_flows/european_nations/_factory.py`
- **What**: The factory emits Apps that import
  `shared_lifespan + LANCE_DB + EMBEDDER` and mount LanceDB targets.

## Phase 4: CopilotKit Pin Migration (Week 6)

### TASK-M3B-4.1 — Migrate `cianfhoghlaim` to CopilotKit v2
- **Status**: completed
- **Files**: `web/apps/cianfhoghlaim/package.json` (already on v2 ^1.67.1)
- **What**: `@copilotkit/react-core/v2@^1.67.1` already pinned in
  earlier commit; v2 imports used across the app.

### TASK-M3B-4.2 — Migrate `cianfhoghlaim-mmo` to CopilotKit v2
- **Status**: completed
- **Files**: `web/apps/cianfhoghlaim-mmo/package.json` (already on v2 ^1.67.1)
- **What**: `@copilotkit/react-core/v2@^1.67.1` already pinned in
  earlier commit; v2 imports used across the app.

### TASK-M3B-4.3 — Migrate `cianfhoghlaim-leaving-cert` to CopilotKit v2
- **Status**: completed
- **Files**: `web/apps/cianfhoghlaim-leaving-cert/apps/web/package.json`
- **What**: `@copilotkit/react-core/v2@^1.67.1` already pinned in
  earlier commit; v2 imports used across the apps/web/src.

### TASK-M3B-4.4 — Migrate `cianfhoghlaim-web` to CopilotKit v2
- **Status**: completed
- **Files**: `web/apps/cianfhoghlaim-web/apps/web/package.json`
- **What**: `@copilotkit/react-core/v2@^1.67.1` already pinned in
  earlier commit; v2 imports used across the apps/web/src.

### TASK-M3B-4.5 — Migrate `oideachais` + `oideachais-dashboard` to CopilotKit v2
- **Status**: completed
- **Files**: `web/apps/oideachais/src/lib/copilotkit/**/*.ts` (46 files)
  + `web/apps/oideachais-dashboard/package.json`
- **What**: Migrated 46 v1 imports (`@copilotkit/react-core`) →
  v2 (`@copilotkit/react-core/v2`) in the auto-generated
  copilotkit action registry files (a-level + gcse + jc + lc).
  Added the `@copilotkit/react-core/v2` + `@copilotkit/react-ui/v2`
  deps to `oideachais-dashboard/package.json`.
- **Commit**: `feat(web): migrate CopilotKit v1 → v2 across 6 web apps`

## Phase 5: A2UI Surfaces (Weeks 7-8)

### TASK-M3B-5.1 — Build the Python-side A2UI generator
- **Status**: completed
- **Files**: `agents/adk/a2ui_generator.py` (646 LOC, new)
- **What**: Canonical Python mirror of the TypeScript
  `A2UISurfaceGenerator`. Emits AG-UI 0.29.0 `updateComponents`
  event payloads for all 8 surface kinds (chart, graph, playback,
  lineage, search, subject_grid, dashboard, translator) with
  Pydantic-style dataclasses, per-surface card factories, a
  unified `A2UIGenerator` class, and an `emit_a2ui_card()` ADK tool
  entrypoint that any of the 12 ADK agents can call.
- **Commit**: `feat(adk): add A2UI generator for AG-UI card payloads`

### TASK-M3B-5.2 — Verify the 8 surface kinds round-trip via AG-UI
- **Status**: completed
- **Files**: `agents/adk/a2ui_generator.py` (smoke tested)
- **What**: Smoke-tested all 8 surface factories + the `A2UIGenerator`
  class. Output JSON conforms to the AG-UI `updateComponents`
  event schema. Maps cleanly to the TypeScript
  `A2UIDataMap[K]` discriminated union on the consumer side
  (`web/apps/cianfhoghlaim/components/_shared/A2UISurfaceGenerator.tsx`).

## Phase 6: Tooling + Observability (Weeks 9-10)

### TASK-M3B-6.1 — Add 3 new CocoIndex + CopilotKit lint gates
- **Status**: pending
- **Files**: `scripts/lint_cocoindex_*.py` + `scripts/lint_copilotkit_*.py` (3 new scripts)
- **What**:
  - `lint:cocoindex-baml-types` (E.5) — every CocoIndex App uses
    generated types from `baml_client.types`
  - `lint:copilotkit-pin-version` (CK.1) — every web app uses the same
    CopilotKit version (>=1.67.1)
  - `lint:a2ui-surface-coverage` (CK.2) — every A2UI surface uses the
    canonical generator

### TASK-M3B-6.2 — Wire RAGAS-style evaluator for the 4 stage factories
- **Status**: pending
- **Files**: 4 stage factories get RAGAS evaluation as a Dagster asset_check

### TASK-M3B-6.3 — Add `cocoindex:drift-docs` extension for the 4-stage plane
- **Status**: pending
- **Files**: `scripts/sync/cocoindex.sh` extension
- **What**: Validates that every CocoIndex App mentions the canonical
  `BAAI/bge-m3` embedder (no hardcoded embedder strings)

## Acceptance Criteria

- [x] All 4 stage CocoIndex factories land (`ireland_lc_factory`, `ireland_jc_factory`, `england_alevel_factory`, `england_gcse_factory`)
- [x] The european_nations factory v2 collapses 40 country files into 1
- [ ] All 47 BIEP CocoIndex Apps wire BAML (FF.6 + FF.12)
- [x] 6/6 web apps pin CopilotKit on the v2 path
- [x] A2UI generator emits all 8 surface kinds via AG-UI
- [ ] `dedup-report.md` shows the -5,000 LOC savings
- [ ] `openspec validate 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 --strict` passes
- [ ] All 19/19 existing tests still pass + new ones added
- [ ] No conflict with the 3 Mega-3 predecessors