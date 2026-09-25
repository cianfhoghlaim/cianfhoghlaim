# k12-teacher-student-pipeline Specification

## Purpose

The K-12 Education Pipeline umbrella for the 4 K-12 stages (aistear →
primary → jc → sc) of the British-Isles-Education-Pipeline (BIEP) v3.
Mirrors the depth of the just-shipped UoG tertiary pipeline:
14 DLT sources (9 K-12 + 5 from tertiary), 4 BAML schemas (2 new +
2 updated), 10 new ADK agents (5 teacher + 5 student; fleet grows
14 → 24), 8 new CocoIndex flows, 1 factory + 3 yaml configs, 20 K-12
walkthrough marimo notebooks, DuckLake analysis queries, and
Dagster 5-layer orchestration (~25 assets).

The teacher's workflows (lesson plan + assessment + SEN + parent +
PD) and the JC/LC student's workflows (homework + CBA + study plan +
wellbeing + exam timetable) mirror the Students' Union agents
(tertiary postprimary clubs + grants + classrep + complaints + elections).

## Requirements

## ADDED Requirements

### Requirement: 9 K-12 DLT sources with real Firecrawl-verified data
The system SHALL provide 9 DLT sources in
`dlt_sources/british_isles/ireland/education/`:
- 5 updated: `aistear.py` (14 principles + learning goals), `primary.py`
  (12 NCCA curriculum areas), `junior_cycle.py` (18 subjects),
  `senior_cycle.py` (40+ subjects + 18 LCA), `oide.py` (4 support programmes)
- 4 new: `pdst.py` (10 subject-specific resources), `teacher_pd.py`
  (merged OIDE + PDST), `class_roster.py` (30 student sample), `teacher_workload.py` (3 teacher sample)

#### Scenario: All 9 K-12 DLT sources yield real Firecrawl data
- **WHEN** `pn dlt_pipeline --source ie.k12.<name>` runs for each of the 9 sources
- **THEN** each source emits ≥1 row with real NCCA / OIDE / PDST / sample student / sample teacher data
- **AND** `git grep "stub\|TODO\|PLACEHOLDER" dlt_sources/british_isles/ireland/education/` returns 0 matches

### Requirement: 4 BAML schemas (2 new + 2 updated) for teacher + student workflows
The system SHALL provide 4 BAML schemas:
- NEW `teacher/teacher_extraction.baml` (7 classes: TeacherPlan, LessonPlan,
  ClassRoster, AssessmentTask, SENRecord, PDRecord, ProLearningModule)
- NEW `student/jc_workflows.baml` (5 classes: HomeworkItem, CBAPlan,
  StudyPlan, WellbeingCheckIn, ExamTimetable)
- NEW `junior_cycle_extraction/jc_subject_extraction.baml`
- NEW `junior_cycle_extraction/cba_task_extraction.baml`

#### Scenario: BAML codegen succeeds
- **WHEN** `baml-cli generate --from baml_src` runs
- **THEN** exit code = 0
- **AND** `bun run ccc:search "ExtractLessonPlan"` returns ≥1 hit

### Requirement: 10 new ADK agents (5 teacher + 5 student — fleet grows 14 → 24)
The system SHALL provide 10 new ADK agents:
- 5 teacher: lesson_planner, assessment_scorer, sen_pastoral_care,
  parent_meeting, professional_learning
- 5 student: homework_tracker, cba_planner, study_plan, wellbeing, exam_timetable
All registered in `agents/agent_registry.py` with `framework_priority`
15-24 (the tertiary SU + uoa_portal agents hold 13-14).

#### Scenario: All 10 agents register + route correctly
- **WHEN** the user invokes `/agents` in CopilotKit
- **THEN** the 24-agent fleet is shown (14 existing + 10 new)
- **AND** `lesson_planner_agent` routes for queries with keywords "lesson plan" + "scheme of work"
- **AND** `study_plan_agent` routes for queries with keywords "study plan" + "leaving cert" + "lc"

### Requirement: K-12 CocoIndex factory + 8 flows + 3 yaml configs
The system SHALL provide:
- `cocoindex_flows/british_isles/ireland/education/_shared.py` (the
  K-12 CocoIndex factory, parallel to `tertiary/uog/_shared.py`)
- 3 long-planned flows: `aistear_embedding`, `primary_embedding`,
  `senior_cycle_embedding`
- 5 new flows: `lesson_plan_flow`, `assessment_task_flow`,
  `class_roster_flow`, `professional_learning_flow`, plus the
  existing `junior_cycle_embedding`
- 3 yaml configs: `_primary_modules.yaml` (50 rows), `_jc_subjects.yaml`
  (18 rows), `_sc_subjects.yaml` (40 rows)

#### Scenario: Factory emits ≥50 + 18 + 40 = 108 CocoIndex Apps
- **WHEN** `python -m cocoindex_flows.british_isles.ireland.education._shared`
- **THEN** `create_k12_entity_flow()` is called for every row in the 3 yaml configs (108 total)
- **AND** each call returns a `coco.App` with name `k12_<entity_type>_<entity_id>_flow`

### Requirement: 20 K-12 walkthrough marimo notebooks
The system SHALL provide 20 walkthrough marimo notebooks in
`notebooks/_shared/k12/walkthroughs/`:
- 8 feature walkthroughs: aistear_framework + primary_curriculum +
  primary_jc_combined + jc_subject_spec + jc_cba + ty_programme +
  lc_subject + teacher_workload
- 5 per-layer walkthroughs: 1_ingestion + 2_materials + 3_model_lifecycle +
  4_asset_generation + 5_agent_ops
- 7 per-model walkthroughs: ocr_vision + text_llm + embedder + rerank +
  image_gen + voice + translation
Pattern mirrors `scripts/generate_tertiary_walkthroughs.py` +
`scripts/generate_k12_walkthroughs.py` (the generator).

#### Scenario: 20 notebooks parse + import cleanly
- **WHEN** `python3 -c "import ast; [ast.parse(open(f).read()) for f in glob.glob('notebooks/_shared/k12/walkthroughs/*.py')]"` runs
- **THEN** exit code = 0
- **AND** `marimo edit notebooks/_shared/k12/walkthroughs/feature_01_aistear_framework.py` renders cleanly

### Requirement: Dagster 5-layer orchestration (~25 K-12 assets)
The system SHALL provide ~25 Dagster assets in:
- `1_ingestion/primary_jc/` (9 DLT asset defs.yaml)
- `2_materials/primary_jc/` (4 BAML extraction assets)
- `3_model_lifecycle/primary_jc/` (embedder routing)
- `4_asset_generation/primary_jc/` (5 CocoIndex assets: aistear + primary +
  jc + sc + lesson_plan)
- `5_agent_ops/primary_jc/` (10 ADK agent ops: 5 teacher + 5 student)

#### Scenario: 5-layer K-12 architecture is mounted
- **WHEN** `dagster dev` runs in `orchestration/`
- **THEN** the K-12 layer is loaded + the 28 assets are listed

### Requirement: K-12 DuckLake analysis queries
The system SHALL provide `notebooks/_shared/k12/ducklake_helpers.py`
with 5 DuckLake 1.0-feature demos against the live K-12 data:
data inlining (aistear_learning_goals insert), data clustering
(SORTED BY area_code on primary_curriculum_areas), bucket
partitioning (BUCKET(1000, student_id) on class_roster), VARIANT type
(json_extract on subject_enrolments), time-travel (AT (VERSION => 5)).

#### Scenario: All 5 DuckLake demos execute
- **WHEN** `walkthrough_k12_demo()` runs against `md:cianfhoghlaim`
- **THEN** all 5 queries return results + the data is consistent

### Requirement: Phase 1 cohort coverage (the canonical 4 stages)
The system SHALL cover all 4 BIEP v3 K-12 stages:
- Aistear (Early Childhood, ages 0-6)
- Primary (Junior Infants → 6th Class, ages 4-12)
- Junior Cycle (1st Year → 3rd Year, ages 12-15)
- Senior Cycle (4th Year → 6th Year + TY + LCA, ages 15-18)

#### Scenario: All 4 stages have at least 1 DLT source + 1 BAML function + 1 notebook
- **WHEN** the operator runs `pn` end-to-end
- **THEN** the aistear + primary + jc + sc + ty + lca stages all produce ≥1 row each

## Cross-references
- `openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/` (the tertiary tier that this K-12 change mirrors)
- `openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/` (the SU package pattern this K-12 change mirrors for teacher + student agents)
- `openspec/specs/british-isles-education-pipeline-v3/spec.md:697` (the BIEP v3 5-stage taxonomy `'aistear' | 'primary' | 'jc' | 'sc' | 'tertiary'`)
