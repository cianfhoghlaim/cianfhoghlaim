## ADDED Requirements

### Requirement: Project to openspec to skill feedback loop

The Cianfhoghlaim platform MUST maintain a formal feedback loop between projects, openspec changes, and skills. (1) When an openspec change is archived, the canonical skill (if any) gets a "Post-archive update" note in its cross-reference table. (2) When a project changes a BAML extraction / DLT source / Dagster asset, the corresponding skill (`baml`, `dlt`, `dagster`) gets a 1-line addition to its "When to use this skill" section. (3) When a project's `STATUS.md` / `REFACTORING.md` / README.md changes, the `data-engineering-pipeline-documentation` skill gets a link to the new content.

#### Scenario: New openspec change updates the canonical skill

- **WHEN** an openspec change is archived
- **THEN** the canonical skill (e.g. `motherduck-architecture` for a MotherDuck change) gets a "Post-archive update: 2026-06-24-..." note in its cross-reference section

#### Scenario: New DLT source updates the dlt skill

- **WHEN** a new DLT source is added under `sruth/oideachais/dlt_sources/`
- **THEN** the `.agents/skills/dlt/SKILL.md` "KCG examples" appendix gets a 1-line addition naming the new source

### Requirement: Quadrant-specific Related skills

Each quadrant's `AGENTS.md` "Related skills" section MUST list only the skills used by that quadrant (no shared "default" list across quadrants). The 4 quadrants are `oideachais`, `meaisinfhoghlaim`, `tuatha`, `croilar`, plus the cross-cutting `infrastructure` layer.

#### Scenario: sruth/oideachais/AGENTS.md lists 12 oideachais-specific skills

- **WHEN** `sruth/oideachais/AGENTS.md` is read
- **THEN** the "Related skills" section lists 12+ skills (dagster, dlt, baml, cocoindex, cognee, lancedb, falkordb, duckdb, motherduck, dignified-python, marimo, ccc, oideachais-storage, oideachais-pipeline, oideachais-leabharlann, oideachais-baml-schemas, oideachais-cognify-knowledge-graph)
- **AND** does NOT list skills specific to other quadrants (e.g. babylonjs for tuatha, hono for croilar)

#### Scenario: Each archived change points at the canonical skill

- **WHEN** an openspec change is archived
- **THEN** the archived `proposal.md` "What changes" section includes a line "Canonical skill: `.agents/skills/<skill>/SKILL.md`" naming the skill that should receive the post-archive note
