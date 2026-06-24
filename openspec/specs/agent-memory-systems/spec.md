# Agent Memory Systems Capability

## Purpose

`agent-memory-systems` is a capability of the Cianfhoghlaim platform. The
corresponding source code lives at `meaisinfhoghlaim/agents/` (12 specialised
agents) and `oideachais/memory/` (application-layer Cognee + Graphiti wrappers).
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

## Cross-references

- [`.agents/skills/cognee/SKILL.md`](../../.agents/skills/cognee/SKILL.md)
- [`.agents/skills/graphiti/SKILL.md`](../../.agents/skills/graphiti/SKILL.md)
- [`.agents/skills/graphiti-core/SKILL.md`](../../.agents/skills/graphiti-core/SKILL.md)
- [`.agents/skills/lancedb/SKILL.md`](../../.agents/skills/lancedb/SKILL.md)
- [`.agents/skills/falkordb/SKILL.md`](../../.agents/skills/falkordb/SKILL.md)
- [`.agents/skills/memgraph/SKILL.md`](../../.agents/skills/memgraph/SKILL.md)
- [`oideachais/memory/`](../../oideachais/memory/) (application-layer wrapper)
- [`meaisinfhoghlaim/agents/`](../../meaisinfhoghlaim/agents/) (model-layer agents)
