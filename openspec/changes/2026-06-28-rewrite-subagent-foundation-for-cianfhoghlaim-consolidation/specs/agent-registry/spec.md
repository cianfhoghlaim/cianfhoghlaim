# agent-registry Specification

## Purpose

`agent-registry` is a capability of the Cianfhoghlaim platform. It
defines the contract that the OpenCode agent + skill + MCP registry
(`opencode.json`) must satisfy to align with the v4
`cianfhoghlaim/` package layout.

The OpenCode agent + skill + MCP registry is the surface that every
subagent reads on startup from `opencode.json`. The registry
currently exposes:

- 7 agents (`build`, `plan`, `data-platform`, `infrastructure`,
  `agent-platform`, `frontend-apps`, `research`).
- 9 MCP servers (`browserbase`, `firecrawl`, `infisical`,
  `motherduck`, `chrome`, `cocoindex-code`, `cognee`, `graphiti`,
  `langfuse`).
- 4 functional + 1 research subagents opt in to a `skill_filter`
  (`data-platform=15`, `infrastructure=15`, `agent-platform=23`,
  `frontend-apps=20`, `research=11` skills).

The canonical operator-facing usage docs are at
[`.agents/skills/INDEXING_AND_COGNITION.md`](../../.agents/skills/INDEXING_AND_COGNITION.md)
(see §8 of that file for the registry surface).

## ADDED Requirements

### Requirement: Functional subagent coverage of the v4 package

The `opencode.json` `agent` registry SHALL define exactly **four
functional subagents** (`data-platform`, `infrastructure`,
`agent-platform`, `frontend-apps`) whose prompts and
`skill_filter` arrays cover every top-level subpackage of the
consolidated `cianfhoghlaim/` Python package. The system SHALL NOT
define subagents named `oideachais`, `meaisinfhoghlaim`, `croilar`,
or `tuatha` (those names reference the deleted `sruth/<quadrant>/`
quadrants).

#### Scenario: Every cianfhoghlaim subpackage is routable

- **GIVEN** the consolidated `cianfhoghlaim/` package at the repo
  root with subpackages `dlt_sources/`, `baml_src/`, `dagster_defs/`,
  `notebooks/`, `agents/meaisinfhoghlaim/`, `web/`, `stacks/`,
  `libraries/`, `cognify/`
- **WHEN** a build agent reads `opencode.json` and dispatches a
  `task` tool call
- **THEN** at least one of the 4 functional subagents can accept
  the dispatch and route to the relevant subpackage
- **AND** no `task` tool call needs to use one of the deleted
  sruth subagent names

#### Scenario: data-platform covers the data layer

- **GIVEN** the `data-platform` subagent is defined in
  `opencode.json`
- **WHEN** a task targets the data plane (DLT sources, BAML
  schemas, Dagster assets, Marimo notebooks, DuckLake / DuckDB /
  MotherDuck storage)
- **THEN** the subagent prompt references the `cianfhoghlaim/`
  paths for those targets
- **AND** the `skill_filter` includes the 6 data-layer skills
  (`dlt`, `dagster`, `baml`, `motherduck`, `duckdb`, `ducklake`)

#### Scenario: infrastructure covers the stacks layer

- **GIVEN** the `infrastructure` subagent is defined in
  `opencode.json`
- **WHEN** a task targets the Docker Compose stacks under
  `cianfhoghlaim/stacks/*/`, or Komodo / Pangolin / Locket /
  Infisical operations
- **THEN** the subagent prompt references the `cianfhoghlaim/stacks/`
  paths
- **AND** the `skill_filter` includes the 6 infrastructure skills
  (`komodo`, `pangolin`, `locket`, `infisical`, `pulumi`,
  `dagger-pipelines`)

#### Scenario: agent-platform covers the AI/ML layer

- **GIVEN** the `agent-platform` subagent is defined in
  `opencode.json`
- **WHEN** a task targets the agent layer
  (`cianfhoghlaim/agents/meaisinfhoghlaim/`), BAML extraction,
  OCR / HTR, LLM routing, Langfuse / MLflow / RAGAS observability,
  or Graphiti / Cognee memory
- **THEN** the subagent prompt references the
  `cianfhoghlaim/agents/meaisinfhoghlaim/` path
- **AND** the `skill_filter` includes the 6 core agent skills
  (`baml`, `litellm`, `langfuse`, `mlflow`, `ragas`, `cognee`,
  `graphiti`)

#### Scenario: frontend-apps covers the web layer

- **GIVEN** the `frontend-apps` subagent is defined in
  `opencode.json`
- **WHEN** a task targets the web layer
  (`cianfhoghlaim/web/apps/*/`), Convex backends, Babylon.js
  scenes, Hono / oRPC / CopilotKit / TanStack Start, or stacks/croilar /
  stacks/tuatha
- **THEN** the subagent prompt references the `cianfhoghlaim/web/`
  paths
- **AND** the `skill_filter` includes the 6 frontend-layer skills
  (`tanstack-start`, `copilotkit-develop`, `convex`, `hono`,
  `orpc`, `babylonjs`)

### Requirement: Dedicated research subagent for browser-driven investigation

The `opencode.json` `agent` registry SHALL define a dedicated
`research` subagent whose `skill_filter` includes the browser-
and search-driven skills needed for autonomous web investigation
(`browserbase`, `firecrawl`, `ccc`, `cognee`, `agent-experience`,
`company-research`, `event-prospecting`, `change-detection`,
`search`, `fetch`, `agent-observability`). The `research`
subagent is the primary executor for the 43-prompt BrowserBase
credit program documented in
`openspec/research/2026-06-28-browserbase-credit-program/`.

#### Scenario: research subagent is dispatchable

- **GIVEN** a build agent dispatches a `task` tool call with
  `subagent_type: "research"`
- **WHEN** the dispatch executes
- **THEN** opencode resolves the subagent to the `research` entry
  in `opencode.json`
- **AND** the `research` subagent has access to the 11 skills
  listed in its `skill_filter`
- **AND** the `research` subagent prompt instructs the agent to
  emit one Markdown file per prompt into
  `openspec/research/2026-06-28-browserbase-credit-program/phase-*/`

#### Scenario: research subagent skill_filter excludes unresolvable skills

- **GIVEN** the `research` subagent `skill_filter` array
- **WHEN** opencode validates the array against the directories
  under `.agents/skills/`
- **THEN** every entry resolves to an existing directory
- **AND** the `indexing-and-cognition` and `competitor-analysis`
  skills are NOT in the array (both are documented in `.md` files
  or sub-paths that do not satisfy the directory-based skill
  filter contract)

### Requirement: Broken MCP entries are removed

The `opencode.json` `mcp` registry SHALL NOT define any MCP server
whose `command` or `url` points at a non-existent path or URL.
Specifically, the `croilar-devtools` MCP server (which pointed at
`sruth/croilar/mcp/devtools/index.ts` before the v4 consolidation)
SHALL be removed.

#### Scenario: croilar-devtools MCP is gone

- **GIVEN** the v4 consolidation deleted the `sruth/croilar/`
  directory tree
- **WHEN** a build agent reads `opencode.json` `mcp` keys
- **THEN** the `croilar-devtools` key is not present
- **AND** the total MCP count is 9 (was 10 before the v4
  consolidation; was 11 before the croilar-devtools removal)

#### Scenario: All MCP commands resolve

- **GIVEN** the 9 MCP servers defined in `opencode.json`
- **WHEN** opencode validates each `command` (for stdio MCPs) or
  `url` (for HTTP MCPs) on startup
- **THEN** every entry resolves to an existing file (stdio) or a
  reachable URL (HTTP)
- **AND** `mise run lint:skills` (or equivalent MCP validation)
  emits no broken-path warnings

#### Scenario: croilar-devtools functionality is tracked separately

- **GIVEN** the `croilar-devtools` MCP removal may break
  downstream consumers of stagehand / firecrawl / codex-cli / E2B
- **WHEN** the build agent finishes the rewrite
- **THEN** a follow-up GitHub issue is opened titled
  "Migrate croilar-devtools MCP server code to
  `cianfhoghlaim/agents/api/_croilar_convex/devtools.ts`"
- **AND** the issue body references
  `openspec/specs/croilar-devtools-hub/spec.md` as the
  temporarily un-implementable spec

### Requirement: INDEXING path references are migrated

The `.agents/skills/INDEXING_AND_COGNITION.md` document SHALL NOT
contain any path reference to the deleted `sruth/<quadrant>/`
quadrants or the old `infrastructure/stacks/<name>/` locations.
Every reference SHALL point at the v4 `cianfhoghlaim/` equivalent.

#### Scenario: No stale path refs in INDEXING_AND_COGNITION.md

- **GIVEN** the INDEXING document at
  `.agents/skills/INDEXING_AND_COGNITION.md`
- **WHEN** the build agent greps for `sruth/`,
  `infrastructure/stacks/`, `croilar-devtools`, or
  `infrastructure/scripts/` substrings
- **THEN** zero matches are returned (matches inside §9's
  intentional migration table are excepted as they document the
  FROM paths for reference)
- **AND** every path reference resolves to an existing path under
  `cianfhoghlaim/`

#### Scenario: §8.1 lists the new subagent names

- **GIVEN** §8.1 of the INDEXING document ("OpenCode agent + skill
  + MCP registry")
- **WHEN** a reader consults the dispatch instructions
- **THEN** the listed `subagent_type` values are exactly
  `data-platform`, `infrastructure`, `agent-platform`,
  `frontend-apps`, `research`
- **AND** the §9 appendix documents the migration from
  `oideachais`, `infrastructure` (legacy), `meaisinfhoghlaim`,
  `croilar`, `tuatha`

#### Scenario: §8.4 health checks emit the expected counts

- **GIVEN** the §8.4 health check Python one-liners
- **WHEN** the build agent runs them against the post-rewrite
  `opencode.json`
- **THEN** `python3 -c "import json; cfg=json.load(open('opencode.json')); print('MCPs:', len(cfg['mcp']), 'Agents:', len(cfg['agent']))"`
  prints `MCPs: 9  Agents: 7`
- **AND** the per-subagent skill counts match `build=0, plan=0,
  data-platform=15, infrastructure=15, agent-platform=23,
  frontend-apps=20, research=11`

### Requirement: Build agent prompt references the new subagent set

The `opencode.json` `agent.build.prompt` field SHALL reference the
new subagent names (`data-platform`, `infrastructure`,
`agent-platform`, `frontend-apps`, `research`) and the new v4
paths (`cianfhoghlaim/`), and SHALL NOT reference the deleted
`sruth/<quadrant>/` quadrants. The prompt SHALL enumerate the
total skill count across all 5 functional + research subagents.

#### Scenario: Build agent prompt lists the 5 new subagents

- **GIVEN** the `build` agent prompt in `opencode.json`
- **WHEN** a reader consults the prompt for the workflow section
- **THEN** the prompt enumerates `data-platform`,
  `infrastructure`, `agent-platform`, `frontend-apps`, `research`
  as the 5 dispatchable subagent types
- **AND** the prompt does NOT reference `oideachais`,
  `meaisinfhoghlaim`, `croilar`, or `tuatha` as subagent names

#### Scenario: Build agent prompt cites v4 paths

- **GIVEN** the `build` agent prompt in `opencode.json`
- **WHEN** a reader consults the prompt for code-search and
  package references
- **THEN** path references resolve under `cianfhoghlaim/` (or its
  subpackages `dlt_sources/`, `baml_src/`, `dagster_defs/`,
  `notebooks/`, `agents/meaisinfhoghlaim/`, `web/`, `stacks/`,
  `libraries/`, `cognify/`)
- **AND** no path reference points at `sruth/<quadrant>/`

#### Scenario: Build agent prompt enumerates skill count

- **GIVEN** the `build` agent prompt in `opencode.json`
- **WHEN** the prompt enumerates the agent's skill inventory
- **THEN** the prompt states a total of 131 skills (was 123 in the
  pre-v4 layout; the 8-skill delta comes from the new
  `data-platform` (6 added: `celtic-ocr-evaluation`, `cocoindex`,
  `embedding-pipeline`, `duckdb`, `ducklake`, `indexing-and-cognition`
  → 5 after drop), `agent-platform` (1 added: `agent-memory-systems`
  → 0 net after the `indexing-and-cognition` drop), and
  `research` (13 brand new → 11 after the 2 drops))
- **AND** the prompt references the per-subagent skill counts as
  listed in §8.4 of the INDEXING document
