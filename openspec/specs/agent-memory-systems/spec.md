# Agent Memory Systems Capability

## Purpose

`agent-memory-systems` is a capability of the Cianfhoghlaim platform. The
corresponding source code lives at `cianfhoghlaim/agents/` (12 specialised
agents) and `cianfhoghlaim/memory/` (application-layer Cognee + Graphiti wrappers).
See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for
the project identity.

This spec was renamed from `memory-systems` to disambiguate it from the OS
"memory" concept and to name the agent context.

## Background

Knowledge graph memory systems, temporal tracking, episodic memory, and
persistent agent memory with multi-backend support (Cognee, Graphiti,
LanceDB, FalkorDB, Memgraph). The full 419-line description that was here
in the old `memory-systems` spec is in the skill
[`.agents/skills/{cognee,graphiti,graphiti-core,lancedb,falkordb,memgraph}/SKILL.md`](../../.agents/skills/).
## Requirements
### Requirement: Multi-backend agent memory

The system SHALL provide persistent agent memory across sessions using
one of the supported backends.

#### Scenario: Cognee memory

- **GIVEN** an agent with Cognee memory enabled
- **WHEN** a user has multiple conversations
- **THEN** the agent recalls previous interactions via `cognee.search()`
  and `cognee.cognify()`

#### Scenario: Graphiti temporal memory

- **GIVEN** an agent with Graphiti memory enabled
- **WHEN** a knowledge graph is built with bi-temporal tracking
- **THEN** the agent can query the graph as of any point in time

#### Scenario: LanceDB semantic memory

- **GIVEN** an agent with LanceDB memory enabled
- **WHEN** a query is embedded with the BGE-M3 or BGE-large-en model
- **THEN** the agent retrieves the top-10 closest chunks from the
  relevant corpus

### Requirement: Agent memory router skill

The agent memory capability MUST be discoverable via a single router skill at `.agents/skills/agent-memory-systems/SKILL.md`. The router SHALL list the 5 backends (Cognee, Graphiti, LanceDB, FalkorDB, Memgraph) with a decision tree and a "pair this skill with" cross-reference table.

#### Scenario: Agent finds the memory router

- **WHEN** an agent searches for "agent memory", "cognee", "graphiti", "long-term memory", or "knowledge graph for agents"
- **THEN** the loader matches `.agents/skills/agent-memory-systems/SKILL.md`
- **AND** the skill points at the underlying memory skills (cognee, graphiti, lancedb, falkordb, memgraph) without duplicating their content

### Requirement: All audited stacks use canonical Infisical URI form
The system SHALL migrate every audited stack's `secrets.env` from the
legacy Jinja `{{ infisical:///key_name }}` form to the Locket-canonical
`infisical://dev-baile/<service>/key_name` form. The
`scripts/stack-doctor.sh` validator SHALL accept both forms during the
migration period.

#### Scenario: mlflow stack secrets.env uses canonical form
- **GIVEN** `bonneagar/stacks/mlflow/secrets.env`
- **WHEN** every `{{ infisical:///` line is read
- **THEN** the value matches the regex `infisical://dev-baile/mlflow/<key>`
  (canonical Locket form)

#### Scenario: lakehouse stack secrets.env uses canonical form
- **GIVEN** `bonneagar/stacks/lakehouse/secrets.env`
- **WHEN** every `{{ infisical:///` line is read
- **THEN** the value matches the regex `infisical://dev-baile/lakehouse/<key>`

#### Scenario: graphiti stack secrets.env uses canonical form
- **GIVEN** `bonneagar/stacks/graphiti/secrets.env`
- **WHEN** every `{{ infisical:///` line is read
- **THEN** the value matches the regex `infisical://dev-baile/graphiti/<key>`

#### Scenario: falkordb stack secrets.env uses canonical form
- **GIVEN** `bonneagar/stacks/falkordb/secrets.env`
- **WHEN** every `{{ infisical:///` line is read
- **THEN** the value matches the regex `infisical://dev-baile/falkordb/<key>`

#### Scenario: stack-doctor validator accepts both URI forms
- **GIVEN** any stack with secrets.env using either form
- **WHEN** `bun run validate-stacks` runs
- **THEN** the validator reports zero "no infisical:// refs" warnings
  for that stack

### Requirement: Blueprint ports match the container's internal port
The system SHALL ensure every `blueprint.yaml` `destination-port`
matches the container's internal port (the right side of the
`host:container` mapping in `compose.yaml`), not the host port.

#### Scenario: langfuse blueprint port is 3000
- **GIVEN** `bonneagar/stacks/langfuse/blueprint.yaml`
- **AND** `bonneagar/stacks/langfuse/compose.yaml` web service
  maps `3001:3000`
- **WHEN** the blueprint is read
- **THEN** `private-resources.langfuse.destination-port` is `3000`
  (the container's internal port)

#### Scenario: graphiti blueprint port is 8000
- **GIVEN** `bonneagar/stacks/graphiti/blueprint.yaml`
- **AND** `bonneagar/stacks/graphiti/compose.yaml` graph
  service exposes `8000:8000`
- **WHEN** the blueprint is read
- **THEN** `private-resources.graphiti.destination-port` is `8000`

#### Scenario: cognee blueprint port is 8000
- **GIVEN** `bonneagar/stacks/cognee/blueprint.yaml`
- **AND** `bonneagar/stacks/cognee/compose.yaml` exposes
  `8100:8000`
- **WHEN** the blueprint is read
- **THEN** `private-resources.cognee.destination-port` is `8000`
  (unchanged from the original — the audit incorrectly suggested
  8100; the host port is 8100 but the container listens on 8000)

### Requirement: All audited stacks have a pangolin.yaml
The system SHALL provide a `pangolin.yaml` (6-label private-resource
form) for every web-facing stack: `mlflow`, `langfuse`, `lakehouse`,
`graphiti`, `falkordb`, `cognee`. The `logfire` stack is exempt
because its UI is SaaS at `https://logfire.pydantic.dev`.

#### Scenario: 6 new pangolin.yaml files exist
- **GIVEN** the 6 stacks listed above
- **WHEN** each `bonneagar/stacks/<name>/pangolin.yaml` is read
- **THEN** it contains a `pangolin.private-resources.<name>` block
  with all 6 labels: `name`, `mode`, `full-domain`,
  `destination-port`, `protocol`, `roles[0]`

#### Scenario: stack-doctor reports zero "no pangolin.yaml" warnings
- **GIVEN** the 6 web-facing stacks
- **WHEN** `bun run validate-stacks` runs
- **THEN** the validator reports zero "missing pangolin.yaml"
  warnings for these 6 stacks

### Requirement: Datadog Python observability is a graceful no-op

The system SHALL show actual Python import examples using the v4 `cianfhoghlaim` package root. Legacy `from cianfhoghlaim...` examples MUST be rewritten when they are code imports rather than documentation shorthand.

#### Scenario: setup_datadog_apm import example uses cianfhoghlaim

- **GIVEN** a Python service that imports the optional Datadog setup helper
- **WHEN** the spec shows the import example
- **THEN** it uses `from cianfhoghlaim.observability.fastapi_middleware import setup_datadog_apm`
- **AND** the helper remains a graceful no-op when `ddtrace` is not installed

### Requirement: LC5 + Gemini consumers of Cognee + Graphiti + FalkorDB

The system SHALL keep the `LC5 + Gemini consumers of Cognee + Graphiti + FalkorDB` requirement inside the main `## Requirements` section of `openspec/specs/agent-memory-systems/spec.md` so OpenSpec strict validation, listing, and archive workflows can see it.

The 3 memory backends (Cognee, Graphiti, and FalkorDB) SHALL be consumed by the LC5-subject pipeline and the Gemini 6-corpus pipeline introduced by the 2026-07-03 pipeline changes.

#### Scenario: Requirement is parsed by strict validation

- **GIVEN** `openspec/specs/agent-memory-systems/spec.md`
- **WHEN** `openspec validate agent-memory-systems --strict` runs
- **THEN** the spec is valid
- **AND** the LC5/Gemini memory-backend requirement is inside the main `## Requirements` section rather than under a delta-style `## ADDED Requirements` section

#### Scenario: Cognee cognify runs over LC5 subjects and Gemini corpora

- **GIVEN** the LC5 + Gemini 6-corpus pipelines
- **WHEN** the L3 memory layer materialises
- **THEN** the system SHALL create Cognee datasets for the LC subjects and Gemini corpora

#### Scenario: Graphiti and FalkorDB initialise the pipeline memory views

- **GIVEN** the same LC5 + Gemini pipelines
- **WHEN** Graphiti and FalkorDB assets materialise
- **THEN** Graphiti streams SHALL be initialised for both pipeline families
- **AND** FalkorDB labels SHALL distinguish the LC5 knowledge graph from the Gemini 6-corpus knowledge graph

### Requirement: NCCA subject agents MUST depend on the MemoryBackend StorageBackend Protocol

The 8 NCCA subject agents MUST depend on the `MemoryBackend`
Protocol via
`from cianfhoghlaim.storage.memf import get_default_backend`
rather than importing `graphiti_client`, `falkordb_client`, or
`memgraph_client` directly.

The wire-up SHALL be exposed as the module-level
`<slug>_agent_wire` attribute holding a `WireSubjectAgent`
instance (from `cianfhoghlaim/agents/tuatha/wiring.py`).

#### Scenario: gaol_agent does not bypass the Protocol

- **GIVEN** `gael_agent.py` at `cianfhoghlaim/agents/tuatha/`
- **WHEN** `grep -n "graphiti_client\|falkordb_client\|memgraph_client" gael_agent.py` runs
- **THEN** the output SHALL be empty (0 matches)
- **AND** the module exposes `gael_agent_wire` after import

#### Scenario: 8 agents each expose a wire with a known backend kind

- **GIVEN** any of the 8 `<slug>_agent.py` modules
- **WHEN** `<slug>_agent_<slug>_agent_wire` is read
- **THEN** `wire.memory_backend_kind` is either `"protocol"`
  (the canonical case where `get_default_backend` resolves the
  `MemoryBackend` Protocol) or `None` (when the StorageBackend
  Protocol could not be imported — a graceful failure mode)

### Requirement: 5-backend `MemoryLayer` Protocol via `agents/memory_layer.py`

The system SHALL provide a `MemoryLayer` Protocol in
`agents/memory_layer.py` that exposes 5 concrete backends:

- **Cognee** — structured knowledge (entities + relationships)
- **Graphiti** — temporal knowledge graph (bi-temporal)
- **LanceDB** — vector RAG (HNSW)
- **FalkorDB** — vector + graph hybrid (Redis-compatible)
- **Memgraph** — production graph (Cypher + MAGE)

The `get_default_memory_layer()` cached factory SHALL resolve
to one of the 5 backends in the canonical order:
Cognee → Graphiti → LanceDB → FalkorDB → Memgraph.

Each `MemoryLayer` instance SHALL expose a `kind` attribute
(one of `{"cognee", "graphiti", "lancedb", "falkordb", "memgraph"}`)
and an `is_available()` method that returns `True` if the
backend is reachable in the current environment.

#### Scenario: `get_default_memory_layer` returns an implementation

- **GIVEN** `agents/memory_layer.py`
- **WHEN** `layer = get_default_memory_layer()`
- **THEN** `isinstance(layer, MemoryLayer)` SHALL be `True`
- **AND** `layer.kind` SHALL be one of
  `{"cognee", "graphiti", "lancedb", "falkordb", "memgraph"}`
- **AND** the returned layer SHALL be cached (subsequent calls
  return the same instance)

#### Scenario: 5 backends are available in the registry

- **GIVEN** `agents/memory_layer.py`
- **WHEN** `python -c "from cianfhoghlaim.agents.memory_layer import MEMORY_LAYERS; print(len(MEMORY_LAYERS))"`
- **THEN** the output SHALL be 5
- **AND** the keys SHALL be `{"cognee", "graphiti", "lancedb", "falkordb", "memgraph"}`

### Requirement: Graceful degradation when memory backend unavailable

The system SHALL NOT propagate `ConnectionError` or
`RuntimeError` when any of the 5 memory backends are
unreachable in the current environment. The cached
`get_default_memory_layer()` factory SHALL fall through to
the next available backend in the cascade order.

Each agent SHALL attach a `memory_layer_kind` field that
reports which backend was successfully resolved.

#### Scenario: factory falls through to the next available backend

- **GIVEN** Cognee is unreachable (e.g. port 8000 not listening)
- **WHEN** `layer = get_default_memory_layer()`
- **THEN** the factory SHALL fall through to Graphiti
- **AND** if Graphiti is also unreachable, the factory SHALL
  fall through to LanceDB
- **AND** the cascade SHALL continue until a backend is found
- **AND** the returned `layer.kind` SHALL be the first
  available backend in the cascade order

#### Scenario: 12 agents have a `memory_layer_kind` field populated

- **GIVEN** the 12 agents are wired via `agents/wiring.py`
- **WHEN** `python -c "from cianfhoghlaim.agents import AGENT_REGISTRY; [print(k, v.memory_layer_kind) for k, v in AGENT_REGISTRY.items()]"`
- **THEN** the command exits 0
- **AND** each agent SHALL have a `memory_layer_kind` field
  set to one of the 5 backend kinds
- **AND** no `ConnectionError` or `RuntimeError` SHALL be raised

### Requirement: `MemoryBackend` Protocol is smoke-tested + the 8 NCCA agents have no direct graphiti/falkordb imports

The system SHALL smoke-test the `MemoryBackend` Protocol +
`get_default_backend()` factory
(at `storage/memf.py`) in a CI-runnable pytest
module that verifies the cascade behaviour
(Graphiti → FalkorDB → InMemoryLanceDB) without requiring
Graphiti or FalkorDB to be reachable in the test environment.

The 8 NCCA subject ADK specialists
(`agents/tuatha/{gael,math,hist,geog,chem,comp,engl,appm}_agent.py`)
SHALL NOT import `graphiti_client`, `falkordb_client`, or
`memgraph_client` directly; they MUST consume the canonical
`MemoryBackend` Protocol via the
`agents/tuatha/wiring.py` module's
`get_default_backend()` binding (or `wire_subject_agent(...)`
which delegates to it).

#### Scenario: `test_memory_backend_smoke.py` exercises the 3-scenario factory contract

- **GIVEN** `tests/test_memory_backend_smoke.py`
- **WHEN** `uv run pytest tests/test_memory_backend_smoke.py`
  runs in a CI environment without Graphiti / FalkorDB reachable
- **THEN** 3 tests SHALL pass:
  - `test_get_default_backend_returns_implementation` —
    `isinstance(backend, MemoryBackend)` AND
    `backend.kind in {"graphiti", "falkordb", "in_memory_lancedb"}`
  - `test_add_episode_round_trips` — adding an `Episode`
    followed by `await backend.search(query, k=1)` returns at
    least 1 hit whose snippet contains the episode body
  - `test_reset_default_backend_returns_fresh_instance` —
    `reset_default_backend()` clears the cached singleton and
    `get_default_backend()` returns a new instance

#### Scenario: 8 NCCA subject agents have zero direct memory-client imports

- **GIVEN** the 8 NCCA subject agent modules at
  `agents/tuatha/{gael,math,hist,geog,chem,comp,engl,appm}_agent.py`
- **WHEN** `grep -n "graphiti_client\|falkordb_client\|memgraph_client"
  agents/tuatha/<slug>_agent.py` runs for each of
  the 8 agents
- **THEN** the output SHALL be empty (0 matches per agent)
- **AND** each agent module SHALL import at least one symbol
  from `agents/tuatha/wiring.py` (the canonical
  wire-up module that depends on `get_default_backend()`)

### Requirement: NEW — In-tree path references are repo-relative

All documentation, scripts, and tools that reference IaC stack files MUST use the repo-relative path `bonneagar/stacks/<name>/...`, NOT the pre-v7 standalone-repo URL pattern. This MUST be enforced by a CI grep that fails the build if the pre-v7 URL pattern appears in any new commit.

#### Scenario: Stack file path is repo-relative

- **WHEN** a script or doc references an IaC stack file
- **THEN** it SHALL use the path `bonneagar/stacks/<name>/<file>`
  (relative to the repo root)
- **AND** it SHALL NOT reference the standalone-repo URL
  `https://github.com/cianfhoghlaim/bonneagar/...`

### Requirement: PlanetScale Postgres Centralisation (agent-memory-systems)

The system SHALL migrate the Cognee + Graphiti + LanceDB + FalkorDB + Memgraph memory backends per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7.

#### Scenario: Cognee connects to PlanetScale PG

- **GIVEN** the Phase B change has archived
- **WHEN** `bonneagar/stacks/cognee/compose.yaml` is inspected
- **THEN** the local Postgres SHALL be removed
- **AND** `DATABASE_URL` SHALL point at PlanetScale PG
- **AND** the `pgvector` extension SHALL be enabled on the PlanetScale branch

#### Scenario: FalkorDB, Memgraph, Graphiti, LanceDB continuity

- **GIVEN** the change has archived
- **WHEN** the per-stack compose.yaml is inspected for FalkorDB / Memgraph
- **THEN** FalkorDB and Memgraph (key-value / graph stores) SHALL remain on their specialised backends
- **AND** only the relational metadata stores SHALL move to PlanetScale PG
- **AND** the decision row in the umbrella spec R7 SHALL reflect this

### Requirement: Memory-stack secret contract is uniform across all 5 backends

The system SHALL expose a uniform `infisical://dev-baile/<svc>/<key>`
URI form for every secret consumed by the 5 memory backends
(`cognee`, `graphiti`, `lancedb`, `falkordb`, `memgraph`). Every
`secrets.env` file SHALL pass `bun run validate-stacks --strict
--check-grammar` with zero MIXED warnings. The legacy Jinja
`{{ infisical:///key?path=/svc }}` form SHALL NOT appear in any
memory-backend `secrets.env` file.

#### Scenario: All 5 backends declare secrets in canonical URI form

- **GIVEN** `bonneagar/stacks/{cognee,graphiti,lancedb,falkordb,memgraph}/secrets.env`
- **WHEN** each file is read
- **THEN** every URI line SHALL match the regex `^[^=]+=infisical://dev-baile/<svc>/<key>$`
- **AND** zero lines SHALL match the legacy `{{ infisical:///... }}` Jinja form

#### Scenario: stack-doctor --strict --check-grammar reports zero mixed stacks

- **WHEN** `bun run validate-stacks --strict --check-grammar` runs
- **THEN** the validator SHALL report `MIXED: 0` for all 5 memory-backend stacks
- **AND** the overall exit code SHALL be 0

### Requirement: Memory-stack health is exposed via the marimo doctor

The system SHALL expose the 5-backend memory-stack health via a
dedicated marimo notebook at `notebooks/24_lakehouse_memory_doctor.py`
AND a CLI doctor at `scripts/lakehouse-memory-doctor.ts` (invoked
through `mise run lakehouse:memory:doctor`). The notebook SHALL
display a 5-column grid (one per backend) with per-backend status,
endpoint ping latency, last cognify/episode timestamp, and vector-index
row count. The CLI SHALL write a JSON health report to
`stedding/memory-health/<utc-ts>.json`.

#### Scenario: Operator opens the marimo memory doctor

- **WHEN** the operator runs `marimo edit notebooks/24_lakehouse_memory_doctor.py`
- **THEN** the notebook SHALL display a 5-column grid: cognee / graphiti / lancedb / falkordb / memgraph
- **AND** each column SHALL show: container status (Up/Down), endpoint ping latency in ms, last cognify/episode timestamp, vector-index row count
- **AND** a "federated search" expander SHALL demo a single query routed across all 5 backends via the `MemoryLayer` Protocol from `agents/memory_layer.py`

#### Scenario: CLI doctor emits a JSON health report

- **WHEN** the operator runs `mise run lakehouse:memory:doctor`
- **THEN** the script SHALL probe the 5 backends via:
  - `GET http://cognee:8000/health`
  - `GET http://graphiti:8000/healthcheck`
  - `GET http://lakehouse-lance-namespace:8182/v1/info`
  - `redis-cli -h falkordb ping`
  - `GET http://memgraph:7687`
- **AND** the script SHALL write a JSON report to `stedding/memory-health/<utc-ts>.json`
- **AND** the script SHALL exit 1 if any backend reports `not_healthy`

## Cross-references

- [`.agents/skills/cognee/SKILL.md`](../../.agents/skills/cognee/SKILL.md)
- [`.agents/skills/graphiti/SKILL.md`](../../.agents/skills/graphiti/SKILL.md)
- [`.agents/skills/graphiti-core/SKILL.md`](../../.agents/skills/graphiti-core/SKILL.md)
- [`.agents/skills/lancedb/SKILL.md`](../../.agents/skills/lancedb/SKILL.md)
- [`.agents/skills/falkordb/SKILL.md`](../../.agents/skills/falkordb/SKILL.md)
- [`.agents/skills/memgraph/SKILL.md`](../../.agents/skills/memgraph/SKILL.md)
- [`cianfhoghlaim/memory/`](../../cianfhoghlaim/memory/) (application-layer wrapper)
- [`cianfhoghlaim/agents/`](../../cianfhoghlaim/agents/) (model-layer agents)

## Migrated from (2026-07-06)

- `cross-domain-registry` — the 8-nation × 7-domain asset-key contract was absorbed into the agent-memory-systems namespace
