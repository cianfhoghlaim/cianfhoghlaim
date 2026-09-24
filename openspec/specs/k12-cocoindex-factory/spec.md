# k12-cocoindex-factory Specification

## Purpose
TBD - created by archiving change 2026-09-23-k12-teacher-student-pipeline-v1. Update Purpose after archive.
## Requirements
### Requirement: Per-stage K12EntitySpec dataclass
The system SHALL provide a `K12EntitySpec` dataclass in
`cocoindex_flows/british_isles/ireland/education/_shared.py`:
- `entity_id: str` (kebab-case slug)
- `stage_id: str` (one of the 6 K12_STAGES)
- `entity_type: str` ('primary_area' | 'jc_subject' | 'sc_subject' | ...)
- `entity_name_en: str`
- `entity_name_ga: str | None`
- `canonical_url: str | None`

#### Scenario: smoke

- **GIVEN** the factory wired per the spec
- **WHEN** the operator runs the smoke test
- **THEN** the requirement passes

### Requirement: Per-stage yaml config loaders
The system SHALL provide 3 yaml config loaders:
- `load_primary_modules_config()` (50 rows)
- `load_jc_subjects_config()` (18 rows)
- `load_sc_subjects_config()` (40 rows)
Total: 108 K-12 entities across the 4 stages (aistear is loaded from
the `dlt_sources/.../aistear.py` resource directly).

#### Scenario: smoke

- **GIVEN** the factory wired per the spec
- **WHEN** the operator runs the smoke test
- **THEN** the requirement passes
s_config()` (40 rows)
Total: 108 K-12 entities across the 4 stages (aistear is loaded from
the `dlt_sources/.../aistear.py` resource directly).

### Requirement: create_k12_entity_flow factory function
The system SHALL provide a `create_k12_entity_flow(config: K12EntitySpec) -> coco.App`
function that:
1. Declares `app = coco.App(coco.AppConfig(name=f"k12_{config.entity_type}_{config.entity_id}_flow"))`
2. Declares `@coco.function(name=...)` + `@coco.fn(...)` decorators (R3 conformance)
3. Returns the app

#### Scenario: smoke

- **GIVEN** the factory wired per the spec
- **WHEN** the operator runs the smoke test
- **THEN** the requirement passes
 a `create_k12_entity_flow(config: K12EntitySpec) -> coco.App`
function that:
1. Declares `app = coco.App(coco.AppConfig(name=f"k12_{config.entity_type}_{config.entity_id}_flow"))`
2. Declares `@coco.function(name=...)` + `@coco.fn(...)` decorators (R3 conformance)
3. Returns the app

### Requirement: 8 K-12 CocoIndex flows
The system SHALL provide 8 CocoIndex flows:
- `cocoindex_flows/subjects/aistear_embedding.py` (aistear principles + learning goals)
- `cocoindex_flows/subjects/primary_embedding.py` (12 primary areas)
- `cocoindex_flows/subjects/junior_cycle_embedding.py` (existing — 18 JC subjects)
- `cocoindex_flows/subjects/senior_cycle_embedding.py` (40+ SC subjects)
- `cocoindex_flows/british_isles/ireland/education/lesson_plan_flow.py` (teacher)
- `cocoindex_flows/british_isles/ireland/education/assessment_task_flow.py` (teacher)
- `cocoindex_flows/british_isles/ireland/education/class_roster_flow.py` (teacher)
- `cocoindex_flows/british_isles/ireland/education/professional_learning_flow.py` (teacher)

#### Scenario: All 8 flows wire via shared_lifespan
- **WHEN** `pn` end-to-end runs the K-12 cohort
- **THEN** all 8 flows are constructed without error + share the BAAI/bge-m3 embedder

