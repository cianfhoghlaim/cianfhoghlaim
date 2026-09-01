## ADDED Requirements

### Requirement: Canonical `StudyPlan` BAML schema

The oideachais-pipeline capability MUST expose a single
canonical `StudyPlan` BAML schema at
`baml_src/british_isles/_shared/study_plan.baml`. The schema
SHALL define:

- `StudyPlan` (top-level) — `weeks_plan: list[StudyPlanWeek]`,
  `milestones: list[StudyPlanMilestone]`,
  `kc_weights: dict[str, float]`,
  `recommended_past_papers: list[PastPaperRef]`,
  `bilingual: StudyPlanBilingual` (EN + GA fields for Gaeilge
  subject; EN only otherwise)
- `StudyPlanWeek` — `week_number: int`, `theme: str`,
  `theme_ga: str | None`, `marking_scheme_focus: list[str]`,
  `estimated_hours: float`, `lo_codes: list[str]`
- `StudyPlanMilestone` — `week: int`, `description: str`,
  `description_ga: str | None`, `assessment_type: Literal["quiz",
  "past_paper", "mock_orale", "essay"]`
- `PastPaperRef` — `year: int`, `paper_id: str`,
  `ncca_page_citation: int` (page number in the official NCCA
  PDF), `marking_scheme_page_citation: int`
- `GenerateStudyPlanAssets(subject: NCCASubjectSlug, lo_codes:
  list[str], duration_weeks: int, dialect: IrishDialect | None)
  -> StudyPlan` — the canonical generator callable from Python +
  TypeScript

The 6 legacy per-subject
`baml_src/british_isles/ireland/education/_legacy/web/<subject>_web.baml`
files SHALL be deleted once the canonical schema passes
`baml-cli test` for all 4 Phase 1 subjects (Chemistry,
Mathematics, Gaeilge, Computer Science).

#### Scenario: A student requests a 12-week study plan for LC Chemistry

- **GIVEN** the student is enrolled in LC Chemistry + has
  identified LO codes `LC-CHEM-3.1` + `LC-CHEM-3.2` + `LC-CHEM-4.5`
- **WHEN** the planner invokes `b.GenerateStudyPlanAssets(subject="chemistry", lo_codes=["LC-CHEM-3.1", "LC-CHEM-3.2", "LC-CHEM-4.5"], duration_weeks=12, dialect=null)`
- **THEN** the response SHALL contain exactly 12 `StudyPlanWeek` entries
- **AND** every `StudyPlanWeek.lo_codes` entry SHALL be a subset of the input `lo_codes`
- **AND** every `PastPaperRef.ncca_page_citation` SHALL point to a real page in the canonical `data/chemistry/marking/` PDF
- **AND** the response SHALL persist to the Convex `study_plans` table via `web/hono-api/src/routes/copilotkit/lc/chemistry.ts`

#### Scenario: A student requests a 16-week study plan for LC Gaeilge with Connacht dialect

- **GIVEN** the student is enrolled in LC Gaeilge + dialect
  preference is Connacht
- **WHEN** the planner invokes `b.GenerateStudyPlanAssets(subject="gaeilge", lo_codes=[...], duration_weeks=16, dialect="connacht")`
- **THEN** every `StudyPlanWeek.theme_ga` SHALL be populated (no null)
- **AND** every `StudyPlanMilestone.description_ga` SHALL be populated
- **AND** the response SHALL additionally produce an
  `OralStudyPlan` (per §B below) with `audio_segments[]` keyed
  by `StudyPlanWeek.week_number`

### Requirement: Canonical `OralStudyPlan` BAML schema (Phase 1 stub; Phase 6 fills)

The oideachais-pipeline capability MUST expose
`baml_src/british_isles/_shared/oral_study_plan.baml` with:

- `OralStudyPlan` — `audio_segments: list[OralStudySegment]`,
  `duration_min: float`, `voice_id: str`,
  `dialect: IrishDialect` (Connacht / Munster / Ulster / standard)
- `OralStudySegment` — `week_number: int`, `text: str`,
  `text_ga: str | None`, `estimated_duration_sec: float`,
  `tts_provider: Literal["chatterbox", "orpheus-tts-3b-ft",
  "facebook-mms-tts-gle"]`
- `GenerateOralStudyPlan(text_plan: StudyPlan, dialect: IrishDialect)
  -> OralStudyPlan` — the canonical generator (Phase 1 stubs
  the callable; Phase 6 wires the real TTS round-trip)

Phase 1 MUST author the schema + a callable stub that returns
an empty `audio_segments[]` with `dialect` echoed. Phase 6 MUST
replace the stub with a real Pipecat + Chatterbox dispatch.

#### Scenario: A Phase 1 stub returns an empty audio_segments list

- **GIVEN** `b.GenerateOralStudyPlan(text_plan, dialect="connacht")`
  is invoked during Phase 1 (before Phase 6 ships)
- **WHEN** the planner invokes the stub
- **THEN** the response SHALL contain `audio_segments=[]`
- **AND** `duration_min=0.0`
- **AND** `voice_id=""` (placeholder; Phase 6 fills)
- **AND** `dialect="connacht"` (echoed from input)

#### Scenario: A Phase 6 wired implementation produces real audio segments

- **GIVEN** the student requests a 12-week Connacht-dialect
  oral study plan for LC Gaeilge after Phase 6 ships
- **WHEN** the planner invokes `b.GenerateOralStudyPlan(text_plan, dialect="connacht")`
- **THEN** the response SHALL contain exactly 12 `OralStudySegment` entries
- **AND** every `OralStudySegment.week_number` SHALL be a subset of `text_plan.weeks_plan[].week_number`
- **AND** the `tts_provider` SHALL be `"facebook-mms-tts-gle"` for `dialect != "standard"` and `"chatterbox"` for `dialect == "standard"`
- **AND** the segments SHALL persist to the Convex `oral_study_plans` + `audio_segments` tables

### Requirement: Per-subject planner module exists

The oideachais-pipeline capability MUST expose
`agents/adk/subjects/lc/planner.py` with the
`generate_study_plan(parameters) -> StudyPlanResponse` callable.
The module MUST be importable via
`from agents.adk.subjects.lc.planner import generate_study_plan`
(per the import site in
`agents/adk/subjects/lc/<subject>.py::get_study_plan`).

The planner SHALL:

- Wrap `b.GenerateStudyPlanAssets(...)` from
  `baml_src/british_isles/_shared/study_plan.baml`
- Rehydrate the response into the Convex `study_plans` table
  via the Hono `/api/copilotkit/lc/<subject>` route
- Emit Langfuse spans under the `lc_study_plan` trace name
- Honour the per-subject `MODEL_REGISTRY.resolve("text_llm",
  "<subject>_primary")` resolution (the Primary alias per
  `2026-08-31-baml-primary-alias-and-fallback-v1`)

#### Scenario: Every per-subject ADK agent can import the planner

- **GIVEN** the planner module exists at
  `agents/adk/subjects/lc/planner.py`
- **WHEN** `pytest tests/test_adk_subject_actions.py -v` runs
- **THEN** all 4 Phase 1 subjects' `get_study_plan` action
  imports SHALL resolve (no `ImportError`)
- **AND** the action handler SHALL call `planner.generate_study_plan(...)`
- **AND** the response SHALL be returned via the Hono
  `POST /get_study_plan` route

### Requirement: Broken stubs are fixed (no `pass # TODO` or `{stub: true}` for Phase 1 subjects)

The oideachais-pipeline capability MUST NOT ship
`pass # TODO` bodies or `{stub: true}` responses in the
following Phase 1 surfaces:

- `agents/adk/voice_agent.py::process_audio()` — Phase 1 ships
  a wired Pipecat client stub that logs the round-trip
  (the real TTS arrives in Phase 6).
- `agents/_workflow_handlers.py::dispatch_study_plan` — Phase 1
  ships a real call to `planner.generate_study_plan`.
- `agents/api/routes/routes/search.py` — Phase 1 ships a real
  `MemoryRouter` import (the canonical RRF hybrid).
- `notebooks/10_biep_pipeline_lakehouse_semantic_01_search.py` —
  Phase 1 ships a real `MemoryRouter` re-export.
- `orchestration/defs/2_materials/lc_extraction/quest_pack_assets.py:326`
  — Phase 1 ships a call to consolidated
  `b.GenerateSubjectQuestPack(...)` (the qpack-template
  consolidated entry).
- `web/hono-api/src/routes/copilotkit/lc/{chemistry, mathematics,
  gaeilge, computer_science}.ts` `POST /get_study_plan` — Phase 1
  wires to `agents.adk.subjects.lc.planner`.
- `web/apps/oideachais/src/lib/copilotkit/lc/{chemistry,
  mathematics, gaeilge, computer_science}.ts` `get_study_plan`
  handler — Phase 1 wires to the same planner.
- `web/apps/oideachais/routes/lc/{chemistry, mathematics, gaeilge,
  computer_science}/study-plan.tsx` — Phase 1 ships a real
  `<StudyPlanCard>` A2UI surface (basic placeholder; Phase 2
  fills the full 11-component catalog).

#### Scenario: A grep for Phase 1 stub patterns returns zero matches

- **WHEN** a developer runs `rg -tpy -tts "pass # TODO|\\{stub:
  true\\}" agents/adk/subjects/lc/ web/hono-api/src/routes/copilotkit/lc/
  web/apps/oideachais/src/lib/copilotkit/lc/ orchestration/defs/2_materials/lc_extraction/`
- **THEN** zero matches SHALL appear for the 4 Phase 1 subjects
- **AND** the `agents/adk/voice_agent.py::process_audio()` body
  SHALL be a wired Pipecat client stub (not `pass`)

### Requirement: Convex schema includes study-plan tables

The oideachais-pipeline capability MUST extend
`web/packages/db/convex/schema.ts` with the Phase 1 tables:

- `study_plans` — `(id, user_id, subject, lo_codes,
  duration_weeks, dialect, weeks_plan_json, milestones_json,
  kc_weights_json, recommended_past_papers_json, created_at,
  langfuse_trace_id)`
- `quest_packs` — `(id, subject, stage, language, lo_codes,
  items_json, created_at)` (populated by the fixed
  `quest_pack_assets.py` Dagster asset)
- `oral_study_plans` — `(id, study_plan_id, dialect,
  duration_min, voice_id, audio_segments_json, created_at)`
  (Phase 1 schema; Phase 6 fills the audio)

The tables SHALL be additive — no existing table SHALL be
removed or renamed.

#### Scenario: Convex schema generates without errors

- **WHEN** a developer runs `cd web && bunx convex dev
  --once --configure new dashboard` after the schema is extended
- **THEN** the schema generation SHALL exit 0
- **AND** `study_plans` + `quest_packs` + `oral_study_plans`
  tables SHALL appear in the generated schema
- **AND** the existing `threads + messages + runs + users +
  agents + subject_caches + knowledge_graph_nodes` tables SHALL
  remain unchanged

### Requirement: 4 LC subjects ship end-to-end study plans (Phase 1 scope)

The oideachais-pipeline capability MUST ship end-to-end
study-plan generation for the 4 Phase 1 subjects:

- **Chemistry** — the showcase default
  (`JOURNEY_DEFAULT_SUBJECT=chemistry_lc`)
- **Mathematics** — the broadest student audience
- **Gaeilge** — the oral-first subject (Connacht / Munster /
  Ulster dialect dispatch)
- **Computer Science** — the newest NCCA LC subject

Each subject MUST expose:

- Per-subject `agents/adk/subjects/lc/<subject>.py` with the 13
  standard actions registered (incl. `get_study_plan`)
- Per-subject
  `web/apps/oideachais/routes/lc/<subject>/study-plan.tsx`
  mounting a `<StudyPlanCard>` A2UI surface
- Per-subject
  `web/hono-api/src/routes/copilotkit/lc/<subject>.ts`
  `POST /get_study_plan` wired to the planner
- Per-subject `notebooks/lc/<subject>.py` "study-plan demo"
  cell calling `planner.generate_study_plan(...)`

#### Scenario: A Chemistry student requests a 12-week study plan via the oideachais web surface

- **GIVEN** the student is on `oideachais/routes/lc/chemistry/study-plan`
- **WHEN** the student selects LO codes + clicks "Generate Study Plan"
- **THEN** the Hono `POST /get_study_plan` route SHALL invoke
  `planner.generate_study_plan(subject="chemistry", ...)`
- **AND** the response SHALL render in the `<StudyPlanCard>`
  A2UI surface within 5 seconds (median)
- **AND** the response SHALL persist to the Convex `study_plans`
  table
- **AND** a Langfuse trace SHALL appear under the `lc_study_plan`
  trace name

#### Scenario: A Gaeilge student requests an oral study plan with Connacht dialect

- **GIVEN** the student is on `oideachais/routes/lc/gaeilge/study-plan`
- **WHEN** the student selects LO codes + Connacht dialect + clicks "Generate Study Plan + Oral"
- **THEN** the planner SHALL invoke
  `b.GenerateStudyPlanAssets(subject="gaeilge", dialect="connacht", ...)`
- **AND** the planner SHALL additionally invoke
  `b.GenerateOralStudyPlan(text_plan, dialect="connacht")` (Phase 1 stub returns empty audio_segments)
- **AND** the response SHALL render in the `<StudyPlanCard>` +
  `<OralStudyPlayer>` A2UI surface (the latter is a basic
  placeholder in Phase 1)