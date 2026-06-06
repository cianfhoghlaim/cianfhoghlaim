# Cianfhoghlaim Oideachais — BAML-First Multi-Stage Agentic Platform

## Why

The current `oideachais/` project has a mature **data layer** (Dagster + DLT + DuckLake + LanceDB + BAML schemas for exam papers and marking schemes) but the **front-end and agent surface are misaligned with the project's bilingual, multi-stage scope**:

1. **Brand drift.** The interactive web app is branded as **"Awen Hub"** (`oideachais/web/apps/web/src/routes/index.tsx:5`, `routeTree.tsx:20`), while the canonical project name across the rest of the monorepo, the published PyPI package, and the `openspec/project.md` is **"Cianfhoghlaim Oideachais"** (`infrastructure/stacks/infrastructure/forgejo/docs/pypi-usage.md:116`, `readme2.md:1`). The MMO/Game theme from `tuatha/` is leaking into the oideachais UI copy (`docs/web/frontend/agentic-platform.md:45,61`).

2. **Scope narrow.** The current Senior Cycle subject focus (11 LC subjects) ignores 4 of the 5 stages of Irish education. Aistear (early childhood) has only 14 source PDFs in the existing cache; Primary has 2; Junior Cycle has 50+; Tertiary (CAO, HEIs, QQI-FET, Apprenticeship) has no coverage at all. The user-facing UI cannot show what has not been ingested.

3. **No UI generation from extracted data.** The BAML extraction pipeline produces rich `CurriculumSpecification`, `ExamPaper`, `MarkingScheme`, `ExaminerReport` objects that the UI does not consume. The 4 existing routes (`/exams`, `/marking-schemes`, `/syllabus`, `/dives`) are static pages that ignore the BAML outputs. The user explicitly asked that *"after ... successfully extract[ing] via baml and indexing ... generate ideas for different cianfhoghlaim oideachais [components]"*.

4. **Bilingual URL pattern is documented but not implemented.** `docs/meaisínfhoghlaim/celtic/Building Bilingual EdTech Platform.md:98` and `openspec/specs/bilingual-content/spec.md:25` specify `/en/calcalas/derivatives` and `/ga/calcalas/díorthaigh` URL-level i18n. The current SPA has a single `en` locale and no IR-route group.

5. **TanStack Start is not actually wired.** The current `oideachais/web/apps/web/app.config.ts` is a plain Vite config, despite docs claiming TanStack Start. The `app.config.ts` and root `tsconfig.json` reference `vinxi` and a non-existent `./app/` directory. There are no `createServerFn` or file-based routes. The CopilotKit AG-UI runtime (`<CopilotKit runtimeUrl="/api/copilotkit">`) is wired in the SPA but not served by `apps/api` (which only mounts `/api/auth/*`, `/rpc/*`, `/api-reference/*`).

6. **Convex is installed but never used.** `infrastructure/stacks/engineering/convex/` exists with a stack; `apps/web/` has no `convex/` directory and no schema. Chat sessions are stored in SQLite (`agents/agno/education_team.py:36`), which is per-container and doesn't survive a restart or share across devices.

7. **Aistear, Primary, Tertiary BAML schemas are absent.** The canonical `baml_src/curriculum_extraction.baml` only has schemas for Learning Outcomes, CurriculumSpecification, ExamPaper, MarkingScheme, ExaminerReport. Aistear (4 themes × 4 age bands × ~30 learning goals) and Tertiary (CAO + QQI + Apprenticeship) have no BAML schemas. Primary has rich schemas in `docs/agents/BAML_COMPREHENSIVE_GUIDE.md:683-728` but they are not in the canonical `baml_src/`.

## What Changes

### 1. Rebrand
- **Replace** "Awen Hub" with "Cianfhoghlaim Oideachais" in 4 source files: `oideachais/web/apps/web/src/routes/index.tsx:5`, `oideachais/web/apps/web/src/routeTree.tsx:20`, `oideachais/web/apps/web/src/components/Header.tsx`, and `readme2.md`.
- **Rename** `AwenChat.tsx` → `OideachasChat.tsx`. Drop the x402/Anam token copy. The MMORPG framing lives in `tuatha/`, not in `oideachais/`.
- **Demote** `docs/web/frontend/agentic-platform.md` and `docs/tuatha/Agentic Education Platform Development.md` to use the Cianfhoghlaim Oideachais brand.
- **Keep** the `oideachais/` monorepo directory name (decision: do not rename the dir; the PyPI package is already `cianfhoghlaim-oideachais`).

### 2. BAML schema canonicalization
- **Move** the Primary schema (`PrimaryStage`, `PrimaryLearningOutcome`, `PrimaryStrand`, `PrimaryCurriculumArea`, `CompetencyLink`, `ExtractPrimaryFramework`) from `docs/agents/BAML_COMPREHENSIVE_GUIDE.md:683-728` to `baml_src/primary.baml`.
- **Add** `baml_src/aistear.baml` — `AistearTheme`, `AistearAgeBand`, `AistearPrinciple`, `AistearLearningGoal`, `AistearDocument`, `Naionra`, `ExtractAistearFramework`, `ExtractNaionraListing`, `BridgeAistearToPrimary`.
- **Add** `baml_src/junior_cycle.baml` — `JuniorCycleSubject` (18), `JuniorCycleShortCourse` (16), `AchievementLevel`, `RubricDescriptor`, `CBATask`, `JCSubjectSpec`, `L2LP_Outcome`, `ExtractJCSpec`, `ExtractCBADescriptor`.
- **Extend** `baml_src/curriculum_extraction.baml` with `LeavingCertSubject` (50+), `Specialism`, `ExamLevel`, `AssessmentComponentType`, `AssessmentComponent`, `SpecialismRubric`, `RubricStyle`, `SubjectRubric`, `LazyExtractExamPaper`, `ExtractSubjectRubric`, `ScoreEssayAgainstRubric`, `CompareMarkingSchemes`, `ExtractionBudget`.
- **Add** `baml_src/tertiary.baml` — `NFQLevel`, `EQFLevel`, `HEIType`, `EntryPathway`, `MatriculationRequirement`, `CAOCourse`, `QqiFetAward`, `Apprenticeship`, `Programme`, `ApplicationTimeline`, `CAOGradeProfile`, and the 7 extract/predict functions.
- **Add** `baml_src/ui_components.baml` — `UIComponentKind` (28 kinds), `UIComponentSuggestion`, `SuggestUIComponents`. The nightly `ui_suggestion` Dagster asset populates a `ui_component_suggestions` LanceDB table that drives the SPA's `<ComponentCatalog>` admin route.

### 3. Multi-stage extraction pipeline
- **Add** 5 new DLT sources: `dlt_sources/ireland/aistear.py`, `primary.py`, `tertiary.py`, and 2 extensions to `junior_cycle.py` and `senior_cycle.py`.
- **Add** 5 new Dagster assets: `aistear_knowledge_graph`, `primary_knowledge_graph`, `junior_cycle_knowledge_graph`, `senior_cycle_knowledge_graph`, `tertiary_knowledge_graph`. Each writes to its own LanceDB table.
- **Add** 5 Cognee cognify triggers with cross-stage edges: `BRIDGES_TO`, `PREPARES_FOR`, `PROGRESSES_TO`, `ASSESSED_BY`, `REQUIRED_FOR`, `DELIVERS`, `LADDERS_INTO`, `ALTERNATIVE_TO`.
- **Add** 1 nightly `baml_extraction_cache_asset` (memoises per `(subject, year, level, paper)`) and 1 `ui_suggestion_asset` (calls `b.SuggestUIComponents` against the populated Cognee index).

### 4. Web migration to real TanStack Start
- **Migrate** `oideachais/web/apps/web` from Vite SPA → real TanStack Start with `createStartHandler`, `getRouter`, `StartClient`, and file-based routes in `apps/web/src/routes/`.
- **Add** `(en)` and `(ga)` route groups with parallel `/en/...` and `/ga/...` URL trees. Irish-language slugs: `c\u00e9imeanna`, `bunscoil`, `iar-bhunscoil`, `scoil-daraigh`, `ardteistim\u00e9ireacht`, `\u00e1bhair`, `c\u00farsa\u00ed`.
- **Add** `<TranslationToggle>` component (in the header) and `<BilingualBlock en ga>` inline component.
- **Add** CopilotKit server runtime in `apps/api/src/copilotkit/runtime.ts` mounted at `/api/copilotkit?stage=...&subject=...&language=...`. Stream AG-UI events (`text`, `tool_call`, `tool_result`, `agent_handoff`, `done`) to the SPA via SSE.

### 5. Convex persistence
- **Add** `oideachais/web/convex/schema.ts` with 5 tables: `subject_sessions`, `practice_attempts`, `annotations`, `classmate_shares`, `extraction_budget`.
- **Wire** Convex client in `apps/web/src/router.tsx` via `<ConvexProvider>`.
- **Replace** the SQLite default in `agents/agno/education_team.py:36` with Convex-backed session storage.

### 6. Agno stage teams
- **Add** `oideachais/data_platform/agents/agno/stage_teams/{aistear,primary,junior_cycle,senior_cycle,tertiary}_team.py` — 5 Agno `Team` instances with stage-specific sub-agents.
- **Add** shared sub-agents in `stage_teams/_shared/`: `CurriculumScout`, `TranslationAgent`, `CogneeGraphQuery`, `SourceCiter`.
- **Wire** AG-UI bridge in `apps/api/src/copilotkit/agui_stream.ts` that wraps `team.run(stream=True, ...)` into the 5 AG-UI event types.

### 7. Marimo dashboards
- **Keep** all 9 existing marimo notebooks (`mission_control`, `lakehouse_inspector`, `pdf_download_dashboard`, `pipeline_e2e_test`, `ducklake_explorer`, `curriculum_educator`, `exam_papers_explorer`, `marking_scheme_analyzer`, `syllabus_visualizer`).
- **Add** 5 new stage-specific notebooks generated from `analysis_plan.md` files via the `explore-data` + `build-notebook` skill flow.
- **Mount** at `/dashboards/$stage` (file-based route in both EN and GA).

### 8. UI component library
- **Add** 20+ new React components (one per `UIComponentKind` in the BAML schema), all bilingual:
  - `<AistearThemesGrid>`, `<NaionraMap>`, `<ParentTip>` (Aistear)
  - `<PrimaryStrandTree>`, `<StageOutcomesMapper>` (Primary)
  - `<JCCBATimeline>`, `<JCShortCourseBadge>`, `<L2LPSpecialist>` (Junior Cycle)
  - `<SCExamPaperCard>`, `<SCMarkingSchemePanel>`, `<SCRubricDescriptorList>`, `<SCPracticeEssayEditor>`, `<SCPointsCalculator>`, `<SCMatriculationAuditor>` (Senior Cycle)
  - `<TertiaryCAOCourseCard>`, `<TertiaryQQILadder>`, `<TertiaryApprenticeshipCard>`, `<TertiaryApplicationTimeline>`, `<TertiaryCAOPointsTrend>` (Tertiary)
  - `<CitationChip>`, `<BilingualBlock>`, `<TranslationToggle>`, `<KeywordCloud>`, `<LearningOutcomePill>` (cross-cutting)
- **Replace** the existing static `/exams`, `/marking-schemes`, `/syllabus` pages with the new dynamic, BAML-driven equivalents.

## Impact

| Surface | Before | After |
|:--|:--|:--|
| Brand | "Awen Hub" | "Cianfhoghlaim Oideachais" |
| Coverage | Senior Cycle (11 subjects) | Aistear + Primary + Junior Cycle + Senior Cycle + Tertiary |
| BAML schema files | 4 (curriculum_extraction, image_generation, generators, clients) | 8 (+ aistear, primary, junior_cycle, tertiary, ui_components) |
| BAML extraction functions | 11 | 30+ |
| Dagster KG assets | 1 (`celtic_language_assets`) | 6 (+ aistear, primary, junior_cycle, senior_cycle, tertiary, ui_suggestion) |
| DLT sources | 14+ | 19+ (5 stage sources + extensions) |
| Cognee datasets | 1 | 6 (+ aistear, primary, junior_cycle, senior_cycle, tertiary) |
| LanceDB knowledge-graph tables | 1 (`celtic_embeddings`) | 6 (+ 5 stage tables) |
| Agno teams | 1 (6-agent education_team) | 6 (5 stage teams + senior_cycle subject_teams) |
| UI routes | 7 (index, exams, marking-schemes, syllabus, dives, lakehouse, runs) | 30+ (5 stage overviews + 5 subject-detail templates + 11 SC subjects + 4 tertiary pages + points calculator + matriculation auditor + dashboards) |
| UI route locales | 1 (en only) | 2 (`/en/` + `/ga/` parallel paths) |
| Bilingual BAML | partial (en/ga optional fields) | full (every BAML class has `*_en` and `*_ga` fields) |
| Chat persistence | SQLite (per container) | Convex (cross-device, classmate-shareable) |
| Web framework | Vite SPA | TanStack Start (file-based routes, SSR) |
| CopilotKit runtime | client only | client + Hono-mounted SSE server |
| Marimo notebooks | 9 | 14 (9 + 5 stage-specific) |
| PyPI package name | `cianfhoghlaim-oideachais` (unchanged) | `cianfhoghlaim-oideachais` (unchanged) |
| Monorepo directory | `oideachais/` (unchanged) | `oideachais/` (unchanged) |

## Out of scope

- Renaming the `oideachais/` monorepo directory to `cianfhoghlaim-oideachais/` (decision: keep the dir name; only the brand is refronted).
- Renaming `códeolas/` back to `códeolas/` (the PyPI package is already `cianfhoghlaim-oideachais`).
- Porting the `tuatha/` MMO documentation onto the oideachais web app (the `tuatha/` theme is shelved).
- Live scraping of `examinations.ie` and CAO.ie — the pipeline will run against `stedding/ingest_queue/` cache (`USE_LOCAL_SCRAPES=true`) first; live scraping is a follow-up.
- Hugging Face dataset publication of the BAML-extracted corpora (deferred to Phase 12).
- The Skill-to-component mapping for `.agents/skills/` (the existing skills are already referenced; this change doesn't add new skills).
