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
