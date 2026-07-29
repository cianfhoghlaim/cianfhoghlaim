# knowledge-sync-loop — delta for 2026-08-15-knowledge-sync-loop-v1

## ADDED Requirements

### Requirement: Layer 1 — Path sync
The system SHALL provide a `mise run sync:paths` task that detects pre-v4 / pre-v7 path drift across the 8 target subdirectories (bonneagar, dlt_sources, orchestration, baml_src, cocoindex, motherduck, meaisinfoghlaim, agents) + the canonical IaC root (bonneagar) + the root manifests (pyproject.toml, mise.toml, turbo.json, package.json, tsconfig.json).

#### Scenario: Path sync runs cleanly
- **WHEN** `mise run sync:paths` is invoked
- **THEN** the task SHALL grep for 6 pre-v7 path patterns (`cianfhoghlaim/dlt/`, `cianfhoghlaim/baml/`, `infrastructure/stacks/`, `infrastructure/komodo/`, `sruth/cianfhoghlaim/`, `infrastructure/iac/dagster/`)
- **AND** the task SHALL write a per-pattern report to `stedding/sync-reports/paths-{date}.md`
- **AND** the task SHALL exit 0 if no matches, exit 1 if any matches

#### Scenario: Retroactive cleanup runs as part of sync:paths
- **WHEN** `sync:paths` is invoked the first time
- **THEN** the task SHALL bulk-sed the 6 known source files with `sruth/` refs in `cocoindex/`
- **AND** the task SHALL replace `sruth/cianfhoghlaim/cocoindex_flows` with `cocoindex/codebase_indexing`
- **AND** the task SHALL mark the `tests_pkg_temp/` ref for deletion in a follow-up change

### Requirement: Layer 2 — CCC index sync
The system SHALL provide a `mise run sync:ccc` task that refreshes the CocoIndex Code (CCC) index + appends the 20th concept guide `openspec-archive-search` to `.cocoindex_code/guides.yml`.

#### Scenario: CCC index refreshes incrementally
- **WHEN** `mise run sync:ccc` is invoked
- **THEN** the task SHALL run `bun run ccc:index` (the incremental path, <10s on the M4 MacBook)
- **AND** the task SHALL append the 20th concept guide `openspec-archive-search` to `.cocoindex_code/guides.yml` if not already present
- **AND** the task SHALL write a per-CCC summary to `stedding/sync-reports/ccc-{date}.md`

#### Scenario: Concept guide surfaces openspec changes
- **WHEN** a user searches CCC for "BIEP v3 Ireland full coverage"
- **THEN** CCC SHALL return the 20th concept guide `openspec-archive-search` in the top 3 hits
- **AND** the guide SHALL list the 5 most recent openspec changes in the `files:` array

### Requirement: Layer 3 — Cognee graph sync
The system SHALL provide a `mise run sync:cognee` task that ingests openspec changes + openspec specs + agent skills into 3 new Cognee clusters.

#### Scenario: Cognee clusters grow over time
- **WHEN** `mise run sync:cognee` is invoked
- **THEN** the task SHALL run 4 Cognee ingestion scripts (2 existing + 2 new for openspec + skills)
- **AND** the task SHALL write a per-cluster summary to `stedding/sync-reports/cognee-{date}.md`

#### Scenario: Cognee has 10 typed clusters after sync
- **WHEN** `cognee-mcp` is queried for the cluster list
- **THEN** the response SHALL include all 10 typed clusters (7 existing + 3 new: `openspec_changes`, `openspec_specs`, `agent_skills`)

### Requirement: Layer 4 — Skill sync
The system SHALL provide a `mise run sync:skills` task that validates the 57 agent skills' frontmatter + path references.

#### Scenario: Skill validation passes cleanly
- **WHEN** `mise run sync:skills` is invoked
- **THEN** the task SHALL run `bash .agents/skills/lint-skills.sh` (the canonical 53+ skills pass)
- **AND** the task SHALL run `python scripts/validate_skill_references.py` to grep-check each `SKILL.md` for path references that don't exist on disk
- **AND** the task SHALL write a per-skill report to `stedding/sync-reports/skills-{date}.md`

#### Scenario: Stale skill detection
- **WHEN** a skill's `SKILL.md` was last modified more than 90 days ago
- **THEN** the sync:skills task SHALL list it in the `stale-skills` section of the report
- **AND** the deployment control panel (notebook 24) SHALL surface the stale-skill list

### Requirement: Layer 5 — MCP health check
The system SHALL provide a `mise run sync:mcp` task that pings all 14 MCP servers with a 5s timeout per server + 30s total timeout.

#### Scenario: All MCP servers reachable
- **WHEN** `mise run sync:mcp` is invoked
- **THEN** the task SHALL ping each of the 14 servers (browserbase, firecrawl, infisical, motherduck, chrome, cocoindex-code, cognee, graphiti, langfuse, hermes, agent-registry, agents-md, apple-photos, huggingface)
- **AND** the task SHALL write a per-server health report to `stedding/sync-reports/mcp-{date}.md`
- **AND** the task SHALL exit 0 if all 14 are reachable, exit 1 if any are down

### Requirement: Sync orchestrator
The system SHALL provide a `mise run sync:all` task that runs Layer 1-5 in sequence + produces a unified summary report.

#### Scenario: Full sync produces a unified report
- **WHEN** `mise run sync:all` is invoked
- **THEN** the task SHALL run `sync:paths`, `sync:ccc`, `sync:cognee`, `sync:skills`, `sync:mcp` in sequence
- **AND** the task SHALL write a unified summary to `stedding/sync-reports/all-{date}.md`
- **AND** the task SHALL exit 0 if all 5 layers pass, exit 1 if any layer fails

### Requirement: Skill evolution feedback loop
The system SHALL grow its knowledge surface over time via the skill evolution feedback loop.

#### Scenario: SKILL.md update triggers re-cognify
- **WHEN** a `.agents/skills/<slug>/SKILL.md` file is modified
- **THEN** the next `mise run sync:skills` SHALL detect the change
- **AND** the task SHALL re-cognify the skill into the `agent_skills` Cognee cluster
- **AND** the task SHALL reindex CCC

### Requirement: openspec evolution feedback loop
The system SHALL grow its knowledge surface over time via the openspec evolution feedback loop.

#### Scenario: openspec change archival triggers re-cognify
- **WHEN** an openspec change is archived via `openspec archive <change-id> --yes`
- **THEN** the next `mise run sync:openspec-to-ccc` SHALL update the 20th concept guide to include the newly-archived change
- **AND** the next `mise run sync:cognee` SHALL cognify the archived change's `proposal.md` + `tasks.md` into the `openspec_changes` Cognee cluster

### Requirement: MCP evolution feedback loop
The system SHALL grow its knowledge surface over time via the MCP evolution feedback loop.

#### Scenario: opencode.json modification triggers health check
- **WHEN** `opencode.json` is modified (a new MCP server added or an existing one updated)
- **THEN** the next `mise run sync:mcp` SHALL detect the change
- **AND** the task SHALL validate the new server is reachable + responds to a healthcheck
- **AND** the task SHALL add the new server to the Cognee `agent_skills` cluster

### Requirement: Dagster sync_health asset
The system SHALL provide a Dagster asset `sync_health` that materializes the latest sync state.

#### Scenario: sync_health materializes on cron
- **WHEN** the `0 */4 * * *` cron fires (every 4 hours)
- **THEN** the `sync_health` asset SHALL read the latest `stedding/sync-reports/all-{date}.md`
- **AND** the asset SHALL emit Dagster metadata: `paths_sync_time`, `ccc_chunk_count`, `cognee_cluster_count`, `skill_pass_rate`, `mcp_server_count_healthy`
- **AND** the asset SHALL trigger a downstream Dagster job `stale_skill_alert` if `skill_pass_rate < 0.95`

### Requirement: Deployment control panel consumes sync reports
The system SHALL provide a marimo notebook `notebooks/24_deployment_control_panel.py` that consumes the sync health reports.

#### Scenario: Deployment control panel shows 5 layer statuses
- **WHEN** a user opens the notebook in marimo
- **THEN** the notebook SHALL read the latest `stedding/sync-reports/all-{date}.md`
- **AND** the notebook SHALL display the 5 layer statuses at the top (paths / ccc / cognee / skills / mcp) with pass/fail indicators
- **AND** the notebook SHALL drill down to the per-layer reports via sidebar links