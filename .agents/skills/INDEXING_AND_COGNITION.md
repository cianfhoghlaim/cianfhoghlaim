---
name: indexing-and-cognition
description: Consolidated setup + MCP reference for the three agent knowledge surfaces — ccc (CocoIndex Code, semantic code search), cognee (knowledge graph over docs), and firecrawl_mcp (live web via the 12 Firecrawl MCP tools). Use when an agent or team member asks "how do I set up ccc?", "how do I start cognee?", "what MCP tools are available for code search?", "what MCP tools are available for doc cognition?", "where is the dual-search workflow documented?", "when should I use firecrawl_search vs ccc:search?", or "why isn't ccc finding X?". Single source of truth for the indexing + cognition half of the agent stack. Lives at .agents/skills/INDEXING_AND_COGNITION.md (this file).
---

# Indexing & Cognition — Setup + MCP Reference

The Cianfhoghlaim monorepo runs **three parallel knowledge surfaces**
that every agent consumes via MCP:

| Surface | What it indexes | Backend | MCP server | Use for |
|:--|:--|:--|:--|:--|
| **CCC** (CocoIndex Code) | 8,845 source files / 257,957 chunks | SQLite + BGE-M3 embeddings | `cocoindex-code` (`ccc mcp`) | "Where is BAML extraction implemented?" "What calls `run_conformance_check`?" |
| **Cognee** | Docs (1,743 `.md` files, ~2,242 docs across 7 typed clusters) | Neo4j graph + LanceDB vectors + DeepSeek V4 Pro | `cognee` (`cognee-mcp`) | "What is the architecture pattern for the agent fleet?" "How does the cognify pipeline differ across stages?" |
| **Firecrawl MCP** | Live web (search / scrape / crawl / map / agent / interact / batch / parse / research / developer) | Firecrawl SaaS + 12 MCP tools + 43M-paper Research Index | `firecrawl` (the platform-level MCP) | "What does upstream say about X right now?" "Find the GitHub issue about this bug" "Find papers on BAML / OCR / curriculum" |

**The triple-search insight (post-2026-08-14):** CCC returns code;
Cognee returns docs; Firecrawl MCP returns live upstream state. An
agent asking "find how BAML extraction is implemented, and does the
upstream BAML still require the same patterns?" gets the code file
from CCC, the architecture explanation from Cognee, AND the current
upstream state from Firecrawl — then merges. The
[`dual-search-architecture`](../openspec/specs/dual-search-architecture/spec.md)
spec formalises the contract.

---

## 1. CCC — Semantic Code Search

### Current state (auto-verified)

| Metric | Value |
|:--|:--|
| Project | `/Users/cianmacandeisigh/dev/kings_college_galway` |
| Settings | `.cocoindex_code/settings.yml` |
| Index DB | `.cocoindex_code/target_sqlite.db` (2.1 GB) |
| Flow state | `.cocoindex_code/cocoindex.db` (incremental tracking) |
| Chunks | **257,957** |
| Files | **8,845** |
| Top languages | javascript (218,719), python (15,236), markdown (8,615), css (4,750), json (2,421), yaml (2,317), typescript (1,666), tsx (1,269), rust (445) |
| Concept guides | **20** in `.cocoindex_code/guides.yml` (loaded into search results when matched) — the 20th is `openspec-archive-search` (added by the `2026-08-15-knowledge-sync-loop-v1` change) |

The index is **already healthy and ccc-ready** — no initial
build needed. The round-1 `cocoindex_readiness_audit`
confirmed 1.4 GB → 2.1 GB as more docs were added; refresh
<10s incremental / ~2-5 min full rebuild.

### First-time setup

```bash
# 1. Install ccc (one-time)
# Already installed at ~/.local/bin/ccc on the M4 MacBook.
# If missing:
#   uv tool install cocoindex-code
#   # OR: brew install cocoindex-code

# 2. Initialize the project (one-time per machine)
bun run ccc:init
# Creates .cocoindex_code/{settings.yml, cocoindex.db, target_sqlite.db}

# 3. Build the index (one-time, ~2-5 min for full monorepo)
bun run ccc:index

# 4. Verify
ccc status
# Expected: "Chunks: 257957  Files: 8845"
```

### Daily-use commands

```bash
# Incremental refresh (only changed files, <10s)
bun run ccc:index

# Semantic search (top-5, ranked by embedding similarity)
bun run ccc:search "Dagster asset partition definition"

# Search with filters
bun run ccc:search --lang python --path 'cianfhoghlaim/*' "BAML extraction function"

# Paginate results
bun run ccc:search --offset 5 --limit 5 "BAML extraction function"

# Summarise a file or directory (uses project's summary feature)
ccc describe cocoindex/_lifespan.py

# List + read concept guides (loaded from .cocoindex_code/guides.yml)
ccc describe .                       # project overview
# Guides surface in search results tagged [guide]; follow the ccc guide <slug> hint
```

### CCC + CocoIndex v1 handoff (round-8 architecture)

Per the `docs-skills-consolidation-pipeline` change (2026-06-16),
the v1-native replacement for the standalone `ccc search` CLI is
the **`cocoindex/codebase_indexing.py`**
CocoIndex v1 App, registered in Dagster under the `codebase`
asset group. It uses the **same embedding model** (`BAAI/bge-m3`)
and the **same LanceDB HNSW index** as the rest of the data
lakehouse.

```bash
# The ccc:index alias now delegates to the v1 App
bun run ccc:index

# v1 search via Python (replaces `ccc search "<query>"`)
uv run python -c "
from cianfhoghlaim.cocoindex.codebase_indexing import code_search
print(code_search('BAML extraction', limit=5))
"
```

A **`codebase_code_graph` Dagster asset** (round-8 phase 1, 2026-06-23)
adds a code-graph companion with 7 node types (`File`, `Function`,
`Class`, `Method`, `Module`, `Interface`, `Variable`) + 7 edge
types (`CONTAINS`, `IMPORTS`, `CALLS`, `EXTENDS`, `IMPLEMENTS`,
`USES`, `DEFINES`). Query via `search_code_graph(file_path=...,
node_type=...)`.

### CCC MCP features (9 tools exposed via `ccc mcp`)

The `cocoindex-code` MCP server (`opencode.json` → `ccc mcp`)
exposes the following tools to every agent:

| MCP tool | What it returns | When to use |
|:--|:--|:--|
| `cocoindex-code_search(query, limit, languages, paths)` | Ranked `[file_path, line_range, score]` tuples (semantic, embedding-based, not keyword) | **Primary discovery tool** — use before grep/find per `AGENTS.md` |
| `cocoindex-code_describe(path)` | Per-file or per-directory summary (public API, contracts, role) | When you already know the path |
| `cocoindex-code_index(refresh)` | Incremental or full re-index | After making significant changes |
| `cocoindex-code_status` | Chunk count, file count, language histogram | Audit / health-check |
| `cocoindex-code_init` | Create `.cocoindex_code/` (one-time per machine) | First-time setup |
| `cocoindex-code_reset` | Wipe index + settings | Recovery from corrupt state |
| `cocoindex-code_doctor` | System health diagnostics | Troubleshooting |
| `cocoindex-code_daemon` | Daemon management (start/stop) | Long-running indexing jobs |
| `cocoindex-code_mcp` | Run as stdio MCP server | The MCP entry point itself |

> **Note:** Some tools (`describe`, `guide`) only exist in ccc
> v0.9+; check `ccc --help` on your machine for the current
> command list.

---

## 2. Cognee — Knowledge Graph over Docs

### Current state (auto-verified)

| Metric | Value |
|:--|:--|
| Stack path | `bonneagar/stacks/cognee/` (Docker Compose) |
| Container | `cognee/cognee:latest` (v1.1.2), port 8100 → 8000 |
| Graph backend | Neo4j (from `bonneagar/stacks/graphiti/`) |
| Vector store | LanceDB (Cognee local mode) |
| LLM | DeepSeek V4 Pro via `https://api.deepseek.com/v1` (OpenAI-compatible) |
| Embedding | OpenAI `text-embedding-3-small` |
| Auth | `ENABLE_BACKEND_ACCESS_CONTROL=false` (local dev), `CACHING=false` |
| Datasets | 7 typed clusters (see §2.3) |

> **Status check:** On the local M4 (bunchloch), the cognee
> container is **not currently running** — Docker daemon isn't
> started. To bring it up, follow §2.1. The MCP server config
> in `opencode.json` is already wired; once the container is
> up, agents immediately gain access via `cognee` MCP.

### 2.1 First-time setup

```bash
# 1. Start Neo4j (Cognee's graph backend)
cd bonneagar/stacks/graphiti
docker compose up neo4j -d
# Verify: curl -s http://localhost:7474 | head -3

# 2. Start Cognee with DeepSeek API (auto-hydrated from Infisical)
cd ../cognee
docker compose up -d
sleep 10  # wait for migrations

# 3. Verify
curl -s http://localhost:8100/docs | head -5    # Swagger HTML
curl -s http://localhost:8100/health | head -5  # health endpoint

# 4. Register a user (one-time, required for auth-gated endpoints)
curl -X POST http://localhost:8100/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@cianfhoghlaim.ie","password":"devpassword"}'
```

### 2.2 Daily-use commands

```bash
# Add documents (HTTP, recommended for batch)
curl -X POST http://localhost:8100/api/v1/add \
  -F "data=@docs/01-cognee/README.md" \
  -F "datasetName=docs-agents"

# Cognify (build the knowledge graph from added docs)
curl -X POST http://localhost:8100/api/v1/cognify \
  -H "Content-Type: application/json" \
  -d '{"datasets": ["docs-agents"]}'

# Cognify in background (for large corpora)
curl -X POST http://localhost:8100/api/v1/cognify \
  -H "Content-Type: application/json" \
  -d '{"datasets": ["docs-agents"], "runInBackground": true}'

# Search (4 most useful types)
# 1. Chunks — fast semantic vector search
curl -X POST http://localhost:8100/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"searchType":"CHUNKS","query":"BAML extraction patterns"}'

# 2. Graph completion — LLM-reasoned graph traversal
curl -X POST http://localhost:8100/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"searchType":"GRAPH_COMPLETION","query":"how does cognify interact with Dagster assets?"}'

# 3. Summaries — topical overview
curl -X POST http://localhost:8100/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"searchType":"SUMMARIES","query":"main topics in infrastructure docs"}'

# 4. Cypher — direct graph queries
curl -X POST http://localhost:8100/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"searchType":"CYPHER","query":"MATCH (n:Entity) RETURN n LIMIT 10"}'

# Visualize the graph (static HTML)
curl -X POST http://localhost:8100/api/v1/visualize \
  -d '{"output_path":"/tmp/cognee_graph.html"}'

# Prune (delete all data)
curl -X POST http://localhost:8100/api/v1/prune
```

### 2.3 The 7 typed clusters (per-cluster cognify model)

The `cognee_readiness_audit` recommended **per-cluster cognify**
to avoid entity-namespace collisions (e.g. `Token` = crypto in
`tuatha/` vs LLM in `meaisínfhoghlaim/`) and enable incremental
updates. The 7 clusters + their `graph_model_file`:

| Cluster | Dataset | Graph model | Core entities |
|:--|:--|:--|:--|
| Data Platform | `docs-data-eng` | `data_platform_graph.py` | DagsterAsset, DltPipeline, LakehouseTable, CocoIndexFlow, LanceDBIndex, SqlMeshModel |
| Infrastructure | `docs-bonneagar` | `infrastructure_graph.py` | KomodoStack, PangolinTunnel, DaggerPipeline, PulumiResource, AnsibleRole |
| Agents & MCP | `docs-agents` | `agents_graph.py` | McpServer, AgentTool, LlmAgent, BamlSchema, BrowserSession |
| ML & AI | `docs-ml` | `ml_graph.py` | FineTunedModel, TrainingDataset, MlflowExperiment, UnslothConfig, LanceDBCollection |
| Celtic Language | `docs-teanga` | `celtic_language_graph.py` | LanguageDataset, HuggingFaceModel, GaeltachtBoundary, CensusTable |
| Web & Frontend | `docs-web` | `web_graph.py` | TanStackRoute, ConvexQuery, BetterAuthProvider, EffectService |
| Tuatha MMO | `docs-tuatha` | `tuatha_graph.py` | GameAsset, SpacetimeDBTable, X402Payment, NpcCharacter |

A federated search layer queries all 7 datasets and re-ranks
merged results by score. Total estimated cognify cost:
**~$6 for 2,242 documents on DeepSeek V4 Pro**.

### 2.4 Cognee MCP features (10 tools exposed via `cognee-mcp`)

The `cognee` MCP server (`opencode.json` → `uvx cognee-mcp`)
exposes the following tools to every agent:

| MCP tool | What it returns | When to use |
|:--|:--|:--|
| `cognee_add(data, dataset_name)` | Add a document or batch to a named dataset | Before cognify |
| `cognee_cognify(datasets, run_in_background)` | Build / refresh the knowledge graph | After every add batch |
| `cognee_search(query, search_type, top_k)` | 4 search types: `CHUNKS` / `GRAPH_COMPLETION` / `SUMMARIES` / `CYPHER` | **Primary** discovery for docs |
| `cognee_recall(query, session_id, top_k)` | Auto-routes search via session cache → permanent graph | When context-sensitive |
| `cognee_list_data()` | List stored datasets | Audit / health-check |
| `cognee_delete(data_id)` | Delete a specific dataset | Cleanup |
| `cognee_prune(prune_data, prune_system)` | Reset all data (data only or full system) | Recovery |
| `cognee_remember(session_id, data)` | Fast session storage (skips cognify) | Agent scratch pad |
| `cognee_improve(dataset_name, session_ids)` | Bridge session Q&A → permanent graph | After agent sessions |
| `cognee_visualize(output_path)` | Static graph visualisation as HTML | Documentation |

> **Search type cheat sheet:** `CHUNKS` for fast / `GRAPH_COMPLETION`
> for depth / `SUMMARIES` for topicals / `CYPHER` for raw graph /
> `FEELING_LUCKY` for auto-routing (cognee decides).

---

## 3. The full MCP inventory (10 servers in `opencode.json`)

| MCP server | Purpose | Tool count | Required? |
|:--|:--|--:|:--|
| **cocoindex-code** | Semantic code search via `ccc mcp` | 9 | ✅ Yes (always on) |
| **cognee** | Knowledge graph over docs via `cognee-mcp` | 10 | ✅ Yes (always on) |
| **graphiti** | Temporal knowledge graph (bi-temporal memory) | 6 | ✅ Yes (always on) |
| **langfuse** | LLM observability (traces, costs, prompt mgmt) | 8 | ✅ Yes (always on) |
| **firecrawl** | Web scraping / crawling / monitoring | 6 | ✅ Yes (always on) |
| **browserbase** | Cloud browser automation (Stagehand) | 12 | ✅ Yes (always on) |
| **chrome** | Local Chrome DevTools MCP (for debugging web apps) | 6 | Optional |
| **motherduck** | DuckDB / MotherDuck analytics | 8 | ✅ Yes (always on) |
| **infisical** | Secrets management | 10 | ✅ Yes (always on) |

**Total: 15 MCP servers, 100+ tools** wired in `opencode.json`.

All secrets are auto-hydrated from Infisical (`dev-baile`
environment) — never hard-coded in `opencode.json`.

---

## 4. The dual-search workflow

**Pattern:** For any "find X" agent query, run both surfaces in
parallel and merge.

```bash
# 1. CCC: find the code
bun run ccc:search "BAML extraction function" --limit 5

# 2. Cognee: find the architecture / pattern docs
curl -X POST http://localhost:8100/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"searchType":"GRAPH_COMPLETION","query":"BAML extraction patterns","datasets":["docs-agents","docs-ml"]}'

# 3. Agent reads both results, merges code (CCC) with explanation (Cognee),
#    then either opens the file (Read tool) or follows a [guide] hint
```

**When to prefer CCC:** any "where is X implemented?", "what
calls Y?", "what's the type signature of Z?", "which file
contains W?" query. Always use before `grep`/`find` per
`AGENTS.md`.

**When to prefer Cognee:** any "what is the pattern for X?",
"how does Y interact with Z?", "what's the architecture of W?",
"what's the difference between the 4 cognitive stages?" query.
Cognee returns prose + relationships, not code.

**When to use both:** "find how X is implemented AND
documented" — agent merges code (CCC) with architecture
(Cognee).

---

## 5. Troubleshooting

### CCC

| Symptom | Fix |
|:--|:--|
| `ccc:search` returns nothing | Run `bun run ccc:index` first (index may be empty or stale) |
| `ccc:search` returns only old files | Run `bun run ccc:index` for incremental refresh |
| Index DB corrupt (> 2 GB with stale data) | `bun run ccc:init && bun run ccc:index` (full rebuild) |
| `ccc:search` is slow (>5s) | Check `ccc status` — chunk count should be < 500K; if higher, run `ccc reset && ccc init && ccc index` |
| MCP server not connecting | Verify `opencode.json` has `"cocoindex-code": {"command": ["ccc", "mcp"], "enabled": true}` |

### Cognee

| Symptom | Fix |
|:--|:--|
| Container won't start | `docker logs cognee` — common: Neo4j unreachable, `LLM_API_KEY` empty |
| `LLMAPIKeyNotSetError` | Check `DEEPSEEK_API_KEY` env var (hydrated from Infisical `dev-baile/deepseek/api_key`) |
| Cognify hangs | `curl -s http://localhost:7474 | head -3` — verify Neo4j is healthy |
| `RateLimitError` | Reduce concurrent cognify batches; DeepSeek has rate limits |
| Search returns no results | Re-run `cognify()` after `add()` — search runs against the graph, not the raw docs |
| Memory growing > 40 GB | `bun run prune` (or `curl -X POST .../prune`) and reduce concurrent cognify |
| MCP server not connecting | Verify `opencode.json` `cognee.env.COGNEE_API_URL = http://localhost:8100` |

### Both

| Symptom | Fix |
|:--|:--|
| Agent doesn't see MCP tools | Restart opencode (the MCP servers reload on start). Verify `opencode.json` is valid JSON. |
| Secrets not hydrating | `mise run secrets:env && mise run secrets:init` — never hand-edit `.env` |

---

## 6. Reference docs (deeper dives)

| Doc | Lines | Purpose |
|:--|--:|:--|
| `.agents/skills/ccc/SKILL.md` | 400 | Agent usage guide for CCC |
| `.agents/skills/ccc/references/integration/CCC_INTEGRATION.md` | 187 | KCG-specific setup + dual-search workflow |
| `.agents/skills/ccc/references/health/cocoindex_readiness_audit.md` | 327 | Index health audit (1.4 GB → 2.1 GB, 8,845 files, 257,957 chunks) |
| `.agents/skills/ccc/references/settings.md` | — | Index settings (`include_patterns`, `exclude_patterns`, embedding model) |
| `.agents/skills/ccc/references/management.md` | — | CLI commands (init, index, search, status, reset, doctor, mcp, daemon) |
| `.agents/skills/cognee/SKILL.md` | 689 | Agent usage guide for Cognee |
| `.agents/skills/cognee/references/docker/COGNEE_SETUP.md` | 190 | Docker setup + API endpoints + ingestion patterns |
| `.agents/skills/cognee/references/architecture/ARCHITECTURE.md` | — | 8-stack cognition pipeline diagram |
| `.agents/skills/cognee/references/infrastructure/INFRASTRUCTURE.md` | — | Supporting stacks (Lakehouse, LakeFS, Dozzle, Beszel) |
| `.agents/skills/cognee/references/cluster-model/cognee_readiness_audit.md` | 517 | Per-cluster cognify rationale + 7-cluster table |

---

## 7. Related skills

- [`.agents/skills/ccc/SKILL.md`](ccc/SKILL.md) — CCC agent usage
- [`.agents/skills/cognee/SKILL.md`](cognee/SKILL.md) — Cognee agent usage
- [`.agents/skills/graphiti/SKILL.md`](graphiti/SKILL.md) — Temporal knowledge graph (cognee's sibling)
- [`.agents/skills/motherduck/SKILL.md`](motherduck/SKILL.md) — DuckDB / MotherDuck analytics
- [`.agents/skills/agent-observability/SKILL.md`](agent-observability/SKILL.md) — Langfuse + MLflow + Ragas
- [`.agents/skills/agent-fleet-orchestration/SKILL.md`](agent-fleet-orchestration/SKILL.md) — 12-agent fleet + OpenCode agent/skill/MCP registry

---

## 8. OpenCode agent, skill, and MCP registry

This section is the **single source of truth** for the three
top-level registries wired into OpenCode. It was added in the
`centralize-agent-context-and-automate` openspec change
(2026-06-27) to give a one-glance view of the agent surface.

### 8.1 The 14 OpenCode agents (`opencode.json` → `agent`)

| Agent | Type | Skill filter | Subagent? | Specialises in |
|:--|:--|:--|:--|:--|
| `build` | Primary | (none — sees all 162 skills) | No | Default BUILD agent. Tools: bash, read, write, edit, glob, grep, webfetch, task, skill, todowrite |
| `plan` | Primary | (none — sees all 162 skills) | No | Default PLAN agent. Read-only by design. |
| `data-platform` | Subagent | 16 skills (dlt, dagster, baml, cognee, ccc, motherduck, lancedb, cocoindex, duckdb, ducklake, dlthub, ibis, marimo, langfuse, mlflow, centralized-registry) | Yes (`subagent_type: data-platform`) | Celtic education data platform (DLT + BAML + Dagster + CocoIndex + MotherDuck) |
| `infrastructure` | Subagent | 16 skills (komodo, pangolin, pulumi, dagger, dagger-pipelines, secrets-management, cloudflare, ccc, dlthub, cocoindex, langfuse, mlflow, risingwave, olake, effect-ts, centralized-registry) | Yes (`subagent_type: infrastructure`) | 94-stack infrastructure mesh (Komodo + Pangolin + Locket + Infisical) |
| `agent-platform` | Subagent | 24 skills (baml, litellm, agent-observability, agent-memory-systems, langfuse, mlflow, ragas, cognee, graphiti-core, lancedb, falkordb, memgraph, unsloth, huggingface, agno, google-adk, dignified-python, pydantic, ccc, dlthub, dagster, duckdb, cocoindex, centralized-registry) | Yes (`subagent_type: agent-platform`) | AI/ML services (agents, OCR, fine-tuning, BAML, LLM routing) |
| `frontend-apps` | Subagent | 21 skills (tanstack-start, copilotkit, hono, convex, better-auth, baml, dagster, dlt, agentic-frontend-frameworks, babylonjs, orpc, effect-ts, cloudflare, ag-ui, marimo, dignified-python, pydantic, ccc, langfuse, cocoindex, centralized-registry) | Yes (`subagent_type: frontend-apps`) | Multi-persona portfolio + Tuatha MMO (Convex + Hono + TanStack + BetterAuth + Babylon.js) |
| `research` | Subagent | 12 skills (browserbase, firecrawl, ccc, cognee, agent-observability, change-detection, crawl4ai, langfuse, mlflow, baml, cocoindex, centralized-registry) | Yes (`subagent_type: research`) | Browser-driven autonomous investigation (BrowserBase + Firecrawl + Cognee) |
| `dev-env-demo` | Subagent | 8 tools | Yes | Dev-env demo agent |
| `orchestrator` | Subagent | (none) | Yes | End-to-end BIEP orchestrator |
| `deep-cuts` | Subagent | (none) | Yes | Structural analyser |
| `notebooks` | Subagent | 5 | Yes | Marimo authoring |
| `baml` | Subagent | 4 | Yes | BAML schema authoring |
| `dagster` | Subagent | 6 | Yes | Dagster asset authoring |
| `mise` | Subagent | 8 | Yes | mise.toml task authoring |
| `proposal-author` | Subagent | 3 | Yes | OpenSpec change authoring |

**Key invariants:**

- **Primary agents (`build`, `plan`) keep no `skill_filter`** —
  they need the full 162-skill surface to act as escape hatches
  when a subagent's scoped skills turn out to be insufficient.
- **Subagent `skill_filter` is opt-in** — a subagent without a
  `skill_filter` falls back to the unfiltered default (all 162
  skills), which preserves the legacy behaviour.
- **Subagent `prompt` is required** — the skill_filter is paired
  with a one-line role prompt that names the quadrant and its
  primary tools.
- **The 5 functional subagents are dispatched via the `task` tool**
  with `subagent_type` set to one of `data-platform`,
  `infrastructure`, `agent-platform`, `frontend-apps`, or
  `research`. The `general` and
  `explore` subagent types are reserved for OpenCode's own
  background work.

### 8.2 The 13-agent model-layer registry (`agents/meaisinfhoghlaim/`)

The Python-side agent inventory lives in
`agents/meaisinfhoghlaim/agents/__init__.py` as a tuple
constant. The 4 functional subagents in `opencode.json` dispatch
to these modules via their prompts.

```python
# From agents/meaisinfhoghlaim/agents/__init__.py
MODEL_LAYER_AGENTS: tuple[str, ...] = (
    "root_agent",                  # 1 root
    "curriculum_agent",            # 12 specialists
    "translation_agent",
    "corpus_agent",
    "research_agent",
    "education_research_agent",
    "bunchloch_research_agent",
    "geospatial_agent",
    "statistics_agent",
    "curriculum_comparison_agent",
    "agui_curriculum_agent",
    "mcp_curriculum_agent",
    "voice_agent",
)
# Total: 13 modules (1 root + 12 specialists)
```

**Add a new model-layer agent** by (1) creating the new
`<name>_agent.py` module, (2) appending the new name to
`MODEL_LAYER_AGENTS` in `__init__.py`, and (3) if the agent
needs new skills, adding them to the relevant `skill_filter`
in `opencode.json`.

### 8.3 The 15 MCP servers (`opencode.json` → `mcp`)

See §3 for the full inventory. The 15 servers are:

**Always-on (9 — the canonical inventory):**

1. `cocoindex-code` (semantic code search, 9 tools)
2. `cognee` (knowledge graph over docs, 10 tools)
3. `graphiti` (temporal knowledge graph, 6 tools)
4. `langfuse` (LLM observability, 8 tools)
5. `firecrawl` (web scraping, 6 tools)
6. `browserbase` (cloud browser automation, 12 tools)
7. `chrome` (local Chrome DevTools, 6 tools, optional)
8. `motherduck` (DuckDB / MotherDuck analytics, 8 tools)
9. `infisical` (secrets management, 10 tools)

**Conditionally enabled (6 — added by recent changes):**

10. `dlt-workspace-mcp` (DLT workspace operations)
11. `hermes` (the multi-channel agent gateway)
12. `agent-registry` (the 12-agent fleet registry)
13. `agents-md` (AGENTS.md file registry)
14. `apple-photos` (Apple Photos ingestion)
15. `huggingface` (HuggingFace Hub operations)

**Add a new MCP server** by appending an entry to `mcp` in
`opencode.json` with `command` (the stdio entrypoint),
optional `enabled: true` (default), and any required
`env` (use the `infisical://dev-baile/<svc>/<key>` Locket-canonical
form via the Locket sidecar, not raw values). Then add a 1-line
row to the §3 table and bump the totals.

### 8.4 Registry health checks

```bash
# 15 agents, 15 MCPs
python3 -c "import json; cfg=json.load(open('opencode.json')); \
print('MCPs:', len(cfg['mcp']), 'Agents:', len(cfg['agent']))"
# Expected: MCPs: 15  Agents: 15

# 5-layer sync health (knowledge-sync-loop, per 2026-08-15-knowledge-sync-loop-v1)
# Layers: paths / ccc / cognee / skills / mcp
# Orchestrator: mise run sync:all (writes stedding/sync-reports/all-{date}.md)
mise run sync:all
# The deployment control panel (notebooks/00_control_panel.py)
# consumes the per-layer reports.

# Per-subagent skill counts
python3 -c "import json; cfg=json.load(open('opencode.json')); \
print({k: len(v.get('skill_filter', [])) \
       for k, v in cfg['agent'].items()})"
# Expected: build=0, plan=0, data-platform=16, infrastructure=16,
#           agent-platform=24, frontend-apps=21, research=12

# 13 model-layer agents
python3 -c "
import ast
with open('agents/meaisinfhoghlaim/agents/__init__.py') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.AnnAssign) \
       and getattr(node.target, 'id', None) == 'MODEL_LAYER_AGENTS':
        print('MODEL_LAYER_AGENTS has', len(node.value.elts), 'entries')
"
# Expected: 13 entries

# 7 cognee graph model files
ls cianfhoghlaim/cognify/cognee_integration/graph_models/*.py 2>/dev/null | wc -l
# Expected: 7 (verify path exists; if not, the graph model files may still be at the legacy location)

# CCC index age (CI gate)
bun run validate-ccc-freshness
# Exits 1 if >7d old on main / >24h on feature branches
```

### 8.5 Centralized registries (NEW 2026-08-15)

The platform now has a single source of truth for every model, schema, pipeline, and stack. Four canonical artifacts:

| Artifact | Path | Purpose |
|:--|:--|:--|
| `MODEL_REGISTRY` | `meaisinfhoghlaim/models/model_registry.py` | 52 entries across 7 families. Resolve via `model_for(family, role, language)` or `filter_models(family)`. |
| `schema` introspection | `notebooks/_shared/schema.py` | 5 helpers: `schema_introspect`, `schema_introspect_table`, `schema_introspect_full`, `list_dlt_sources`, `list_cocoindex_apps`, `list_baml_classes`. |
| `deployment-choice.yaml` | repo root | The canonical enablement file. Read/written by the marimo notebook + web UI + CLI. |
| 00_control_panel notebook | `notebooks/00_control_panel.py` | The 5-tab marimo control panel (Models / Pipelines / Datasets / Stacks / Registry). |

```bash
# Audit: detect hardcoded model strings that bypass MODEL_REGISTRY
mise run lint:registry
# Expected: "Found 0 hardcoded model strings in audited files"

# List every MODEL_REGISTRY entry grouped by family
mise run models:list
# Expected: 52 entries (ocr_vision 20 / text_llm 13 / embedder 3 / rerank 3 /
#           image_gen 5 / voice 5 / translation 3)

# Open the deployment control panel
mise run notebook:control-panel
# or: marimo edit notebooks/00_control_panel.py

# Verify the schema introspection helpers
PYTHONPATH="$PWD/notebooks/_shared:$PWD" uv run python -c "
import sys, types
sys.modules['ibis'] = types.ModuleType('ibis')
import schema
print(f'DLT sources: {len(schema.list_dlt_sources())}')
print(f'CocoIndex Apps: {len(schema.list_cocoindex_apps())}')
print(f'BAML classes: {len(schema.list_baml_classes())}')
"
# Expected: 1963, ~53 (factory + shims), 838
```

The 3 openspec specs are at `openspec/specs/centralized-model-registry/`, `centralized-schema-registry/`, and `deployment-control-panel/`. The change proposal is archived at `openspec/changes/archive/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/`.

---

**Last updated:** 2026-08-15 (post-`centralized-model-registry` change: added §8.5 with the 4 canonical artifacts + 3 new specs + 4 new mise tasks).
**Owner:** Build agent (canonical home: `.agents/skills/INDEXING_AND_COGNITION.md`).

---

## 9. The cianfhoghlaim v4 consolidation (2026-06-28)

The five former pre-v4 quadrant directories were merged into a
single `cianfhoghlaim/` Python package. The former quadrant-specific
subagents were rewritten to align with the new tree.

### 9.1 Directory migration map

| Former surface (pre-2026-06-28) | Current path (v7) |
|:--|:--|
| Oideachais data platform (5-stage PDF pipeline, BAML, DLT sources) | repo root with `dlt_sources/`, `baml_src/`, `cocoindex/`, `orchestration/`, `notebooks/` |
| Oideachais official-media DLT source | `dlt_sources/official_media/` |
| Oideachais BAML schemas | `baml_src/` |
| Oideachais notebooks | `notebooks/` |
| Oideachais TanStack Start app | `web/apps/cianfhoghlaim-web/` |
| Meaisínfhoghlaim agents, OCR, and LLM stack | `agents/` + `meaisinfhoghlaim/` |
| Meaisínfhoghlaim agent registry | `agents/` |
| Meaisínfhoghlaim OCR registry | `meaisinfhoghlaim/ocr/` |
| Meaisínfhoghlaim language data | `dlt_sources/language/` |
| Tuatha Babylon.js MMO + Crypteolas | `agents/tuatha/` + `web/apps/tuatha-ui/` |
| Tuatha UI | `web/apps/tuatha-ui/` |
| Croílár portfolio + portal | `web/apps/croilar-web/` + `web/apps/croilar-portal/` |
| Codeolas code intelligence library | (removed in v7 — absorbed into `libraries/codeolas/` under `sruth/`) |
| Cognee stack | `bonneagar/stacks/cognee/` |
| Graphiti stack | `bonneagar/stacks/graphiti/` |
| Infisical stack | `bonneagar/stacks/infisical/` |
| Pangolin stack | `bonneagar/stacks/pangolin/` |
| Cognee graph models scripts | `orchestration/defs/3_model_lifecycle/cognify/` |

> **Updated 2026-08-13** (per the count drift rebase) — every
> path in the table now resolves on disk post-v7 flattening.
> The data engineering surface is now routed via
> `dlt_sources/DATA_PLATFORM_ROUTER.md` (added by the
> 2026-08-13-skill-consolidation-and-extension-v1 change).

### 9.2 Subagent migration map

The 5 former quadrant subagents were replaced with **4 functional
subagents + 1 research subagent** in `opencode.json`:

| Old subagent (pre-2026-06-28) | New subagent | Skill count | Routes to |
|:--|:--|--:|:--|
| `oideachais` | `data-platform` | 15 | `dlt/`, `orchestration/`, `baml_src/`, `notebooks/` |
| `infrastructure` | `infrastructure` | 15 | `bonneagar/stacks/*/`, komodo, pangolin, locket |
| `meaisinfhoghlaim` | `agent-platform` | 23 | `agents/`, `agents/meaisinfhoghlaim/`, BAML, OCR, LLM routing, Langfuse, MLflow, RAGAS |
| `croilar` + `tuatha` | `frontend-apps` | 20 | `web/`, Convex, Babylon.js, Hono |
| (new) | `research` | 11 | BrowserBase, Firecrawl, CCC, Cognee, change-detection |

**Skill name migration notes (2026-06-29, `skill_filter` audit pass):**

The pre-v4 subagent `skill_filter` arrays referenced ~35 legacy
skill names that no longer exist as top-level skills (e.g.
`cianfhoghlaim-pipeline`, `kcg-pangolin-stack`, `agent-fleet-orchestration`,
`document-intelligence`, `tuatha-mmo`, `pent-elemental-cosmology`,
`croilar-stream-registry`, etc.). These have all been replaced with
top-level skills that resolve to existing directories under
`.agents/skills/`. The new entries were selected to preserve the
per-subagent intent (data plane / infrastructure mesh / agent fleet
/ web surfaces / research), match the per-subagent skill counts
mandated by the `agent-registry` spec, and dedupe entries that
appeared twice (e.g. `agentic-frontend-frameworks` was in the
`frontend-apps` filter twice).

The build-agent prompt (this file's owner) was rewritten to
reference the new subagent names and the `cianfhoghlaim/` paths.
The five pre-v4 quadrant subagent types are gone.

### 9.3 MCP migration

The `croilar-devtools` MCP server (which pointed at
`web/apps/croilar-web/mcp/devtools/index.ts`) was **removed** because
the `web/apps/croilar-web/` directory no longer exists. The croilar
dev-tools surface is temporarily un-implementable; a follow-up
GitHub issue tracks the migration of the MCP server code to
`agents/api/_croilar_convex/devtools.ts`.

Total MCP count: **9** (was 10 before the consolidation).

### 9.4 Spec deltas

This rewrite is tracked by
[`openspec/changes/2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation/`](../../openspec/changes/2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation/)
and defines a new canonical spec:
[`openspec/specs/agent-registry/spec.md`](../../openspec/specs/agent-registry/spec.md).

---

## 10. Code-search canonical entrypoint

Three surfaces expose the Cianfhoghlaim codebase to agents.
This section resolves the dual CLI vs v1 App vs graph
companion split that the `ccc` skill's DEPRECATION NOTICE
banner + the `cocoindex/codebase_indexing.py` v1 App
introduced.

### 10.1 The 3 surfaces

| Surface | Entry point | Use for |
|:--|:--|:--|
| **CCC CLI** (kept for developer shortcuts) | `bun run ccc:search "<query>"` | One-off terminal searches; quick discovery; `ccc --help` introspection |
| **CocoIndex v1 App** (canonical replacement) | `from cocoindex.codebase_indexing import code_search` | Pipelines + Python embedding into agent code; the post-deprecation canonical |
| **Graph companion** (code-structure queries) | `search_code_graph(file_path=..., node_type=...)` | "What calls function X?" / "What implements interface Y?" queries |

### 10.2 Decision matrix — which surface for which task

| Task | Surface | Why |
|:--|:--|:--|
| "Find the file that implements X" | CCC CLI (`bun run ccc:search`) | Fastest path; ad-hoc; no code change |
| "Find the file that implements X" (in an agent) | v1 App (`code_search`) | Type-safe Python API; no subprocess |
| "What functions does this file contain?" | Graph companion (`search_code_graph(file_path=..., node_type="Function")`) | Returns a list of 7-typed nodes (File/Function/Class/Method/Module/Interface/Variable) |
| "What calls function X?" | Graph companion (`search_code_graph(node_type="Function", calls="X")`) | 7-typed edge traversal (CONTAINS / IMPORTS / CALLS / EXTENDS / IMPLEMENTS / USES / DEFINES) |
| "Find all FastAPI routes in this repo" | Infrastructure companion (`search_api_endpoints(framework="fastapi")`) | Scoped to a specific surface |
| "What config files exist at depth ≤ 4?" | Infrastructure companion (`search_config(query=..., kind="compose")`) | 12 typed config kinds |
| Production embedding pipeline | v1 App (`code_search` in a Dagster asset) | The Dagster `codebase` asset group wraps this |

### 10.3 Code samples

```python
# Surface 1 — CCC CLI (terminal)
# $ bun run ccc:search "Dagster asset partition definition"
# Returns ranked [file_path, line_range, score] tuples.

# Surface 2 — CocoIndex v1 App (Python)
from cocoindex.codebase_indexing import code_search
results = code_search("BAML extraction function", limit=5)
for r in results:
    print(f"{r['file_path']}:{r['line_range']}  score={r['score']:.3f}")

# Surface 3 — Graph companion (code-structure)
from cocoindex.codebase_indexing import search_code_graph

# "What calls run_conformance_check?"
callers = search_code_graph(
    node_type="Function",
    calls="run_conformance_check",
)
# Returns the list of Function nodes that CALL run_conformance_check
```

### 10.4 The 4 infrastructure companions

The v1 App also exposes 4 typed "infrastructure companions"
that index the configuration surface (rather than source
code). All registered in
`orchestration/defs/unified_embedding_assets.py`:

| Companion | Indexes | Query helper | Use for |
|:--|:--|:--|:--|
| `api_endpoints` | FastAPI / Hono / TanStack Start / Convex HTTP routes | `search_api_endpoints(query, framework=None, method=None, limit=20)` | "Show me all FastAPI POST routes" |
| `filesystem_layout` | Every directory up to depth 4 with per-dir file-type histogram | `search_filesystem(query, min_depth=None, limit=10)` | "What directories live at depth 3?" |
| `storage_backends` | 9 backend kinds (lancedb / duckdb / ducklake / postgres / garage / r2 / d1 / kv / iceberg) | `search_storage(query, kind=None, limit=20)` | "List all LanceDB indexes" |
| `config_files` | 12 config kinds (compose / mise / package / pyproject / turbo / wrangler / env / k8s / pulumi / dg / github / justfile) | `search_config(query, kind=None, limit=15)` | "Show me all Docker Compose stacks" |

Each companion writes to its own LanceDB table; the
unified v1 App + the 4 companions share the same
embedder (`BAAI/bge-m3`, 1024-d) per
`cocoindex/_shared/_lifespan.py:107`.

### 10.5 The DEPRECATION NOTICE context

The `ccc` skill carries a DEPRECATION NOTICE banner
because the canonical replacement is the v1 App. The CLI
itself is **kept on disk** (the `bun run ccc:init`,
`bun run ccc:index`, `bun run ccc:search` developer
shortcuts are still useful) but new production code MUST
route through `cocoindex.codebase_indexing.code_search` or
the graph companion.

The `ccc` retirement was scheduled for 2026-07-15 but was
retained past that date by user direction
(`openspec/changes/2026-07-14-fix-foundation-v7-flattening-and-baml-drift-v1`).

### 10.6 Quick reference

```bash
# CLI shortcuts (kept for developer ergonomics)
bun run ccc:init       # first time only (creates .cocoindex_code/)
bun run ccc:index      # incremental refresh (<10s) / full rebuild (~2-5 min)
bun run ccc:search "your query"
ccc describe .         # project overview
ccc describe cocoindex/_lifespan.py    # per-file summary
ccc status             # chunk count + file count + language histogram

# v1 App (Python — canonical replacement)
uv run python -c "from cocoindex.codebase_indexing import code_search; print(code_search('BAML extraction', limit=5))"

# Graph companion
uv run python -c "from cocoindex.codebase_indexing import search_code_graph; print(search_code_graph(file_path='meaisinfhoghlaim/models/registry.py', node_type='Function'))"

# Infrastructure companions
uv run python -c "from cocoindex.codebase_indexing import search_api_endpoints; print(search_api_endpoints(framework='fastapi', method='POST'))"
```

### 10.7 Cross-references

- [`./ccc/SKILL.md`](ccc/SKILL.md) — the CCC CLI skill (with the DEPRECATION NOTICE banner)
- [`./cocoindex/SKILL.md`](cocoindex/SKILL.md) — the CocoIndex v1 master skill
- [`../../cocoindex/codebase_indexing.py`](../../cocoindex/codebase_indexing.py) — the v1 App canonical source
- [`../../cocoindex/AGENTS.md`](../../cocoindex/AGENTS.md) — the CocoIndex embedding layer
- [`../../orchestration/defs/unified_embedding_assets.py`](../../orchestration/defs/unified_embedding_assets.py) — the 4 infrastructure companions

---

**Last updated**: 2026-08-13 (added §10 Code-search canonical entrypoint — resolves the CLI vs v1 App vs graph companion split; 3 surfaces + decision matrix + code samples + 4 infrastructure companions).
**Owner**: Build agent.