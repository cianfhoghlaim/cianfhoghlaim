# Tasks — Cianfhoghlaim Oideachais BAML-First Multi-Stage Agentic Platform

## Phase 0 — OpenSpec and Rebrand (week 0)

- [ ] 1. Create `openspec/changes/cianfhoghlaim-oideachais-baml-first/{proposal.md, tasks.md, specs/}` with the 11 spec deltas.
- [ ] 2. Rebrand `sruth/oideachais/web/apps/web/src/routes/index.tsx:5` from `Welcome to Awen Hub` to `Fáilte go Cianfhoghlaim Oideachais`.
- [ ] 3. Rebrand `sruth/oideachais/web/apps/web/src/routeTree.tsx:20` from `Awen Hub — Oideachais Education Engine` to `Cianfhoghlaim Oideachais`.
- [ ] 4. Rebrand `sruth/oideachais/web/apps/web/src/components/Header.tsx`: logo text `AWEN HUB` → `CIANFHOGHLAIM OIDEACHAIS`; drop RPG-fantasy tagline; add `<TranslationToggle>` slot.
- [ ] 5. Rename `sruth/oideachais/web/apps/web/src/components/AwenChat.tsx` → `OideachasChat.tsx`; update `routeTree.tsx` import; drop x402/Anam token copy.
- [ ] 6. Update `readme2.md` title and intro from "Cianfhoghlaim & Awen Hub" to "Cianfhoghlaim Oideachais" (single brand).
- [ ] 7. Update `docs/ARCHITECTURE_DEPLOYMENT.md:91` "Start the Awen Hub Frontend" → "Start the Cianfhoghlaim Oideachais web app".
- [ ] 8. Replace `Awen Hub` with `Cianfhoghlaim Oideachais` in `docs/web/frontend/agentic-platform.md` and `docs/sruth/tuatha/Agentic Education Platform Development.md`; demote the x402 "Learn-to-Earn" narrative.
- [ ] 9. Validate the change: `openspec validate cianfhoghlaim-oideachais-baml-first --strict`.

## Phase 1 — BAML canonical schema (week 1)

- [ ] 10. Create `baml_src/aistear.baml` with `AistearTheme`, `AistearAgeBand`, `AistearPrinciple`, `AistearLearningGoal`, `AistearDocument`, `Naionra`, `ExtractAistearFramework`, `ExtractNaionraListing`, `BridgeAistearToPrimary`.
- [ ] 11. Create `baml_src/primary.baml` — move `PrimaryStage`, `PrimaryLearningOutcome`, `PrimaryStrand`, `PrimaryCurriculumArea`, `CompetencyLink`, `ExtractPrimaryFramework` from `docs/agents/BAML_COMPREHENSIVE_GUIDE.md:683-728` (keep the doc as a cross-reference, not the source of truth).
- [ ] 12. Create `baml_src/junior_cycle.baml` with `JuniorCycleSubject` (18), `JuniorCycleShortCourse` (16), `AchievementLevel`, `RubricDescriptor`, `CBATask`, `JCSubjectSpec`, `L2LP_Outcome`, `ExtractJCSpec`, `ExtractCBADescriptor`.
- [ ] 13. Extend `baml_src/curriculum_extraction.baml` with `LeavingCertSubject` (50+), `Specialism`, `ExamLevel`, `AssessmentComponentType`, `AssessmentComponent`, `SpecialismRubric`, `RubricStyle`, `SubjectRubric`, `LazyExtractExamPaper`, `ExtractSubjectRubric`, `ScoreEssayAgainstRubric`, `CompareMarkingSchemes`, `ExtractionBudget`.
- [ ] 14. Create `baml_src/tertiary.baml` with `NFQLevel`, `EQFLevel`, `HEIType`, `EntryPathway`, `MatriculationRequirement`, `CAOCourse`, `QqiFetAward`, `Apprenticeship`, `Programme`, `ApplicationTimeline`, `CAOGradeProfile`, and the 7 extract/predict functions.
- [ ] 15. Create `baml_src/ui_components.baml` with `UIComponentKind` (28 kinds), `UIComponentSuggestion`, `SuggestUIComponents`.
- [ ] 16. Update `baml_src/generators.baml` to register the 5 new BAML client aliases: `aistear`, `primary`, `junior_cycle`, `senior_cycle`, `tertiary` (each pointing at `litellm/gemini-2.0-flash` as default; `litellm/anthropic/claude-sonnet-4-20250514` for tertiary essay scoring).
- [ ] 17. Run `baml-cli generate` to regenerate the BAML Python and TypeScript clients.
- [ ] 18. Run `baml-cli test` (the existing `test ExtractRelationshipsTest` etc. must still pass; add `test ExtractAistearFrameworkTest`, `test ExtractPrimaryFrameworkTest`, `test ExtractTertiaryRequirementsTest`).
- [ ] 19. Create `sruth/oideachais/data_platform/subjects/stages.json` (5 stages × multilingual metadata), `sruth/oideachais/data_platform/subjects/lc_subjects.json` (50+ subjects), `sruth/oideachais/data_platform/subjects/jc_subjects.json` (18 + 16), `sruth/oideachais/data_platform/subjects/hei.json` (8 NUI/IoT institutions).
- [ ] 20. Create `sruth/oideachais/data_platform/subjects/baml_context/{aistear,primary,junior_cycle,senior_cycle,tertiary}.baml` — 5 short context files that pre-load the BAML `client` with the right system prompt, exam board conventions, and rubric style for that stage.

## Phase 2 — Extraction pipeline (week 2)

- [ ] 21. Create `sruth/oideachais/data_platform/dlt_sources/ireland/aistear.py` — `@dlt.source aistear_curriculum` (14 source PDFs on curriculumonline.ie; primary candidates: `ncca.ie/en/early-childhood/`, `gov.ie/en/department-of-education/topics/early-years/`).
- [ ] 22. Create `sruth/oideachais/data_platform/dlt_sources/ireland/primary.py` — `@dlt.source primary_curriculum` (12 curriculum areas × 4 stages).
- [ ] 23. Extend `sruth/oideachais/data_platform/dlt_sources/ireland/junior_cycle.py` — add `junior_cycle_cb_tasks` resource (the 2 CBAs per subject).
- [ ] 24. Extend `sruth/oideachais/data_platform/dlt_sources/ireland/senior_cycle.py` — add `lazy_extract_exam_paper` resource that fires BAML on-demand.
- [ ] 25. Create `sruth/oideachais/data_platform/dlt_sources/ireland/tertiary.py` — `@dlt.source tertiary_courses` (CAO.ie + 8 NUI/HEI sites; Skyvern/Stagehand for JS-heavy sites).
- [ ] 26. Create 5 new Dagster assets:
  - `sruth/oideachais/data_platform/dagster_defs/assets/aistear_kg.py` (extract → embed → cognify)
  - `.../primary_kg.py`
  - `.../junior_cycle_kg.py`
  - `.../senior_cycle_kg.py` (joins `pdf_extracted_text` + `exam_materials_assets`)
  - `.../tertiary_kg.py`
  Each writes to its own LanceDB table and Cognee dataset.
- [ ] 27. Create the cross-stage Cognee cognify asset: `sruth/oideachais/data_platform/cognee_integration/cross_stage_cognify.py` — defines the 8 cross-stage edges (`BRIDGES_TO`, `PREPARES_FOR`, `PROGRESSES_TO`, `ASSESSED_BY`, `REQUIRED_FOR`, `DELIVERS`, `LADDERS_INTO`, `ALTERNATIVE_TO`).
- [ ] 28. Create `sruth/oideachais/data_platform/dagster_defs/assets/ui_suggestion.py` — the nightly `ui_suggestion_asset` that calls `b.SuggestUIComponents` against the populated Cognee index and writes to LanceDB `ui_component_suggestions` table.
- [ ] 29. Register all 5 KG assets + 1 ui_suggestion asset + 1 cross_stage_cognify asset in `sruth/oideachais/data_platform/dagster_defs/definitions.py`.
- [ ] 30. Test against `stedding/ingest_queue/` cache with `USE_LOCAL_SCRAPES=true`; verify a full end-to-end run with `uv run dagster dev -m dagster_defs.definitions`.

## Phase 3 — Rebrand + TanStack Start migration (week 3-4)

- [ ] 31. Install TanStack Start: `bun add -D @tanstack/react-start@latest @tanstack/router-plugin@latest vinxi@latest` in `sruth/oideachais/web/`.
- [ ] 32. Rewrite `sruth/oideachais/web/app.config.ts` to use `defineConfig` from `@tanstack/react-start` + `vinxi`.
- [ ] 33. Move `sruth/oideachais/web/apps/web/src/routeTree.tsx` to `sruth/oideachais/web/apps/web/src/routes/__root.tsx` (file-based). Convert the existing 7 routes to file-based: `index.tsx`, `exams.tsx`, `marking-schemes.tsx`, `syllabus.tsx`, `lakehouse.tsx`, `runs.tsx`, `dives.tsx`.
- [ ] 34. Add `(en)` and `(ga)` route groups with the 5 stage overview routes + subject-detail templates (per the spec deltas in `specs/sruth/oideachais/web/tanstack-start-migration/`).
- [ ] 35. Add `<TranslationToggle>` and `<BilingualBlock en ga />` components.
- [ ] 36. Update `sruth/oideachais/web/apps/web/Dockerfile` for the TanStack Start dev server: `bun run --bun vite dev --host 0.0.0.0 --port 3001`.
- [ ] 37. Verify `bun run dev` from the workspace root works end-to-end with the new file-based routes.
- [ ] 38. Add a `mise turbo dev:oideachais` task alias for the new dev workflow.

## Phase 4 — CopilotKit runtime + AG-UI bridge (week 4)

- [ ] 39. Create `sruth/oideachais/web/apps/api/src/copilotkit/runtime.ts` — the Hono route mounted at `/api/copilotkit` that streams AG-UI events to the SPA.
- [ ] 40. Create `sruth/oideachais/web/apps/api/src/copilotkit/agui_stream.ts` — the bridge that wraps `team.run(stream=True, ...)` into the 5 AG-UI event types.
- [ ] 41. Create `sruth/oideachais/web/apps/api/src/copilotkit/stage_router.ts` — resolves the right Agno `Team` from the `stage` query param.
- [ ] 42. Mount the runtime in `sruth/oideachais/web/apps/api/src/index.ts`.
- [ ] 43. Add 7 new oRPC procedures in `sruth/oideachais/web/apps/api/src/routers/`:
  - `aistear.ts` (`aistear.getThemes`, `aistear.getLearningGoals`, `aistear.getNaionra`)
  - `primary.ts` (`primary.getCurriculumArea`, `primary.getStrand`)
  - `junior_cycle.ts` (`junior_cycle.getSpecs`, `junior_cycle.getCBATasks`)
  - `senior_cycle.ts` (`senior_cycle.getExamPaper`, `senior_cycle.getMarkingScheme`, `senior_cycle.getSubjectRubric`, `senior_cycle.scoreEssay`)
  - `tertiary.ts` (`tertiary.getCAOCourses`, `tertiary.getMatriculationRules`, `tertiary.getApplicationTimeline`, `tertiary.auditMatriculation`, `tertiary.predictPoints`)
  - `baml.ts` (`baml.lazyExtract`, `baml.suggestUIComponents`)
  - `i18n.ts` (`i18n.translate` — lazy EN↔GA via litellm/irish)
- [ ] 44. Wire the `AwenChat` → `OideachasChat` rename in `sruth/oideachais/web/apps/web/src/routes/`.
- [ ] 45. Add CORS and SSE headers in the Hono app for the CopilotKit runtime.

## Phase 5 — UI generated from BAML keywords (week 5-6)

- [ ] 46. Build the 5 stage overview pages: `/en/stages/{aistear,primary,junior_cycle,senior_cycle,tertiary}.tsx` and the `(ga)` mirrors.
- [ ] 47. Build the 5 subject-detail templates: `/en/subjects/$slug.tsx` (handles Aistear principles, Primary strands, JC specs, SC specs, Tertiary courses).
- [ ] 48. Build the 4 tertiary sub-pages: `/en/courses/$courseCode.tsx`, `/en/qqi-fet.tsx`, `/en/apprenticeships.tsx`, `/en/application-timeline.tsx` (with `/ga/` mirrors).
- [ ] 49. Build the points calculator `/en/points-calculator.tsx` and matriculation auditor `/en/matriculation-auditor.tsx` (with `/ga/` mirrors as `/pointí-áireamháin.tsx`, `/agallamh-inghlactha.tsx`).
- [ ] 50. Build the 20+ new components from `UIComponentKind` (per Phase 5 of the implementation plan).
- [ ] 51. Add `<ComponentCatalog>` admin route (file-based, at `/en/admin/components.tsx` and `/ga/admin/components.tsx`) that reads the `ui_component_suggestions` LanceDB table.
- [ ] 52. Add `<CitationChip>` to every BAML-extracted fact; links to NCCA/SEC/CAO/HEI source URL.
- [ ] 53. Replace the 4 static routes (`/exams`, `/marking-schemes`, `/syllabus`, `/dives`) with the new dynamic, BAML-driven equivalents.

## Phase 6 — Convex persistence (week 6)

- [ ] 54. Verify `infrastructure/stacks/engineering/convex/` is deployable; bring it up with `docker compose -f compose.yaml -f sidecar.yaml up -d`.
- [ ] 55. Create `sruth/oideachais/web/convex/schema.ts` with the 5 tables (`subject_sessions`, `practice_attempts`, `annotations`, `classmate_shares`, `extraction_budget`).
- [ ] 56. Create the 4 Convex mutation files: `subject_sessions.ts`, `practice_attempts.ts`, `annotations.ts`, `classmate_shares.ts`, `extraction_budget.ts`.
- [ ] 57. Wire Convex client in `sruth/oideachais/web/apps/web/src/router.tsx` via `<ConvexProvider>`.
- [ ] 58. Replace the SQLite default in `sruth/oideachais/data_platform/agents/agno/education_team.py:36` with Convex-backed session storage (via `ConvexDb` adapter if Agno supports it; otherwise a thin Convex wrapper around the existing `SqliteDb`).
- [ ] 59. Add the Convex deploy URL to the `sruth/oideachais/compose.yaml` and `apps/api` env (`CONVEX_URL`, `CONVEX_DEPLOY_KEY`).

## Phase 7 — Agno stage teams (week 7-8)

- [ ] 60. Create the 5 stage team files in `sruth/oideachais/data_platform/agents/agno/stage_teams/`:
  - `aistear_team.py` (sub-agents: `ThemeNavigator`, `PrincipleMapper`, `NaionraFinder`, `ParentTipGenerator`)
  - `primary_team.py` (sub-agents: `StrandExplorer`, `CurriculumFetcher`, `StageOutcomesMapper`)
  - `junior_cycle_team.py` (sub-agents: `SubjectSpecRetriever`, `CBADescriptorGuide`, `ShortCourseAdvisor`, `Level2LPSpecialist`)
  - `senior_cycle_team.py` (sub-agents: `PaperAnalyst`, `MarkingSchemeDecoder`, `ExaminerInsights`, `RubricJudge`, `ComparisonAgent`, `PracticeCoach`, `PointsCalculator`, `MatriculationAuditor`)
  - `tertiary_team.py` (sub-agents: `CAOCourseFinder`, `QQIFETLadder`, `ApprenticeshipAdvisor`, `MatriculationCheck`, `ApplicationTimelineGuide`, `HEIComparer`)
- [ ] 61. Create the 4 shared sub-agents in `stage_teams/_shared/`: `CurriculumScout`, `TranslationAgent`, `CogneeGraphQuery`, `SourceCiter`.
- [ ] 62. Replace the existing 6-agent `education_team.py` with a thin compatibility shim that dispatches to the 5 stage teams.
- [ ] 63. Add the 5 stage teams to `sruth/oideachais/data_platform/agent_os/config.yaml`.

## Phase 8 — Marimo dashboards (week 9-10)

- [ ] 64. Create 5 `analysis_plan.md` files in `sruth/oideachais/notebooks/analysis_plan/`:
  - `aistear.md` (questions about Aistear participation rates, theme distribution, naíonra density by county)
  - `primary.md` (questions about Primary strand distribution, Stage 1→4 progression, language medium uptake)
  - `junior_cycle.md` (questions about JC grade distribution, CBA completion, short course uptake)
  - `senior_cycle.md` (questions about LC grade distribution, marking scheme drift, subject difficulty trends)
  - `tertiary.md` (questions about CAO points trends, NUI matriculation, QQI laddering)
- [ ] 65. Run the `explore-data` + `build-notebook` skill flow to generate 5 marimo notebooks in `sruth/oideachais/notebooks/dashboards/`.
- [ ] 66. Mount the dashboards at `/dashboards/$stage` (file-based routes in both EN and GA).
- [ ] 67. Embed a stage-relevant chart on each stage overview page.

## Phase 9 — Practice, points, matriculation, polish (week 10-11)

- [ ] 68. Build the `<SCPracticeEssayEditor>` with `@tanstack/react-form` and a "Submit" button that calls `baml.scoreEssay`.
- [ ] 69. Build the `<SCPointsCalculator>` (H1-H8, O1-O8, H6+25 bonus math, per `docs/web/BAML, Graphiti, Tanstack AI Pipeline.md:263`).
- [ ] 70. Build the `<SCMatriculationAuditor>` (grade-vs-requirement table with pass/fail).
- [ ] 71. Add a PDF.js viewer (`@react-pdf/renderer` or `pdfjs-dist`) for the SC exam papers and marking schemes.
- [ ] 72. Add Convex-backed annotations on PDF documents.
- [ ] 73. Add the Better Auth sign-in flow (replace the stub `Header.tsx` "Sign In" button); add `/en/login.tsx`, `/en/account.tsx`, `/ga/s\u00e9\u00e9-isteach.tsx`, `/ga/cuntas.tsx`.
- [ ] 74. Wire the `cal-diy` integration for exam-date calendar overlays.

## Phase 10 — Production hardening (week 12)

- [ ] 75. Switch dev Dagster → production-tier `infrastructure/stacks/engineering/dagster/` (Locket + 4-cpu/4G daemon).
- [ ] 76. Wire AgentOS as A2A peer (add `oideachais-agentos:7772` to the `lakehouse` network).
- [ ] 77. Wire `oideachais.observability.fastapi_middleware` into `apps/api` for end-to-end Langfuse tracing.
- [ ] 78. Add a weekly RAGAS evaluation Dagster job (per-team) that stores metrics in MLflow.
- [ ] 79. Update `sruth/oideachais/compose.yaml` healthcheck on the `api` service to check the `/api/copilotkit` endpoint.
- [ ] 80. Update `docs/ARCHITECTURE_RATIONALE.md` to reflect the new bilingual, multi-stage Cianfhoghlaim Oideachais brand.
- [ ] 81. Git: `git pull --rebase`, `git add -A`, commit per phase, `git push`, verify `git status` shows "up to date with origin".

## Total: 81 tasks, 12 weeks
