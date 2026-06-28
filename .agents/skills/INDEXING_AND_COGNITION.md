---
name: indexing-and-cognition
description: Consolidated setup + MCP reference for the two agent knowledge surfaces — ccc (CocoIndex Code, semantic code search) and cognee (knowledge graph over docs). Use when an agent or team member asks "how do I set up ccc?", "how do I start cognee?", "what MCP tools are available for code search?", "what MCP tools are available for doc cognition?", "where is the dual-search workflow documented?", or "why isn't ccc finding X?". Single source of truth for the indexing + cognition half of the agent stack. Lives at .agents/skills/INDEXING_AND_COGNITION.md (this file).
---

# Indexing & Cognition — Setup + MCP Reference

The Cianfhoghlaim monorepo runs **two parallel knowledge surfaces**
that every agent consumes via MCP:

| Surface | What it indexes | Backend | MCP server | Use for |
|:--|:--|:--|:--|:--|
| **CCC** (CocoIndex Code) | 8,845 source files / 257,957 chunks | SQLite + BGE-M3 embeddings | `cocoindex-code` (`ccc mcp`) | "Where is BAML extraction implemented?" "What calls `run_conformance_check`?" |
| **Cognee** | Docs (1,743 `.md` files, ~2,242 docs across 7 typed clusters) | Neo4j graph + LanceDB vectors + DeepSeek V4 Pro | `cognee` (`cognee-mcp`) | "What is the architecture pattern for the agent fleet?" "How does the cognify pipeline differ across stages?" |

**The dual-search insight:** CCC returns code; Cognee returns docs.
An agent asking "find how BAML extraction is implemented" gets
the code file from CCC and the architecture explanation from
Cognee, then merges.

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
| Concept guides | **19** in `.cocoindex_code/guides.yml` (loaded into search results when matched) |

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
ccc describe cianfhoghlaim/dlt_sources/_lifespan.py

# List + read concept guides (loaded from .cocoindex_code/guides.yml)
ccc describe .                       # project overview
# Guides surface in search results tagged [guide]; follow the ccc guide <slug> hint
```

### CCC + CocoIndex v1 handoff (round-8 architecture)

Per the `docs-skills-consolidation-pipeline` change (2026-06-16),
the v1-native replacement for the standalone `ccc search` CLI is
the **`cianfhoghlaim/cocoindex_flows/codebase_indexing.py`**
CocoIndex v1 App, registered in Dagster under the `codebase`
asset group. It uses the **same embedding model** (`BAAI/bge-m3`)
and the **same LanceDB HNSW index** as the rest of the data
lakehouse.

```bash
# The ccc:index alias now delegates to the v1 App
bun run ccc:index

# v1 search via Python (replaces `ccc search "<query>"`)
uv run python -c "
from sruth.oideachais.cocoindex_flows.codebase_indexing import code_search
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
| Stack path | `cianfhoghlaim/stacks/cognee/` (Docker Compose) |
| Container | `cognee/cognee:latest` (v1.1.2), port 8100 → 8000 |
| Graph backend | Neo4j (from `cianfhoghlaim/stacks/graphiti/`) |
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
cd cianfhoghlaim/stacks/graphiti
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

**Total: 9 MCP servers, 75+ tools** wired in `opencode.json`.

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
| `.agents/skills/ccc/references/kcg-integration/CCC_INTEGRATION.md` | 187 | KCG-specific setup + dual-search workflow |
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

### 8.1 The 7 OpenCode agents (`opencode.json` → `agent`)

| Agent | Type | Skill filter | Subagent? | Specialises in |
|:--|:--|:--|:--|:--|
| `build` | Primary | (none — sees all 123 skills) | No | Default BUILD agent. Tools: bash, read, write, edit, glob, grep, webfetch, task, skill, todowrite |
| `plan` | Primary | (none — sees all 123 skills) | No | Default PLAN agent. Read-only by design. |
| `oideachais` | Subagent | 9 skills (dlt, dagster, baml, cognee, ccc, oideachais-pipeline, oideachais-storage, oideachais-cocoindex-v1, motherduck) | Yes (`subagent_type: oideachais`) | Celtic education data platform (DLT + BAML + Dagster + CocoIndex + MotherDuck) |
| `infrastructure` | Subagent | 16 skills (stack-ops, infrastructure-stacks, secrets-management, kcg-pangolin-stack, kcg-locket-sidecar, kcg-infrastructure-audit, kcg-bunchloch, kcg-convergence, kcg-deploy-runbooks, pangolin, komodo, docker-compose, dagger, dagger-pipelines, pulumi, kubernetes) | Yes (`subagent_type: infrastructure`) | 94-stack infrastructure mesh (Komodo + Pangolin + Locket + Infisical) |
| `meaisinfhoghlaim` | Subagent | 22 skills (baml, litellm, document-intelligence, celtic-language-ai, irish-llm-on-device, agent-fleet-orchestration, agent-observability, kcg-ml-models, langfuse, mlflow, ragas, cognee, graphiti, graphiti-core, lancedb, falkordb, memgraph, embedding-pipeline, peft, trl, unsloth, huggingface) | Yes (`subagent_type: meaisinfhoghlaim`) | AI/ML services (agents, OCR, fine-tuning, BAML, LLM routing) |
| `croilar` | Subagent | 12 skills (tanstack-start, copilotkit, hono, convex, better-auth, baml, dagster, dlt, croilar-stream-registry, agentic-frontend-frameworks, frontend-topology, webapp-testing) | Yes (`subagent_type: croilar`) | Multi-persona portfolio (Convex + Hono + TanStack + BetterAuth) |
| `tuatha` | Subagent | 12 skills (babylonjs, tuatha-mmo, pent-elemental-cosmology, tuatha-achievement-ledger, tuatha-mcp-server-tools, tuatha-platform, british-isles-formative-assessment, baml, dagger, tanstack-start, copilotkit, celtic-language-ai) | Yes (`subagent_type: tuatha`) | Celtic MMO + crypteolas (Babylon.js + SpacetimeDB + BAML) |

**Key invariants:**

- **Primary agents (`build`, `plan`) keep no `skill_filter`** —
  they need the full 123-skill surface to act as escape hatches
  when a subagent's scoped skills turn out to be insufficient.
- **Subagent `skill_filter` is opt-in** — a subagent without a
  `skill_filter` falls back to the unfiltered default (all 123
  skills), which preserves the legacy behaviour.
- **Subagent `prompt` is required** — the skill_filter is paired
  with a one-line role prompt that names the quadrant and its
  primary tools.
- **The 5 sruth-subagents are dispatched via the `task` tool**
  with `subagent_type` set to one of `data-platform`,
  `infrastructure`, `agent-platform`, `frontend-apps`, or
  `research`. The `general` and
  `explore` subagent types are reserved for OpenCode's own
  background work.

### 8.2 The 13-agent model-layer registry (`cianfhoghlaim/agents/meaisinfhoghlaim/`)

The Python-side agent inventory lives in
`cianfhoghlaim/agents/meaisinfhoghlaim/agents/__init__.py` as a tuple
constant. The 4 functional subagents in `opencode.json` dispatch
to these modules via their prompts.

```python
# From cianfhoghlaim/agents/meaisinfhoghlaim/agents/__init__.py
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

### 8.3 The 9 MCP servers (`opencode.json` → `mcp`)

See §3 for the full inventory. The 9 servers are:

1. `cocoindex-code` (semantic code search, 9 tools)
2. `cognee` (knowledge graph over docs, 10 tools)
3. `graphiti` (temporal knowledge graph, 6 tools)
4. `langfuse` (LLM observability, 8 tools)
5. `firecrawl` (web scraping, 6 tools)
6. `browserbase` (cloud browser automation, 12 tools)
7. `chrome` (local Chrome DevTools, 6 tools, optional)
8. `motherduck` (DuckDB / MotherDuck analytics, 8 tools)
9. `infisical` (secrets management, 10 tools)

**Add a new MCP server** by appending an entry to `mcp` in
`opencode.json` with `command` (the stdio entrypoint),
optional `enabled: true` (default), and any required
`env` (use the `infisical://dev-baile/<svc>/<key>` Locket-canonical
form via the Locket sidecar, not raw values). Then add a 1-line
row to the §3 table and bump the totals.

### 8.4 Registry health checks

```bash
# 7 agents, 9 MCPs
python3 -c "import json; cfg=json.load(open('opencode.json')); \
print('MCPs:', len(cfg['mcp']), 'Agents:', len(cfg['agent']))"
# Expected: MCPs: 9  Agents: 7

# Per-subagent skill counts
python3 -c "import json; cfg=json.load(open('opencode.json')); \
print({k: len(v.get('skill_filter', [])) \
       for k, v in cfg['agent'].items()})"
# Expected: build=0, plan=0, data-platform=15, infrastructure=16,
#           agent-platform=23, frontend-apps=20, research=11

# 13 model-layer agents
python3 -c "
import ast
with open('cianfhoghlaim/agents/meaisinfhoghlaim/agents/__init__.py') as f:
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

---

**Last updated:** 2026-06-28 (post-`2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation`).
**Owner:** Build agent (canonical home: `.agents/skills/INDEXING_AND_COGNITION.md`).

---

## 9. The cianfhoghlaim v4 consolidation (2026-06-28)

The five former `sruth/<quadrant>/` quadrants were merged into a
single `cianfhoghlaim/` Python package. The five
sruth-subagents were rewritten to align with the new tree.

### 9.1 Directory migration map

| Former path (pre-2026-06-28) | Current path (v4) |
|:--|:--|
| `sruth/oideachais/` (5-stage PDF pipeline, BAML, dlt_sources) | `cianfhoghlaim/` (root, with `dlt_sources/`, `baml_src/`, `dagster_defs/`, `notebooks/`) |
| `sruth/oideachais/dlt_sources/official_media/` | `cianfhoghlaim/dlt_sources/official_media/` |
| `sruth/oideachais/baml_src/` | `cianfhoghlaim/baml_src/` |
| `sruth/oideachais/notebooks/` | `cianfhoghlaim/notebooks/` |
| `sruth/oideachais/web/` (TanStack Start) | `cianfhoghlaim/web/apps/oideachais-web/` |
| `sruth/meaisinfhoghlaim/` (agents, OCR, LLM stack) | `cianfhoghlaim/agents/meaisinfhoghlaim/` (root subpkg) |
| `sruth/meaisinfhoghlaim/agents/` | `cianfhoghlaim/agents/meaisinfhoghlaim/agents/` |
| `sruth/meaisinfhoghlaim/ocr/` | `cianfhoghlaim/agents/meaisinfhoghlaim/ocr/` |
| `sruth/meaisinfhoghlaim/language/gaeilge/` | `cianfhoghlaim/agents/meaisinfhoghlaim/language/gaeilge/` |
| `sruth/tuatha/` (Babylon.js MMO, crypteolas) | `cianfhoghlaim/web/apps/tuatha-ui/` + `cianfhoghlaim/stacks/tuatha/` |
| `sruth/tuatha/ui/` | `cianfhoghlaim/web/apps/tuatha-ui/` |
| `sruth/croilar/` (Convex portfolio) | `cianfhoghlaim/web/apps/croilar-web/` + `cianfhoghlaim/web/apps/croilar-portal/` |
| `sruth/codeolas/` (code intelligence library) | `cianfhoghlaim/libraries/codeolas/` |
| `infrastructure/stacks/cognee/` | `cianfhoghlaim/stacks/cognee/` |
| `infrastructure/stacks/graphiti/` | `cianfhoghlaim/stacks/graphiti/` |
| `infrastructure/stacks/infisical/` | `cianfhoghlaim/stacks/infisical/` |
| `infrastructure/stacks/pangolin/` | `cianfhoghlaim/stacks/pangolin/` |
| `infrastructure/scripts/cognee-graph-models/` | `cianfhoghlaim/cognify/cognee_integration/graph_models/` |

### 9.2 Subagent migration map

The 5 sruth-subagents were replaced with **4 functional
subagents + 1 research subagent** in `opencode.json`:

| Old subagent (pre-2026-06-28) | New subagent | Skill count | Routes to |
|:--|:--|--:|:--|
| `oideachais` | `data-platform` | 15 | `cianfhoghlaim/dlt_sources/`, `dagster_defs/`, `baml_src/`, `notebooks/` |
| `infrastructure` | `infrastructure` | 16 | `cianfhoghlaim/stacks/*/`, komodo, pangolin, locket |
| `meaisinfhoghlaim` | `agent-platform` | 23 | `cianfhoghlaim/agents/meaisinfhoghlaim/`, BAML, OCR, LLM routing, Langfuse, MLflow, RAGAS |
| `croilar` + `tuatha` | `frontend-apps` | 20 | `cianfhoghlaim/web/`, Convex, Babylon.js, Hono |
| (new) | `research` | 11 | BrowserBase, Firecrawl, CCC, Cognee, change-detection |

The build-agent prompt (this file's owner) was rewritten to
reference the new subagent names and the `cianfhoghlaim/` paths.
The five `sruth/`-prefixed subagent types are gone.

### 9.3 MCP migration

The `croilar-devtools` MCP server (which pointed at
`sruth/croilar/mcp/devtools/index.ts`) was **removed** because
the `sruth/croilar/` directory no longer exists. The croilar
dev-tools surface is temporarily un-implementable; a follow-up
GitHub issue tracks the migration of the MCP server code to
`cianfhoghlaim/agents/api/_croilar_convex/devtools.ts`.

Total MCP count: **9** (was 10 before the consolidation).

### 9.4 Spec deltas

This rewrite is tracked by
[`openspec/changes/2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation/`](../../openspec/changes/2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation/)
and defines a new canonical spec:
[`openspec/specs/agent-registry/spec.md`](../../openspec/specs/agent-registry/spec.md).