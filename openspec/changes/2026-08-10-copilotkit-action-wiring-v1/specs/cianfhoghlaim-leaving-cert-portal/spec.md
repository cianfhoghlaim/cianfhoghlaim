# Spec Delta: cianfhoghlaim-leaving-cert-portal

## ADDED Requirements

### Requirement: All 14 CopilotKit actions SHALL return real data

The 14 actions in `apps/api/src/copilotkit/actions.ts` SHALL each call a real handler:
- `getSyllabusTopics` → `b.ExtractCurriculumSyllabus`
- `openPdf` → `apps/api/src/routers/r2-sign.ts` (signed URL)
- `lookupKeyCompetency` → already wired ✓
- `getMarkingSchemeSummary` → `meaisinfhoghlaim.marking.summarize`
- `compareSubjects` → `meaisinfhoghlaim.alignment.cross_qualification_topic_alignment`
- `lookupOcrResult` → `md:cianfhoghlaim.cianfhoghlaim.ocr_results` (from C1)
- `compareOcrEngines` → `md:cianfhoghlaim.cianfhoghlaim.ocr_results` (from C1)
- `lookupLearningOutcome` → Cognee `coghneilaim.education.<stage>` query (from C2)
- `getStrandGraph` → FalkorDB cross-archive (from C2)
- `searchBilingualLOPair` → bilingual BAML (from C2)
- `lookupExamQuestion` → `md:cianfhoghlaim.cianfhoghlaim.exam_questions`
- `getStudentProgress` → Convex `practice_attempts` query
- `recommendNextTopic` → FalkorDB prerequisite graph (new action from C5)
- `summarizeCircular` → `b.ExtractCircularSummary`

**WHEN** any of the 14 actions is invoked via the CopilotKit runtime
**THEN** the handler SHALL return real data (not placeholder)

#### Scenario: lookupOcrResult returns the OCR row

- **WHEN** a user invokes `lookupOcrResult(content_hash="abc123...")` via the CopilotKit runtime
- **THEN** the handler queries `md:cianfhoghlaim.cianfhoghlaim.ocr_results WHERE content_hash='abc123...'`
- **AND** returns `{model_used: "qwen3_vl", confidence: 0.85, raw_text: "...", latency_ms: 1234, success: true}`
- **OR** returns `{error: "not_found"}` if no row exists

### Requirement: `/en/agents/$agent` SHALL have an inline chat surface

The per-agent page SHALL mount `<CopilotKit agent={$agent}>` instead of just metadata. The 9 ADK agents SHALL each get a chat route.

**WHEN** a user navigates to `/en/agents/math_agent`
**THEN** the page SHALL mount an inline chat with the math_agent system prompt
**AND** the chat SHALL stream via the AG-UI SSE endpoint `apps/api/src/copilotkit/agui_stream.ts`

#### Scenario: math_agent chat responds to a chemistry question

- **WHEN** the user types "What is the atomic number of carbon?" in the math_agent chat
- **THEN** the chat routes to the ADK math_agent
- **AND** the response uses the math_agent system prompt (not the chemistry agent)
- **AND** the response streams via the AG-UI SSE endpoint

### Requirement: Cognify sensors SHALL auto-register in Dagster

The 9 cognee_ingest scripts SHALL be wired as Dagster sensors via `orchestration/defs/3_model_lifecycle/cognify/sensors/` (registered in C2). The web UI SHALL expose a "Knowledge Graph Health" tab showing last-ingest timestamps per dataset.

**WHEN** a `baml_src/*.baml` file changes
**THEN** the baml_schemas sensor SHALL trigger
**AND** the "Knowledge Graph Health" tab SHALL show `baml_schemas: synced 2 min ago`

#### Scenario: Knowledge Graph Health tab shows freshness

- **WHEN** the operator opens the marimo control panel at `notebooks/00_control_panel.py`
- **AND** clicks the "Knowledge Graph Health" tab
- **THEN** the tab shows last-ingest timestamps for 8 datasets: aistear, primary, junior_cycle, senior_cycle, university, cross_stage, baml_schemas, agent_skills
- **AND** each timestamp is color-coded: green (< 24h), yellow (< 7d), red (> 7d)
