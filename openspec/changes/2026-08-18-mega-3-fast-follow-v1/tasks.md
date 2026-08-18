# Tasks — Mega-3 Fast-Follow

## Phase A: Build the 5 Integration Helpers (1 week)

### TASK-FF.1 — Build `BAMLFunctionTool`
- **Status**: pending
- **Files**: `agents/integrations/baml_function_tool.py` (~200 LOC)
- **What**: Wrap any BAML `async def` as a `FunctionTool`. The helper auto-detects the BAML function from `baml_client.async_client.b` and exposes it as a Google ADK `FunctionTool` with the right schema.
- **Replaces**: 18 hand-written `FunctionTool` wrappers in `agents/tools/*.py` (-1,200 LOC)
- **Reference**: `agents/meaisinfhoghlaim/agents/adk/litellm_agent.py` (canonical LiteLlm wrapper pattern)

### TASK-FF.2 — Build `marimo_baml`
- **Status**: pending
- **Files**: `notebooks/_shared/marimo_baml.py` (~200 LOC)
- **What**: Expose `b.Extract*` as `mo.ui.chat` + `mo.ai.llm`. The helper imports the BAML client and wraps each function as a chat handler.
- **Replaces**: 19 `setup_biep_registry_header` call sites + BAML function duplication in notebooks (-400 LOC)
- **Reference**: `docs/marimo-examples/examples/ai/chat/openai_example.py` (the canonical marimo chat pattern)

### TASK-FF.3 — Build `agent_ui_bridge.py`
- **Status**: pending
- **Files**: `agents/integrations/agent_ui_bridge.py` (~300 LOC)
- **What**: Full port of `ag-ui-adk.ADKAgent` + `CopilotKitRuntime`. Wires any `LlmAgent` to CopilotKit's AG-UI protocol.
- **Replaces**: 6 `BuiltInPlanner` boilerplate patterns (-150 LOC)
- **Reference**: `docs/copilotkit/examples/showcases/adk-dashboard/agent/agent.py`

### TASK-FF.4 — Build `marimo_to_copilotkit.py`
- **Status**: pending
- **Files**: `notebooks/_shared/marimo_to_copilotkit.py` (~200 LOC)
- **What**: Mounts every marimo notebook as a CopilotKit tool. Uses `mo.ui.chat` + `mo.ai.llm` to expose notebook functions.
- **Replaces**: 4 component fetch patterns (-300 LOC)
- **Reference**: `docs/copilotkit/examples/showcases/multi-agent-canvas/agent/`

### TASK-FF.5 — Build `cocoindex_query_api.py`
- **Status**: pending
- **Files**: `cocoindex/_shared/cocoindex_query_api.py` (~250 LOC)
- **What**: Every CocoIndex App exposes a `search(query, top_k=5) -> List[Chunk]` Python closure. The closure wraps `lancedb.Table.search` with the canonical embedder.
- **Replaces**: 47 ad-hoc `lancedb.connect(CIANFHOGHLAIM_LANCEDB_URL)` calls (-800 LOC)
- **Reference**: `docs/cocoindex/examples/text_embedding_lancedb/main.py` (the query demo)

## Phase B: Wire the Helpers (3 days)

### TASK-FF.6 — Wire 5 lc6 BAML functions into 47 BIEP CocoIndex Apps
- **Status**: pending
- **Files**: `cocoindex/biep_parity/ireland_lc_factory.py` + 6 per-subject files
- **What**: Each CocoIndex App calls `b.ExtractCurriculumSyllabus(...)`, `b.ExtractExamPaperLayout(...)`, etc. via the BAMLFunctionTool.
- **Replaces**: Direct LLM calls in CocoIndex (duplicated logic)
- **Reference**: `docs/cocoindex/examples/patient_intake_extraction_baml/main.py`

### TASK-FF.7 — Wire 12 ADK agents as `CopilotRuntime.agents`
- **Status**: pending
- **Files**: `web/apps/cianfhoghlaim/app.config.ts` + 12 routes
- **What**: Each ADK agent is registered as `CopilotRuntime.agents[name]` so the CopilotKit UI can route to it.
- **Replaces**: Manual AG-UI bridges (-500 LOC)
- **Reference**: `docs/copilotkit/examples/showcases/deep-agents/agent/agent.py`

### TASK-FF.9 — Wire 6 LC-subject BAML functions as `curriculum_agent`'s tools
- **Status**: pending
- **Files**: `agents/adk/curriculum_agent.py` (~50 LOC)
- **What**: `curriculum_agent` registers `ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`, `ExtractMarkingScheme`, `ExtractCrossLinguistic`, `ExtractSyllabusDiagram`, `ExtractTopic` as tools via `BAMLFunctionTool`.
- **Replaces**: Hand-written `FunctionTool` wrappers (-300 LOC)
- **Reference**: `agents/tools/curriculum_search.py`

### TASK-FF.11 — Wire 4-path OCR ensemble BAML into CocoIndex
- **Status**: pending
- **Files**: `cocoindex/british_isles/england/education/ensembled_extraction.py` (~120 LOC)
- **What**: The 4-path ensemble becomes a single BAML function with `spawn` blocks (per Plan 1 A.1) wrapped as a CocoIndex App.
- **Replaces**: Sequential Python orchestration
- **Reference**: `docs/baml-demos/baml-deep-research-demo/main.py` (the spawn pattern)

### TASK-FF.12 — Adopt `baml_py.Pdf.from_base64` direct input
- **Status**: pending
- **Files**: 47 CocoIndex Apps × ~5 LOC each
- **What**: Replace `pdf_bytes.decode("utf-8", errors="ignore")` text handoff with `baml_py.Pdf.from_base64(...)` direct PDF input.
- **Replaces**: Embed→string→BAML handoff
- **Reference**: `docs/cocoindex/examples/patient_intake_extraction_baml/main.py:16`

## Phase C: Dedup Wins (2 days)

### TASK-FF.13 — Build `cocoindex/subjects/_factory.py`
- **Status**: pending
- **Files**: `cocoindex/subjects/_factory.py` (~300 LOC)
- **What**: Collapse 4 hand-written files (`lc_subject_embedding.py` 290 + `junior_cycle_embedding.py` 213 + `education_subject_embedding.py` 69 + `cross_subject_competency_embedding.py` 230 = 804 LOC) into 1 factory with `SUBJECT_CONFIG` parameter table.
- **Replaces**: 804 LOC (-504 LOC net after adding the factory)
- **Reference**: `cocoindex/biep_parity/ireland_lc_factory.py` (the canonical factory pattern)

### TASK-FF.14 — Delete 13 `cocoindex/biep_parity/*_education_embedding.py` shims
- **Status**: pending
- **Files**: 13 shim files
- **What**: Delete the 6 `ireland_lc_*_embedding.py` shims (already replaced by `ireland_lc_factory.py`) + 7 jurisdiction shims (`en_*`, `ga_*`, `ni_*`, `sct_*`, `wls_*`, `isle_of_man_*`, `jersey_*`, `guernsey_*` — already replaced by `bi_factory.py`).
- **Removes**: 169 LOC
- **Reference**: `cocoindex/biep_parity/ireland_lc_mathematics_embedding.py:1` (the 1-line shim docstring confirms this)

### TASK-FF.16 — Build `baml_src/british_isles/_shared/qpack_template.baml`
- **Status**: pending
- **Files**: `baml_src/british_isles/_shared/qpack_template.baml` (~250 LOC)
- **What**: Collapse 8 `qpack_*.baml` files (`qpack_mathematics` 382 + `qpack_gaeilge` 345 + `qpack_chemistry` 342 + `qpack_history` 323 + `qpack_geography` 313 + `qpack_english` 307 + `qpack_computer_science` 290 + `qpack_applied_mathematics` 368 = 2,670 LOC) into 1 template with `subject` parameter.
- **Replaces**: 2,670 LOC (-1,670 LOC net after adding the template)
- **Reference**: `baml_src/british_isles/ireland/education/lc_extraction/curriculum_syllabus.baml` (the existing 14-LC-subject template pattern)

### TASK-FF.17 — Delete 13 `_legacy/grading/*.baml` files
- **Status**: pending
- **Files**: 13 files in `baml_src/british_isles/ireland/education/_legacy/grading/`
- **What**: Delete the 7 deprecated grading files (mathematics/chemistry/geography/english/gaeilge/computer_science + the 6 boards) — covered by the unified LC extraction.
- **Removes**: 350 LOC
- **Reference**: `baml_src/british_isles/ireland/education/_legacy/grading/README.md`

### TASK-FF.18 — Build `web/apps/cianfhoghlaim/components/_shared/FetchPanel.tsx`
- **Status**: pending
- **Files**: `web/apps/cianfhoghlaim/components/_shared/FetchPanel.tsx` (~80 LOC)
- **What**: A shared `FetchPanel` component that all 4 components (KnowledgeGraphPanel, PipelineStatus, RecentActivityFeed, SubjectAgentGrid) can use to fetch data from the Convex backend.
- **Replaces**: Duplicated `useState` + `useEffect` + `fetch` patterns (-300 LOC)
- **Reference**: `web/apps/cianfhoghlaim/components/KnowledgeGraphPanel.tsx`

## Phase D: Surface Adoption (1 day)

### TASK-FF.8 — Adopt A2UI Protocol for 12 ADK agents
- **Status**: pending
- **Files**: `web/apps/cianfhoghlaim/components/` + 12 A2UI surface files
- **What**: Replace hand-written chart/graph/playback/lineage surfaces with A2UI declarative surfaces.
- **Replaces**: Hand-written React components (-300 LOC)
- **Reference**: `docs/copilotkit/examples/showcases/adk-dashboard/agent/state.py` (the A2UI surface pattern)

## Phase E: Education Tour (1 day)

### TASK-FF.10 — Build `notebooks/00_baml_tour.py`
- **Status**: pending
- **Files**: `notebooks/00_baml_tour.py` (~300 LOC)
- **What**: An educative notebook demonstrating every BAML feature used by the BIEP v3 jurisdiction dashboards. Mirrors the `00_marimo_patterns_tour.py` pattern but for BAML.
- **Reference**: `notebooks/00_marimo_patterns_tour.py` (the canonical patterns tour)

## Acceptance Criteria

- [ ] All 5 helpers land (`agents/integrations/`, `notebooks/_shared/`, `cocoindex/_shared/`)
- [ ] All 12 crown jewels wire the helpers to the 47 CocoIndex Apps + 12 ADK agents + 2 web apps
- [ ] All 6 dedup wins land (-3,063 LOC removed this step, -8,833 net after adding the helpers)
- [ ] `dedup-report.md` shows the line-by-line savings
- [ ] `openspec validate 2026-08-18-mega-3-fast-follow-v1 --strict` passes
- [ ] All 19/19 existing tests still pass + new ones added
- [ ] No conflict with `2026-08-17-biep-v3-bring-up-v1` or `2026-08-17-hygiene-drift-cleanup-v1`