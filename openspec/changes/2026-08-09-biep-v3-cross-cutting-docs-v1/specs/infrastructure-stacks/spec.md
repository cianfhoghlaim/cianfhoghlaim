## MODIFIED Requirements

### Requirement: BIEP v3 stack cross-cutting concerns (P3)

The system SHALL have:
1. `cross-repo-sync.md` for all 4 affected openspec changes
2. 4 spec deltas (one per jurisdiction pipeline change)
3. 4 mise task aliases
4. 3 docs files

#### Scenario: cross-repo-sync.md

- **WHEN** `find openspec/changes/ -name "cross-repo-sync.md" | wc -l` runs
- **THEN** ≥ 4 matches SHALL be found

#### Scenario: 4 new mise task aliases

- **WHEN** `mise tasks | grep "biep:v3:"` runs
- **THEN** 4 tasks SHALL be listed (lakehouse:smoke-test, registry:seed, marimo:wasm:export, test-runs:ingest)

#### Scenario: 3 new docs files

- **WHEN** `ls docs/{lakehouse/smoke-test-2026-08-06,baml/biiep-v3-client-canon,dagster/group-name-underscore-migration}.md` runs
- **THEN** all 3 files SHALL exist