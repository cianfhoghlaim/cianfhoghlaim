# Agent Instructions

This project uses standard GitHub/Forgejo issues for task tracking. Please use `gh` or standard `git` workflows.

## Priority quick reference

The 5 priority skills, the 4 priority commands, the 4 priority
compose stacks, and the 4 priority openspec specs at a glance.
**Read this first**; the rest of the file is detail.

### Priority skills (10 of 67)

| Skill | When to load |
|:--|:--|
| [`motherduck`](.agents/skills/motherduck/SKILL.md) | MotherDuck storage pattern (managed / BYOB / DuckLake / own-compute) + MCP server |
| [`ccc`](.agents/skills/ccc/SKILL.md) | **Code search** — use `ccc search` before `grep` / `find` |
| [`browser-tools`](.agents/skills/browser-tools/SKILL.md) | Pick the right browser tool (Stagehand / Firecrawl MCP / Firecrawl CLI / Playwright / safe-browser) |
| [`agent-observability`](.agents/skills/agent-observability/SKILL.md) | Langfuse v3 + MLflow GenAI + RAGAS trace-based + Logfire |
| [`centralized-registry`](.agents/skills/centralized-registry/SKILL.md) | **The single source of truth for models + schemas** — MODEL_REGISTRY + notebooks/_shared/schema.py + deployment-choice.yaml (post-2026-08-15). Load this when adding/changing/toggling any model, schema, pipeline, or stack. |
| [`openspec`](openspec/AGENTS.md) | Spec-driven change management (96 capability specs) |
| [`indexing-and-cognition`](.agents/skills/INDEXING_AND_COGNITION.md) | Consolidated setup + MCP reference for `ccc` (semantic code search) + `cognee` (knowledge graph over docs). Use when an agent or team member asks "how do I set up ccc?", "how do I start cognee?", "what MCP tools are available?", or "how does the dual-search workflow work?" |
| [`pangolin-cli`](.agents/skills/pangolin-cli/SKILL.md) | Pangolin CLI v0.17 — machine-client tunneling, `pangolin up`, `pangolin configure opencode`, launchd/systemd service-install |
| [`pangolin-ai-gateway`](.agents/skills/pangolin-ai-gateway/SKILL.md) | The 2026-Q3 identity-aware AI Gateway contract — public+private overlapping resources, Custom providers, budgets, session logs |
| [`marimo-embed`](.agents/skills/marimo-embed/SKILL.md) | Embed marimo notebooks in TanStack Start pages via the marimo-server-on-Pangolin pattern (sandboxed iframe) |

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
openspec list --specs              # list all 96 capability specs
openspec list                      # list all pending changes
openspec validate <change-id> --strict    # MUST pass before commit
openspec archive <change-id> --yes        # after deploy
```

The **3 new post-2026-08-15 specs** (centralized-model-registry + centralized-schema-registry + deployment-control-panel) join the priority list:

| Spec | One-liner |
|:--|:--|
| [`centralized-model-registry`](openspec/specs/centralized-model-registry/spec.md) | The single canonical model registry (52 entries / 7 families) — drives LiteLLM, BAML, agents, embedders, image-gen, voice, translation |
| [`centralized-schema-registry`](openspec/specs/centralized-schema-registry/spec.md) | BAML is the single source of truth — Pydantic + Zod are codegen; 96 hand-written Pydantic duplicates removed |
| [`deployment-control-panel`](openspec/specs/deployment-control-panel/spec.md) | The 5-tab marimo control panel + web UI + CLI for picking models/pipelines/datasets/stacks; writes to `deployment-choice.yaml` |

### Priority mise tasks

The mise.toml task catalogue is now organized by **6 domain namespaces**
(post the 2026-08-19-domain-driven-mise-task-catalog-v1 change). Pick
the task for the domain you're working on today:

```bash
# Daily "I'm working on X" commands (omnibus tasks per domain)
mise run core                     # dev env (sync + install + lint + test + format)
mise run core:ci                  # the canonical CI gate (lint + test + openspec:validate-all + devops:validate-stacks)
mise run devops                   # IaC + 89 stacks + Komodo/Pangolin/Locket/Infisical
mise run data                     # lakehouse + BIEP + Dagster + baml_src + CocoIndex + motherduck + notebooks
mise run ml                       # meaisinfhoghlaim (OCR/HTR/Alignment/Celtic) + 12-agent fleet + MODEL_REGISTRY
mise run web                      # web/apps + web/packages + web/hono-api + Turborepo

# Surgical subcommands (when you know exactly what you want)
mise run lint:skills              # validate .agents/skills/ metadata (65 skills pass)
mise run lint:drift-docs          # validate every AGENTS.md number claim against ground truth
mise run openspec:validate-all    # CI gate for every openspec change + spec (131 items pass)
mise run devops:validate-stacks   # validate all 89 Docker Compose stacks against the 6-file GOLD_STANDARD
mise run data:dagster:up          # launch the Dagster UI on :3335
mise run data:biep:milestone -- 1 # run BIEP v3 milestone m1
mise run ml:registry:audit         # verify all 24 VISION_MODELS are live on HF Hub
mise run web:dev tuatha-ui        # per-app dev server via Turbo filter
```

> **Back-compat:** the old bare/colon task names (e.g. `lint`, `sync`,
> `dagster:dev`, `cic:stack-doctor`, `iac:health`) remain valid for 1
> release cycle as aliases.

### Priority sync commands

```bash
mise run sync:all                  # run all 14 sync layers (paths + ccc + cognee + skills + mcp + dagster + drift-docs + spec-agents + baml + stacks + dlt + agents + notebooks + firecrawl)
mise run lint:drift-docs           # validate every AGENTS.md number claim against ground truth (per the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 change)
mise run openspec:validate         # run `openspec validate --strict` against the pending change under review
```

### Priority compose stacks (4 of 93)

| Stack | Port | Domain |
|:--|--:|:--|
| `oideachais` | 3080, 3335, 7777, 7778, 8000 | `cianfhoghlaim.cianfhoghlaim.ie` |
| `litellm` | 4000 | `litellm.cianfhoghlaim.ie` (LLM gateway) |
| `langfuse` | 3000 | `langfuse.cianfhoghlaim.ie` (LLM observability) |
| `lakehouse` | 3900-3904, 5433, 8181-8182 | internal (Garage S3 + Postgres + Lakekeeper) |

The full inventory of 93 stacks is at
[`bonneagar/AGENTS.md`](bonneagar/AGENTS.md) (the IaC subdirectory
owns the stack catalogue; see the `## Repo Boundary` section below).

### `~/dev/` working-copy inventory (local-only — gitignored)

Before reaching for `ls ~/dev`, read
[`stedding/AGENTS_STEDDING.MD`](stedding/AGENTS_STEDDING.MD). That file
labels every subdirectory under `~/dev/` (active monorepos, hackathon
trees, sister repos, stedding junkyard, backup snapshots) so an agent
can pick the right working tree without re-asking. **Local-only — do
not commit; `stedding/` is gitignored.**

## Monorepo topology

See [`README.md`](README.md#monorepo-topology-v7--flattened-polyglot)
for the full TypeScript-workspace + Python-sub-package tables — kept
in one place to avoid the two copies drifting apart (they had, badly,
before the 2026-08 docs consolidation). Quick orientation: `agents/`,
`baml_src/`, `cocoindex_flows/`, `dlt_sources/`, `orchestration/`,
`meaisinfhoghlaim/` are the Python sub-packages; `web/apps/*` +
`web/packages/*` are the bun workspaces; `bonneagar/` is the IaC
subdirectory (see [`bonneagar/README.md`](bonneagar/README.md)).

## Search: ccc + cognee + firecrawl_mcp

Three complementary surfaces. ccc and cognee are local + free;
firecrawl_mcp is external + metered. Every agent session that runs
`firecrawl_search` MUST also emit a `ccc:search` query so both tool
names appear in the Langfuse trace.

| Question type | Tool | Why |
|:--|:--|:--|
| "What is in our code that does X?" | `bun run ccc:search "X"` | Local, FREE, semantic, instant |
| "What does our docs corpus say about X?" | `cognee.search(X)` | Local, FREE, semantic |
| "What does upstream say about X **right now**?" | `firecrawl_search` (categories: `developer`) | External, metered, fresh |
| "Show me the **page** at <known URL>" | `firecrawl_scrape` | Replaces ad-hoc `webfetch` |
| "Find every URL on a domain" | `firecrawl_map` (with `search:`) | Faster than crawling whole site |
| "Pull all pages from a path" | `firecrawl_crawl` | Bounded, async, with `includePaths` regex |
| "Investigate across unknown sources" | `firecrawl_agent` | Autonomous, async, multi-source |
| "Operate a login-gated page" | `firecrawl_interact` | Playwright-style, profile-aware |
| "Parse a local PDF/DOCX/XLSX" | `firecrawl_parse` | Two-call upload handoff |
| "Find papers / read passages / citations" | `firecrawl_research_*` | 43M-paper PubMed/bioRxiv/arXiv index |
| "Find a primary-source coding answer" | `firecrawl_developer_search` | GitHub issues/PRs/README/curated docs |

The `FirecrawlMCPClient` wrapper at
`agents/meaisinfhoghlaim/firecrawl_mcp/client.py` exposes the MCP
tools with Pydantic validation + Langfuse `@observe`.

### Developer onboarding (one command)

```bash
bun run setup
# expands to: mise install && bun install && uv sync && bun run secrets:env && bun run secrets:init
```

### Centralized registries

One canonical source of truth per model/schema/pipeline/stack concern
— see [`README.md`](README.md#centralized-registries) for the current
artifact list and [`.agents/skills/centralized-registry/SKILL.md`](.agents/skills/centralized-registry/SKILL.md)
for the full guide, including the `model_for()` and `schema_introspect()`
patterns. Two model registries currently co-exist
(`meaisinfhoghlaim/models/registry.py` and the newer
`model_registry.py`) — check both; see
[`meaisinfhoghlaim/README.md#known-gaps`](meaisinfhoghlaim/README.md#known-gaps).


## Secrets Bootstrap (do not skip)

Secrets follow a strict three-way contract. **Never** hand-edit `.env`:

1. **Source of truth** — `dev-baile` environment in the self-hosted Infisical vault (Komodo+Pangolin stack on `arm1-oci`).
2. **Template** — `.infisical.env` (committed) — every value is an `infisical://dev-baile/...` reference.
3. **Hydrated runtime** — `.env` (gitignored) — written by `mise`/`locket`/`bun run secrets:init` from the template.

> **Migration note (2026-06):** The earlier 1Password + SOPS + Komodo
> secrets workflow from the predecessor `bonneagar` project
> (documented in the now-deleted `sruth/cianfhoghlaim/datasets/secrets_management_plan.md`)
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

> **Post-v4 (2026-06-28):** the 4 quadrant AGENTS.md files are
> gone. All quadrant routing happens inside the consolidated
> `AGENTS.md` (which itself links to the per-area
> sub-package `AGENTS.md` files). Use the
> `## Repo Boundary` section below for the canonical 3-repo split.

When the user asks "where do I add X?", route using the
`## Repo Boundary` table below.

---

## Infrastructure & Secrets (Critical for Agents)

### Pangolin Convergence Architecture
- **Control Plane (`arm1-oci`)**: Handles routing (Pangolin), identity (Pocket ID), and orchestration (Komodo).
- **Workload Host (`bunchloch` - MacBook M4)**: Handles memory-intensive workloads (Vector DBs, Graph DBs, LLM Inference, local analytics).

### Secrets Management (Infisical + mise)
- Secrets are **automatically injected** via `mise` hooks when entering a directory.
- `infisical export` resolves all secrets instantly into an ignored `.env` file from a `.infisical.env` template.
- **DO NOT** attempt to manually manage, write, or look for `.env` files when configuring MCP servers or running tools. The environment is already hydrated.

## Repo Boundary

The 2-repo split (post-v7 flattening) is enforced by this section.
The `bonneagar/` IaC is now a SUBDIRECTORY of cianfhoghlaim, not a
separate repo. The only remaining separately-managed repo is
`leabharlann` (the 3.4 GB corpus).

When a task touches infrastructure, secrets, or the core
agent-runtime, route to the correct location BEFORE writing any
code.

| Domain | Location |
|:--|:--|
| Data platform (DLT + Dagster + BAML + CocoIndex + marimo) | `{dlt_sources,orchestration,baml_src,cocoindex_flows,notebooks}/` |
| Agent fleet (13 root agents + 8 NCCA subjects) | `agents/` — see [`agents/README.md`](agents/README.md) |
| OCR/HTR/alignment agents specifically | `agents/meaisinfhoghlaim/` |
| Frontend apps (TanStack Start + Convex + Hono + CopilotKit) | `web/apps/*/` |
| OpenSpec changes + specs | `openspec/` |
| MotherDuck Dives/Flights metadata | `motherduck/` |
| IaC (Komodo + Pangolin + Infisical clients) | `bonneagar/iac/` (IN THIS REPO) |
| 93 Docker Compose stacks | `bonneagar/stacks/<name>/` |
| Komodo resource-syncs + procedures | `bonneagar/komodo/` |
| Pangolin config | `bonneagar/pangolin/` |
| Deploy runbooks | `bonneagar/deploy-runbooks/` |
| Leabharlann corpus | `leabharlann/` (SEPARATE REPO at `github.com/cianfhoghlaim/leabharlann`) |

> **Hard rule**: An agent MUST NOT write into the `leabharlann/`
> worktree from this repo (it's a separate repo with its own git
> history). For cross-repo changes, create an openspec change with
> a `cross-repo-sync.md` file that lists the commit plan for each
> repo.

## OpenSpec Change Management

Two new conventions land with this change:

1. **`## Dependencies` section** — every `proposal.md` declares
   `Blocked by: <change-id>` edges. The new change CANNOT
   archive until the blocker archives.
2. **`cross-repo-sync.md`** — for any change touching >1 repo,
   this file lists the commit plan + branches + push targets
   for each repo.

Both conventions are enforced by the
`2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1`
openspec change (see its `specs/bonneagar-iac-merge/spec.md`
delta).

## OpenCode Safety

Repeatedly deploying arm-oci core stacks (`openchamber`,
`backrest`, `olm-arm1-oci`) from opencode sessions has broken
the opencode instance itself when the session shared a
process namespace with the deployed container. To prevent
recurrence:

1. **MUST run `bun run preflight:arm-oci`** before any
   `iac:bootstrap`, `iac:plan`, or `km deploy stack <arm-oci-*>`.
2. **MUST NOT run `iac:bootstrap` from inside a container** —
   the process namespace check will refuse it.
3. **MUST NOT run `iac:bootstrap` from an opencode session
   whose PID shares a namespace with `openchamber`,
   `openclaw`, `hermes`, `komodo`, `pangolin`, or `infisical`**.
4. The pre-flight script is at `scripts/preflight-arm-oci.ts`
   and exposes `--dry-run` (default), `--strict`,
   `--emit-md`, and `--skip-namespace` (dev only).

The safety gate is enforced by the
`2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1`
openspec change (see its
`specs/infrastructure-stacks/spec.md` delta — Requirement
"preflight:arm-oci safety script").

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

### Observability & Evaluation

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| [`langfuse`](.agents/skills/langfuse/SKILL.md) | LLM observability platform | Prompt management, A/B testing, trace-based analytics |
| [`ragas`](.agents/skills/ragas/SKILL.md) | RAG evaluation framework | Trace-based metrics, faithfulness, answer relevance |

### UI & Agent Interaction

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| [`copilotkit`](.agents/skills/copilotkit/skills/copilotkit-develop/SKILL.md) | AI agent UI framework (10 sub-skills — develop/setup/debug/upgrade/etc.) | React components, multi-agent support, state management |

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
- **Centralized Registries**: Load [`centralized-registry`](.agents/skills/centralized-registry/SKILL.md) when adding/changing/toggling any model, schema, pipeline, or stack. The canonical surfaces are `MODEL_REGISTRY` (52 entries / 7 families), `notebooks/_shared/schema.py` (5 introspection helpers), `deployment-choice.yaml` (the enablement file), and the `00_control_panel.py` marimo notebook (the 5-tab UI).

### Core Data Platform (`dlt/` + `orchestration/`)
- **Orchestration**: Load [`dagster`](.agents/skills/dagster/SKILL.md) (specifically the expert routing rules inside it). This ensures you know how to build `MultiPartitionsDefinition` and avoid absolute namespace errors.
- **Extraction**: Load [`dlt`](.agents/skills/dlt/SKILL.md). This skill router will point you to `create-filesystem-pipeline` (crucial for our `USE_LOCAL_SCRAPES` strategy) or `create-rest-api-pipeline`.
- **Storage & Lakehouse**: Load [`motherduck`](.agents/skills/motherduck/SKILL.md). This serves as the master router to help you pick between `motherduck-ducklake` (our Garage S3 architecture), `motherduck-duckdb-sql`, or `motherduck-connect`.

### Team Workflow Stack (lives in bonneagar/stacks/{n8n,vikunja,cal-diy}/)
- **Workflow authoring / debugging**: n8n visual pipeline editor at `n8n.cianfhoghlaim.ie` (private). The 6 seeded workflows live in `bonneagar/stacks/n8n/workflows/team-*.json` and are imported by the `n8n-init` one-shot container.
- **Task management + Gantt + team sharing**: Vikunja REST API at `vikunja.cianfhoghlaim.ie/api/v1/`. Kanban + Gantt + list views; team group shared across `client-work`, `internal`, `support` projects.
- **Scheduling**: cal-diy (cal.com community build) at `calcom.cianfhoghlaim.ie`. Team booking page at `/team`, per-member pages at `/<member-slug>`. Outbound webhooks → n8n.
- **LLM backbone**: All workflow LLM steps use the OpenCode Go API (`$OPENAI_BASE_URL/chat/completions`) as a unified OpenAI-compatible endpoint. Models: `kimi-k2.6`, `glm-5.1`, `minimax-m2.5`, `mimo-v2.5`, `deepseek-v4-flash`.

### Analytics & Notebooks (`notebooks/`)
- **Data Exploration**: Load [`explore-data`](.claude/skills/explore-data/SKILL.md) to query endpoints or databases and generate an `analysis_plan.md` artifact.
- **Notebook Assembly**: Load [`build-notebook`](.claude/skills/build-notebook/SKILL.md) to translate the `analysis_plan.md` into a fully functional, highly reactive `marimo` Python notebook.

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
3. **Integrate DuckDB** with dlt/dagster for local development
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

## Remote access (Pangolin.app + Pangolin CLI)

Pangolin.app is the macOS WireGuard GUI VPN client (already installed + connected on
this MacBook). It tunnels `*.cianfhoghlaim.ie` private resources from any device on the
local network — use it whenever you need to reach the marimo server, the cianfhoghlaim-cognee
UI, the Langfuse dashboard, the lakehouse viewer, the litellm proxy, the unsloth Studio, or
any other private resource from inside the bunchloch Docker network.

For machine-client access (background services, CI, headless containers), use the
Pangolin CLI instead:

```bash
curl -fsSL https://static.pangolin.net/get-cli.sh | bash   # installs to /usr/local/bin (requires sudo)
pangolin login                                              # browser-based user auth
pangolin up --attach                                        # foreground tunnel
pangolin service install client --id <id> --secret <secret> --endpoint https://pangolin.cianfhoghlaim.ie
```

For coding-agent wire-up (OpenCode, Claude Code, Codex, Gemini CLI):

```bash
pangolin configure opencode --resource ai.cianfhoghlaim.ie
```

See `.agents/skills/pangolin-cli/SKILL.md` for full details + the Docker sidecar + Kubernetes
patterns.

## VLM testing surface

The bunchloch MacBook now hosts a self-hosted VLM stack reachable through the Pangolin
AI Gateway at `https://ai.cianfhoghlaim.ie`. Three ways to reach the fleet:

1. **Preferred**: `https://ai.cianfhoghlaim.ie/v1/chat/completions` (identity-aware via
   the Pangolin.app tunnel; placeholder key `none` for the private resource)
2. **Fallback**: `http://localhost:4000/v1` (LiteLLM proxy on the bunchloch docker network)
3. **Direct**: `http://192.168.148.5:8889/v1` (the unsloth-serve container on the
   bunchloch `cianfhoghlaim` docker network — bypasses the gateway)

The 12 unsloth-served models + the 20 ocr_vision models in MODEL_REGISTRY all share
this surface. See `notebooks/_shared/evaluation/vlm_registry_benchmark.py` for the
benchmark notebook that exercises all 12 models against 3 standard prompts (NCCA
syllabus PDF page + LC marking-scheme snippet + Ordnance Survey map extract).

For the future (deferred to `2026-09-26-bunchloch-vlm-stacks-v1/`):
- `invokeai-local` (Stable Diffusion XL + Flux image gen on `:9090`)
- `comfyui-local` (ComfyUI workflows + OpenAI bridge on `:8188` + `:9000`)

## arm1-oci SSH quick reference

The Pangolin control plane + Newt connector run on the OCI arm (`140.238.96.148`). SSH
config is at `~/.ssh/config` (host alias: `oci.arm1`):

```bash
# Verify reachability (use this as the health gate)
ssh -o ConnectTimeout=5 -o BatchMode=yes oci.arm1 'true'

# Inspect the running Pangolin stack
ssh oci.arm1 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"'
# Pangolin: fosrl/pangolin:ee-1.21.1 (running, healthy)
# Newt:     fosrl/newt:1.16.0
# Traefik:  reverse proxy for *.cianfhoghlaim.ie

# Check Pangolin + Newt version compatibility
ssh oci.arm1 'docker exec pangolin -- pangolin --version'   # 1.21.x (Enterprise)
docker exec newt-bunchloch -- newt --version                # 1.16.x

# Open browser SSH to a bunchloch machine from the Pangolin UI
# https://pangolin.cianfhoghlaim.ie → Sites → bunchloch → Machines → SSH
# Requires pangolin ≥ 1.19 (✓) + newt ≥ 1.13 (✓)

# Push secrets to the Infisical vault on arm1-oci
ssh oci.arm1 'infisical secrets set <KEY> "<value>" --project-id d900f50a-acbf-446b-b4f6-e439710253e4 --env dev-baile --path /<service>'
```

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
Never import `cianfhoghlaim.data_platform...` from within the data platform itself. Always use relative or local package imports (e.g., `from dlt_sources.ireland...`). Failing to do so causes critical `ModuleNotFoundError` crashes in the Dagster orchestrator.

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
