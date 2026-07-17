# indexing-and-cognition Specification

## Purpose

`indexing-and-cognition` is a capability of the Cianfhoghlaim
platform. It covers the three agent knowledge surfaces — CCC
(CocoIndex Code semantic search over the monorepo source),
Cognee (knowledge graph over documentation), and the OpenCode
agent + skill + MCP registry that exposes those surfaces to the
build/plan/sruth subagents. The canonical home for the
operator-facing usage docs is
[`.agents/skills/INDEXING_AND_COGNITION.md`](../../.agents/skills/INDEXING_AND_COGNITION.md).

## Background

Two parallel knowledge surfaces feed every agent in the monorepo:

- **CCC** (CocoIndex Code) — indexes 8,845 source files /
  257,957 chunks in a SQLite + BGE-M3 embedding index; backs the
  `cocoindex-code` MCP server (9 tools).
- **Cognee** — indexes 1,743 `.md` docs (~2,242 documents across
  7 typed clusters) in a Postgres+pgvector backend (the in-house
  cognee stack at `bonneagar/stacks/cognee/`); backs the
  `cognee` MCP server (10 tools).

A third registry, the **OpenCode agent + skill + MCP registry**,
is the surface that every agent (`build`, `plan`, `oideachais`,
`infrastructure`, `meaisinfhoghlaim`, `croilar`, `tuatha`) reads
on startup from `opencode.json`. Currently the registry has:

- 7 agents (1 primary + 1 read-only + 5 sruth-subagents).
- 10 MCP servers (browserbase, firecrawl, infisical, motherduck,
  chrome, cocoindex-code, cognee, graphiti, langfuse,
  croilar-devtools).
- 5 sruth-subagents opt in to a `skill_filter` (oideachais=9,
  infrastructure=16, meaisinfhoghlaim=22, croilar=12, tuatha=12
  skills); the primary `build`/`plan` agents see all 123 skills.
## Requirements
### Requirement: CCC v1 is the canonical CocoIndex code-search surface

The system SHALL provide a single CocoIndex v1 App at
`cianfhoghlaim/cocoindex_flows/codebase_indexing.py` named
`CodebaseIndex` as the canonical semantic code search surface. The
system SHALL NOT call the legacy `ccc search` CLI in any production
code path; the legacy CLI SHALL be retained only as a CLI fallback
until 2026-07-15 (per the `cocoindex-v1-migration` spec).

#### Scenario: Build-time code search uses the v1 App

- **GIVEN** the `bun run ccc:index` task in `package.json` + `mise.toml`
- **WHEN** the task runs
- **THEN** it invokes `uv run cocoindex update cianfhoghlaim.cocoindex_flows.codebase_indexing:CodebaseIndex`
- **AND** writes the `codebase_chunks` LanceDB table to the `codebase` asset group

#### Scenario: Agent code search uses the v1 App

- **GIVEN** an OpenCode agent that needs to search the codebase
- **WHEN** the agent invokes a search tool
- **THEN** the tool routes through the `cocoindex-code` MCP server (which exposes the 9 ccc MCP tools backed by the v1 index)
- **AND** does NOT shell out to the legacy `ccc search` CLI

### Requirement: Cognee uses Postgres+pgvector as the unified backend

The system SHALL run Cognee against a single
`bonneagar/stacks/cognee/` Docker Compose stack that uses
`pgvector/pgvector:pg17` as the unified graph + vector backend
(`VECTOR_DB_PROVIDER=pgvector`, `GRAPH_DATABASE_PROVIDER=postgres`,
`DB_PROVIDER=postgres`). The system SHALL NOT depend on a separate
Neo4j, FalkorDB, or Memgraph container for the in-house Cognee
deployment.

#### Scenario: Cognee compose uses pgvector

- **GIVEN** `bonneagar/stacks/cognee/compose.yaml`
- **WHEN** the file is read
- **THEN** the `cognee` service declares `VECTOR_DB_PROVIDER: pgvector`
- **AND** the `DB_PROVIDER` and `GRAPH_DATABASE_PROVIDER` env vars both point at the same `cognee-postgres` service
- **AND** the `cognee-postgres` service is `pgvector/pgvector:pg17`

#### Scenario: Cognee does not depend on Neo4j

- **GIVEN** the 5 sruth-quadrant agents that call `cognee.search()`
- **WHEN** the agents run against the in-house cognee stack
- **THEN** they SHALL NOT require the `bonneagar/stacks/graphiti/` Neo4j container to be up
- **AND** the `cognee` MCP server's `env` block SHALL have exactly the 3 canonical keys (`COGNEE_API_URL`, `COGNEE_API_KEY`, `LLM_API_KEY`) and no `NEO4J_*` keys (the `graphiti` MCP server is the canonical consumer of `NEO4J_*` env vars, because it backs the graphiti service)

### Requirement: The 7 typed cognify clusters are the canonical Cognee dataset shape

The system SHALL expose the 7 typed cognify clusters
(`docs-data-eng`, `docs-bonneagar`, `docs-agents`, `docs-ml`,
`docs-teanga`, `docs-web`, `docs-tuatha`) as the canonical Cognee
dataset shape. Each cluster SHALL have a corresponding
`graph_model_file` declaring the entity types and edge types for
the cluster's domain (per the `cognee_readiness_audit` 7-cluster
recommendation). The graph model files SHALL live at
`infrastructure/scripts/cognee-graph-models/<cluster>_graph.py`
and SHALL expose a `GRAPH_NODE_TYPES: tuple[str, ...]` constant and
a `get_graph_model()` helper.

#### Scenario: All 7 cluster graph model files exist

- **GIVEN** the 7 cluster names
- **WHEN** `infrastructure/scripts/cognee-graph-models/` is read
- **THEN** it SHALL contain `data_platform_graph.py`, `infrastructure_graph.py`, `agents_graph.py`, `ml_graph.py`, `celtic_language_graph.py`, `web_graph.py`, `tuatha_graph.py`

#### Scenario: Federated search spans all 7 clusters

- **GIVEN** an agent invokes `cognee.search(query, ...)`
- **WHEN** the search is a `GRAPH_COMPLETION` or `CHUNKS` query
- **THEN** the search SHALL span all 7 typed clusters
- **AND** results SHALL be re-ranked across clusters by score (federated search layer)

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
- **THEN** it SHALL contain: `build`, `plan`, `oideachais`, `infrastructure`, `meaisinfhoghlaim`, `croilar`, `tuatha`
- **AND** `default_agent` SHALL be `build`

#### Scenario: Sruth-subagent prompt names the sruth

- **GIVEN** the `agent.cianfhoghlaim.prompt` field
- **WHEN** the prompt is read
- **THEN** its first line SHALL name `cianfhoghlaim/` (the sruth it serves) and reference the 4-agent `mise run py:typecheck && mise run turbo typecheck` quality gate

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
- **AND** the `croilar-devtools` command path SHALL resolve to `cianfhoghlaim/mcp/devtools/index.ts` (a file that exists on disk)

#### Scenario: MCP secrets use Locket-canonical form

- **GIVEN** any `mcp.<name>.env.<key>` field
- **WHEN** the field value is read
- **THEN** it SHALL match the regex `infisical://dev-baile/<svc>/<key>` OR `${ENV_VAR_NAME}` for shell-expansion variables
- **AND** it SHALL NOT contain plaintext credentials

### Requirement: CCC index freshness CI gate

The system SHALL expose a CI gate `bun run validate-ccc-freshness`
that:

1. Reads `.cocoindex_code/cocoindex.db` (and falls back to
   `target_sqlite.db`).
2. Returns exit 0 if the index was last refreshed within the
   threshold (default: 7 days for the main branch, 24 hours for
   feature branches).
3. Returns exit 1 with a clear message if the index is stale; the
   missing-index case is a hard fail on main and a soft warning
   (exit 0) on feature branches.

#### Scenario: Fresh index passes the gate

- **GIVEN** `.cocoindex_code/cocoindex.db` was refreshed 2 days ago
- **WHEN** `bun run validate-ccc-freshness` runs on the main branch
- **THEN** the script exits 0 and prints "OK (last update: 2.0d ago, threshold: 7d on main)"

#### Scenario: Stale index fails the gate

- **GIVEN** `.cocoindex_code/cocoindex.db` was refreshed 10 days ago
- **WHEN** `bun run validate-ccc-freshness` runs on the main branch
- **THEN** the script exits 1 and prints "STALE — last index update was 10.0d ago (threshold: 7d on main). Run `bun run ccc:index` to refresh."

### Requirement: Git pre-commit hook refreshes the CCC index (best-effort)

The system SHALL install a git pre-commit hook at
`.git/hooks/pre-commit` that runs `bun run validate-ccc-freshness`
and prints a yellow WARN line to stderr when the index is stale.
The hook SHALL be best-effort: it SHALL NEVER block a commit (always
exit 0). The hook SHALL auto-skip when the user passes `--no-verify`
(the existing git escape hatch). The hook source SHALL live at
`scripts/templates/pre-commit` and SHALL be installed idempotently
via `bash scripts/install-hooks.sh` (the `mise run hooks:install`
alias).

#### Scenario: Stale index triggers a warning

- **GIVEN** the pre-commit hook is installed (via `bash scripts/install-hooks.sh`)
- **AND** `.cocoindex_code/cocoindex.db` is >7d old on the main branch
- **WHEN** the user runs `git commit -m "..."`
- **THEN** the hook prints a yellow `[pre-commit] CCC index may be stale:` line to stderr
- **AND** the commit still proceeds (exit 0 from the hook)

#### Scenario: No-verify bypass works

- **GIVEN** the pre-commit hook is installed
- **WHEN** the user runs `git commit --no-verify -m "..."`
- **THEN** the pre-commit hook is skipped entirely
- **AND** the commit proceeds without the freshness check

### Requirement: Skill scoping is opt-in via per-agent `skill_filter`

The system SHALL allow each OpenCode agent to declare an optional
`skill_filter` array of skill names. When declared, only the listed
skills SHALL be loaded into that agent's context. When omitted, all
skills SHALL be loaded (the current default). The skill loader
SHALL respect the filter at agent-startup time, not retroactively.
Primary agents (`build`, `plan`) SHALL keep no `skill_filter` (they
are the escape hatch and need the full 123-skill surface).

#### Scenario: Default agent sees all skills

- **GIVEN** the `agent.build` block in `opencode.json`
- **AND** the block does NOT declare a `skill_filter` field
- **WHEN** the build agent starts
- **THEN** the skill loader SHALL load all 123 skills from `.agents/skills/`

#### Scenario: Sruth agent can opt in to a subset

- **GIVEN** the `agent.oideachais` block in `opencode.json`
- **AND** the block declares `skill_filter: ["dlt", "dagster", "baml", "cognee", "ccc", "cianfhoghlaim-pipeline", "cianfhoghlaim-storage", "cianfhoghlaim-cocoindex-v1", "motherduck"]`
- **WHEN** the oideachais sruth-subagent starts
- **THEN** the skill loader SHALL load only those 9 skills
- **AND** the other 114 skills SHALL NOT appear in the agent's context

### Requirement: Agent registry is the canonical agent inventory

The system SHALL expose a canonical
`cianfhoghlaim/agents/` inventory (12 specialists + 1 root
agent = 13 `.py` modules) as the model-layer agent surface. The
13-module list SHALL be exposed at import time as a
`MODEL_LAYER_AGENTS: tuple[str, ...]` constant in
`cianfhoghlaim/agents/__init__.py`. The OpenCode
`agent.<name>` blocks SHALL be the runtime surface that dispatches
to the model-layer inventory; every sruth-subagent's prompt SHALL
reference the corresponding `sruth/<name>/AGENTS.md` and the
`agent-fleet-orchestration` skill.

#### Scenario: Model-layer inventory has 13 .py modules

- **GIVEN** the 5 sruth subagents
- **WHEN** the model-layer inventory at `cianfhoghlaim/agents/*.py` is read
- **THEN** it SHALL contain 13 `.py` modules (root + 12 specialists): `root_agent.py`, `curriculum_agent.py`, `translation_agent.py`, `corpus_agent.py`, `research_agent.py`, `education_research_agent.py`, `bunchloch_research_agent.py`, `geospatial_agent.py`, `statistics_agent.py`, `curriculum_comparison_agent.py`, `agui_curriculum_agent.py`, `mcp_curriculum_agent.py`, `voice_agent.py`
- **AND** the inventory SHALL be importable as `meaisinfhoghlaim.agents`
- **AND** the `MODEL_LAYER_AGENTS` tuple SHALL list exactly those 13 module basenames

#### Scenario: Sruth prompt references the per-sruth AGENTS.md

- **GIVEN** the `agent.cianfhoghlaim.prompt` field
- **WHEN** the prompt is read
- **THEN** it SHALL reference `cianfhoghlaim/AGENTS.md` + the `agent-fleet-orchestration` skill
- **AND** it SHALL NOT duplicate the content of `cianfhoghlaim/AGENTS.md` (the prompt is a thin dispatch contract, not a doc)

### Requirement: No superseded `infrastructure/legacy/{ANALYSIS,LOCKET-MODES}.md`

The system SHALL NOT include
`infrastructure/legacy/ANALYSIS.md` or
`infrastructure/legacy/LOCKET-MODES.md`. These 2 documents were
superseded by current skill docs:

  1. `ANALYSIS.md` (15,539 bytes) — superseded by
     `.agents/skills/kcg-pangolin-stack/SKILL.md`
     (2025-12 predecessor-project analysis)
  2. `LOCKET-MODES.md` (8,630 bytes) — superseded by
     `.agents/skills/kcg-locket-sidecar/SKILL.md`
     (v0 predecessor analysis)

The `infrastructure/legacy/README.md` archive index SHALL remain
as the canonical entry point for the 4 archived TypeScript
scripts (`cloudflare-dns.ts`, `pangolin-setup.ts`, `servers.ts`,
`taisce-deploy.ts`) that are still documented in README.md.

After the files are removed, there SHALL be NO dangling
cross-references to the deleted files in any active surface
of the repo (skill docs, infrastructure scripts, agent fleet
prompts, etc.).

#### Scenario: Files removed

- **WHEN** `ls infrastructure/legacy/` is run
- **THEN** the directory SHALL contain only `README.md`
- **AND** `ANALYSIS.md` + `LOCKET-MODES.md` SHALL NOT exist

#### Scenario: No dangling cross-references

- **WHEN** `grep -rn "legacy/ANALYSIS\|legacy/LOCKET-MODES" .` is run (excluding `.git`/`.venv`/`__pycache__`)
- **THEN** the only matches SHALL be inside `openspec/changes/archive/2026-06-27-infrastructure-audit-phase-2-delete-superseded-legacy-docs/` (historical record) and inside `openspec/specs/indexing-and-cognition/spec.md` (canonical spec)
- **AND** there SHALL be NO active references in `.agents/skills/*.md`, `infrastructure/*`, `spaces/*`, `sruth/*`, or any other active surface
- **AND** the 2 dangling cross-references in `.agents/skills/kcg-pangolin-stack/SKILL.md:155` + `.agents/skills/kcg-locket-sidecar/SKILL.md:201` SHALL be removed

#### Scenario: README.md remains canonical archive index

- **WHEN** `cat infrastructure/legacy/README.md` is run
- **THEN** the file SHALL document the 4 archived TypeScript scripts and the Komodo migration paths
- **AND** it SHALL remain the canonical archive index (referenced by `infrastructure/komodo/README.md:35`)

#### Scenario: Spec delta format compliant

- **WHEN** `openspec validate infrastructure-audit-phase-{2,3}-delete-superseded-legacy-docs --strict` is run
- **THEN** both changes MUST pass strict validation
- **AND** the spec delta MUST land in `openspec/specs/indexing-and-cognition/spec.md` (the canonical home for the indexing + cognition capability)

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

### Requirement: `bun run ccc:v1:search` SHALL return parseable JSON

The canonical CCC v1 search command SHALL return a JSON array of result chunks on stdout, parseable by `json.loads`, and SHALL exit with code 0.

#### Scenario: Substring search returns JSON

- **WHEN** the user runs `bun run ccc:v1:search "LANCE_DB" --limit 3`
- **THEN** the command SHALL exit with code 0
- **AND** stdout SHALL be a JSON array of dicts each with `file_path`, `line_no`, `snippet`, `relevance`
- **AND** the command SHALL NOT raise `SyntaxError` from the bun shell-escape wrapper

#### Scenario: Semantic search returns JSON

- **WHEN** the user runs `bun run ccc:v1:search "embedding similarity" --semantic --limit 5`
- **THEN** the command SHALL exit with code 0 within 10 seconds (subsequent calls; first call may take 5-10s for BGE-M3 model load)
- **AND** stdout SHALL be a JSON array ranked by vector distance

#### Scenario: Graceful fallback when canonical module is unavailable

- **WHEN** `from cianfhoghlaim.cocoindex.codebase_indexing import search_codebase` raises `ImportError` (e.g. missing `chunking.languages` sub-module in the v4 tree)
- **THEN** the wrapper SHALL fall back to a direct LanceDB query at `.cocoindex_code/lancedb/codebase_chunks.lance`
- **AND** SHALL write a `# module_import_failed: <reason>` comment to stderr (NOT stdout, so JSON parsing is unaffected)
- **AND** SHALL still return JSON on stdout

#### Scenario: ADK `ccc_search` tool delegates to the canonical wrapper

- **WHEN** the ADK `ccc_search` tool is called with `query="LANCE_DB"`, `limit=5`
- **THEN** the tool SHALL invoke `uv run python scripts/ccc_v1_search.py "LANCE_DB" --limit 15`
- **AND** SHALL NOT raise any error
- **AND** SHALL return up to 5 structured chunks

### Requirement: Lance Namespace 0.9 Contract Conformance

The `bonneagar/stacks/lakehouse/lance-sidecar/` custom Python sidecar SHALL
implement the lance-namespace 0.9 REST contract, including the
context-header rename from `x-lance-ctx-*` to `header.<name>` (introduced in
PR #358, released with lance-namespace 0.9.0 on 2026-07-01).

#### Scenario: Lance sidecar uses the v0.9 context-header prefix

- **WHEN** `bonneagar/stacks/lakehouse/lance-sidecar/main.py` is read
- **THEN** every outgoing REST request SHALL set context headers with
  the `header.<name>` prefix (NOT `x-lance-ctx-<name>`)
- **AND** `requirements.txt` SHALL pin
  `pylance>=8.0.0` (was `>=0.26.0`; the 0.x → 8.0 jump shipped 2026-07-01)
  and `lance-namespace-urllib3-client>=0.0.30` (was `>=0.0.21`; the 0.9
  release added 9 months of contract changes)

#### Scenario: Lakehouse lance-sidecar passes the v0.9 health probe

- **WHEN** `curl -sf http://localhost:8182/v1/info` returns HTTP 200
- **THEN** the response body SHALL contain `{"version": "0.9.x", ...}`
  per the upstream contract
- **AND** zero requests in the access log SHALL carry
  `x-lance-ctx-*` headers (those would indicate a stale client)

## Migrated from (2026-07-06)

- `chunkhound-code-search` — the deprecated ChunkHound capability (semantic code search via MVCC + Tree-sitter + LanceDB) was superseded by this spec; users should now use the v1 `codebase_indexing` CocoIndex App
