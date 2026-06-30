# graphiti

## Purpose for the Cianfhoghlaim project

Graphiti is the **temporal knowledge graph** for the platform.
Its bi-temporal model is uniquely suited to curriculum data that
changes on two time axes: "valid time" (when a syllabus was in
effect for students) and "transaction time" (when the syllabus
document was published/ingested). When the Irish government
reforms the LC Maths syllabus in 2027, Graphiti records the 2023
syllabus as valid from 2023 to 2027 and the new syllabus from
2027 onward — both are queryable.

After the `centralise-data-plane` rewrite (2026-07-30) the
broken Neo4j backend profile was REMOVED; Graphiti now uses the
shared `falkordb` stack instance as its sole graph backend.
The service was also renamed from `graph` to `graphiti`.

## Why it stays in komodo/pangolin/infisical GitOps

Graphiti is a **Stage 3 stack** in the agent-platform cluster —
it depends on falkordb (Stage 1) and the LiteLLM gateway (Stage 2)
for LLM-based entity extraction. The `OPENAI_API_KEY` env points
at litellm's master key, not at OpenAI directly. The
`deploy-graphiti-bunchloch` procedure enforces the dependency
order.

## FalkorDB Backend Contract

| Resource | Docker DNS | Auth |
|:--|:--|:--|
| FalkorDB | `falkordb:6379` (external network `falkordb`) | `FALKORDB_PASSWORD` (from falkordb/*) |
| Database | `default_db` (configurable via `FALKORDB_GRAPHITI_DB`) | n/a |
| LLM endpoint | `http://litellm:4000/v1` | `OPENAI_API_KEY = LITELLM_MASTER_KEY` |

## Cross-references

- **Ops**: `bonneagar/stacks/graphiti/` (the 6-file GOLD_STANDARD)
- **Code**: `meaisinfhoghlaim/memory/` (Graphiti memory patterns per `.agents/skills/agent-memory-systems/SKILL.md`)
- **Komodo procedure**: `deploy-graphiti-bunchloch.toml` (3-stage: falkordb → graphiti → 3 health checks)
- **Pangolin**: `https://graphiti.cianfhoghlaim.ie/healthcheck` (Member role + tinyauth)

## Tags

- `host:bunchloch`
- `tier:agent-platform`
- `project:cianfhoghlaim`
- `group:memory` (depends on `foundation.falkordb` + `observability.litellm`)
