## Why

10 KCG-authoritative skills were written before the 2026-06
package state and are now out of date. The skills have been
the source of agent decisions for ~6 months, and the underlying
package releases have moved on. This change refreshes each skill
with the latest package features so agents see the 2026-06
state of the world.

## What changes

A "## 2026-06 update" section is appended to each of the
following skills:

| Skill | Update |
|:--|:--|
| `cocoindex` | CocoIndex v1.0.1–1.0.7: per-argument `memo_key`, `coco.auto_refresh`, per-slice `stats_group`, new connectors (OCI Object Storage, Apache Iggy, Turbopuffer, Neo4j, FalkorDB, LanceDB optimisations), LiteLLM STT, 8 new code-splitter languages, Postgres + SQL security fixes |
| `dagster` | `dg` CLI + Components API: `dg init`, `dg scaffold`, `dg build`, `dg dev`; YAML-defined Components; the 5 KCG code-locations (oideachais, tuath, crypteolas, croilar, meaisin_heartbeat) |
| `cognee` | Temporal cognify via `time_range=...`; session memory + `improve()` 4-stage bridge; auto-routing search via `recall(session_id=...)` |
| `oideachais-storage` | DuckLake 1.0 GA (ACID, time-travel, schema evolution, single-SQL catalog); Lance Namespace sidecar pattern; refreshed mental model table |
| `kcg-leabharlann-pipeline` | CocoIndex v1 + Cognee 0.1+ temporal in the 5-stage leabharlann flow; the 3 new v1 Apps |
| `agent-observability` | Langfuse v3 (prompt management v2, per-model cost, session grouping, dataset tracking); MLflow GenAI evaluation; RAGAS trace-based metrics; Logfire MCP preview |
| `agentic-frontend-frameworks` | AG-UI protocol (CopilotKit's agent↔UI SSE standard); Pydantic AI + Gateway + DBOS; Convex + Cloudflare integration |
| `tuatha-mmo` | Babylon.js 7 + WebGPU (the default renderer); SpacetimeDB v2 (row-level access control, subscriptions, WS compression); x402 micropayments on Base L2 (gated features only) |
| `motherduck-architecture` | (Updated in B1.) DuckLake 1.0 GA on MotherDuck; the 4 storage patterns (managed / BYOB / DuckLake / own-compute); the "when NOT to use" decision tree |
| `firecrawl` | (Updated in B2.) The Firecrawl MCP variant — see the cross-link to `browser-tools` + `firecrawl-cli` |

`stagehand` was deleted in B2; the new `browser-tools` skill
absorbs the Stagehand v3 content.

## Out of scope

- `motherduck-data-modeling`, `motherduck-analytics`,
  `motherduck-connections`, `browser-tools`, `firecrawl-cli` —
  already covered by the B1 + B2 changes
- `agent-memory-systems`, `dagger-pipelines`,
  `infrastructure-stacks`,
  `data-engineering-pipeline-documentation` — already
  2026-06-aligned in B4
