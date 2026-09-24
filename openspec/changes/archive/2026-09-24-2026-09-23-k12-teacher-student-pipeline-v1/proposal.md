# Change: k12-teacher-student-pipeline-v1

## Why

The BIEP v3 umbrella covers 5 stages (aistear → primary → jc → sc → tertiary).
The recent `2026-09-23-consolidate-uog-tertiary-pipeline-v1` + `2026-09-23-uog-tertiary-real-data-upgrade-v1` changes shipped the **tertiary** tier with: 14 real DLT sources, 8 BAML files, 10 CocoIndex flows, 24 walkthrough notebooks, DuckLake + Unsloth Studio integration, and the Students' Union ADK agents.

The **K-12 tiers** (aistear + primary + jc + sc) are missing the same depth:

| Gap | UoG tertiary | K-12 |
|---|---|---|
| Teacher-centric ADK agents | 0 (student-only via SU) | **0** — need 5: lesson_planner, assessment_scorer, sen_pastoral_care, parent_meeting, professional_learning |
| Student-centric ADK agents | 5 (SU agents for clubs + grants + classrep + complaints + elections) | **5 needed** for secondary (JC + LC + TY): homework_tracker, cba_planner, study_plan, wellbeing_checkin, exam_timetable |
| Teacher-centric BAML classes | 0 | **7 needed**: TeacherPlan, LessonPlan, ClassRoster, AssessmentTask, SENRecord, PDRecord, ProLearningModule |
| Student-centric BAML classes | 0 | **5 needed**: HomeworkItem, CBAPlan, StudyPlan, WellbeingCheckIn, ExamTimetable |
| OIDE/PDST/NCCA teacher-PD integration | N/A | **0** — need 3 new DLT sources (oide.py + pdst.py + teacher_pd.py) |
| Class roster / attendance / SEN | N/A | **0** — need class_roster.py + teacher_workload.py |
| Aistear / Primary / JC / SC CocoIndex flows | tertiary has 10 | **only 2/8 implemented** (aistear_embedding + primary_embedding + senior_cycle_embedding are PLANNED per `british-isles-education-pipeline-v3/spec.md:712-721` but not built) |
| Walkthrough marimo notebooks | tertiary has 20 | **0 K-12 walkthroughs** |

This change ships the full K-12 teacher + student pipeline mirroring the tertiary tier.

## What Changes

### Code — new (~95 files)

**Tier 1 — DLT sources**
- 5 updated with real Firecrawl data: `aistear.py`, `primary.py`, `junior_cycle.py`, `senior_cycle.py`, `oide.py`
- 4 new: `pdst.py`, `class_roster.py`, `teacher_pd.py`, `teacher_workload.py`

**Tier 2 — BAML schemas**
- `baml_src/british_isles/ireland/education/teacher/teacher_extraction.baml` (NEW — 7 teacher classes + 5 extraction functions)
- `baml_src/british_isles/ireland/education/student/jc_workflows.baml` (NEW — 5 student classes + 5 extraction functions)
- `baml_src/british_isles/ireland/education/junior_cycle_extraction/jc_subject_extraction.baml` (NEW — fills the empty dir)
- `baml_src/british_isles/ireland/education/junior_cycle_extraction/cba_task_extraction.baml` (NEW)
- Extend `baml_src/british_isles/ireland/education/primary/primary_extraction.baml` with per-area extraction functions

**Tier 3 — ADK agents (10 new — fleet grows 14 → 24)**
- `agents/meaisinfhoghlaim/educational/teachers/lesson_planner_agent.py`
- `agents/meaisinfhoghlaim/educational/teachers/assessment_scorer_agent.py`
- `agents/meaisinfhoghlaim/educational/teachers/sen_pastoral_care_agent.py`
- `agents/meaisinfhoghlaim/educational/teachers/parent_meeting_agent.py`
- `agents/meaisinfhoghlaim/educational/teachers/professional_learning_agent.py`
- `agents/meaisinfhoghlaim/educational/students_jc/homework_tracker_agent.py`
- `agents/meaisinfhoghlaim/educational/students_jc/cba_planner_agent.py`
- `agents/meaisinfhoghlaim/educational/students_jc/study_plan_agent.py`
- `agents/meaisinfhoghlaim/educational/students_jc/wellbeing_agent.py`
- `agents/meaisinfhoghlaim/educational/students_jc/exam_timetable_agent.py`

**Tier 4 — CocoIndex factory + flows (8 new)**
- `cocoindex_flows/british_isles/ireland/education/_shared.py` (NEW — the per-stage K-12 CocoIndex factory, parallel to `tertiary/uog/_shared.py`)
- `cocoindex_flows/subjects/aistear_embedding.py` (the long-planned one)
- `cocoindex_flows/subjects/primary_embedding.py` (the long-planned one)
- `cocoindex_flows/subjects/senior_cycle_embedding.py` (the long-planned one)
- `cocoindex_flows/british_isles/ireland/education/lesson_plan_flow.py`
- `cocoindex_flows/british_isles/ireland/education/assessment_task_flow.py`
- `cocoindex_flows/british_isles/ireland/education/class_roster_flow.py`
- `cocoindex_flows/british_isles/ireland/education/professional_learning_flow.py`
- `cocoindex_flows/_shared/_primary_modules.yaml` (50-row primary factory config)
- `cocoindex_flows/_shared/_jc_subjects.yaml` (18-row JC factory config)
- `cocoindex_flows/_shared/_sc_subjects.yaml` (40-row SC factory config)

**Tier 5 — marimo walkthrough notebooks (20 new + 1 generator + 1 DuckLake helper)**
- `scripts/generate_k12_walkthroughs.py`
- `notebooks/_shared/k12/ducklake_helpers.py`
- `notebooks/_shared/k12/walkthroughs/{20 files}` (8 feature + 5 layer + 5 model + 2 student/teacher — actually 20)

**Tier 6 — Dagster orchestration (~25 assets)**
- `orchestration/defs/1_ingestion/primary_jc/_layer/defs.yaml` + 9 DLT asset subdirs
- `orchestration/defs/2_materials/primary_jc/_layer/defs.yaml` + 4 BAML extraction asset subdirs
- `orchestration/defs/3_model_lifecycle/primary_jc/_layer/defs.yaml` + embedder routing
- `orchestration/defs/4_asset_generation/primary_jc/_layer/defs.yaml` + 5 CocoIndex asset subdirs
- `orchestration/defs/5_agent_ops/primary_jc/_layer/defs.yaml` + 10 ADK agent op subdirs

### Code — modified
- `agents/agent_registry.py` (fleet 14 → 24)
- `agents/routing_keywords.py` (+5 teacher + 5 student keyword buckets)
- `orchestration/defs/4_budget/firecrawl_budget_asset.py` (+14 firecrawl budget allocations for K-12)
- `baml_src/clients.baml` (+5 K-12 BAML clients)
- `scripts/osint_allowlists/ireland_tertiary.yaml` (extend with K-12 entries — but actually no, this file is tertiary; K-12 gets its own `ireland_k12.yaml`)

### Code — new openspec specs
- `openspec/specs/k12-teacher-student-pipeline/spec.md` (NEW umbrella spec)
- `openspec/specs/k12-cocoindex-factory/spec.md` (NEW per-stage CocoIndex factory spec)

## Out of scope (Phase 3)
- Per-subject deep extraction for the 6 LC priority subjects (the BIEP v3 v1 active)
- BIEP v4 umbrella spec consolidating all 5 stages
- Cognee cross-stage edges (`Teacher teaches Module`, `Student enrolled in Module`, `Student has Parent who is ClassRep`)
- `students_union` rename to `students_union_postprimary`

## Dependencies
`Blocked by: none` (the 2026-09-23-consolidate-uog-tertiary-pipeline-v1 + 2026-09-23-uog-tertiary-real-data-upgrade-v1 changes have landed the per-tier patterns this K-12 change mirrors).
`Affected repos: cianfhoghlaim`.

## Verification
1. `openspec validate 2026-09-23-k12-teacher-student-pipeline-v1 --strict` exits 0
2. `git grep "stub\|TODO\|PLACEHOLDER" dlt_sources/british_isles/ireland/education/` returns 0 matches
3. The 10 new agents register in `agents/agent_registry.py` (fleet = 24)
4. `python3 -c "import ast; [ast.parse(open(f).read()) for f in glob.glob('agents/meaisinfhoghlaim/educational/**/*.py')]"` exits 0
5. The 20 K-12 walkthrough notebooks parse + import cleanly
6. The 8 new CocoIndex flows wire via the same `_lifespan.py` shared_lifespan
7. `git grep "kings_college_galway\|ollscoil-na-gaillimhe"` returns 0 (sister-repo artifacts purged)
