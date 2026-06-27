# Spec Delta: no-dead-cognee-ingest-archive-script

## ADDED Requirements

### Requirement: No dead `cognee-ingest-archive.py`

The system SHALL NOT include
`infrastructure/scripts/cognee-ingest-archive.py`. This 434-line
script ingested 4 target groups that were all deleted or
restructured by the `docs-restructuring` +
`docs-skills-consolidation-pipeline` +
`centralize-agent-context-and-automate` openspec changes (rounds
1-9 of docs consolidation):

  1. `docs/archive/2026-06-06-*` (deleted by `docs-restructuring`)
  2. `docs/*.pdf` at project root (deleted by `docs-restructuring`)
  3. `docs/auto-deploy-stacks.toml` (deleted by `docs-restructuring`)
  4. `docs/INDEX.md` + `docs/00_index.md` (replaced by
     `.agents/skills/INDEXING_AND_COGNITION.md`)

The active Cognee ingestion helper SHALL remain
`infrastructure/scripts/cognee-ingest-docs.py` (184 lines, wired
into 3 `mise.toml` task aliases + `.forgejo/workflows/cognee-ingest.yaml`
+ `.github/workflows/cognee-ingest.yaml` + the
`agent-observability` skill).

#### Scenario: Script file removed

- **WHEN** `ls infrastructure/scripts/cognee-ingest-archive.py` is run
- **THEN** the file SHALL NOT exist
- **AND** `ls infrastructure/scripts/` SHALL contain only the 8 active scripts: `cognee-ingest-docs.py`, `cognee-graph-models/` (dir), `create-olm-clients.sh`, `deploy-cf.sh`, `dev.sh`, `setup-pangolin-komodo.sh`, `stack.sh`, `sync-blueprints.sh`

#### Scenario: Active sibling script still works

- **WHEN** `mise run cognee:ingest --dry-run` is executed
- **THEN** the canonical `cognee-ingest-docs.py --dry-run --all` SHALL run cleanly
- **AND** the active `cognee-ingest-docs.py` SHALL remain unchanged (no try/except ImportError fallback to the deleted script)

#### Scenario: No fallback shims

- **WHEN** the round 11 change is committed
- **THEN** there SHALL be no `try/except ImportError` fallback, no `__getattr__` lazy import, no deprecation warning, no `.bak` file
- **AND** the deleted script SHALL be removed outright (the file is preserved at `openspec/changes/archive/2026-06-27-infrastructure-audit-phase-1-delete-dead-cognee-ingest-archive/` if needed)

#### Scenario: Pre-existing user-in-flight modifications preserved

- **WHEN** the round 11 change is committed
- **THEN** the user's pre-existing modification to `infrastructure/scripts/cognee-ingest-docs.py` SHALL remain unchanged (out of scope — only the dead archive script is touched)