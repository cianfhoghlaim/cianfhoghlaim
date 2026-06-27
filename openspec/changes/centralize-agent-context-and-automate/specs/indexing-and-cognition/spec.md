## ADDED Requirements

### Requirement: Cognee cluster graph model files are the canonical dataset shape
The system SHALL provide a `graph_model_file` for each of the 7
typed cognify clusters at
`infrastructure/scripts/cognee-graph-models/<cluster>_graph.py`.
Each file SHALL declare the entity types (nodes) + edge types
(relationships) for its cluster's domain. The 7 clusters are:
`docs-data-eng`, `docs-bonneagar`, `docs-agents`, `docs-ml`,
`docs-teanga`, `docs-web`, `docs-tuatha`.

#### Scenario: All 7 cluster graph model files exist
- **GIVEN** the canonical 7-cluster cognify model documented in
  `.agents/skills/INDEXING_AND_COGNITION.md` §2.3
- **WHEN** `infrastructure/scripts/cognee-graph-models/*.py` is
  read
- **THEN** it SHALL contain exactly 7 files:
  `data_platform_graph.py`, `infrastructure_graph.py`,
  `agents_graph.py`, `ml_graph.py`, `celtic_language_graph.py`,
  `web_graph.py`, `tuatha_graph.py`

#### Scenario: Cluster graph model file declares entity types
- **GIVEN** `infrastructure/scripts/cognee-graph-models/data_platform_graph.py`
- **WHEN** the file is read
- **THEN** it SHALL declare the 6 entity types for the
  Data Platform cluster: `DagsterAsset`, `DltPipeline`,
  `LakehouseTable`, `CocoIndexFlow`, `LanceDBIndex`,
  `SqlMeshModel`
- **AND** the entity types SHALL be exposed as a
  `GRAPH_NODE_TYPES: tuple[str, ...]` constant for tooling

### Requirement: Cognee MCP server env has only the 3 canonical keys
The system SHALL declare the `cognee` MCP server config in
`opencode.json` with exactly 3 env keys: `COGNEE_API_URL`,
`COGNEE_API_KEY`, and `LLM_API_KEY`. No `NEO4J_*` env vars SHALL
appear in the `cognee` MCP server's `env` block (the in-house
cognee stack uses Postgres+pgvector, not Neo4j). The
`graphiti` MCP server is the canonical consumer of `NEO4J_*` env
vars (it backs the graphiti service, which depends on Neo4j).

#### Scenario: opencode.json mcp.cognee.env has the 3 canonical keys
- **GIVEN** the `opencode.json` `mcp.cognee` block
- **WHEN** the `env` sub-object is read
- **THEN** it SHALL contain exactly the 3 keys: `COGNEE_API_URL`,
  `COGNEE_API_KEY`, `LLM_API_KEY`
- **AND** it SHALL NOT contain any `NEO4J_*` key

### Requirement: Model-layer agent registry is the canonical 13-agent inventory
The system SHALL expose a `MODEL_LAYER_AGENTS: tuple[str, ...]`
constant at `sruth/meaisinfhoghlaim/agents/__init__.py` listing
the 13 model-layer agent modules (1 root + 12 specialists) that
the OpenCode sruth-subagents dispatch to.

#### Scenario: MODEL_LAYER_AGENTS has 13 entries
- **GIVEN** `sruth/meaisinfhoghlaim/agents/__init__.py`
- **WHEN** the `MODEL_LAYER_AGENTS` constant is imported
- **THEN** it SHALL contain exactly 13 entries: `root_agent`,
  `curriculum_agent`, `translation_agent`, `corpus_agent`,
  `research_agent`, `education_research_agent`,
  `bunchloch_research_agent`, `geospatial_agent`,
  `statistics_agent`, `curriculum_comparison_agent`,
  `agui_curriculum_agent`, `mcp_curriculum_agent`,
  `voice_agent`

### Requirement: OpenCode agents may opt in to a skill subset
The system SHALL allow each OpenCode agent in `opencode.json` to
declare an optional `skill_filter: list[str]` field. When declared,
only the listed skills SHALL be loaded into that agent's context.
When omitted, all 123 skills SHALL be loaded (the current default
for the `build` and `plan` primary agents).

#### Scenario: Sruth-subagent declares a skill_filter
- **GIVEN** the `agent.oideachais` block in `opencode.json`
- **AND** the block declares
  `skill_filter: ["dlt", "dagster", "baml", "cognee", "ccc",
  "oideachais-pipeline", "oideachais-storage",
  "oideachais-cocoindex-v1", "motherduck"]`
- **WHEN** the oideachais sruth-subagent starts
- **THEN** the skill loader SHALL load only those 9 skills
- **AND** the other 114 skills SHALL NOT appear in the agent's
  context

#### Scenario: Primary agent has no skill_filter
- **GIVEN** the `agent.build` or `agent.plan` block in
  `opencode.json`
- **WHEN** the agent starts
- **THEN** the `skill_filter` field SHALL be absent (or null)
- **AND** all 123 skills SHALL be loaded

### Requirement: CCC index freshness CI gate
The system SHALL expose a CI gate script
`scripts/validate-ccc-freshness.ts` that reads
`.cocoindex_code/cocoindex.db`, computes the index age, and
returns:
- exit 0 if the index is fresh (≤ 7 days for `main`, ≤ 24 hours
  for any other branch)
- exit 1 with a clear "index stale" message otherwise.

The script SHALL be wired into `package.json` + `mise.toml` as
`bun run validate-ccc-freshness` and `mise run
validate-ccc-freshness`.

#### Scenario: Fresh index passes the gate
- **GIVEN** `.cocoindex_code/cocoindex.db` was refreshed 2 days
  ago on the `main` branch
- **WHEN** `bun run validate-ccc-freshness` runs
- **THEN** the script exits 0 and prints
  "index fresh: 2 days old (threshold: 7 days)"

#### Scenario: Stale index fails the gate
- **GIVEN** `.cocoindex_code/cocoindex.db` was refreshed 10 days
  ago on the `main` branch
- **WHEN** `bun run validate-ccc-freshness` runs
- **THEN** the script exits 1 and prints
  "index stale: 10 days old (threshold: 7 days). Run
  `bun run ccc:index` to refresh."

### Requirement: Best-effort pre-commit hook refreshes the CCC index
The system SHALL install a git pre-commit hook at
`.git/hooks/pre-commit` (via the `scripts/install-hooks.sh`
installer) that runs `bun run ccc:index` (incremental refresh,
<10s) on staged files before each commit. The hook SHALL be
best-effort: it warns but never blocks the commit. The
`--no-verify` flag SHALL skip the hook entirely (the existing
git escape hatch).

#### Scenario: Pre-commit hook runs the v1 App
- **GIVEN** the user runs `git commit -m "..."` with at least 1
  staged `.py` or `.ts` file
- **WHEN** the pre-commit hook runs
- **THEN** it invokes `bun run ccc:index` and either:
- silently succeeds (index refreshed) and the commit proceeds, OR
- prints a warning to stderr but the commit still proceeds

#### Scenario: --no-verify bypasses the hook
- **GIVEN** the user runs `git commit --no-verify -m "..."`
- **WHEN** the commit runs
- **THEN** the pre-commit hook is skipped entirely
- **AND** the commit proceeds without CCC refresh

### Requirement: v0 CocoIndex modules are scheduled for hard removal on 2026-07-15
The system SHALL declare the 10 deprecated v0 CocoIndex modules in
`sruth/oideachais/cocoindex_flows/_v0_archive/` as scheduled for
hard removal on 2026-07-15. A `DEPRECATED.md` file at the root of
`_v0_archive/` SHALL document the retirement timeline, the
replacement (the v1 App `sruth/oideachais/cocoindex_flows/codebase_indexing.py`),
and the deprecation warning emitted by `bun run ccc:search`.

#### Scenario: DEPRECATED.md exists in _v0_archive/
- **GIVEN** `sruth/oideachais/cocoindex_flows/_v0_archive/DEPRECATED.md`
- **WHEN** the file is read
- **THEN** it SHALL document the 2026-07-15 hard-removal date
- **AND** it SHALL point to
  `sruth/oideachais/cocoindex_flows/codebase_indexing.py` as the
  v1 replacement

#### Scenario: Legacy ccc:search emits a deprecation warning
- **GIVEN** the user runs `bun run ccc:search "foo"`
- **WHEN** the task runs
- **THEN** it SHALL print
  "DEPRECATED: ccc:search will be removed on 2026-07-15. Use
  ccc:v1:search instead." to stderr
- **AND** the legacy `ccc search "foo"` CLI call SHALL still
  execute (the deprecation is a warning, not a removal)
