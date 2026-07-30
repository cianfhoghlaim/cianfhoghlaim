# Spec delta: `agent-definitions-sync-loop`

This delta is part of the openspec change
`2026-08-15-agent-definitions-sync-loop-v1`. It registers the new
`sync:agents` orchestrator + the 5 sub-layers + the new Cognee
cluster + the 25th CCC concept guide.

## ADDED Requirements

### Requirement: Layer 1 - sync:agents-drift

The system SHALL provide a `bash scripts/sync/agents-drift.sh` task
that detects agent definition drift across the 188 files.

#### Scenario: Agent drift detection runs cleanly
- **WHEN** `bash scripts/sync/agents-drift.sh` is invoked
- **THEN** the task SHALL scan all 188 files at `agents/`
- **AND** the task SHALL detect:
  - Agents not registered in `agents/agent_registry.py`
  - AGENTS.md count claims that don't match the actual file count
  - Routing keywords missing from `agents/routing_keywords.py`
  - Stale model references (e.g. `gemma-3-4b-it` after the model-registry cleanup)
- **AND** the task SHALL write a per-file report to
  `stedding/sync-reports/agents-drift-{date}.md`

### Requirement: Layer 2 - sync:agents-ccc

The system SHALL provide a `bash scripts/sync/agents-ccc.sh` task
that refreshes the CCC index + appends the **25th concept guide**
`agent-fleet-search` to `.cocoindex_code/guides.yml`.

#### Scenario: 25th concept guide surfaces the agent fleet
- **WHEN** `bash scripts/sync/agents-ccc.sh` is invoked
- **THEN** the task SHALL append the `agent-fleet-search` guide
  to `.cocoindex_code/guides.yml`
- **AND** the task SHALL run `bun run ccc:index` for incremental refresh

### Requirement: Layer 3 - sync:agents-cognee

The system SHALL provide a `bash scripts/sync/agents-cognee.sh` task
that ingests the 188 agent files into the **14th Cognee cluster**
`agent_definitions`.

#### Scenario: Cognee has 14 typed clusters after sync
- **WHEN** `cognee-mcp` is queried for the cluster list
- **THEN** the response SHALL include all 14 typed clusters
  (13 existing + `agent_definitions`)

### Requirement: Layer 4 - sync:agents-test

The system SHALL provide a `bash scripts/sync/agents-test.sh` task
that runs the agent registration test + reports which agents are
properly registered + which are missing.

#### Scenario: Agent registration test runs
- **WHEN** `bash scripts/sync/agents-test.sh` is invoked
- **THEN** the task SHALL run the agent registration test
- **AND** the task SHALL report pass/fail per agent

### Requirement: Layer 5 - sync:agents-lint

The system SHALL provide a `bash scripts/sync/agents-lint.sh` task
that reports per-subdir stats + the canonical `agents/AGENTS.md` +
the 8 NCCA subject specialists + the 12-agent fleet.

#### Scenario: Per-subdir stats
- **WHEN** `bash scripts/sync/agents-lint.sh` is invoked
- **THEN** the task SHALL produce a per-subdir report to
  `stedding/sync-reports/agents-lint-{date}.md`
- **AND** the task SHALL show the per-subdir .py file counts +
  the 5 AGENTS.md + the canonical agent documentation

### Requirement: Agent definitions evolution feedback loop

The system SHALL grow its knowledge surface over time via the
agent definitions evolution feedback loop.

#### Scenario: Agent file change triggers re-cognify
- **WHEN** a file under `agents/` is modified
- **THEN** the next `sync:agents-cognee` SHALL detect the change
  (via file mtime comparison)
- **AND** the task SHALL re-cognify the modified file into the
  `agent_definitions` Cognee cluster
- **AND** the task SHALL update the 25th CCC concept guide
