# Stacks Sync Loop (Layer 8)

## Purpose

The Layer 8 of the 8-layer pull-based sync architecture. Validates the 89 Docker Compose stacks at `bonneagar/stacks/` (per `infrastructure-stacks` spec) + closes the IaC surface gap detected in the Week 4 audit (the 4 known violators + the 109 stack-doctor CRITICALS).
## Requirements
### Requirement: Layer 1 — `sync:stacks-drift`

The system SHALL provide a `bash scripts/sync/stacks-drift.sh` task that detects GOLD_STANDARD violations + name collisions + legacy `oideachais/` references in the 89 stacks at `bonneagar/stacks/`.

#### Scenario: Stacks drift detection runs cleanly

- **WHEN** `bash scripts/sync/stacks-drift.sh` is invoked
- **THEN** the task SHALL scan all 89 stacks at `bonneagar/stacks/`
- **AND** the task SHALL detect:
  - Stacks missing any of the 6 GOLD_STANDARD files (compose.yaml + sidecar.yaml + secrets.env + pangolin.yaml + blueprint.yaml + .env.example)
  - Name collisions (e.g. `meaisínfhoghlaim` with fada vs `meaisinfhoghlaim` without)
  - Legacy `oideachais/` references in stack YAML / env files
- **AND** the task SHALL write a per-stack report to `stedding/sync-reports/stacks-drift-{date}.md`

### Requirement: Layer 2 — `sync:stacks-ccc`

The system SHALL provide a `bash scripts/sync/stacks-ccc.sh` task that refreshes the CCC index + appends the **23rd concept guide** `stack-catalog-search` to `.cocoindex_code/guides.yml`.

#### Scenario: 23rd concept guide surfaces the stack catalog

- **WHEN** `bash scripts/sync/stacks-ccc.sh` is invoked
- **THEN** the task SHALL append the `stack-catalog-search` guide to `.cocoindex_code/guides.yml`
- **AND** the task SHALL run `bun run ccc:index` for incremental refresh
- **AND** a user searching CCC for "stack-catalog-search" SHALL get the new guide in the top 3 hits

### Requirement: Layer 3 — `sync:stacks-cognee`

The system SHALL provide a `bash scripts/sync/stacks-cognee.sh` task that ingests the 89 stack catalog entries into the **12th Cognee cluster** `stacks_catalog`.

#### Scenario: Cognee has 12 typed clusters after sync

- **WHEN** `cognee-mcp` is queried for the cluster list
- **THEN** the response SHALL include all 12 typed clusters (11 existing + `stacks_catalog`)

### Requirement: Layer 4 — `sync:stacks-validate`

The system SHALL provide a `bash scripts/sync/stacks-validate.sh` task that runs `bash scripts/stack-doctor.sh` + parses the output.

#### Scenario: stack-doctor audit runs

- **WHEN** `bash scripts/sync/stacks-validate.sh` is invoked
- **THEN** the task SHALL run `bash scripts/stack-doctor.sh`
- **AND** the task SHALL parse the output to extract:
  - The total CRITICAL count (109 per Week 4 audit)
  - The 4 known GOLD_STANDARD violators (browser, ludusavi, moonlight, storybook)
  - The 89 stacks count

### Requirement: Layer 5 — `sync:stacks-health`

The system SHALL provide a `bash scripts/sync/stacks-health.sh` task that reports per-stack health (GOLD_STANDARD status + drift count + Cognee cluster populated + CCC indexed).

#### Scenario: Per-stack health report

- **WHEN** `bash scripts/sync/stacks-health.sh` is invoked
- **THEN** the task SHALL produce a per-stack report to `stedding/sync-reports/stacks-health-{date}.md`
- **AND** the report SHALL show the per-stack GOLD_STANDARD status + the drift count + the Cognee cluster status

### Requirement: Stacks evolution feedback loop

The system SHALL grow its knowledge surface over time via the stacks evolution feedback loop.

#### Scenario: stack file change triggers re-cognify

- **WHEN** a file under `bonneagar/stacks/<stack>/` is modified
- **THEN** the next `sync:stacks-cognee` SHALL detect the change (via file mtime comparison)
- **AND** the task SHALL re-cognify the modified stack into the `stacks_catalog` Cognee cluster
- **AND** the task SHALL update the 23rd CCC concept guide to include the newly-modified stack

### Requirement: `stacks_sync_health` Dagster asset

The system SHALL provide a `stacks_sync_health` Dagster asset at `orchestration/defs/sync_assets.py` that reads the latest `stedding/sync-reports/stacks-{date}.md` + emits Dagster metadata (stack_count, gold_standard_clean_count, gold_standard_violator_count, legacy_oideachais_ref_count).

#### Scenario: stacks_sync_health materializes after sync:stacks

- **WHEN** `mise run sync:stacks` writes a new report to `stedding/sync-reports/stacks-{date}.md`
- **THEN** the `stacks_assets_sensor` SHALL fire (within the 1-hour minimum_interval_seconds)
- **AND** the `stacks_sync_health` asset SHALL re-materialize with the new metrics

### Requirement: Stacks sync dashboard notebook

The system SHALL provide a marimo dashboard at `notebooks/27_stacks_sync_dashboard.py` that consumes `stedding/sync-reports/stacks-{date}.md` + surfaces the 89-stack per-stack status + the 4 known violators + the 6-file GOLD_STANDARD pattern.

#### Scenario: Stacks dashboard renders the per-stack table

- **WHEN** `uv run marimo edit notebooks/27_stacks_sync_dashboard.py` is invoked
- **THEN** the notebook SHALL display the per-stack GOLD_STANDARD status table
- **AND** the notebook SHALL display the 4 known violators (browser, ludusavi, moonlight, storybook)
- **AND** the notebook SHALL display the 12 Cognee clusters (incl. `stacks_catalog`)

### Requirement: `stacks-sync` skill

The system SHALL provide a `.agents/skills/stacks-sync/SKILL.md` skill that documents Layer 8 + the 5 sub-layers + the stacks evolution feedback loop.

#### Scenario: stacks-sync skill appears in the skill count

- **WHEN** `mise run lint:skills` is invoked
- **THEN** the count SHALL be 58 (was 57 — added `stacks-sync`)

### Requirement: 23rd CCC concept guide `stack-catalog-search`

The system SHALL append the 23rd CCC concept guide `stack-catalog-search` to `.cocoindex_code/guides.yml`.

#### Scenario: stack-catalog-search surfaces the 89 stacks

- **WHEN** a user runs `ccc search "stack compose.yaml sidecar.yaml pangolin"`
- **THEN** the response SHALL include the 23rd concept guide in the top 3 hits
- **AND** the guide SHALL list the 89 stacks + the 6-file GOLD_STANDARD pattern

### Requirement: sync:stacks also validates Tailscale + Cloudflare sidecar consistency

The system SHALL extend `sync:stacks-validate` to also verify that
every stack with `network_mode: host` or `internal: true` has a
matching Tailscale ACL entry at `bonneagar/tailscale/acl-{host}.json`
+ a Cloudflare tunnel route at `bonneagar/cloudflare/tunnel-routes/`.

#### Scenario: stack with internal: true has a missing Tailscale ACL

- **GIVEN** `bonneagar/stacks/agent-os/compose.yaml` has `internal: true`
- **WHEN** `mise run sync:stacks-validate` is invoked
- **THEN** the task SHALL check for `bonneagar/tailscale/acl-bunchloch.json`
- **AND** the task SHALL fail if the ACL doesn't reference the stack's
  5 service ports + the 2 outbound credentials paths
- **AND** the report SHALL list the missing ACL entries

#### Scenario: All stacks have complete Tailscale + Cloudflare integration

- **GIVEN** all 89 stacks have `internal: true` or `network_mode: host`
- **WHEN** `mise run sync:stacks-validate` is invoked
- **THEN** the task SHALL verify each stack has a matching Tailscale ACL
  + Cloudflare tunnel route
- **AND** the task SHALL exit 0 if all stacks are consistent
- **AND** the task SHALL exit 1 if any stack is missing the integration

## Cross-references

- `openspec/changes/2026-08-15-knowledge-sync-loop-v1/` (the foundation)
- `openspec/changes/2026-08-15-retroactive-pre-v7-cleanup-v1/` (Layer 6)
- `openspec/changes/2026-08-15-baml-sync-loop-v1/` (Layer 7)
- `openspec/specs/infrastructure-stacks/spec.md` (the 89-stack catalogue)
- `bonneagar/stacks/` (the 89 stacks)
- `scripts/stack-doctor.sh` (the canonical stack audit)
- `scripts/sync/` (the existing 8 sync scripts)
