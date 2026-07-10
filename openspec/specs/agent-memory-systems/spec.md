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
The system SHALL treat Datadog APM + LLMObs as an opt-in optional
backend. When the `ddtrace` / `datadog` packages are not installed
(they are not in the production image), the `setup_datadog_apm` and
`setup_datadog_llmobs` functions SHALL be no-ops. The Pydantic Settings
`datadog_enabled` field SHALL default to `False` so the no-op path is
the canonical default.

#### Scenario: setup_datadog_apm is a no-op when ddtrace is missing
- **GIVEN** a Python service that imports
  `from cianfhoghlaim.observability.fastapi_middleware import setup_datadog_apm`
- **AND** the `ddtrace` package is not installed
- **WHEN** `setup_datadog_apm(app)` is called at app startup
- **THEN** the function returns `None` without raising

#### Scenario: unified_tracer datadog_enabled default is False
- **GIVEN** `cianfhoghlaim/observability/unified_tracer.py`
- **WHEN** the `datadog_enabled` parameter is read
- **THEN** the default value is `False` (not `True`)

#### Scenario: Pydantic Settings datadog_enabled default is False
- **GIVEN** `cianfhoghlaim/config/base.py` or
  `cianfhoghlaim/ocr/config/base.py`
- **WHEN** the `datadog_enabled` field default is read
- **THEN** the value is `Field(default=False)`

#### Scenario: logfire is the canonical Python tracing backend
- **GIVEN** the observability skill
  `.agents/skills/agent-observability/SKILL.md`
- **WHEN** "Layer 1: Traces" is read
- **THEN** it references Langfuse + Logfire (not Datadog APM + LLMObs)

<!-- v4 extension — 2026-07-03 -->

### Requirement: LC5 + Gemini consumers of Cognee + Graphiti + FalkorDB

The 3 memory backends (Cognee + Graphiti + FalkorDB) SHALL be
consumed by the new LC5-subject pipeline (5 subjects) and the new
Gemini 6-corpus pipeline (224 PDFs across 6 corpora) introduced in
the 2026-07-03 changes.

#### Scenario: Cognee cognify runs over 5 LC subjects + 6 Gemini corpora

- **GIVEN** the LC5 + Gemini 6-corpus pipelines (per
  `openspec/changes/2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams/`
  and `openspec/changes/2026-07-03-gemini-6-corpus-pipeline/`)
- **WHEN** the L3 layer materialises
- **THEN** 5 + 6 = 11 Cognee datasets SHALL be created:
  - 5 LC: `oideachais_<subject>` for chemistry / computer_science /
    gaeilge / geography / mathematics
  - 6 Gemini: `gemini_<corpus>_research` for law / medical /
    politics / culture / technology / other

#### Scenario: Graphiti temporal streams for LC5 + Gemini

- **GIVEN** the same LC5 + Gemini pipelines
- **WHEN** Graphiti adds episodes
- **THEN** 5 LC Graphiti streams + 6 Gemini Graphiti streams = 11
  total streams SHALL be initialised
- **AND** for the Gemini pipeline, the `event_time` SHALL be
  extracted from PDF prose (NOT file mtime) per the user decision
  "PDF content only"

#### Scenario: FalkorDB cross-subject graph for LC5 + cross-corpus for Gemini

- **GIVEN** the same LC5 + Gemini pipelines
- **WHEN** FalkorDB labels are queried
- **THEN** `falkordb_label="lc5_knowledge_graph"` SHALL contain
  the Subject → Topic → LO → Year → Q graph (5 LC subjects merged)
- **AND** `falkordb_label="gemini_6_corpus_kg"` SHALL contain the
  Corpus → CaseProfile → Party → Jurisdiction → Statute → TimelineEvent
  graph (6 Gemini corpora merged)


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
