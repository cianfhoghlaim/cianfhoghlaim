---
title: 'Cianfhoghlaim - AI Agent Instructions'
domain: 'agents'
status: 'stable'
description: 'Project identity, quadrant map, critical constraints, and routing rules for AI agents working in the Cianfhoghlaim monorepo.'
read_when:
  - looking for documentation on this topic
  - starting any task in this codebase
updated: '2026-06-13'
supersedes:
  - docs/CLAUDE.md
  - docs/00-core/CLAUDE.md (prior version)
ccc_query_hints:
  - cianfhoghlaim project identity
  - monorepo quadrants routing
truth: sole

---

# Cianfhoghlaim - AI Agent Instructions

> **Read `docs/00_index.md` first** — it is the canonical routing table for every
> canonical doc, every agent skill, and every OpenSpec change. This file is
> the project identity + constraints; the index is the navigation.

## 1. PROJECT_IDENTITY

**Cianfhoghlaim** (Irish: *deep learning*) is a bilingual (en/ga) Celtic
language education platform with an AI-augmented data lakehouse, a
multi-persona portfolio surface, and a Celtic MMO consumer.

The **purpose** of the codebase is to:

- ingest Irish + UK + pan-Celtic curriculum (NCCA, SEC, DfE, CfE, CfW, CCEA, SQA, WJEC) into a unified lakehouse,
- surface it through marimo dashboards (analyst UI), TanStack front-ends (public), and a Celtic MMO (game UI),
- and back it with a graph-of-knowledge (Cognee + LanceDB + DuckLake) that AI agents can query.

## 2. QUADRANT MAP (5 top-level + 8 workspace members)

The post-restructure monorepo (June 2026) is **5 quadrants**. `infrastructure/`
is the *fifth* — it is what makes the other 4 runnable.

| Top-level dir | Quadrant | Purpose | Workspace status |
|---|---|---|---|
| `oideachais/` | **Data lakehouse** (Dagster + DLT + DuckLake + LanceDB + Cognee + CocoIndex) | The heart: 30+ DLT sources, 4-cycle curriculum pipeline, embeddings, knowledge graph | uv workspace **member** |
| `tuatha/` | **Celtic MMO consumer** (FastAPI + Axum + Babylon.js + Crypteolas + x402) | Game front-end + premium endpoints + per-character MMO content | uv workspace **member** (+ `tuatha/codeolas`, `tuatha/crypteolas`, `tuatha/apps/crypteolas_demo`) |
| `croilar/` | **Multi-persona portfolio** (TanStack + Hono + Convex + BetterAuth) | The reference implementation; Aleyum, music/CV/Labels data plane | uv workspace **member** |
| `meaisínfhoghlaim/` | **AI/ML quadrant** (agents, OCR, Celtic language data, ML pipelines, evaluation, quality, catalog) | Eight integrated components: agents, OCR/HTR, Celtic-language DLT sources, alignment, RAGAS eval, content quality, model catalog | uv workspace **member** (adopted this round) |
| `infrastructure/` | **Deploy** (Pangolin, Komodo, Forgejo, Infisical, Ansible, Pulumi, browser stack) | Sovereign zero-trust deploy; 88 Docker Compose stacks | uv workspace **member** (+ `infrastructure/browser`) |

> **Sub-packages** (8 nested workspace members that are *under* the quadrants):
> `tuatha/codeolas`, `tuatha/crypteolas`, `tuatha/apps/crypteolas_demo`,
> `infrastructure/browser`, `oideachais/mcp/mcpo`.
>
> **Total**: 5 quadrants + 8 sub-members = 13 uv-workspace packages.

## 3. CRITICAL_CONSTRAINTS

### 3.1 Database safety
- **DuckDB: SINGLE_THREADED_ONLY.** Concurrent access = segfault / data corruption. Use the `SerialDatabaseExecutor` pattern (see `docs/02-data-platform/STORAGE.md`).
- **LanceDB: MVCC safe** across processes; **single-threaded within process** via `SerialDatabaseExecutor`.
- **HNSW indexes: DROP before bulk insert** for >50 rows; rebuild after.
- **DuckLake: zero-copy registration** — register Parquet files, do not copy data.
- **Snapshots before mutations** — every data-change asset should snapshot first (for time-travel recovery).

### 3.2 Storage mental model (one-liner)
- **Writes** go to **DuckLake** (Parquet on Garage S3, PostgreSQL catalog).
- **Reads** (marimo, SPA, public) go through **MotherDuck** (`md:oideachais`).
- **Long-tail catalogue** lives in **Apache Iceberg** via Lakekeeper (port 8181/8182). The platform does not write to it today; it exists for future parity.
- **ChangeDetection.io** is *deployed* at `/Users/cianmacandeisigh/dev/kings_college_galway/infrastructure/stacks/tools/changedetection` and on `arm1-oci` — use it as the canonical change-watcher for the public sources in `oideachais/sources.yaml`.

### 3.3 LLM stack hierarchy
```
BAML (structured extraction in DE pipelines)  ←  oideachais/dlt_sources
       ↓
litellm (LLM routing)                          ←  infrastructure, root
       ↓
ADK / AGNO (agent orchestration)               ←  oideachais/agents, meaisínfhoghlaim/agents
       ↓
ccc cocoindex-code (semantic index over the codebase)  ←  .agents/skills + .cocoindex_code/
       ↓
Cognee (knowledge graph memory)                ←  oideachais/cognee_integration
```

- BAML is **mandatory** for LLM extraction inside the data engineering pipelines (`oideachais/dlt_sources`, `oideachais/cocoindex_flows`, `oideachais/cognee_integration`). It is the structured-extraction layer.
- **litellm** is the routing layer; agents and pipelines call into it via `meaisínfhoghlaim/llm_router.py` (or directly).
- **ADK + AGNO** are the agent-orchestration frameworks; they call litellm, not the other way around.
- **ccc cocoindex-code** is a *codebase* search index (different from CocoIndex; lowercase `ccc`, lives in `.cocoindex_code/`). It's what agent skills use to find the right file at runtime.
- **Cognee** is the knowledge-graph layer that turns extracted entities into a queryable graph.

### 3.4 Embedding performance (100x cost)
- **Batch ≥ 100** embeddings per API call. Unbatched = ~100× slower.
- Drop HNSW indexes for bulk inserts >50 rows; rebuild after.

### 3.5 Browser automation decision tree
For **scraping**:
1. `firecrawl` MCP (opencode.json; paid or self-hosted)
2. `sruth-browser` selfhosted (in-tree at `infrastructure/browser/sruth_browser/`)
3. `Firecrawl` API (paid fallback)

For **browser interaction** (form fills, logins):
1. `browserbase` MCP
2. `Stagehand` selfhosted
3. `skyvern` selfhosted

For **LLM-driven bulk extraction** of page descriptions: use the **site_analysis** package at `oideachais/site_analysis/` (BAML `SiteAnalysis` schema, JSON-RPC to MCP, stub mode under `USE_LOCAL_SCRAPES=true`).

### 3.6 Irish language processing
- Irish is <0.1% of web content (~20% model performance gap). Use specialized models: UCCIX-Llama2-13B-Instruct, GaBERT, Qwen2.5-Math.
- Handle dialects: Connacht, Munster, Ulster, Standard.

### 3.7 Path & namespace rules
- **Zero absolute namespaces inside `oideachais/`**: never import `oideachais.data_platform.*` or `oideachais.middleware.*` from within `oideachais/`. Use relative or local-package imports.
  - Enforced by `oideachais/tests/sources/test_cross_namespace.py`.
- **Quoted golden path** from the cross-DLT asset-key rename: every source id is `{nation}.{domain}.{entity}`. See `docs/02-data-platform/cross-domain-registry.md`.

## 4. FRONT-END TOPOLOGY (no single doc had this)

| Surface | Stack | Auth | Data plane |
|---|---|---|---|
| `oideachais/web` | TanStack Start | none (lakehouse front-end) | DuckLake / MotherDuck |
| `croilar/apps/web` | TanStack + Hono | none | Convex (TanStack queries) |
| `croilar/apps/portal` | TanStack + Hono | BetterAuth + Pocket ID SSO + SIWE (crypto wallet) | Convex + DuckLake |
| `tuatha/ui` | Babylon.js | in-game Crypteolas token | in-game state + DuckLake |
| marimo (any stack) | marimo server | none (analyst UI) | DuckLake / MotherDuck via MCP |

## 5. AGENT SKILLS

- **128** agent skills under `.agents/skills/` (was 63 under `.claude/skills/`, superseded).
- The **Skill-to-Doc map** at the bottom of `docs/00_index.md` tells you which doc to read for which skill.
- `ccc` (cocoindex-code, the lower-case CLI) is the runtime search index; `bun run ccc:search "query"` finds the right file at runtime.

## 6. OPENSPEC WORKFLOW

- **`openspec/changes/`** — proposed work in progress. Validate with `openspec validate <id> --strict`. Archive with `openspec archive <id> --yes` after deploy.
- **`openspec/specs/`** — 32 canonical capability specs. The openspec recipe says each spec needs ≥1 Requirement + ≥1 Scenario. The CI task `bun run validate-openspec-stale` flags any spec with 0 requirements.
- **`openspec/plans/`** — research artefacts and deferred roadmaps. Status: `research` or `deferred`. See `openspec/plans/STATUS.md`.
- **`docs/00-deploy-plans/`** — concrete deployment plans for the 5 deferred tangents, derived from the consolidated docs. Status: `deferred`. See `docs/00-deploy-plans/STATUS.md`.

## 7. VALIDATION COMMANDS

```bash
# Lint + typecheck
mise run lint
mise run py:typecheck

# Tests
mise run test
# OR per-tree
uv run --with pytest --with pytest-asyncio --package oideachais python -m pytest --confcutdir=oideachais oideachais/tests/

# OpenSpec
openspec validate lateralise-british-isles-domains --strict

# Doc stale-path check
bun run validate-docs

# OpenSpec stale-change / empty-spec check
bun run validate-openspec-stale

# Healthchecks
python -c "import duckdb, lancedb, dlt, dagster, cognee; print('all OK')"
```

## 8. ERROR RECOVERY

### 8.1 Database corruption
1. Stop all processes
2. Restore from `oideachais/.dagster_home/` snapshot
3. Verify single-threaded access
4. Restart with `SerialDatabaseExecutor`

### 8.2 Embedding timeout
1. Reduce batch size to 50
2. Add exponential backoff
3. Check LiteLLM rate limits
4. Consider local embedding model

### 8.3 Index rebuild failure
1. Drop all HNSW indexes
2. Vacuum database
3. Recreate indexes one at a time
4. Monitor memory usage

## 9. CONSTRAINT CHECKLIST

Before any data operation:
- [ ] Using `SerialDatabaseExecutor` for DuckDB?
- [ ] Batch size ≥100 for embeddings?
- [ ] HNSW indexes dropped for bulk >50 rows?
- [ ] BAML schema validated for LLM extraction?
- [ ] Irish content using specialized model (UCCIX / GaBERT)?
- [ ] Deduplication applied to multi-result queries?
- [ ] Cross-namespace check passes (`oideachais/tests/sources/test_cross_namespace.py`)?
- [ ] Path stale-ref check passes (`bun run validate-docs`)?
