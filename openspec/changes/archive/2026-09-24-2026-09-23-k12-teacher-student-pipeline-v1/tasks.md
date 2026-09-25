# Tasks: 2026-09-23-k12-teacher-student-pipeline-v1

## 1. Group A — DLT sources updated with real Firecrawl data (5 updates + 4 new = 9 files)

- [x] **A1** `dlt_sources/british_isles/ireland/education/aistear.py` — replace stub with 14 real Aistear principles + learning goals from `https://www.curriculumonline.ie/early-childhood/` (live URL verified)
- [x] **A2** `dlt_sources/british_isles/ireland/education/primary.py` — replace stub with 12 real NCCA primary curriculum areas (English, Gaeilge, Mathematics, SESE Science, SESE History, SESE Geography, Visual Arts, Music, Drama, PE, SPHE, Religion) from `https://www.curriculumonline.ie/primary/curriculum-areas/`
- [x] **A3** `dlt_sources/british_isles/ireland/education/junior_cycle.py` — extend with all 18 real JC subjects from `https://ncca.ie/en/junior-cycle/subjects-and-short-courses/subjects/`
- [x] **A4** `dlt_sources/british_isles/ireland/education/senior_cycle.py` — extend with all 40+ real SC subjects + LCA + TY programmes from `https://ncca.ie/en/senior-cycle/`
- [x] **A5** `dlt_sources/british_isles/ireland/education/oide.py` (NEW) — real OIDE primary + post-primary support services from `https://oide.ie/schools-support/primary-in-school-support/` + `https://oide.ie/post-primary/home/`
- [x] **A6** `dlt_sources/british_isles/ireland/education/pdst.py` (NEW) — real PDST subject-specific resources
- [x] **A7** `dlt_sources/british_isles/ireland/education/teacher_pd.py` (NEW) — merged OIDE + PDST teacher-PD layer
- [x] **A8** `dlt_sources/british_isles/ireland/education/class_roster.py` (NEW) — class register + attendance + SEN flags
- [x] **A9** `dlt_sources/british_isles/ireland/education/teacher_workload.py` (NEW) — teacher timetable + class assignments

## 2. Group B — BAML schemas (2 new + 2 updated)

- [x] **B1** `baml_src/british_isles/ireland/education/teacher/teacher_extraction.baml` (NEW — 7 teacher classes + 5 extraction functions: ExtractTeacherPlan, ExtractLessonPlan, ExtractClassRoster, ExtractAssessmentTask, ExtractSENRecord)
- [x] **B2** `baml_src/british_isles/ireland/education/student/jc_workflows.baml` (NEW — 5 student classes + 5 extraction functions: ExtractHomeworkItem, ExtractCBAPlan, ExtractStudyPlan, ExtractWellbeingCheckIn, ExtractExamTimetable)
- [x] **B3** `baml_src/british_isles/ireland/education/junior_cycle_extraction/jc_subject_extraction.baml` (NEW — fills the empty dir)
- [x] **B4** `baml_src/british_isles/ireland/education/junior_cycle_extraction/cba_task_extraction.baml` (NEW)
- [x] **B5** Extend `baml_src/british_isles/ireland/education/primary/primary_extraction.baml` with per-area extraction functions (ExtractPrimaryArea)
- [x] **B6** `baml-cli generate --from baml_src` exits 0

## 3. Group C — ADK agents (10 new — fleet grows 14 → 24)

- [x] **C1** `agents/meaisinfhoghlaim/educational/teachers/lesson_planner_agent.py` (BAML-driven lesson plan generation from NCCA spec)
- [x] **C2** `agents/meaisinfhoghlaim/educational/teachers/assessment_scorer_agent.py` (CBA + LC exam paper scoring via Gemini 2.5 Pro)
- [x] **C3** `agents/meaisinfhoghlaim/educational/teachers/sen_pastoral_care_agent.py` (SEN records + pastoral care)
- [x] **C4** `agents/meaisinfhoghlaim/educational/teachers/parent_meeting_agent.py` (parent-teacher meeting prep)
- [x] **C5** `agents/meaisinfhoghlaim/educational/teachers/professional_learning_agent.py` (OIDE/PDST course recommender)
- [x] **C6** `agents/meaisinfhoghlaim/educational/students_jc/homework_tracker_agent.py` (per-subject homework tracker)
- [x] **C7** `agents/meaisinfhoghlaim/educational/students_jc/cba_planner_agent.py` (JC Classroom-Based Assessment planner)
- [x] **C8** `agents/meaisinfhoghlaim/educational/students_jc/study_plan_agent.py` (LC revision tracker)
- [x] **C9** `agents/meaisinfhoghlaim/educational/students_jc/wellbeing_agent.py` (student wellbeing check-in)
- [x] **C10** `agents/meaisinfhoghlaim/educational/students_jc/exam_timetable_agent.py` (State Exams Commission timetable)
- [x] **C11** Update `agents/agent_registry.py` (fleet 14 → 24) + `agents/routing_keywords.py` (+10 keyword buckets)

## 4. Group D — K-12 CocoIndex factory + 8 flows + 3 yaml configs

- [x] **D1** `cocoindex_flows/british_isles/ireland/education/_shared.py` (NEW — the per-stage K-12 CocoIndex factory, parallel to `tertiary/uog/_shared.py`)
- [x] **D2** `cocoindex_flows/subjects/education_subject_embedding.py` (the long-planned one — `aistear_embedding` renamed)
- [x] **D3** `cocoindex_flows/subjects/education_subject_embedding.py` (the long-planned one — `primary_embedding` merged into one)
- [x] **D4** `cocoindex_flows/subjects/education_subject_embedding.py` (the long-planned one — `senior_cycle_embedding` merged into one)
- [x] **D5** `cocoindex_flows/british_isles/ireland/education/lesson_plan_flow.py` (NEW)
- [x] **D6** `cocoindex_flows/british_isles/ireland/education/assessment_task_flow.py` (NEW)
- [x] **D7** `cocoindex_flows/british_isles/ireland/education/class_roster_flow.py` (NEW)
- [x] **D8** `cocoindex_flows/british_isles/ireland/education/professional_learning_flow.py` (NEW)
- [x] **D9** `cocoindex_flows/_shared/_primary_modules.yaml` (50-row primary factory config)
- [x] **D10** `cocoindex_flows/_shared/_jc_subjects.yaml` (18-row JC factory config)
- [x] **D11** `cocoindex_flows/_shared/_sc_subjects.yaml` (40-row SC factory config)

## 5. Group E — K-12 marimo walkthrough notebooks (20 new + 1 generator + 1 DuckLake helper)

- [x] **E1** `scripts/generate_k12_walkthroughs.py` (the generator, parallel to `generate_tertiary_walkthroughs.py`)
- [x] **E2** `notebooks/_shared/k12/ducklake_helpers.py` (K-12 DuckLake analysis queries — parallel to the tertiary one)
- [x] **E3** Generate 30 K-12 walkthrough marimo notebooks in `notebooks/_shared/k12/walkthroughs/`:
  - 10 feature: aistear_framework, primary_curriculum, primary_jc_combined, jc_subject_spec, jc_cba, ty_programme, lc_subject, teacher_lesson_planner, teacher_assessment_scorer, sen_pastoral_care
  - 5 layer: 1_ingestion, 2_materials, 3_model_lifecycle, 4_asset_generation, 5_agent_ops (for K-12)
  - 5 model: ocr_vision, text_llm, embedder, rerank, voice (the K-12-relevant models)
  - 5 ADK 2 deep-research dashboards (Stage F): adk2_aistear, adk2_primary, adk2_jc, adk2_sc, adk2_tertiary
  - 5 teacher dashboards (Stage F): teacher_curriculum, teacher_workload, teacher_cba, teacher_pd, teacher_class
  - 5 student dashboards (Stage F): student_aistear, student_primary, student_jc, student_sc, student_wellbeing

## 6. Group F — Dagster orchestration (~25 assets)

- [x] **F1** `orchestration/defs/1_ingestion/primary_jc/_layer/defs.yaml` + 9 DLT asset subdirs (aistear + primary + jc + sc + oide + pdst + teacher_pd + class_roster + teacher_workload)
- [x] **F2** `orchestration/defs/2_materials/primary_jc/_layer/defs.yaml` + 4 BAML extraction asset subdirs
- [x] **F3** `orchestration/defs/3_model_lifecycle/primary_jc/_layer/defs.yaml` + embedder routing
- [x] **F4** `orchestration/defs/4_asset_generation/primary_jc/_layer/defs.yaml` + 5 CocoIndex asset subdirs (aistear + primary + sc + lesson_plan + assessment_task)
- [x] **F5** `orchestration/defs/5_agent_ops/primary_jc/_layer/defs.yaml` + 10 ADK agent op subdirs (5 teacher + 5 student)
- [x] **F6** Update `orchestration/defs/4_budget/firecrawl_budget_asset.py` (+14 firecrawl budget allocations for K-12)

## 7. Group G — Openspec change + verification + commit + push

- [x] **G1** `openspec/specs/k12-teacher-student-pipeline/spec.md` (NEW umbrella spec with ~8 Requirements + ~20 Scenarios)
- [x] **G2** `openspec/specs/k12-cocoindex-factory/spec.md` (NEW per-stage CocoIndex factory spec)
- [x] **G3** `openspec validate --strict` exits 0
- [ ] **G4** `openspec archive --yes` (archive the change)
- [ ] **G5** `git add -A && git commit && git push`
