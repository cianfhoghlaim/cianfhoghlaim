# drizzle-agentic-schema Specification

## Purpose
TBD - created by archiving change 2026-09-24-web-agentic-deep-refactor-v1. Update Purpose after archive.

## Requirements

### Requirement: K-12 agentic tables + student + teacher_workload + class_registry
The system SHALL provide 12 new Drizzle tables (per the 2026-09-24 change):
- `project` (singleton — the canonical cianfhoghlaim project)
- `student` (K-12 student profile: class_id + year_level + SEN + EAL)
- `class_registry` + `class_roster` (per-class membership)
- `teacher_workload` (per-teacher timetable + SEN tutorials + CPD periods)
- `agent_lesson_plan`, `agent_homework_item`, `agent_cba_plan`, `agent_wellbeing_checkin`, `agent_exam_timetable`, `agent_sen_record` (the 6 K-12 agentic workflow outputs)

#### Scenario: lesson_planner_agent writes a lesson plan to agent_lesson_plan
- **WHEN** the lesson_planner_agent (ADK 2 Pillar-1 workflow) returns a LessonPlan
- **THEN** the lesson_planner tool writes one row to agent_lesson_plan
- **AND** the SPA's CopilotKit /actions endpoint returns the lesson plan via GET /agent_lesson_plan/:id

### Requirement: Drizzle migration is SQLite-flavor compatible
The system SHALL use `TEXT` (JSON-encoded strings) for JSON columns (per Cloudflare D1 + PGlite + better-sqlite3 compatibility). NOT `jsonb` (which is PostgreSQL-only).

#### Scenario: The migration runs on D1
- **WHEN** `bun run drizzle-kit migrate` runs against a Cloudflare D1 database
- **THEN** all 12 new tables are created without `jsonb` errors
- **AND** the Python + TS layers use `json.loads` / `json.dumps` to read + write the JSON-encoded TEXT columns

### Requirement: Foreign-key cascading deletes
The system SHALL use `onDelete: "cascade"` for the FK from agent_* tables → student + student → class_registry (per GDPR + Children First Act 2015 — when a student leaves the school, their agentic outputs go with them).

#### Scenario: GDPR delete cascades
- **WHEN** `DELETE FROM student WHERE id = 's00003'`
- **THEN** the corresponding rows in agent_lesson_plan + agent_homework_item +
  agent_cba_plan + agent_wellbeing_checkin + agent_exam_timetable + agent_sen_record
  are also deleted (cascade)
