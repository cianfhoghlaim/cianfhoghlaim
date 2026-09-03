# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: Agent skills use v4 namespace paths

The system SHALL keep every `.agents/skills/` Markdown file aligned with the post-v4 `cianfhoghlaim/` namespace and directory layout. Skill documentation MUST NOT introduce pre-v4 `sruth/<quadrant>/...` path references except in archived point-in-time artifacts outside `.agents/skills/`.

For application code examples, skill documentation SHALL use import paths rooted at `cianfhoghlaim`, `meaisinfhoghlaim`, `tuatha`, or `croilar` as appropriate for the v4 package surface. For filesystem path examples, skill documentation SHALL use the actual v4 homes such as `cianfhoghlaim/dlt/`, `cianfhoghlaim/baml_src/`, `cianfhoghlaim/cocoindex/`, `cianfhoghlaim/orchestration/`, `cianfhoghlaim/agents/`, and `cianfhoghlaim/web/apps/*/`.

#### Scenario: Skill drift check stays clean

- **GIVEN** a contributor edits any file under `.agents/skills/`
- **WHEN** `grep -rln "sruth/" .agents/skills/` runs
- **THEN** the command returns 0 files
- **AND** `mise run lint:skills` reports all registered skills pass

#### Scenario: Skill examples use v4 application paths

- **GIVEN** a skill documents an oideachais DLT source
- **WHEN** it references the source's filesystem location
- **THEN** it uses `cianfhoghlaim/dlt/...` rather than `sruth/oideachais/dlt_sources/...`
- **AND** if it shows a Python import example, the example uses `from cianfhoghlaim...` for actual code imports

#### Scenario: Bonneagar infra drift remains out of repo scope

- **GIVEN** a drift reference exists inside the separate `bonneagar/` repo/worktree
- **WHEN** this Cianfhoghlaim OpenSpec change is implemented
- **THEN** the `bonneagar/` file is not modified from this repo
- **AND** any follow-up is tracked as a separate repo-boundary task
