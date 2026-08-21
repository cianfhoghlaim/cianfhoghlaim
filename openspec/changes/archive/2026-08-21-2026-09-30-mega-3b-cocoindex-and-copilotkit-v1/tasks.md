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

### TASK-M3B-2.1 — Build `ireland_jc_factory.py` (Junior Cycle factory)
- **Status**: pending
- **Files**: `cocoindex_flows/biep_parity/ireland_jc_factory.py` (~300 LOC, new)
- **What**: 8 NCCA JC subjects × EN + GA = 16 CocoIndex Apps.
  Parameterised on `JC_SUBJECT_CONFIG` (the canonical 8-row table).

### TASK-M3B-2.2 — Build `england_alevel_factory.py` (A-Level factory)
- **Status**: pending
- **Files**: `cocoindex_flows/biep_parity/england_alevel_factory.py` (~400 LOC, new)
- **What**: 15 A-Level subjects × 3 boards = 45 CocoIndex Apps.
  Parameterised on `ALEVEL_SUBJECT_CONFIG` (the canonical 15-row table).

### TASK-M3B-2.3 — Build `england_gcse_factory.py` (GCSE factory)
- **Status**: pending
- **Files**: `cocoindex_flows/biep_parity/england_gcse_factory.py` (~300 LOC, new)
- **What**: 9 GCSE subjects × 3 boards = 27 CocoIndex Apps.
  Parameterised on `GCSE_SUBJECT_CONFIG` (the canonical 9-row table).

### TASK-M3B-2.4 — Wire BAML into the existing `ireland_lc_factory.py`
- **Status**: pending
- **Files**: `cocoindex_flows/biep_parity/ireland_lc_factory.py`
- **What**: Add `b.Extract*` calls + BAMLFunctionTool wiring.
  (The factory already exists per the 2026-08-15 change.)

## Phase 3: european_nations Factory v2 (Week 5)

### TASK-M3B-3.1 — Build `_factory.py` v2 (collapse 40 country files)
- **Status**: pending
- **Files**: `cocoindex_flows/european_nations/_factory.py` (~500 LOC, rewrite)
- **What**: Delete the 40 hand-written `cocoindex_flows/european_nations/<country>/education_embedding.py`
  files. Replace with 1 factory that consumes `NATION_CONFIG` (40 rows).
  Generates 40 CocoIndex Apps.
- **Replaces**: ~3,000 LOC → 500 LOC net (-2,500 LOC)

### TASK-M3B-3.2 — Verify the 40 european_nations Apps conform R1-R4
- **Status**: pending
- **Files**: `mise run cocoindex:conformance`
- **What**: The factory generates Apps that import `shared_lifespan + LANCE_DB + EMBEDDER`.

## Phase 4: CopilotKit Pin Migration (Week 6)

### TASK-M3B-4.1 — Bump `cianfhoghlaim-mmo` to CopilotKit v2.0
- **Status**: pending
- **Files**: `web/apps/cianfhoghlaim-mmo/package.json`
- **What**: Replace `@copilotkit/react-core@^1.10.0` with
  `@copilotkit/react-core/v2@^1.67.1` + `@copilotkit/react-ui@^1.67.1`.
  Migrate v1.x patterns to v2.x (the createA2UIMessageRenderer +
  A2UIProvider pattern).
- **Replaces**: v1.10 API drift (-500 LOC)

### TASK-M3B-4.2 — Wire 12 ADK agents as `CopilotRuntime.agents`
- **Status**: pending
- **Files**: `web/apps/cianfhoghlaim/app.config.ts` + 12 routes
- **What**: Each ADK agent is registered as `CopilotRuntime.agents[name]`
  so the CopilotKit UI can route user messages to any of the 12 agents.

## Phase 5: A2UI Surfaces (Weeks 7-8)

### TASK-M3B-5.1 — Build the A2UI surface generator
- **Status**: pending
- **Files**: `web/apps/cianfhoghlaim/components/_shared/A2UISurfaceGenerator.tsx` (~250 LOC, new)
- **What**: 1 generator that takes a surface kind (chart, graph, playback,
  lineage, search) + structured data and renders the A2UI surface
  declaratively. Replaces 8 hand-written surface files (-600 LOC).

### TASK-M3B-5.2 — Migrate 4 existing components to use the A2UI generator
- **Status**: pending
- **Files**: `web/apps/cianfhoghlaim/components/{KnowledgeGraphPanel,PipelineStatus,RecentActivityFeed,SubjectAgentGrid}.tsx`
- **What**: Replace hand-written chart/graph implementations with
  A2UI surfaces driven by the canonical generator.

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

- [ ] All 4 stage CocoIndex factories land (`ireland_lc_factory`, `ireland_jc_factory`, `england_alevel_factory`, `england_gcse_factory`)
- [ ] The european_nations factory v2 collapses 40 country files into 1
- [ ] All 47 BIEP CocoIndex Apps wire BAML (FF.6 + FF.12)
- [ ] `cianfhoghlaim-mmo` CopilotKit pin is bumped to v2.0
- [ ] All 8 A2UI surfaces share 1 generator
- [ ] `dedup-report.md` shows the -5,000 LOC savings
- [ ] `openspec validate 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 --strict` passes
- [ ] All 19/19 existing tests still pass + new ones added
- [ ] No conflict with the 3 Mega-3 predecessors