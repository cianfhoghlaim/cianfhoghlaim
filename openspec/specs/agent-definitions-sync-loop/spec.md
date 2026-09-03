# Agent Definitions Sync Loop (Layer 10)

## Purpose

The Layer 10 of the 10-layer pull-based sync architecture. Validates the
188 agent files + the 12-agent fleet + the 8 NCCA subject specialists
across 7 agent subdirs (agents/ + agents/adk/ + agents/agno/ +
agents/api/ + agents/tools/ + agents/tuatha/ + agents/meaisinfhoghlaim/).

Agent definition drift is silent: when a developer adds a new agent to
the 12-agent fleet but doesn't register it in `agents/agent_registry.py`
+ doesn't update `agents/routing_keywords.py` + doesn't add an
AGENTS.md, the breakage doesn't surface until the next agent
registration test. The 8 NCCA subject specialists (in
`agents/tuatha/agents/`) are particularly prone to drift because they
were added incrementally.

This change extends the sync loop with **Layer 10 — `sync:agents`** that
closes the agent definitions gap.
## Requirements
### Requirement: Layer 1 — `sync:agents-drift`

The system SHALL provide a `bash scripts/sync/agents-drift.sh` task that
detects agent definition drift across the 188 files.

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

### Requirement: Layer 2 — `sync:agents-ccc`

The system SHALL provide a `bash scripts/sync/agents-ccc.sh` task that
refreshes the CCC index + appends the **25th concept guide**
`agent-fleet-search` to `.cocoindex_code/guides.yml`.

#### Scenario: 25th concept guide surfaces the agent fleet

- **WHEN** `bash scripts/sync/agents-ccc.sh` is invoked
- **THEN** the task SHALL append the `agent-fleet-search` guide
  to `.cocoindex_code/guides.yml`
- **AND** the task SHALL run `bun run ccc:index` for incremental refresh
- **AND** a user searching CCC for "12-agent fleet" SHALL get the new
  guide in the top 3 hits

### Requirement: Layer 3 — `sync:agents-cognee`

The system SHALL provide a `bash scripts/sync/agents-cognee.sh` task
that ingests the 188 agent files into the **14th Cognee cluster**
`agent_definitions`.

#### Scenario: Cognee has 14 typed clusters after sync

- **WHEN** `cognee-mcp` is queried for the cluster list
- **THEN** the response SHALL include all 14 typed clusters
  (13 existing + `agent_definitions`)

#### Scenario: agent_definitions cluster grows over time

- **WHEN** `bash scripts/sync/agents-cognee.sh` is invoked
- **THEN** the task SHALL ingest the 188 agent files via
  `scripts/cognee_ingest_agent_definitions.py`
- **AND** the cluster SHALL have a per-file summary

### Requirement: Layer 4 — `sync:agents-test`

The system SHALL provide a `bash scripts/sync/agents-test.sh` task that
runs the agent registration test + reports which agents are properly
registered + which are missing.

#### Scenario: Agent registration test runs

- **WHEN** `bash scripts/sync/agents-test.sh` is invoked
- **THEN** the task SHALL run the agent registration test
- **AND** the task SHALL report pass/fail per agent
- **AND** the task SHALL document the manual
  `uv run python -c "from cianfhoghlaim.agents.agent_registry import AGENT_REGISTRY; assert len(AGENT_REGISTRY) >= 12"`
  flow for CI gating

### Requirement: Layer 5 — `sync:agents-lint`

The system SHALL provide a `bash scripts/sync/agents-lint.sh` task that
reports per-subdir stats + the canonical `agents/AGENTS.md` + the 8 NCCA
subject specialists + the 12-agent fleet.

#### Scenario: Per-subdir stats

- **WHEN** `bash scripts/sync/agents-lint.sh` is invoked
- **THEN** the task SHALL produce a per-subdir report to
  `stedding/sync-reports/agents-lint-{date}.md`
- **AND** the task SHALL show the per-subdir .py file counts + the 5
  AGENTS.md + the canonical agent documentation

### Requirement: Layer 6 — `sync:agents` orchestrator

The system SHALL provide a `bash scripts/sync/agents.sh` task that runs
all 5 layers in sequence.

#### Scenario: sync:agents orchestrator runs all 5 layers

- **WHEN** `bash scripts/sync/agents.sh` is invoked
- **THEN** the task SHALL run sync:agents-drift + sync:agents-ccc +
  sync:agents-cognee + sync:agents-test + sync:agents-lint in sequence
- **AND** the task SHALL write a unified report to
  `stedding/sync-reports/agents-{date}.md`

### Requirement: Agent definitions evolution feedback loop

The system SHALL grow its knowledge surface over time via the agent
definitions evolution feedback loop.

#### Scenario: Agent file change triggers re-cognify

- **WHEN** a file under `agents/` is modified
- **THEN** the next `sync:agents-cognee` SHALL detect the change
  (via file mtime comparison)
- **AND** the task SHALL re-cognify the modified file into the
  `agent_definitions` Cognee cluster
- **AND** the task SHALL update the 25th CCC concept guide to include
  the newly-modified file

### Requirement: `agents_sync_health` Dagster asset

The system SHALL provide an `agents_sync_health` Dagster asset at
`orchestration/defs/sync_assets.py` that reads the latest
`stedding/sync-reports/agents-{date}.md` + emits Dagster metadata
(file_count, agents_md_count, ncca_subject_count).

#### Scenario: agents_sync_health materializes after sync:agents

- **WHEN** the `agents_sync_health` asset materializes
- **THEN** the asset SHALL read the latest agents sync report
- **AND** the asset SHALL emit Dagster metadata:
  `file_count`, `agents_md_count`, `ncca_subject_count`,
  `agent_subdir_count`

### Requirement: agent-definitions layer status surfaces in deployment control panel

The system SHALL surface the `sync:agents` Layer 10 status in the
deployment control panel marimo notebook (`notebooks/24_deployment_control_panel.py`)
with one click-to-run button + the latest sync report preview.

#### Scenario: Deployment control panel surfaces agents layer

- **WHEN** the user opens `notebooks/24_deployment_control_panel.py`
- **THEN** the "agents" layer status SHALL show ✅ done / ⚠️ pending / 🚫 failing
- **AND** clicking the agents button SHALL emit a click-to-run marker
  (the actual `mise run sync:agents` invocation is operator-side)
- **AND** the latest sync report from `stedding/sync-reports/agents-{date}.md`
  SHALL be shown as a preview tooltip

## Cross-references

- `openspec/changes/2026-08-15-knowledge-sync-loop-v1/` (the foundation)
- `openspec/changes/2026-08-15-stacks-sync-loop-v1/` (Layer 8)
- `openspec/changes/2026-08-15-dlt-sync-loop-v1/` (Layer 9)
- `agents/` (the 12-agent fleet + the 188 .py files)
- `agents/AGENTS.md` (the canonical agent documentation)
- `agents/tuatha/` (the 8 NCCA subject specialists)