# Spec Delta — CopilotKit AG-UI Runtime (Hono-mounted)

## MODIFIED Requirements

### Requirement: CopilotKit Runtime (server-side)

The system SHALL serve the CopilotKit AG-UI runtime from `oideachais/web/apps/api` at the `/api/copilotkit` path, streaming AG-UI events to the SPA via SSE.

#### Scenario: Runtime Mounted
- **GIVEN** `oideachais/web/apps/api/src/copilotkit/runtime.ts`
- **WHEN** `oideachais/web/apps/api/src/index.ts` is read
- **THEN** the Hono app mounts the runtime at `/api/copilotkit/*`
- **AND** the SPA's `<CopilotKit runtimeUrl="/api/copilotkit">` is now functional
- **AND** the runtime forwards requests to the Agno stage team resolved by `?stage=...&subject=...&language=...` query params

#### Scenario: AG-UI Event Stream
- **GIVEN** a user message from the SPA
- **WHEN** the runtime processes it
- **THEN** the Agno `team.run(stream=True, ...)` is invoked
- **AND** the response is wrapped in the 5 AG-UI event types: `text`, `tool_call`, `tool_result`, `agent_handoff`, `done` (per `docs/tuatha/AGENTS.md`)
- **AND** the events are streamed back to the SPA via SSE with the right Content-Type headers

#### Scenario: Stage Routing
- **GIVEN** a `?stage=senior_cycle&subject=mathematics&language=ga` query
- **WHEN** the runtime resolves the team
- **THEN** it calls `stage_router.ts` to get the right Agno `Team` instance
- **AND** the `OideachasChat` panel renders the streamed events with bilingual labels

## ADDED Requirements

### Requirement: Hono oRPC Endpoints per Stage
The system SHALL provide 13 new oRPC procedures in `oideachais/web/apps/api/src/routers/`.

#### Scenario: Per-Stage Routers
- **GIVEN** the new `apps/api/src/routers/` directory
- **WHEN** the new files are listed
- **THEN** they include:
  - `aistear.ts` — `aistear.getThemes`, `aistear.getLearningGoals`, `aistear.getNaionra(geo_bbox)`
  - `primary.ts` — `primary.getCurriculumArea`, `primary.getStrand`
  - `junior_cycle.ts` — `junior_cycle.getSpecs`, `junior_cycle.getCBATasks`
  - `senior_cycle.ts` — `senior_cycle.getExamPaper`, `senior_cycle.getMarkingScheme`, `senior_cycle.getSubjectRubric`, `senior_cycle.scoreEssay`
  - `tertiary.ts` — `tertiary.getCAOCourses`, `tertiary.getMatriculationRules`, `tertiary.getApplicationTimeline`, `tertiary.auditMatriculation`, `tertiary.predictPoints`
  - `baml.ts` — `baml.lazyExtract`, `baml.suggestUIComponents`
  - `i18n.ts` — `i18n.translate` (lazy EN↔GA via litellm/irish)

#### Scenario: Lazy BAML Extraction
- **GIVEN** a SPA request to open a past paper
- **WHEN** the SPA calls `baml.lazyExtract({subject, year, level, paper, session_id})`
- **THEN** the procedure checks the `exam_paper_extractions` LanceDB table for a cached result
- **AND** if not found, calls `b.LazyExtractExamPaper` and stores the result
- **AND** increments the `extraction_budget` Convex row for that session
- **AND** if the budget is exceeded, returns an error prompting the user to come back tomorrow

### Requirement: Better Auth + Convex Session Continuity
The system SHALL persist chat sessions in Convex so they survive container restarts and can be shared across devices.

#### Scenario: Session Persistence
- **GIVEN** a chat session starts in the SPA
- **WHEN** the Agno team is invoked
- **THEN** the session is created in the `subject_sessions` Convex table
- **AND** the `agno_session_id` is stored alongside the `user_id` and `subject`
- **AND** on subsequent messages, the session is looked up and continued
- **AND** the existing `SqliteDb` in `education_team.py:36` is replaced by a Convex-backed wrapper (or ConvexDB if Agno supports it natively)
