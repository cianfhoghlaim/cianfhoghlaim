# Agent Instructions

This project uses standard GitHub/Forgejo issues for task tracking. Please use `gh` or standard `git` workflows.

## Priority quick reference

The 5 priority skills, the 4 priority commands, the 4 priority
compose stacks, and the 4 priority openspec specs at a glance.
**Read this first**; the rest of the file is detail.

### Priority skills (7 of 155)

| Skill | When to load |
|:--|:--|
| [`motherduck`](.agents/skills/motherduck/SKILL.md) | MotherDuck storage pattern (managed / BYOB / DuckLake / own-compute) + MCP server |
| [`ccc`](.agents/skills/ccc/SKILL.md) | **Code search** — use `ccc search` before `grep` / `find` |
| [`browser-tools`](.agents/skills/browser-tools/SKILL.md) | Pick the right browser tool (Stagehand / Firecrawl MCP / Firecrawl CLI / Playwright / safe-browser) |
| [`agent-observability`](.agents/skills/agent-observability/SKILL.md) | Langfuse v3 + MLflow GenAI + RAGAS trace-based + Logfire |
| [`centralized-registry`](.agents/skills/centralized-registry/SKILL.md) | **The single source of truth for models + schemas** — MODEL_REGISTRY + notebooks/_shared/schema.py + deployment-choice.yaml (post-2026-08-15). Load this when adding/changing/toggling any model, schema, pipeline, or stack. |
| [`openspec`](openspec/AGENTS.md) | Spec-driven change management (94 specs, 4 shared — added secrets-management in the 2026-08-15 openspec change) |
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
openspec list --specs              # list all 92 capability specs (1 new post-2026-08-15 — bonneagar-infra-remediation-v2)
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

```bash
mise run lint:skills               # validate .agents/skills/ metadata (53/53 as of v4 consolidation)
mise run turbo dev                 # monorepo dev (bun + uv + turbo)
mise run secrets:init              # sync .infisical.env → dev-baile vault
mise run dagster:oideachais        # launch the lakehouse Dagster UI
# Shipped by the 2026-07-30 → 2026-08-01 openspec trilogy (3 new tasks):
mise run cic:stack-doctor          # validate all 89 Docker Compose stacks against the 6-file GOLD_STANDARD (canonical CI gate)
mise run stack-doctor:strict       # cic:stack-doctor + --strict --check-grammar (fails on missing infisical:// refs OR mixed bare/Jinja grammar in any secrets.env; NEW in Change 1, 2026-07-30)
mise run deploy:full               # one-command 7-phase full-stack deploy orchestrator with resumable checkpoint at ~/.cianfhoghlaim/deploy-state.json; entry shell + TS state machine; NEW in Change 3, 2026-08-01
```

### Priority sync commands

```bash
mise run sync:all                  # run all 8 sync layers (paths + ccc + cognee + skills + mcp + dagster + drift-docs + spec-agents)
mise run lint:drift-docs           # validate every AGENTS.md number claim against ground truth (per the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 change)
mise run openspec:validate         # run `openspec validate --strict` against the pending change under review
```

### Priority compose stacks (4 of 89)

| Stack | Port | Domain |
|:--|--:|:--|
| `oideachais` | 3080, 3335, 7777, 7778, 8000 | `cianfhoghlaim.cianfhoghlaim.ie` |
| `litellm` | 4000 | `litellm.cianfhoghlaim.ie` (LLM gateway) |
| `langfuse` | 3000 | `langfuse.cianfhoghlaim.ie` (LLM observability) |
| `lakehouse` | 3900-3904, 5433, 8181-8182 | internal (Garage S3 + Postgres + Lakekeeper) |

The full inventory of 94 stacks is at
[`../bonneagar/AGENTS.md`](../bonneagar/AGENTS.md) (the IaC
repo owns the stack catalogue; see the `## IaC Repo Boundary`
section below for the ownership table).

## Monorepo Topology (v7 — Flattened Polyglot)

Cianfhoghlaim is a **bun + uv + turbo polyglot monorepo**. Two
language graphs live side by side, orchestrated by `turbo.json`
and a single `mise.toml` toolchain. Post-v7 (2026-07-17), the
Python package IS the repo root — no more `cianfhoghlaim/`
nesting.

### TypeScript graph (bun workspaces)

The root `package.json` declares these `workspaces` and is the only manifest bun resolves:

| Workspace | Path | Purpose |
|:--|:--|:--|
| `cianfhoghlaim-web` | `web/apps/cianfhoghlaim-web/` | TanStack Start + React front-end (the public web app) |
| `tuatha-ui` | `web/apps/tuatha-ui/` | Túatha educational MMO front-end |
| `croilar-web` | `web/apps/croilar-web/` | Croílár multi-persona portfolio |
| `croilar-portal` | `web/apps/croilar-portal/` | Croílár portfolio dashboard |
| `tuatha-demo` | `web/apps/tuatha-demo/` | Tuatha Babylon.js demo |
| `game_showcase` | `web/apps/game_showcase/` | Web game showcase |
| `cianfhoghlaim-mcp-filesystem` | `web/apps/cianfhoghlaim-mcp-filesystem/` | Filesystem MCP server for the data platform |
| `hono-api` | `web/hono-api/` | Hono API gateway |

The IaC (`iac:bootstrap`, `iac:health`, etc.) lives in the
`bonneagar/` subdirectory and is reached via
`bun run --cwd bonneagar ...`.

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

## Triple-search architecture (ccc + cognee + firecrawl_mcp)

Per the `2026-08-14-firecrawl-mcp-ccc-dual-search-v1` change, the
agent stack now has **3 complementary search surfaces**. ccc and
cognee are local + free; firecrawl_mcp is external + metered. Every
agent session that runs `firecrawl_search` MUST also emit a
`ccc:search` query so both tool names appear in the Langfuse trace.

```
        ccc (code)              cognee (docs)       firecrawl_mcp (live web)
            │                       │                       │
            │   semantic/local      │   semantic/local      │   semantic/external
            │   FREE                │   FREE                │   metered (credits)
            │                       │                       │
            ▼                       ▼                       ▼
        ──────────────┬─────────────┴───────────────┬───────────────────
                      ▼                             ▼
              Local-fast lane                  External-deep lane
                      │                             │
                      └──────────────┬──────────────┘
                                     ▼
                            Agent (3-way merged)
```

**Routing table** (which tool wins for each question type):

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
| "Self-debug a Firecrawl call that failed" | `firecrawl_scrape /support/ask` | Agent-to-agent support |

The `FirecrawlMCPClient` wrapper at
`agents/meaisinfhoghlaim/firecrawl_mcp/client.py` exposes all 12 MCP
tools with Pydantic validation + Langfuse `@observe`. See the
[`dual-search-architecture`](../openspec/specs/dual-search-architecture/spec.md)
spec for the formal requirements.

### Python graph (uv workspace)

Post-v7, the root `pyproject.toml` IS the package — no workspace
shell. The single Python package is `cianfhoghlaim` (uv-built from
the repo root). Sub-packages:

| Sub-package | Path | Purpose |
|:--|:--|:--|
| `agents` | `agents/` | The 12-agent meaisínfhoghlaim fleet + ADK shims |
| `baml` | `baml/` | The BAML extraction schemas (LC + Celtic + multi-nation) |
| `cocoindex` | `cocoindex/` | The CocoIndex v1 Apps (42+ flows) |
| `dlt` | `dlt/` | DLT sources + destinations |
| `orchestration` | `orchestration/` | Dagster assets + jobs + schedules + sensors |
| `codeolas` | `libraries/codeolas/` | Code intelligence library (publishable sub-package) |

**v4 consolidation (2026-06-28):** All 5 former quadrants
(`sruth/oideachais`, `sruth/meaisinfhoghlaim`, `sruth/tuatha`,
`sruth/croilar`, `sruth/codeolas`) plus `infrastructure/browser/` +
`/leabharlann/` were merged into the single `cianfhoghlaim/` package
(see `openspec/changes/archive/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/`).
The 4 former quadrant `sruth/<quadrant>/AGENTS.md` files were
retired; the consolidated cianfhoghlaim sub-tree docs are at
`AGENTS.md` + the per-area sub-package AGENTS.md
files inside the repo.
Plan 1 (active): Ireland (5 education stages × EN + GA) + leabharlann
corpus (6 subdirs × 216 docs).

Members import each other via `[tool.uv.sources]` (e.g. `cianfhoghlaim` imports
`codeolas`).

### Pipeline orchestration

- `turbo.json` — cross-language task graph (`build`, `dev`, `typecheck`, `lint`, `format`, `test`, `clean`, `dagster`, `ccc:index`, `spec:validate`).
- `mise.toml` — toolchain (`python 3.12`, `uv`, `bun`, `dagger`, `pulumi`, `duckdb`, `sops`, `opencode`) **and** the developer task aliases (`mise turbo dev`, `mise ccc:search …`, `mise secrets:init`, `mise dagster:oideachais`, etc.).
- `dg.toml` — Dagster `dg` workspace that loads `oideachais`, `tuatha`, `croilar`, and `meaisínfhoghlaim` code-locations into a single UI. (Phase 0.1 of `lateralise-british-isles-domains` added croilar + meaisínfhoghlaim.)

### Developer onboarding (one command)

```bash
bun run setup
# expands to: mise install && bun install && uv sync && bun run secrets:env && bun run secrets:init
```

> **Note:** The `mise run lint:skills` task currently reports **157
> skills pass** (the v4 consolidation reduced the skill count from
> the historical 123 — see `openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/`).

### Centralized registries (post-2026-08-15)

The platform now has **one canonical source of truth** for every model, schema, pipeline, and stack — replacing the ~70 hardcoded model strings + 96 hand-written Pydantic duplicates + 54 nearly-identical CocoIndex Apps that the audit found.

| Asset | Path | Purpose |
|:--|:--|:--|
| **`MODEL_REGISTRY`** | `meaisinfhoghlaim/models/model_registry.py` | 52 entries across 7 families (ocr_vision / text_llm / embedder / rerank / image_gen / voice / translation). Use `model_for(family, role, language)` or `filter_models(family)`. |
| **`schema` introspection** | `notebooks/_shared/schema.py` | 5 helpers: `schema_introspect(conn)`, `schema_introspect_table(conn, name)`, `list_dlt_sources()`, `list_cocoindex_apps()`, `list_baml_classes()`. |
| **Deployment control panel** | `notebooks/00_control_panel.py` | The 5-tab marimo notebook (Models / Pipelines / Datasets / Stacks / Registry). Operates on `deployment-choice.yaml`. |
| **`deployment-choice.yaml`** | repo root | The canonical enablement file. Read/written by the notebook + web UI + CLI. |
| **`registry_audit.py`** | `scripts/registry_audit.py` | Detects hardcoded model strings that bypass `MODEL_REGISTRY`. Wired as `mise run lint:registry`. |
| **`litellm_agent.py`** | `agents/adk/litellm_agent.py` | The `make_litellm_agent()` helper + `litellm_model("minimax")` wrapper for ADK agents. |
| **CocoIndex factory pattern** | `cocoindex/european_nations/_factory.py` | Reference for collapsing N CocoIndex Apps into 1 factory. Used by the 40 European-nation Apps. |
| **Dagster `JurisdictionAssetsBase`** | `orchestration/defs/2_materials/_base/jurisdiction_assets_base.py` | The base class for the 10 per-jurisdiction Dagster asset wrappers. |

**Quick start for the most common needs:**

```python
# 1. Pick a model (replaces hardcoded "gemini-2.0-flash" etc.)
from meaisinfhoghlaim.models import model_for
default = model_for("text_llm", "default")              # → "minimax-m3"
irish  = model_for("text_llm", "irish", language="ga")  # → "uccix-mistral-24b"
embed  = model_for("embedder", "default")               # → "BAAI/bge-m3"

# 2. Discover the lakehouse schema (replaces hardcoded table lists)
from notebooks._shared.schema import (
    list_dlt_sources, list_cocoindex_apps, list_baml_classes,
)
print(f"DLT sources: {len(list_dlt_sources())}")        # → 1963
print(f"CocoIndex Apps: {len(list_cocoindex_apps())}")  # → ~53 (factory Apps + shims)
print(f"BAML classes: {len(list_baml_classes())}")      # → 838

# 3. Open the deployment control panel
# $ mise run notebook:control-panel
# (or: marimo edit notebooks/00_control_panel.py)
```


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
| Data platform (DLT + Dagster + BAML + CocoIndex + marimo) | `{dlt,orchestration,baml,cocoindex,notebooks}/` |
| Agent fleet (12 agents + OCR + BAML + LLM routing) | `agents/meaisinfhoghlaim/` |
| Frontend apps (TanStack Start + Convex + Hono + CopilotKit) | `web/apps/*/` |
| OpenSpec changes + specs | `openspec/` |
| MotherDuck Dives/Flights metadata | `motherduck/` |
| IaC (Komodo + Pangolin + Infisical clients) | `bonneagar/iac/` (IN THIS REPO) |
| 88 Docker Compose stacks | `bonneagar/stacks/<name>/` |
| Komodo resource-syncs + procedures | `bonneagar/komodo/` |
| Pangolin config | `bonneagar/pangolin/` |
| Deploy runbooks | `bonneagar/deploy-runbooks/` |
| Leabharlann corpus (216 docs × 6 subdirs) | `leabharlann/` (SEPARATE REPO at `github.com/cianfhoghlaim/leabharlann`) |

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
