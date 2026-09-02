## ADDED Requirements

### Requirement: 5 jurisdiction orchestrators invoke canonical Extract<Jurisdiction>SubjectSpec + materialise to Convex

The british-isles-education-pipeline capability MUST wire each of the
5 jurisdiction orchestrators at
`orchestration/defs/2_materials/{england,wales,scotland,
northern_ireland,isle_of_man}_education/<jur>_assets.py` to the
canonical BAML extraction function
`b.Extract<Jurisdiction>SubjectSpec(pdf_text, subject_slug, stage,
source_url)` defined in
`baml_src/british_isles/{en,wl,sc,ni,im}/education/<jur>_extraction.baml`
— **replacing** the prior `getattr(b, fn_name, None)` fallback which
silently produced `rows_extracted: 0`.

Each orchestrator MUST:

1. Read the canonical PDF via `pypdf` (the canonical LC PDF reader —
   the same one the `quest_pack_assets.py` module uses).
2. Invoke `b.Extract<Jurisdiction>SubjectSpec(pdf_text, subject_slug,
   stage, source_url)` and capture the typed
   `<Jurisdiction>SubjectSpec` row.
3. Materialise the result to the canonical Convex table
   `<jurisdiction>_subject_specs` (`england_subject_specs`,
   `wales_subject_specs`, `scotland_subject_specs`,
   `northern_ireland_subject_specs`, or
   `isle_of_man_subject_specs`) via
   `convex.ConvexClient.mutation(f"{table}:create", payload)`.
4. Surface the extracted/convex-written counts on the asset's return
   value (`baml_extractions`, `extracted_count`,
   `convex_written_count`).
5. Degrade gracefully — when BAML or Convex are unavailable, the
   asset still returns a structured dict with a `reason` for each
   missing extraction (matching the
   `_write_quest_pack_to_convex` graceful-degradation pattern).

Additionally, the Hono planner service at
`web/hono-api/src/routes/copilotkit/lc/<subject>.ts` MUST bridge to
the canonical Python planner at
`agents/adk/subjects/lc/planner.py::generate_study_plan(...)` via a
subprocess call (using `node:child_process::execFile` with the Python
module path as a fixed string, JSON input over stdin, JSON output
over stdout), replacing the prior `studyPlanStubResponse(...)`
literal response on the 4 mounted routes
(`/api/copilotkit/lc/{chemistry, mathematics, gaeilge,
computer_science}/get_study_plan`).

#### Scenario: Hono /get_study_plan returns the live planner response

- **GIVEN** the Python planner at
  `agents/adk/subjects/lc/planner.py` is importable
- **WHEN** a TanStack Start `useStudyPlan` hook POSTs
  `{"subject": "chemistry", "lo_codes": ["LC-CHEM-LO-3.1"], "duration_weeks": 12}`
  to `/api/copilotkit/lc/chemistry/get_study_plan`
- **THEN** the Hono route invokes `python -c "from
  agents.adk.subjects.lc.planner import generate_study_plan; ..."`
  via `child_process::execFile`
- **AND** the parsed JSON response includes the canonical Phase 1
  stub shape (or the live BAML response shape) with
  `phase: "phase1_stub"` (or `"phase1_wired"`) + `weeks_plan[]` +
  `langfuse_trace_id`
- **AND** the front-end `useStudyPlan` hook receives the typed
  `StudyPlanResponse` instead of just the in-process stub

#### Scenario: Hono /get_study_plan falls back to the in-process stub on subprocess failure

- **GIVEN** the Python interpreter is not available, or the planner
  raises
- **WHEN** the same TanStack Start POST fires
- **THEN** the Hono route catches the subprocess error
- **AND** returns the `studyPlanStubResponse(subject, params)` JSON
  with `phase: "phase1_stub"` + `stub_reason: "hono_planner_subprocess_failed_or_unavailable"`
- **AND** the front-end renders the stub without errors

#### Scenario: England orchestrator invokes b.ExtractEnglandSubjectSpec + writes Convex row

- **WHEN** the Dagster asset `england_aqa_a_level_loaded` materialises
- **THEN** for each cohort row, the asset calls
  `invoke_jurisdiction_extractor(jurisdiction="england",
  pdf_path=row.pdf_path, subject_slug=row.subject,
  source_url=row.source_url, stage="LEAVING_CERT")`
- **AND** the result includes `b.ExtractEnglandSubjectSpec`'s return
  value (the typed `ENSubjectSpec` row) as `spec`
- **AND** the result's `convex_written` is True when
  `materialise_subject_spec_to_convex("england", ...)` successfully
  inserts into `england_subject_specs`
- **AND** the asset's return value reports `extracted_count >= 1`
  and `convex_written_count >= 1` for any cohort with a readable PDF

#### Scenario: Wales / Scotland / Northern Ireland / Isle of Man orchestrators follow the same pattern

- **WHEN** the `wales_extractions`, `scotland_extractions`,
  `northern_ireland_extractions`, or `isle_of_man_extractions` asset
  materialises
- **THEN** the asset calls
  `invoke_jurisdiction_extractor(jurisdiction="<jur>", ...)`
- **AND** the BAML extraction function invoked is the canonical one
  (`b.ExtractWalesSubjectSpec` / `b.ExtractScotlandSubjectSpec` /
  `b.ExtractNorthernIrelandSubjectSpec` /
  `b.ExtractIsleOfManSubjectSpec`)
- **AND** the result materialises to the matching
  `<jurisdiction>_subject_specs` Convex table
- **AND** the existing `rows_extracted`, `ragas_scores`, `counts`
  return fields stay populated (backwards-compatible with the Phase 9
  shape)

#### Scenario: Graceful degradation when BAML or Convex is unavailable

- **GIVEN** either `baml_client` is not importable or `convex`
  Python package is not installed
- **WHEN** any of the 5 orchestrators materialises
- **THEN** the asset returns `{"rows_extracted": 0, "ragas_scores":
  {}, "convex_written": 0, "reason": "baml_function_not_registered"}`
  (or equivalent for the per-orchestrator shape)
- **AND** Dagster still records a successful asset materialisation
  (the asset doesn't fail)
- **AND** the asset's metadata reports the `reason` so the operator
  can act on the degradation

#### Scenario: 5 Convex tables are additive (no schema renames)

- **WHEN** the operator inspects
  `web/apps/cianfhoghlaim-nua/convex/schema.ts`
- **THEN** the schema declares exactly 18 tables — the 4 root tables
  (`users`, `study_plans`, `oral_study_plans`,
  `ncce_learning_graphs`) + 8 per-subject tables (`accounting`,
  `business`, `french`, `history`, `art`, `music`,
  `applied_mathematics`, `physics`) + the 5 new
  `<jurisdiction>_subject_specs` tables + 1 NCSE ledger
- **AND** no existing table is renamed or removed
- **AND** the new 5 tables each carry a `by_jurisdiction`,
  `by_subject`, and `by_stage` index
