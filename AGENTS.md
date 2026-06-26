# Agent Instructions

This project uses standard GitHub/Forgejo issues for task tracking. Please use `gh` or standard `git` workflows.

## Priority quick reference

The 5 priority skills, the 4 priority commands, the 4 priority
compose stacks, and the 4 priority openspec specs at a glance.
**Read this first**; the rest of the file is detail.

### Priority skills (6 of 123)

| Skill | When to load |
|:--|:--|
| [`motherduck`](.agents/skills/motherduck/SKILL.md) | MotherDuck storage pattern (managed / BYOB / DuckLake / own-compute) + MCP server |
| [`ccc`](.agents/skills/ccc/SKILL.md) | **Code search** — use `ccc search` before `grep` / `find` |
| [`browser-tools`](.agents/skills/browser-tools/SKILL.md) | Pick the right browser tool (Stagehand / Firecrawl MCP / Firecrawl CLI / Playwright / safe-browser) |
| [`agent-observability`](.agents/skills/agent-observability/SKILL.md) | Langfuse v3 + MLflow GenAI + RAGAS trace-based + Logfire |
| [`openspec`](openspec/AGENTS.md) | Spec-driven change management (32 specs, 4 shared) |
| [`indexing-and-cognition`](.agents/skills/INDEXING_AND_COGNITION.md) | Consolidated setup + MCP reference for `ccc` (semantic code search) + `cognee` (knowledge graph over docs). Use when an agent or team member asks "how do I set up ccc?", "how do I start cognee?", "what MCP tools are available?", or "how does the dual-search workflow work?" |

### ccc code search (always use before grep)

```bash
bun run ccc:init     # first time only (creates .cocoindex_code/target_sqlite.db)
bun run ccc:index    # rebuild the index after any major file move
bun run ccc:search "Dagster asset partition definition"   # semantic search
```

If the index is missing or stale, the agent **owns** running
`ccc:index` — do not ask the user.

### Priority openspec commands

```bash
openspec list --specs              # list all 32 capability specs
openspec list                      # list all pending changes
openspec validate <change-id> --strict    # MUST pass before commit
openspec archive <change-id> --yes        # after deploy
```

### Priority mise tasks

```bash
mise run lint:skills               # validate .agents/skills/ metadata (123/123)
mise run turbo dev                 # monorepo dev (bun + uv + turbo)
mise run secrets:init              # sync .infisical.env → dev-baile vault
mise run dagster:oideachais        # launch the lakehouse Dagster UI
```

### Priority compose stacks (4 of 94)

| Stack | Port | Domain |
|:--|--:|:--|
| `oideachais` | 3080, 3335, 7777, 7778, 8000 | `oideachais.cianfhoghlaim.ie` |
| `litellm` | 4000 | `litellm.cianfhoghlaim.ie` (LLM gateway) |
| `langfuse` | 3000 | `langfuse.cianfhoghlaim.ie` (LLM observability) |
| `lakehouse` | 3900-3904, 5433, 8181-8182 | internal (Garage S3 + Postgres + Lakekeeper) |

The full inventory of 94 stacks is at
[`infrastructure/AGENTS.md`](infrastructure/AGENTS.md).

## Monorepo Topology (v2 — Polyglot)

Cianfhoghlaim is a **bun + uv + turbo polyglot monorepo**. Two language graphs live side by side, orchestrated by `turbo.json` and a single `mise.toml` toolchain.

### TypeScript graph (bun workspaces)

The root `package.json` declares these `workspaces` and is the only manifest bun resolves:

| Workspace | Path | Purpose |
|:--|:--|:--|
| `oideachais-web` | `sruth/oideachais/web/` | TanStack Start + React front-end (the public web app) |
| `oideachais-mcp-filesystem` | `sruth/oideachais/mcp/filesystem/` | Filesystem MCP server for the data platform |
| `tuatha-ui` | `sruth/tuatha/ui/` | Túatha educational MMO front-end |

There is **no** runtime business logic at the root. The root `package.json` only orchestrates: setup, turbo passthroughs, secret management, dagster, komodo/pangolin/locket glue, ccc indexing, and OpenSpec.

## CCC + Cognee dual-search diagram

ccc searches code; cognee searches docs. An agent asking "find how
BAML extraction is implemented" gets the code file from ccc and the
explanation from cognee, then merges.

```
        ccc                          cognee
    (code search)             (docs cognition)
       │                            │
       ▼                            ▼
  Find what BAML           Find what BAML extraction
  extraction calls do      documentation says
       │                            │
       └────────────┬───────────────┘
                    ▼
            Agent (merged)
```

### Python graph (uv workspaces)

The root `pyproject.toml` is a uv-workspace **shell** (no dependencies, no console scripts). Members:

| Member | Path | Purpose |
|:--|:--|:--|
| `oideachais` | `sruth/oideachais/` | Celtic education data platform (Dagster, DLT, LanceDB) |
| `meaisinfhoghlaim` | `sruth/meaisinfhoghlaim/` | AI/ML services (agents, OCR, Celtic-language, ML pipelines) |
| `tuath` | `sruth/tuatha/` | Educational MMO + crypto platform (Babylon.js, siwe, x402) |
| `códeolas` | `códeolas/` | Code intelligence library (publishable) |
| `sruth-browser` | `infrastructure/browser/` | Browser automation client (Stagehand, MCP) |
| `mcpo` | `sruth/oideachais/mcp/mcpo/` | MCPO bridge (optional) |

Members import each other via `[tool.uv.sources]` (e.g. `oideachais` imports `sruth-browser`, `códeolas`).

### Pipeline orchestration

- `turbo.json` — cross-language task graph (`build`, `dev`, `typecheck`, `lint`, `format`, `test`, `clean`, `dagster`, `ccc:index`, `spec:validate`).
- `mise.toml` — toolchain (`python 3.12`, `uv`, `bun`, `dagger`, `pulumi`, `duckdb`, `sops`, `opencode`) **and** the developer task aliases (`mise turbo dev`, `mise ccc:search …`, `mise secrets:init`, `mise dagster:oideachais`, etc.).
- `dg.toml` — Dagster `dg` workspace that loads `oideachais`, `tuatha`, `croilar`, and `meaisínfhoghlaim` code-locations into a single UI. (Phase 0.1 of `lateralise-british-isles-domains` added croilar + meaisínfhoghlaim.)

### Developer onboarding (one command)

```bash
bun run setup
# expands to: mise install && bun install && uv sync && bun run secrets:env && bun run secrets:init
```

## Secrets Bootstrap (do not skip)

Secrets follow a strict three-way contract. **Never** hand-edit `.env`:

1. **Source of truth** — `dev-baile` environment in the self-hosted Infisical vault (Komodo+Pangolin stack on `arm1-oci`).
2. **Template** — `.infisical.env` (committed) — every value is an `infisical://dev-baile/...` reference.
3. **Hydrated runtime** — `.env` (gitignored) — written by `mise`/`locket`/`bun run secrets:init` from the template.

> **Migration note (2026-06):** The earlier 1Password + SOPS + Komodo
> secrets workflow from the predecessor `bonneagar` project
> (documented in the now-deleted `sruth/oideachais/datasets/secrets_management_plan.md`)
> is **superseded** by this Infisical + Locket + mise flow. 1Password
> was migrated to Infisical in 2026-06; `sops` and `age` keys are
> retained in `mise.toml` only for legacy compatibility and should
> not be used for new secrets. Do not re-introduce the 1Password
> `op run` / `op://` URI pattern in new code — use the Infisical
> `infisical://dev-baile/...` URI pattern exclusively.

The scripts live at the **root** of the repository (not in a nested package):

| Script | Purpose | When to run |
|:--|:--|:--|
| `bun run scripts/create-env.ts` | Create the `dev-baile` environment + folders in the vault | First time only |
| `bun run scripts/init-vault.ts` | Read `.env` + `.infisical.env`; create / update each vault secret | Whenever `.env` or `.infisical.env` changes |
| `mise run secrets:init` | Same as the bun script above (mise alias) | — |
| `mise run locket:exec -- <cmd>` | Wrap a command with Locket secret injection at runtime | Production containers |

`mise` directory hooks then keep `.env` in sync on every `cd` and the Locket sidecar re-injects on every container start.

## Codebase Indexing & Spec-Driven Development

### `ccc` — semantic code search (cocoindex-code)

`ccc` (CocoIndex Code) gives every agent a per-project semantic index in `.cocoindex_code/target_sqlite.db`. Treat it as a first-class tool — **always** use it before `grep`/`find`.

```bash
bun run ccc:init     # first time only
bun run ccc:index    # (re)build the index
bun run ccc:search "Dagster asset partition definition"
```

If the index is missing or stale, the agent **owns** running `ccc:index` — do not ask the user. Full skill in [`.agents/skills/ccc/SKILL.md`](.agents/skills/ccc/SKILL.md).

### `openspec` — spec-driven changes

`openspec/` is the canonical change-management surface. The workflow is `list → write proposal/tasks/spec deltas → validate --strict → implement → archive`.

```bash
bun run spec:list
bun run spec:validate my-change-id --strict
bun run spec:archive my-change-id
```

Full workflow in [`openspec/AGENTS.md`](openspec/AGENTS.md).

## Quadrant AGENTS.md files

Each top-level quadrant has its own `AGENTS.md` with developer-quick-reference routing tables:

- [`sruth/oideachais/AGENTS.md`](sruth/oideachais/AGENTS.md) — Celtic education data platform
- [`sruth/meaisinfhoghlaim/AGENTS.md`](sruth/meaisinfhoghlaim/AGENTS.md) — AI/ML services
- [`sruth/tuatha/AGENTS.md`](sruth/tuatha/AGENTS.md) — Educational MMO + crypto
- [`sruth/croilar/AGENTS.md`](sruth/croilar/AGENTS.md) — Multi-persona portfolio

When the user asks "where do I add X?", route to the matching `AGENTS.md`'s
"Quick routing" table.

---

## Infrastructure & Secrets (Critical for Agents)

### Pangolin Convergence Architecture
- **Control Plane (`arm1-oci`)**: Handles routing (Pangolin), identity (Pocket ID), and orchestration (Komodo).
- **Workload Host (`bunchloch` - MacBook M4)**: Handles memory-intensive workloads (Vector DBs, Graph DBs, LLM Inference, local analytics).

### Secrets Management (Infisical + mise)
- Secrets are **automatically injected** via `mise` hooks when entering a directory.
- `infisical export` resolves all secrets instantly into an ignored `.env` file from a `.infisical.env` template.
- **DO NOT** attempt to manually manage, write, or look for `.env` files when configuring MCP servers or running tools. The environment is already hydrated.

## Agent Capabilities

### Agent Frameworks

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| [`agno`](.agents/skills/agno/SKILL.md) | Multi-agent orchestration with tool calling | AgentOS, stateless execution, full async knowledge base, unified media (v2.0+) |
| [`google-adk`](.agents/skills/google-adk/SKILL.md) | Google's Agent Development Kit | Multi-Agent Workflow Engine, NodeRunner, Native Inter-Agent Routing (v2.1+) |

### Knowledge & Memory Systems

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| [`graphiti-core`](.agents/skills/graphiti-core/SKILL.md) | Temporal knowledge graph memory | Bi-temporal model, episodic memory, temporal tracking |
| [`graphiti`](.agents/skills/graphiti/SKILL.md) | Knowledge graph for agents | HNSW indexing (v0.5+), MVCC safety, hybrid search |
| [`cognee`](.agents/skills/cognee/SKILL.md) | Graph-based knowledge management | Graph traversal (v0.1+), temporal tracking, multi-modal support |
| [`lancedb`](.agents/skills/lancedb/SKILL.md) | Vector database for RAG | HNSW indexing (v0.15+), MVCC safety, hybrid search |

### Data Pipelines & Orchestration

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| [`dagster`](.agents/skills/dagster/SKILL.md) | Data orchestration platform | Asset-based pipelines (v1.13+), branch deployments, AI skills integration |
| [`dlt`](.agents/skills/dlt/SKILL.md) | Data load tool for pipelines | dlt+ Projects & Cache, Pythonic pipelines, schema inference |
| [`sqlmesh`](.agents/skills/sqlmesh/SKILL.md) | Data transformation framework | DuckDB integration, virtual data warehouse, CI/CD |

### Observability & Evaluation

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| [`langfuse`](.agents/skills/langfuse/SKILL.md) | LLM observability platform | Prompt management, A/B testing, trace-based analytics |
| [`ragas`](.agents/skills/ragas/SKILL.md) | RAG evaluation framework | Trace-based metrics, faithfulness, answer relevance |

### UI & Agent Interaction

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| [`copilotkit`](.agents/skills/copilotkit/SKILL.md) | AI agent UI framework | React components, multi-agent support, state management |
| [`vinxi`](.agents/skills/vinxi/SKILL.md) | Full-stack framework (Poimandres) | Vite-based, server components, edge runtime |

### Model Training & Fine-tuning

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| [`unsloth`](.agents/skills/unsloth/SKILL.md) | LLM fine-tuning | Multilingual support (v2024.12+), flash attention, 2x faster |
| [`tanstack-start`](.agents/skills/tanstack-start/SKILL.md) | React framework | React Server Components (v1.94+), edge runtime, streaming suspense |

## Domain-to-Skill Mapping

To ensure you use the appropriate skills for the different aspects of the project, strictly adhere to this mapping:

### Codebase Exploration & General Development
- **Code Search**: Use [`ccc`](.agents/skills/ccc/SKILL.md) (CocoIndex Code) for semantic search over the codebase. Prefer `ccc search` over raw `grep`/`find` to get context-aware, relevant files instantly.
- **Python Quality**: Use [`dignified-python`](.agents/skills/dignified-python/SKILL.md) for LBYL exception handling patterns, ABC interfaces, and explicit module boundaries.

### Core Data Platform (`sruth/oideachais/data_platform`)
- **Orchestration**: Load [`dagster`](.agents/skills/dagster/SKILL.md) (specifically the expert routing rules inside it). This ensures you know how to build `MultiPartitionsDefinition` and avoid absolute namespace errors.
- **Extraction**: Load [`dlt`](.agents/skills/dlt/SKILL.md). This skill router will point you to `create-filesystem-pipeline` (crucial for our `USE_LOCAL_SCRAPES` strategy) or `create-rest-api-pipeline`.
- **Storage & Lakehouse**: Load [`motherduck`](.agents/skills/motherduck/SKILL.md). This serves as the master router to help you pick between `motherduck-ducklake` (our Garage S3 architecture), `motherduck-duckdb-sql`, or `motherduck-connect`.

### Team Workflow Stack (`infrastructure/stacks/{engineering/n8n,tools/vikunja,tools/cal-diy}/`)
- **Workflow authoring / debugging**: n8n visual pipeline editor at `n8n.cianfhoghlaim.ie` (private). The 6 seeded workflows live in `engineering/n8n/workflows/team-*.json` and are imported by the `n8n-init` one-shot container.
- **Task management + Gantt + team sharing**: Vikunja REST API at `vikunja.cianfhoghlaim.ie/api/v1/`. Kanban + Gantt + list views; team group shared across `client-work`, `internal`, `support` projects.
- **Scheduling**: cal-diy (cal.com community build) at `calcom.cianfhoghlaim.ie`. Team booking page at `/team`, per-member pages at `/<member-slug>`. Outbound webhooks → n8n.
- **LLM backbone**: All workflow LLM steps use the OpenCode Go API (`$OPENAI_BASE_URL/chat/completions`) as a unified OpenAI-compatible endpoint. Models: `kimi-k2.6`, `glm-5.1`, `minimax-m2.5`, `mimo-v2.5`, `deepseek-v4-flash`.

### Analytics & Notebooks (`sruth/oideachais/notebooks`)
- **Data Exploration**: Load [`explore-data`](.agents/skills/explore-data/SKILL.md) to query endpoints or databases and generate an `analysis_plan.md` artifact.
- **Notebook Assembly**: Load [`build-notebook`](.agents/skills/build-notebook/SKILL.md) to translate the `analysis_plan.md` into a fully functional, highly reactive `marimo` Python notebook.

## Tool Integration Patterns

### Multi-Agent Coordination

Use [`google-adk`](.agents/skills/google-adk/SKILL.md) or [`agno`](.agents/skills/agno/SKILL.md) for:

- **Sequential workflows**: Research → Analyze → Write
- **Parallel execution**: Multiple agents working simultaneously
- **Hierarchical patterns**: Orchestrator managing specialist agents

### Knowledge Graph Memory

Use [`graphiti-core`](.agents/skills/graphiti-core/SKILL.md) for temporal tracking.

### Data Pipeline Patterns

Use [`dagster`](.agents/skills/dagster/SKILL.md) assets with [`dlt`](.agents/skills/dlt/SKILL.md) sources.

### RAG Evaluation

Use [`ragas`](.agents/skills/ragas/SKILL.md) with [`langfuse`](.agents/skills/langfuse/SKILL.md) tracing.

## Best Practices

### Agent Development

1. **Use knowledge graphs** for complex relationships ([`agno`](.agents/skills/agno/SKILL.md) v2.0+, [`cognee`](.agents/skills/cognee/SKILL.md) v0.1+)
2. **Implement temporal tracking** for evolving data ([`graphiti-core`](.agents/skills/graphiti-core/SKILL.md))
3. **Leverage MVCC safety** for concurrent operations ([`lancedb`](.agents/skills/lancedb/SKILL.md) v0.15+, [`graphiti`](.agents/skills/graphiti/SKILL.md) v0.5+)
4. **Use hybrid search** for better relevance ([`lancedb`](.agents/skills/lancedb/SKILL.md), [`graphiti`](.agents/skills/graphiti/SKILL.md))

### Data Engineering

1. **Define assets first** in Dagster for better observability
2. **Use streaming support** in dlt (v1.4+) for real-time data
3. **Integrate DuckDB** with sqlmesh for local development
4. **Implement incremental loading** with cursor-based extraction

### Observability

1. **Trace all LLM calls** with Langfuse decorators
2. **A/B test prompts** using Langfuse prompt management
3. **Evaluate RAG systems** with RAGAS trace-based metrics
4. **Monitor costs and latency** across all agent interactions

### UI/UX

1. **Use CopilotKit components** for consistent AI interfaces
2. **Implement streaming suspense** with TanStack Start (v1.94+)
3. **Leverage React Server Components** for better performance
4. **Support multi-agent interfaces** for complex workflows

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds

## 🤖 Critical Agent Protocols & Habits

As an autonomous agent operating within the Cianfhoghlaim stack (via OpenCode, Roo, or Cline), you **MUST** adhere to these recursive habits to prevent regressions and maintain stability:

### 1. Zero Absolute Namespaces in Data Pipelines
Never import `oideachais.data_platform...` from within the data platform itself. Always use relative or local package imports (e.g., `from dlt_sources.ireland...`). Failing to do so causes critical `ModuleNotFoundError` crashes in the Dagster orchestrator.

### 2. Respect the Ingestion Cache
Before executing live web scrapes (e.g., Firecrawl on `examinations.ie`) that drain API credits and risk rate limits, always test `dlt` pipelines with the fallback cache enabled:
`os.environ['USE_LOCAL_SCRAPES'] = 'true'`
This automatically routes extraction to the highly curated `stedding/ingest_queue/`.

### 3. Strict Secret Hydration
**Never create manual `.env` files.** If a secret is missing:
1. Add it to the `.infisical.env` template.
2. Run `bun run secrets:init` (a.k.a. `bun run scripts/init-vault.ts`) to synchronize it with the remote `dev-baile` Infisical vault.
3. Allow the `mise` directory hooks or `locket inject` to hydrate the runtime environment automatically.

### 4. Self-Documenting Telemetry
Upon finishing a complex task, pipeline update, or major deployment, you **MUST** execute the synchronization script:
`./scripts/sync_agent_docs.sh`
This updates the local telemetry blocks across `README.md` and ensures no rogue imports were introduced.
