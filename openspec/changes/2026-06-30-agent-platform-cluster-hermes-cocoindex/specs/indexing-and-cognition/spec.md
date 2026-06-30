# `indexing-and-cognition` capability spec — agent-discovery + freshness delta

The indexing-and-cognition capability spec governs the 3
agent knowledge surfaces: CCC (CocoIndex Code semantic
search over the monorepo source), Cognee (knowledge graph
over documentation), and the OpenCode agent + skill + MCP
registry that exposes those surfaces to the build/plan/
sruth subagents.

This delta adds 2 new CocoIndex v1 Apps for agent discovery
(`agent_registry` + `agents_md`), 1 new Dagster sensor for
incremental re-indexing (`ccc_freshness_sensor`), 1 new
CI gate (hard-fail on PRs that touch `opencode.json` or any
`AGENTS.md` file), and 1 new Dagster asset for LiteLLM
uptime (`embedding_model_health`).

## ADDED Requirements

### Requirement: agent_registry v1 App is the canonical agent discovery surface

The system SHALL provide a CocoIndex v1 App at
`cianfhoghlaim/cocoindex/agent_registry.py` named
`AgentRegistryIndex` that indexes the 7 `opencode.json`
`agent.*` blocks + the 10 `mcp.*` server blocks into a new
`agent_registry` LanceDB table, embedded with BGE-m3
1024-dim. The App SHALL expose a query helper
`async def search_agents(query: str, kind: str = "agent",
mode: str | None = None, limit: int = 10)` that returns
ranked agent matches.

The `agent_registry` LanceDB table SHALL have the columns:
`id` (stable, via `IdGenerator()`), `kind` ("agent" | "mcp"),
`name`, `description`, `model`, `mode`, `prompt` (for agents),
`command` (for mcp), `tags` (comma-joined from opencode.json
`agent.*.tags`).

#### Scenario: search_agents returns the 7 agents ranked

- **GIVEN** `opencode.json` declares 7 agents (build, plan,
  data-platform, infrastructure, agent-platform, frontend-apps,
  research)
- **AND** the `agent_registry` v1 App has materialised
- **WHEN** a developer runs
  `await search_agents("which agent handles dagster pipelines", kind="agent", limit=3)`
- **THEN** the function SHALL return the top-3 agents ranked
  by BGE-m3 cosine similarity to the query
- **AND** the `data-platform` agent SHALL be in the top-3
  (it lists `dagster` in its `skill_filter`)

#### Scenario: search_agents returns the 10 mcp servers ranked

- **GIVEN** `opencode.json` declares 10 MCP servers
  (browserbase, firecrawl, infisical, motherduck, chrome,
  cocoindex-code, cognee, graphiti, langfuse, huggingface)
- **AND** the `agent_registry` v1 App has materialised
- **WHEN** a developer runs
  `await search_agents("which mcp server exposes langfuse traces", kind="mcp", limit=2)`
- **THEN** the function SHALL return the `langfuse` MCP
  server as the top-1 result

### Requirement: agents_md v1 App is the canonical AGENTS.md discovery surface

The system SHALL provide a CocoIndex v1 App at
`cianfhoghlaim/cocoindex/agents_md.py` named `AgentsMdIndex`
that indexes the root `AGENTS.md` + the 5 per-area AGENTS.md
files (oideachais, meaisinfhoghlaim, tuatha, croilar,
bonneagar) into a new `agents_md` LanceDB table, chunked at
2048 tokens with 256-token overlap, embedded with BGE-m3
1024-dim. The App SHALL expose a query helper
`async def search_agents_md(query: str, area: str | None = None,
limit: int = 10)`.

The `agents_md` LanceDB table SHALL have the columns: `id`
(stable), `area` ("oideachais" | "meaisinfhoghlaim" |
"tuatha" | "croilar" | "bonneagar" | "root"), `file_path`,
`chunk_index`, `text`, `routing_tables` (the 4 markdown
table blocks extracted as serialized JSON).

#### Scenario: search_agents_md finds infrastructure routes

- **GIVEN** the `agents_md` v1 App has materialised
- **WHEN** a developer runs
  `await search_agents_md("how do I add a new docker compose stack", area="bonneagar", limit=3)`
- **THEN** the function SHALL return the top-3 chunks from
  `bonneagar/AGENTS.md` ranked by BGE-m3 cosine similarity
- **AND** the top-1 result SHALL mention the 6-file
  GOLD_STANDARD pattern

#### Scenario: AGENTS.md files are the canonical discovery source

- **GIVEN** the `agents_md` v1 App has materialised
- **AND** a new agent is added to `opencode.json` with
  `description: "Handles Stack Overflow API ingest"`
- **WHEN** the `ccc_freshness_sensor` (see below) fires a
  re-index of `agents_md`
- **THEN** the new agent's description SHALL be searchable
  via `search_agents(query="Stack Overflow API ingest", limit=1)`
  within 1 hour of the commit
- **AND** no manual `bun run ccc:index` invocation is
  required

### Requirement: ccc_freshness_sensor runs every 30 min and triggers re-index when stale

The system SHALL install a Dagster sensor at
`cianfhoghlaim/dagster/sensors/ccc_freshness_sensor.py` named
`ccc_freshness_sensor` that polls
`.cocoindex_code/cocoindex.db` mtime every 30 minutes. When
the mtime is > 24 hours old on the `main` branch (or > 7 days
on a release branch), the sensor SHALL fire a `RunRequest` to
re-run the 3 CocoIndex v1 App materialisations:
`codebase_index`, `agent_registry_index`, `agents_md_index`.

The sensor SHALL log the freshness check to stdout; the
`embedding_model_health` asset (see below) SHALL surface the
staleness to Langfuse as a trace event.

#### Scenario: Stale index triggers re-index

- **GIVEN** `.cocoindex_code/cocoindex.db` was last refreshed
  25 hours ago
- **AND** the current branch is `main`
- **WHEN** the `ccc_freshness_sensor` polls
- **THEN** the sensor SHALL fire a `RunRequest` for
  `codebase_index` + `agent_registry_index` + `agents_md_index`
- **AND** the sensor SHALL emit a Dagster event log:
  `[ccc_freshness] index is stale (25.0h > 24.0h threshold); firing re-index`

#### Scenario: Fresh index is a no-op

- **GIVEN** `.cocoindex_code/cocoindex.db` was last refreshed
  2 hours ago
- **WHEN** the `ccc_freshness_sensor` polls
- **THEN** the sensor SHALL emit a no-op log:
  `[ccc_freshness] index is fresh (2.0h < 24.0h threshold); skipping`
- **AND** no `RunRequest` SHALL be fired

### Requirement: CCC freshness is a hard CI fail on PRs that touch opencode.json or AGENTS.md files

The system SHALL install a Forgejo Actions workflow at
`.forgejo/workflows/ccc-freshness.yml` that runs
`bun run validate-ccc-freshness` on every PR. The workflow
SHALL hard-fail the PR (exit 1) when **both** of the
following are true:

1. The freshness check exits 1 (index is stale).
2. The PR diff touches `opencode.json` or any `**/AGENTS.md`
   file (per `git diff --name-only origin/main...HEAD`).

The workflow SHALL print a yellow `WARN:` line on stale
indices that don't touch those paths (to keep PRs moving
when the staleness is unrelated to the change).

#### Scenario: PR touching opencode.json with stale index fails CI

- **GIVEN** `.cocoindex_code/cocoindex.db` was last refreshed
  10 days ago
- **AND** a PR is opened that modifies `opencode.json`
  (adding a new MCP server)
- **WHEN** the Forgejo Actions workflow runs
- **THEN** `bun run validate-ccc-freshness` SHALL exit 1
- **AND** the workflow SHALL hard-fail the PR with
  `STALE — last index update was 10.0d ago. PR touches opencode.json; run \`bun run ccc:index\` and push the updated index.`

#### Scenario: PR not touching opencode.json is a soft warn

- **GIVEN** `.cocoindex_code/cocoindex.db` was last refreshed
  10 days ago
- **AND** a PR is opened that modifies only
  `docs/02-data-platform/dagster-orchestration.md`
- **WHEN** the Forgejo Actions workflow runs
- **THEN** `bun run validate-ccc-freshness` SHALL exit 1
- **AND** the workflow SHALL print a yellow `WARN:` line
  to the GitHub Actions log
- **AND** the workflow SHALL exit 0 (soft warning; the
  PR can still merge)

### Requirement: embedding_model_health asset check guards LiteLLM uptime

The system SHALL provide a Dagster asset at
`cianfhoghlaim/dagster/assets/embedding_model_health.py`
named `embedding_model_health` that polls
`http://litellm:4000/health/liveliness` every 5 minutes and
computes a rolling average of the last 100 completions'
latency. The asset SHALL emit a Dagster `AssetCheck` that
fails (exit 1) when the rolling average > 500 ms.

#### Scenario: Healthy LiteLLM passes the check

- **GIVEN** LiteLLM is up and the rolling avg latency is
  120 ms
- **WHEN** the `embedding_model_health` asset check runs
- **THEN** the check SHALL exit 0
- **AND** the asset materialisation SHALL be marked as
  `success`

#### Scenario: Degraded LiteLLM fails the check

- **GIVEN** LiteLLM is up but the rolling avg latency is
  800 ms (degraded)
- **WHEN** the `embedding_model_health` asset check runs
- **THEN** the check SHALL exit 1
- **AND** a Slack notification SHALL be sent to the
  `#kcg-llm-gateway` channel via the Langfuse webhook
- **AND** the asset materialisation SHALL be marked as
  `failed`

## Cross-references

- [`.agents/skills/oideachais-cocoindex-v1/SKILL.md`](../../.agents/skills/oideachais-cocoindex-v1/SKILL.md)
- [`.agents/skills/ccc/SKILL.md`](../../.agents/skills/ccc/SKILL.md)
- [`cianfhoghlaim/cocoindex/agent_registry.py`](../../cianfhoghlaim/cocoindex/agent_registry.py)
- [`cianfhoghlaim/cocoindex/agents_md.py`](../../cianfhoghlaim/cocoindex/agents_md.py)
- [`openspec/changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/proposal.md`](../proposal.md)
