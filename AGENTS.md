# Agent Instructions

This project uses standard GitHub/Forgejo issues for task tracking. Please use `gh` or standard `git` workflows.

## New in 2026-08-23-uog-personal-archive-tertiary-modules-v1 (UoG personal archive → tertiary subject pipeline)

Lifts `leabharlann/ollscoil_na_gaillimhe/` + transcript PDFs to
feature parity with the leaving-cycle subject pipeline (4 CocoIndex
v1 Apps, 10 typed Cognee edges, 6 Dagster assets, 8-tab Marimo
notebook, Convex + CopilotKit + Genie + ADK, tests + observability +
thesis figures).

**Source**: `leabharlann/ollscoil_na_gaillimhe/` (auto-discovered; no curated drop-PDF UI as primary entry).

**F-granularity destination**: per-question, per-assignment, per-topic — chatable via `notebooks/15_personal_archive.py`, Convex `chatOverMyArchive`, CopilotKit `<AskMyArchive />`, Genie tile, ADK agent `personal_archive_module_assistant`.

**Transferability**: 9 env vars + a generic `UniversityPersonalArchiveConfig` Pydantic model; any university student can point it at their own `leabharlann/<university>/` corpus.

**Key file paths**:

| Layer | Path |
|---|---|
| Openspec proposal + tasks | `openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/{proposal.md,tasks.md}` |
| Spec | `openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/specs/cianfhoghlaim-personal-archive-typed-modules/spec.md` |
| BAML schema | `baml_src/british_isles/ireland/education/university/personal_archive_extraction.baml` |
| DLT source | `dlt_sources/filesystem/uog_personal_archive.py` |
| HTR ensemble | `dlt_sources/filesystem/_htr_ensemble.py` |
| Generic factory | `dlt_sources/british_isles/ireland/education/university/personal_archive/uog_personal_archive_source.py` |
| DuckLake tables | `dlt_sources/_lakehouse/personal_archive_destinations.py` |
| CocoIndex Apps | `cocoindex_flows/british_isles/ireland/education/university/personal_archive_embedding.py` |
| Cognee edges | `scripts/graph_storage/cognify/rules/personal_archive_typed_edges.py` |
| Marimo notebook | `notebooks/15_personal_archive.py` |
| Dagster assets | `orchestration/defs/uog_personal_archive.py` |
| Convex chat | `web/apps/cianfhoghlaim/convex/personalArchive.ts` |
| CopilotKit | `web/apps/cianfhoghlaim/components/AskMyArchive.tsx` |
| Genie UI | `web/apps/cianfhoghlaim/genie/personal_archive_browser.ts` |
| ADK agent | `agents/adk/personal_archive_module_assistant.py` |
| Thesis figures | `orchestration/defs/uog_personal_archive_figures.py` |
| Grafana dashboard | `observability/dashboards/personal_archive.json` |
| Tests | `tests/personal_archive/` (12 tests) |

**Quickstart**:

```bash
# Run the test suite (12 passing)
uv run pytest tests/personal_archive/ -v

# Validate the openspec change
uv run openspec validate 2026-08-23-uog-personal-archive-tertiary-modules-v1 --strict

# Materialise the DuckLake tables (smoke test)
uv run python -c "import duckdb; from dlt_sources._lakehouse import register_personal_archive_tables; con = duckdb.connect(':memory:'); register_personal_archive_tables(con); print('OK')"

# Auto-classify a sample file
uv run python -c "from pathlib import Path; from dlt_sources.filesystem.uog_personal_archive import _classify_file; print(_classify_file(Path('leabharlann/ollscoil_na_gaillimhe/mata/networks/CS4423 - Networks/cian_mac_liathain_assignment_3.pdf')))"
```

## Priority quick reference

The 5 priority skills, the 4 priority commands, the 4 priority
compose stacks, and the 4 priority openspec specs at a glance.
**Read this first**; the rest of the file is detail.

### Priority skills (7 of 64)

| Skill | When to load |
|:--|:--|
| [`motherduck`](.agents/skills/motherduck/SKILL.md) | MotherDuck storage pattern (managed / BYOB / DuckLake / own-compute) + MCP server |
| [`ccc`](.agents/skills/ccc/SKILL.md) | **Code search** — use `ccc search` before `grep` / `find` |
| [`browser-tools`](.agents/skills/browser-tools/SKILL.md) | Pick the right browser tool (Stagehand / Firecrawl MCP / Firecrawl CLI / Playwright / safe-browser) |
| [`agent-observability`](.agents/skills/agent-observability/SKILL.md) | Langfuse v3 + MLflow GenAI + RAGAS trace-based + Logfire |
| [`centralized-registry`](.agents/skills/centralized-registry/SKILL.md) | **The single source of truth for models + schemas** — MODEL_REGISTRY + notebooks/_shared/schema.py + deployment-choice.yaml (post-2026-08-15). Load this when adding/changing/toggling any model, schema, pipeline, or stack. |
| [`openspec`](openspec/AGENTS.md) | Spec-driven change management (96 capability specs) |
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
openspec list --specs              # list all 96 capability specs
openspec list                      # list all pending changes
openspec validate <change-id> --strict    # MUST pass before commit
openspec archive <change-id> --yes        # after deploy
```

The **3 new post-2026-08-15 specs** (centralized-model-registry + centralized-schema-registry + deployment-control-panel) join the priority list:

| Spec | One-liner |
|:--|:--|
| [`centralized-model-registry`](openspec/specs/centralized-model-registry/spec.md) | The single canonical model registry (76 entries / 7 families) — drives LiteLLM, BAML, agents, embedders, image-gen, voice, translation |
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
mise run devops                   # IaC + 99 stacks + Komodo/Pangolin/Locket/Infisical
mise run data                     # lakehouse + BIEP + Dagster + baml_src + CocoIndex + motherduck + notebooks
mise run ml                       # meaisinfhoghlaim (OCR/HTR/Alignment/Celtic) + 12-agent fleet + MODEL_REGISTRY
mise run web                      # web/apps + web/packages + web/hono-api + Turborepo

# Surgical subcommands (when you know exactly what you want)
mise run lint:skills              # validate .agents/skills/ metadata (166 skills pass)
mise run lint:drift-docs          # validate every AGENTS.md number claim against ground truth
mise run openspec:validate-all    # CI gate for every openspec change + spec (146 items pass)
mise run devops:validate-stacks   # validate all 94 Docker Compose stacks against the 6-file GOLD_STANDARD
mise run data:dagster:up          # launch the Dagster UI on :3335
mise run data:biep:milestone -- 1 # run BIEP v3 milestone m1
mise run data:all:up               # bring up the FULL data plane (lakehouse + logfire + langfuse + mlflow + dagster)
mise run ml:registry:audit         # verify all 22 ocr_vision models are live on HF Hub
mise run ml:litellm:regenerate     # regenerate config.yaml from MODEL_REGISTRY (now auto-runs in CI per 2026-08-21)

# New in 2026-08-22 dev-tooling-refactor v2 (bun 1.4 + mise fmt + uv 0.12 + openspec 1.10):
mise run core:bun:prune            # bun prune (remove unused packages; bun 1.4+)
mise run core:bun:audit:fix       # bun audit fix (auto-upgrade vulns; bun 1.4+)
mise run core:bun:dedupe           # bun dedupe (remove duplicate versions; bun 1.4+)
mise run core:bun:format           # bunx prettier --write . (the missing formatter)
mise run core:bun:parallel         # bun run --parallel
mise run core:mise:fmt             # mise fmt (auto-format mise.toml)
mise run core:mise:fmt:check       # mise fmt --check (CI gate)
mise run core:mise:upgrade         # mise upgrade (the mise CLI itself)
mise run core:uv:lock:refresh      # uv lock --refresh (re-resolve)
mise run core:uv:lock:upgrade      # uv lock --upgrade (upgrade all packages)
mise run core:uv:tree:json         # uv tree --format=json (programmatic)
mise run core:uv:format            # uv format (Python formatter, uv 0.12+)
mise run openspec:upgrade          # print the bun add -g @fission-ai/openspec@1.10.0 command

# New in 2026-08-23 dev-tooling-refactor v3 (version pinning + spec hygiene):
mise run core:tool-versions:report          # print a table of all installed tools + resolved versions
mise run core:tool-versions:check-stale    # exit 1 if any pinned tool is > 1 major behind latest
mise run lint:spec:purpose                 # fail CI if any openspec has a TBD Purpose section

# Subproject tasks (after mise 2026.8.10+ is installed, the root aliases route to subprojects):
cd bonneagar && mise run devops:health   # IaC subproject
cd agents && mise run ml:agents:smoke    # agent-fleet subproject
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

### Priority compose stacks (4 of 94)

| Stack | Port | Domain |
|:--|--:|:--|
| `oideachais` | 3080, 3335, 7777, 7778, 8000 | `cianfhoghlaim.cianfhoghlaim.ie` |
| `litellm` | 4000 | `litellm.cianfhoghlaim.ie` (LLM gateway) |
| `langfuse` | 3000 | `langfuse.cianfhoghlaim.ie` (LLM observability) |
| `lakehouse` | 3900-3904, 5433, 8181-8182 | internal (Garage S3 + Postgres + Lakekeeper) |

The full inventory of 99 stacks is at
[`bonneagar/AGENTS.md`](bonneagar/AGENTS.md) (the IaC subdirectory
owns the stack catalogue; see the `## Repo Boundary` section below).

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

## OpenCode Agent Dispatch Matrix (NEW 2026-08-23)

Per the `2026-08-23-agent-opencode-agent-coverage-expansion-v1` change,
the 15 agents under `.opencode/agents/*.md` are organized into 3 tiers:

| Tier | Agent | When to dispatch |
|:-----|:------|:-----------------|
| **Primary (4)** | `build` | Default BUILD agent. Full skill_filter (no restriction). |
| **Primary (4)** | `plan` | Read-only planning. Default dispatch for "plan this" tasks. |
| **Functional subagent (5)** | `data-platform` | DLT + Dagster + BAML + CocoIndex + MotherDuck + marimo tasks. Dispatch via `task` tool with `subagent_type: data-platform`. |
| **Functional subagent (5)** | `infrastructure` | Komodo + Pangolin + Locket + Infisical + 94-stack IaC. Dispatch via `task` tool with `subagent_type: infrastructure`. |
| **Functional subagent (5)** | `agent-platform` | BAML + LiteLLM + Langfuse + MLflow + RAGAS + Graphiti + Cognee + 12-agent fleet. Dispatch via `task` tool with `subagent_type: agent-platform`. |
| **Functional subagent (5)** | `frontend-apps` | TanStack Start + Convex + Hono + CopilotKit + AG-UI + marimo + Babylon.js. Dispatch via `task` tool with `subagent_type: frontend-apps`. |
| **Functional subagent (5)** | `research` | BrowserBase + Firecrawl + CCC + Cognee + change-detection. Dispatch via `task` tool with `subagent_type: research`. |
| **Domain subagent (10)** | `baml`, `dagster`, `mise`, `notebooks`, `orchestrator`, `proposal-author`, `deep-cuts`, `dev-env-demo` | Scoped to a single domain (BAML schema authoring, Dagster asset authoring, mise task authoring, marimo notebook authoring, openspec change authoring, deep structural analysis, dev-env demos). |

**Dispatch rules:**

- **Always use `build` (the default)** for general tasks — it has the full skill_filter.
- **Prefer a functional subagent** when the task is clearly within one of the 5 functional surfaces (data, infra, agents, web, research). The subagent gets a scoped skill_filter that improves focus + reduces token usage.
- **Prefer a domain subagent** when the task is specifically about authoring (e.g., "write a new Dagster asset" → `dagster` subagent).
- **Never dispatch `research` for tasks that require making changes** — the `research` subagent is read-only.

The full agent list + their `skill_filter` arrays live in `opencode.json` under the `agent` key. The 15 agent `.md` files under `.opencode/agents/` are the per-agent prompts (split out from the inline `prompt` field per the dev-tooling refactor).

## Domain-to-Skill Mapping

To ensure you use the appropriate skills for the different aspects of the project, strictly adhere to this mapping:

### Codebase Exploration & General Development
- **Code Search**: Use [`ccc`](.agents/skills/ccc/SKILL.md) (CocoIndex Code) for semantic search over the codebase. Prefer `ccc search` over raw `grep`/`find` to get context-aware, relevant files instantly.
- **Python Quality**: Use [`dignified-python`](.agents/skills/dignified-python/SKILL.md) for LBYL exception handling patterns, ABC interfaces, and explicit module boundaries.
- **Centralized Registries**: Load [`centralized-registry`](.agents/skills/centralized-registry/SKILL.md) when adding/changing/toggling any model, schema, pipeline, or stack. The canonical surfaces are `MODEL_REGISTRY` (76 entries / 7 families), `notebooks/_shared/schema.py` (5 introspection helpers), `deployment-choice.yaml` (the enablement file), and the `00_control_panel.py` marimo notebook (the 5-tab UI).

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

### 5. Concurrent-Write Safety Protocol (NEW 2026-08-22)

**Problem:** Multiple agents (orchestrator, 5 subagents, IDE sessions, hooks) operate against the same git working tree concurrently. Without a guard, an agent's carefully-staged diff can be wiped out by another agent's `git reset` / `git checkout --` / `git restore` / `git stash` operation. This was the root cause of the 2026-08-22 incident where 8 PR #5 file modifications were lost mid-session.

**Mandatory 4-step file edit protocol** (every file edit, every agent, every session):

```bash
# STEP 1 — BEFORE editing: verify the file is in the expected state
git status -- <path/to/file>
git diff -- <path/to/file>   # should be empty for tracked files
sha256sum <path/to/file>    # record the hash for cross-check

# STEP 2 — Make the edit (use Edit tool, Write tool, or shell sed/awk)
# ... your edit here ...

# STEP 3 — AFTER editing: verify the diff is what you expected
git diff -- <path/to/file>
sha256sum <path/to/file>    # should differ from STEP 1

# STEP 4 — Stage ONLY the intended files (NOT `git add -A` which scoops up unrelated changes)
git add <path/to/file>
git status -- <path/to/file>   # verify staged state

# COMMIT — always commit immediately after staging, in the SAME shell context
git commit -m "..."
git push origin <branch>
```

**If STEP 3 reveals unexpected changes** (different line counts, missing hunks, extra files):
- **ABORT** the commit immediately
- Run `git status` to inspect the full working tree
- Look for concurrent-agent artifacts: `.tmp_*` directories, branch-switch commits, stash entries, reflog
- Run `git reflog --date=iso | head -20` to see recent operations
- Re-apply the lost edits if possible; otherwise escalate to the orchestrator

**Forbidden patterns** (always cause concurrent-write disasters):
- ❌ `git add -A` / `git add .` — scoops up unrelated changes from concurrent agents
- ❌ `git stash --include-untracked` followed by `git stash pop` — race conditions with other stashes
- ❌ `git reset --hard` without first running `git stash`
- ❌ `git checkout -- <path>` without first verifying the file is clean
- ❌ `git restore --staged <path>` without re-running the safety protocol
- ❌ Multi-agent commits on the same branch without explicit coordination
- ❌ `git commit --amend` if any concurrent agent may have pushed between commit and push

**Safe patterns** (use these instead):
- ✅ `git add <specific/path>` — explicit file list
- ✅ `git status -- <path>` before AND after each edit
- ✅ One commit per task (not mega-commits with many unrelated changes)
- ✅ Use `git worktree add <path> <branch>` to isolate multi-agent work
- ✅ Commit IMMEDIATELY after staging (don't batch)

**The "CLAIM A FILE" pattern** (when multiple agents touch the same area):
```bash
# Agent A claims the dagster files
echo "$(date -Iseconds) agent A claims dagster/*" > /tmp/agent-claims.log

# Agent B waits or picks a different area
# Agent A finishes, commits, then releases the claim
echo "$(date -Iseconds) agent A releases dagster/*" >> /tmp/agent-claims.log
```

**Full openspec contract:** see `openspec/specs/repo-hygiene-agent-routing/spec.md` (3 ADDED Requirements added by `2026-08-22-concurrent-agent-write-safety-v1`).

**Reference incident:** the 2026-08-22 PR #5 file-loss event — see `openspec/changes/archive/2026-08-22-2026-08-22-lakehouse-observability-stacks-modernization-v1/proposal.md` § Notes section for the post-mortem.
