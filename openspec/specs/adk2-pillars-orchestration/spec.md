# adk2-pillars-orchestration Specification

## Purpose
TBD - created by archiving change 2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1. Update Purpose after archive.

## Requirements

### Requirement: Pillar 1 — Workflow graphs (3 graphs)
The system SHALL provide 3 ADK 2 `Workflow(edges=...)` graphs:
- `teacher_daily_workflow`: plan_today → lesson_planner → assessment_scorer → sen_pastoral
- `student_secondary_workflow`: load_subjects → homework_tracker → cba_planner → study_plan → exam_timetable
- `tertiary_personal_workflow`: load_profile → uoa_portal → students_union_root

#### Scenario: teacher_daily_workflow runs end-to-end
- **WHEN** the operator invokes `teacher_daily_workflow`
- **THEN** the workflow runs plan_today (0 LLM) → lesson_planner (agent) → assessment_scorer (agent) → sen_pastoral (agent)
- **AND** each agent node emits 1 LLM call + the function node emits 0
- **AND** the workflow respects `mode="single_turn"` if a collaborative branch fires

### Requirement: Pillar 2 — Collaborative root orchestrators (3 roots)
The system SHALL provide 3 root orchestrators with `sub_agents=[...]` + `mode="single_turn"`:
- `teacher_root`: 5 sub_agents (lesson_planner + assessment_scorer + sen_pastoral + parent_meeting + professional_learning)
- `student_root`: 5 sub_agents (homework_tracker + cba_planner + study_plan + wellbeing + exam_timetable)
- `students_union_root`: 5 sub_agents (the existing 5 SU specialists; add `mode="single_turn"`)

#### Scenario: teacher_root fans out to multiple specialists in parallel
- **WHEN** the operator invokes `teacher_root` with a multi-faceted teacher query
- **THEN** the relevant subset of specialists is invoked in parallel (one LLM call each)
- **AND** the coordinator synthesizes one answer from the specialist outputs
- **AND** `mode="single_turn"` mode means the coordinator sees all outputs in one turn

### Requirement: Pillar 3 — Dynamic deep-research (5 pipelines)
The system SHALL provide 5 deep-research pipelines using `@node(parallel_worker=True)` + recursive `ctx.run_node`:
- `aistear_deep_research` (4 themes × parallel workers)
- `primary_deep_research` (12 areas)
- `jc_deep_research` (18 subjects)
- `sc_deep_research` (40+ subjects)
- `tertiary_deep_research` (4 colleges + 18 schools + MAX_DEPTH=2 recursion)

#### Scenario: aistear_deep_research fans out across the 4 Aistear themes
- **WHEN** the operator invokes `aistear_deep_research`
- **THEN** the decompose agent decides the sub-questions at runtime (3-7, bounded by `DecomposerOutput`)
- **AND** each sub-question is researched in parallel via `@node(parallel_worker=True)`
- **AND** the synthesize agent merges the findings into one briefing
