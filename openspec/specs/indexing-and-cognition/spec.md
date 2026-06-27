# indexing-and-cognition Specification

## Purpose

`indexing-and-cognition` is a capability of the Cianfhoghlaim platform.
It covers the three agent knowledge surfaces — CCC (CocoIndex Code
semantic search over the monorepo source), Cognee (knowledge graph
over documentation), and the OpenCode agent + skill + MCP registry
that exposes those surfaces to the build/plan/sruth subagents. The
canonical home for the operator-facing usage docs is
[`.agents/skills/INDEXING_AND_COGNITION.md`](../../.agents/skills/INDEXING_AND_COGNITION.md).

## Background

Two parallel knowledge surfaces feed every agent in the monorepo:

- **CCC** (CocoIndex Code) — indexes 8,845 source files / 257,957
  chunks in a SQLite + BGE-M3 embedding index; backs the
  `cocoindex-code` MCP server (9 tools).
- **Cognee** — indexes 1,743 `.md` docs (~2,242 documents across 7
  typed clusters) in a Postgres+pgvector backend (the in-house
  cognee stack at `infrastructure/stacks/cognee/`); backs the
  `cognee` MCP server (10 tools).

A third registry, the **OpenCode agent + skill + MCP registry**, is
the surface that every agent (`build`, `plan`, `oideachais`,
`infrastructure`, `meaisinfhoghlaim`, `croilar`, `tuatha`) reads on
startup from `opencode.json`. Currently the registry has:

- 7 agents (1 primary + 1 read-only + 5 sruth-subagents).
- 10 MCP servers (browserbase, firecrawl, infisical, motherduck,
  chrome, cocoindex-code, cognee, graphiti, langfuse,
  croilar-devtools).
- 0 explicit skill scoping — every agent currently sees all 123
  skills in `.agents/skills/`.

## Requirements

### Requirement: CCC v1 is the canonical CocoIndex code-search surface

The system SHALL provide a single CocoIndex v1 App at
`sruth/oideachais/cocoindex_flows/codebase_indexing.py` named
`CodebaseIndex` as the canonical semantic code search surface. The
system SHALL NOT call the legacy `ccc search` CLI in any production
code path; the legacy CLI SHALL be retained only as a CLI fallback
until 2026-07-15 (per the `cocoindex-v1-migration` spec).

#### Scenario: Build-time code search uses the v1 App

- **GIVEN** the `bun run ccc:index` task in `package.json` +
  `mise.toml`
- **WHEN** the task runs
- **THEN** it invokes
  `uv run cocoindex update sruth.oideachais.cocoindex_flows.codebase_indexing:CodebaseIndex`
- **AND** writes the `codebase_chunks` LanceDB table to the
  `codebase` asset group

#### Scenario: Agent code search uses the v1 App

- **GIVEN** an OpenCode agent that needs to search the codebase
- **WHEN** the agent invokes a search tool
- **THEN** the tool routes through the `cocoindex-code` MCP server
  (which exposes the 9 ccc MCP tools backed by the v1 index)
- **AND** does NOT shell out to the legacy `ccc search` CLI

### Requirement: Cognee uses Postgres+pgvector as the unified backend

The system SHALL run Cognee against a single
`infrastructure/stacks/cognee/` Docker Compose stack that uses
`pgvector/pgvector:pg17` as the unified graph + vector backend
(`VECTOR_DB_PROVIDER=pgvector`, `GRAPH_DATABASE_PROVIDER=postgres`,
`DB_PROVIDER=postgres`). The system SHALL NOT depend on a separate
Neo4j, FalkorDB, or Memgraph container for the in-house Cognee
deployment.

#### Scenario: Cognee compose uses pgvector

- **GIVEN** `infrastructure/stacks/cognee/compose.yaml`
- **WHEN** the file is read
- **THEN** the `cognee` service declares
  `VECTOR_DB_PROVIDER: pgvector`
- **AND** the `DB_PROVIDER` and `GRAPH_DATABASE_PROVIDER` env vars
  both point at the same `cognee-postgres` service
- **AND** the `cognee-postgres` service is `pgvector/pgvector:pg17`

#### Scenario: Cognee does not depend on Neo4j

- **GIVEN** the 5 sruth-quadrant agents that call `cognee.search()`
- **WHEN** the agents run against the in-house cognee stack
- **THEN** they SHALL NOT require the
  `infrastructure/stacks/graphiti/` Neo4j container to be up
- **AND** the `cognee` MCP server's `env` block SHALL have
  exactly the 3 canonical keys (`COGNEE_API_URL`,
  `COGNEE_API_KEY`, `LLM_API_KEY`) and no `NEO4J_*` keys
  (the `graphiti` MCP server is the canonical consumer of
  `NEO4J_*` env vars, because it backs the graphiti service)

### Requirement: The 7 typed cognify clusters are the canonical Cognee dataset shape

The system SHALL expose the 7 typed cognify clusters
(`docs-data-eng`, `docs-bonneagar`, `docs-agents`, `docs-ml`,
`docs-teanga`, `docs-web`, `docs-tuatha`) as the canonical Cognee
dataset shape. Each cluster SHALL have a corresponding
`graph_model_file` declaring the entity types and edge types for
the cluster's domain (per the
`cognee_readiness_audit` 7-cluster recommendation).

#### Scenario: All 7 cluster graph model files exist

- **GIVEN** the 7 cluster names
- **WHEN** `infrastructure/scripts/cognee-graph-models/` is read
- **THEN** it SHALL contain
  `data_platform_graph.py`, `infrastructure_graph.py`,
  `agents_graph.py`, `ml_graph.py`, `celtic_language_graph.py`,
  `web_graph.py`, `tuatha_graph.py`

#### Scenario: Federated search spans all 7 clusters

- **GIVEN** an agent invokes `cognee.search(query, ...)`
- **WHEN** the search is a `GRAPH_COMPLETION` or `CHUNKS` query
- **THEN** the search SHALL span all 7 typed clusters
- **AND** results SHALL be re-ranked across clusters by score
  (federated search layer)

### Requirement: OpenCode agent registry has 7 agents

The system SHALL declare exactly 7 OpenCode agents in `opencode.json`
under the `agent` key: 1 build (primary), 1 plan (read-only primary),
and 5 sruth-subagents (oideachais, infrastructure, meaisinfhoghlaim,
croilar, tuatha). Each agent SHALL have a `description`, `model`,
`mode`, `color`, and `prompt` field. The `default_agent` SHALL be
`build`.

#### Scenario: All 7 agents declared

- **GIVEN** `opencode.json` `agent.<name>` block
- **WHEN** the JSON is read
- **THEN** it SHALL contain: `build`, `plan`, `oideachais`,
  `infrastructure`, `meaisinfhoghlaim`, `croilar`, `tuatha`
- **AND** `default_agent` SHALL be `build`

#### Scenario: Sruth-subagent prompt names the sruth

- **GIVEN** the `agent.oideachais.prompt` field
- **WHEN** the prompt is read
- **THEN** its first line SHALL name `oideachais/` (the sruth it
  serves) and reference the 4-agent
  `mise run py:typecheck && mise run turbo typecheck` quality gate

### Requirement: OpenCode MCP server registry has 10 servers

The system SHALL declare the canonical 10 MCP servers in
`opencode.json` under the `mcp` key: `browserbase`, `firecrawl`,
`infisical`, `motherduck`, `chrome`, `cocoindex-code`, `cognee`,
`graphiti`, `langfuse`, `croilar-devtools`. Every `type: local`
server SHALL have a `command` array and an `enabled: true` flag;
every server that needs a secret SHALL reference it via
`infisical://dev-baile/<svc>/<key>` (the Locket-canonical form).

#### Scenario: All 10 MCP servers declared

- **GIVEN** `opencode.json` `mcp.<name>` block
- **WHEN** the JSON is read
- **THEN** it SHALL contain all 10 servers above
- **AND** the `croilar-devtools` command path SHALL resolve to
  `sruth/croilar/mcp/devtools/index.ts` (a file that exists on
  disk)

#### Scenario: MCP secrets use Locket-canonical form

- **GIVEN** any `mcp.<name>.env.<key>` field
- **WHEN** the field value is read
- **THEN** it SHALL match the regex
  `infisical://dev-baile/<svc>/<key>` OR `${ENV_VAR_NAME}` for
  shell-expansion variables
- **AND** it SHALL NOT contain plaintext credentials

### Requirement: CCC index freshness CI gate

The system SHALL expose a CI gate
`bun run validate-ccc-freshness` that:

1. Reads `.cocoindex_code/cocoindex.db`
2. Returns exit 0 if the index was last refreshed within the
   threshold (default: 7 days for the main branch, 24 hours for
   feature branches)
3. Returns exit 1 with a clear message if the index is stale.

#### Scenario: Fresh index passes the gate

- **GIVEN** `.cocoindex_code/cocoindex.db` was refreshed 2 days
  ago
- **WHEN** `bun run validate-ccc-freshness` runs on the main
  branch
- **THEN** the script exits 0 and prints "index fresh: 2 days
  old"

#### Scenario: Stale index fails the gate

- **GIVEN** `.cocoindex_code/cocoindex.db` was refreshed 10 days
  ago
- **WHEN** `bun run validate-ccc-freshness` runs on the main
  branch
- **THEN** the script exits 1 and prints
  "index stale: 10 days old (threshold: 7 days). Run `bun run
  ccc:index` to refresh."

### Requirement: Git pre-commit hook refreshes the CCC index

The system SHALL install a git pre-commit hook at
`.git/hooks/pre-commit` that runs `bun run ccc:index` (incremental
refresh, <10s) on staged files before each commit. The hook SHALL
auto-skip when the user passes `--no-verify` (the existing git
escape hatch).

#### Scenario: Pre-commit hook runs the v1 App

- **GIVEN** the user runs `git commit -m "..."` with at least 1
  staged `.py` or `.ts` file
- **WHEN** the pre-commit hook runs
- **THEN** it invokes
  `bun run ccc:index` and either:
  - silently succeeds (index refreshed) and the commit proceeds, OR
  - prints a warning but the commit still proceeds (the hook is
    `best-effort`; we never block commits)

#### Scenario: No-verify bypass works

- **GIVEN** the user runs `git commit --no-verify -m "..."`
- **WHEN** the commit runs
- **THEN** the pre-commit hook is skipped entirely
- **AND** the commit proceeds without CCC refresh

### Requirement: Skill scoping is opt-in via per-agent `skill_filter`

The system SHALL allow each OpenCode agent to declare an optional
`skill_filter` array of skill names. When declared, only the listed
skills SHALL be loaded into that agent's context. When omitted, all
skills SHALL be loaded (the current default). The skill loader
SHALL respect the filter at agent-startup time, not retroactively.

#### Scenario: Default agent sees all skills

- **GIVEN** the `agent.build` block in `opencode.json`
- **AND** the block does NOT declare a `skill_filter` field
- **WHEN** the build agent starts
- **THEN** the skill loader SHALL load all 123 skills from
  `.agents/skills/`

#### Scenario: Sruth agent can opt in to a subset

- **GIVEN** the `agent.oideachais` block in `opencode.json`
- **AND** the block declares
  `skill_filter: ["dlt", "dagster", "baml", "cognee", "ccc", "oideachais-pipeline", "oideachais-storage", "oideachais-cocoindex-v1", "motherduck"]`
- **WHEN** the oideachais sruth-subagent starts
- **THEN** the skill loader SHALL load only those 9 skills
- **AND** the other 114 skills SHALL NOT appear in the agent's
  context

### Requirement: Agent registry is the canonical agent inventory

The system SHALL expose a canonical `sruth/meaisinfhoghlaim/agents/`
inventory (12 specialists + 1 root agent = 13 .py modules) as the
model-layer agent surface. The OpenCode `agent.<name>` blocks SHALL
be the runtime surface that dispatches to the model-layer
inventory; every sruth-subagent's prompt SHALL reference the
corresponding `sruth/<name>/AGENTS.md` and the
`agent-fleet-orchestration` skill.

#### Scenario: Model-layer inventory has 13 .py modules

- **GIVEN** the 5 sruth subagents
- **WHEN** the model-layer inventory at
  `sruth/meaisinfhoghlaim/agents/*.py` is read
- **THEN** it SHALL contain 13 `.py` modules (root + 12
  specialists): `root_agent.py`, `curriculum_agent.py`,
  `translation_agent.py`, `corpus_agent.py`, `research_agent.py`,
  `education_research_agent.py`, `bunchloch_research_agent.py`,
  `geospatial_agent.py`, `statistics_agent.py`,
  `curriculum_comparison_agent.py`, `agui_curriculum_agent.py`,
  `mcp_curriculum_agent.py`, `voice_agent.py`
- **AND** the inventory SHALL be importable as
  `sruth.meaisinfhoghlaim.agents`

#### Scenario: Sruth prompt references the per-sruth AGENTS.md

- **GIVEN** the `agent.oideachais.prompt` field
- **WHEN** the prompt is read
- **THEN** it SHALL reference `oideachais/AGENTS.md` + the
  `agent-fleet-orchestration` skill
- **AND** it SHALL NOT duplicate the content of
  `oideachais/AGENTS.md` (the prompt is a thin dispatch
  contract, not a doc)
