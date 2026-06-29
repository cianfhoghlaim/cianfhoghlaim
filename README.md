# Cianfhoghlaim — Coláiste na Déisigh

> *The cianfhoghlaim application monorepo: a unified Celtic education platform, AI research laboratory, and multi-persona portfolio by Cian Mac an Déisigh Uí Liatháin (Deacy-Lyons).*

[![Polyglot](https://img.shields.io/badge/polyglot-bun_%2B_uv_%2B_turbo-blue)](#)
[![Dagster](https://img.shields.io/badge/dagster-228_assets-4B8BBE)](cianfhoghlaim/assets/)
[![v4](https://img.shields.io/badge/consolidation-v4-2026--06--28-orange)](openspec/changes/archive/)
[![License](https://img.shields.io/badge/license-BUSL_1.1-green)](LICENSE.md)

---

## TL;DR — What this is, today

`cianfhoghlaim` is a polyglot monorepo (`bun + uv + turbo`) that ingests the
curriculums and exam papers of the British Isles, makes them interactive and
bilingual through self-hosted AI, and serves as the personal research-and-
deployment platform of Cian Mac an Déisigh Uí Liatháin. After the **v4
consolidation of 2026-06-28**, all the application code lives in a single
Python package, [`cianfhoghlaim/`](./cianfhoghlaim/), served by a single
Dagster code-location and orchestrated by a single monorepo. The GitOps
foundation (`bonneagar`) and the digital library (`leabharlann`) live in
their own sibling repos and are exposed here as **git worktrees at the
root of the workspace** — they are *not* `git subtree`s, so the monorepo
push stays small (a few KB of README + skill metadata, not 3.4 GB of
PDFs). The platform is wired together by a **5-subagent OpenCode
foundation** (`data-platform`, `infrastructure`, `agent-platform`,
`frontend-apps`, `research`) backed by a 59-skill knowledge library
indexed by [cocoindex-code (ccc)](.agents/skills/ccc/SKILL.md).

---

## Repository constellation

This repository (`cianfhoghlaim/cianfhoghlaim`) is the **application
monorepo**. Two companion repositories live as their own GitHub repos
and are exposed here as **standalone git worktrees at the root of the
workspace**, so each domain has its own independent release cadence,
secrets boundary, and review surface — and so the monorepo push stays
small.

| Repo | Domain | Sibling repo | Worktree at the root |
|:--|:--|:--|:--|
| [**cianfhoghlaim/cianfhoghlaim**](https://github.com/cianfhoghlaim/cianfhoghlaim) (you are here) | Application monorepo: Python package, agents, web apps, Dagster pipelines, CocoIndex flows, OCR registry | n/a | this repo |
| [**cianfhoghlaim/bonneagar**](https://github.com/cianfhoghlaim/bonneagar) | GitOps foundation: Pulumi, Ansible, Komodo, Pangolin, Dagger, 90 compose stacks, secrets templates | [`bonneagar`](https://github.com/cianfhoghlaim/bonneagar) | `./bonneagar/` (branch `bonneagar-main` → `bonneagar/main`) |
| [**cianfhoghlaim/leabharlann**](https://github.com/cianfhoghlaim/leabharlann) | Digital library: Gaeilge, mata, aigne, ollscoil, Zotero papers, Gemini deep-research reports (2,400 files, 3.4 GB) | [`leabharlann`](https://github.com/cianfhoghlaim/leabharlann) | `./leabharlann/` (branch `leabharlann-main` → `leabharlann/main`) |

All three repositories are licensed under the **Business Source License
1.1** (BUSL-1.1) by the same Licensor. See [`LICENSE.md`](./LICENSE.md).

> *Bonneagar* — Scottish Gaelic for *infrastructure*.
> *Leabharlann* — Irish for *library*.

### Why worktrees, not subtrees?

The 3.4 GB of PDFs in `leabharlann` and the 6.9 MB of compose stacks in
`bonneagar` are too large to commit into the application monorepo's
git history. Embedding them as `git subtree`s would make every
`git push` upload 3 GB of binary data, slow CI to a crawl, and bloat
clone size for every contributor. The worktree approach keeps the
content *visible and editable* from this workspace without committing
it to this repo.

### Working with the sibling repos

```bash
# Edit the leabharlann corpus
cd leabharlann
# ... edit a PDF metadata file ...
git add -A
git commit -m "docs(zotero): add new paper on Irish NLP"
git push                       # → leabharlann-main → leabharlann/main → the GitHub repo

# Edit the bonneagar compose stacks
cd ../bonneagar
# ... edit infrastructure/stacks/litellm/compose.yaml ...
git add -A
git commit -m "chore(litellm): bump image tag"
git push                       # → bonneagar-main → bonneagar/main → the GitHub repo
```

From the monorepo's perspective, the worktrees are the canonical
*upstream* copies of the sibling repos. The monorepo consumes them
through relative paths:

- `./bonneagar/stacks/litellm/compose.yaml` — referenced in
  `infrastructure/AGENTS.md` (the bonneagar worktree's own quick-ref)
  and in [`docs/PHASE_0.3_DEPLOY_RUNBOOK.md`](docs/PHASE_0.3_DEPLOY_RUNBOOK.md)
- `./leabharlann/gaeilge/` — referenced in the Cognee dataset
  `oideachais_culture_heritage`
- `./leabharlann/zotero/` — referenced in the CocoIndex v1 App
  `leabharlann_zotero`

To pull the latest from the sibling repos:

```bash
git fetch bonneagar main
git fetch leabharlann main
cd bonneagar   && git merge --ff-only bonneagar/main   && cd ..
cd leabharlann && git merge --ff-only leabharlann/main && cd ..
```

---

## Temporary architecture diagram

> ⚠️ **Temporary.** This ASCII diagram is a stand-in for a Mermaid / d2
> diagram that will land in the next `docs-restructuring` openspec change.
> It shows the **3-tier host topology** (arm1-oci → cax41-hetzner →
> bunchloch) overlaid with the 3 repos, the 5 subagents, and the
> Lakehouse data plane.

```
                            ┌──────────────────────────────────────────────────────────┐
                            │  THE 5 DISPATCHABLE SUBAGENTS  (opencode.json)            │
                            │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───┴───┐
                            │  │   data-  │ │  infra-  │ │  agent-  │ │ frontend │ │research│
                            │  │ platform │ │ structure│ │ platform │ │  -apps   │ │       │
                            │  │   (15)   │ │   (16)   │ │   (23)   │ │   (20)   │ │  (11) │
                            │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬───┘
                            └───────┼────────────┼────────────┼────────────┼───────────┼─────┘
                                    │            │            │            │           │
            ┌───────────────────────┼────────────┼────────────┼────────────┼───────────┼────────────┐
            │  APPLICATION MONOREPO │            │            │            │           │            │
            │  (cianfhoghlaim/)     │            │            │            │           │            │
            │  ┌────────────────────▼────────────▼────────────▼────────────▼───────────▼──────────┐ │
            │  │                        cianfhoghlaim/ Python package                              │ │
            │  │                                                                                    │ │
            │  │  core/  (16 first-class stack pkgs)   sources/nations/  agents/                  │ │
            │  │  pipelines/  (5-stage: ingest→expose)  assets/  (Dagster code-location)           │ │
            │  │  ocr/  stacks/  web/  libraries/codeolas/  notebooks/  cognify/  embeddings/    │ │
            │  │                                                                                    │ │
            │  │  BAML  •  DLT  •  Dagster  •  CocoIndex v1  •  DuckLake  •  LanceDB  •  Cognee   │ │
            │  │  Langfuse  •  MLflow  •  RAGAS  •  12-agent fleet  •  marimo  •  TanStack Start │ │
            │  └────────────────────────────────────────────────────────────────────────────────────┘ │
            │                                                                                        │
            │   ┌────────────────────────────────────────────────────────────────────────────────┐   │
            │   │  GIT WORKTREES at the root of the workspace  (NOT subtrees — no 3 GB push)   │   │
            │   │  ┌────────────────────────────┐    ┌────────────────────────────┐            │   │
            │   │  │  ./bonneagar/              │    │  ./leabharlann/            │            │   │
            │   │  │  branch: bonneagar-main    │    │  branch: leabharlann-main  │            │   │
            │   │  │  tracking: bonneagar/main  │    │  tracking: leabharlann/main│            │   │
            │   │  │                            │    │                            │            │   │
            │   │  │  90 compose stacks         │    │  2,400 files, 3.4 GB       │            │   │
            │   │  │  Pulumi, Komodo, Pangolin  │    │  Gaeilge, mata, aigne      │            │   │
            │   │  │  Dagger, Ansible, secrets  │    │  Zotero, gemini_research    │            │   │
            │   │  │  6.9 MB total              │    │  (NOT in this monorepo)    │            │   │
            │   │  └────────────────────────────┘    └────────────────────────────┘            │   │
            │   └────────────────────────────────────────────────────────────────────────────────┘   │
            │                                                                                        │
            │       web/  apps/{oideachais-web, tuatha-ui, croilar-web, croilar-portal, …}/         │
            │             + hono-api/                                                               │
            └────────────────────────────────────────────────────────────────────────────────────────┘
                                                                                                        │
            ┌────────────────────────────────────────────────────────────────────────────────────────┐   │
            │  LLM GATEWAY  (LiteLLM, http://litellm:4000/v1)                                       │   │
            │  default_model = "minimax" alias  →  7-tier fallback                                    │   │
            │  opencode-go/minimax-m3-slot{0,1,2} → qwen3.7-max → kimi-k2.6 → glm-4.6 → local/math  │   │
            └────────────────────────────────────────────────────────────────────────────────────────┘   │
                                                                                                        │
            ┌────────────────────────────────────────────────────────────────────────────────────────┐   │
            │  3-TIER HOST TOPOLOGY                                                                 │   │
            │                                                                                        │   │
            │  arm1-oci     Oracle Ampere A1, 4 OCPU, 24 GB   →  Pangolin + Komodo + Garage S3      │   │
            │  cax41-hetzner Hetzner CAX41 ARM, 16 vCPU, 32 GB  →  Memgraph + FalkorDB + MLflow   │   │
            │  bunchloch    MacBook M4 Max, 14c, 48 GB         →  llama-swap + mlx-omni + Bria FIBO │   │
            └────────────────────────────────────────────────────────────────────────────────────────┘   │
                                                                                                        │
            ┌────────────────────────────────────────────────────────────────────────────────────────┐   │
            │  LAKEHOUSE DATA PLANE                                                                 │   │
            │  DLT  →  DuckLake (Parquet on Garage S3 + Postgres catalog)                           │   │
            │              ↓                                                                       │   │
            │  BAML  →  CocoIndex v1  →  LanceDB (BGE-M3, HNSW)                                    │   │
            │              ↓                                                                       │   │
            │  Cognee  →  FalkorDB (GraphRAG) + Graphiti (bi-temporal episodes)                     │   │
            │              ↓                                                                       │   │
            │  MotherDuck (md:oideachais)  →  marimo dashboards  +  AG-UI agents                    │   │
            └────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## The v4 consolidation (2026-06-28)

The five original **sruthanna** (`oideachais`, `meaisinfhoghlaim`, `tuatha`,
`croilar`, `crypteolas`) — plus the **browser** core module and the
**codeolas** C++ sub-package — were consolidated into a single Python
package, `cianfhoghlaim/`. The work was tracked in the openspec change
[`2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4`](openspec/changes/archive/)
and shipped as commit
`4bc20fd12 chore(v4): consolidate 5 sruth quadrants + browser + leabharlann into cianfhoghlaim`.

**Key outcomes:**

- **Single Python package** `cianfhoghlaim/` (with `libraries/codeolas/` as
  a publishable sub-package) instead of 5 sruthanna + a separate browser
  module.
- **Single Dagster code-location** at `cianfhoghlaim/assets/definitions.py`
  with 228 assets across 21 groups.
- **96 source files** at `cianfhoghlaim/sources/{nations,languages,_preserved}/`
  (Plan 1: Ireland 5 stages × EN + GA; Plan 2: EN/NI/WLS/SCT/IOM as
  preserved stubs; legacy Crown Dependencies JEY/GGY archived).
- **OCR registry** — 9 vision + 4 classical + 3 image-gen models in a
  single registry at `cianfhoghlaim/ocr/`.
- **CocoIndex v4 OCR-aware flows** (`ocr_aware_flow` + `leabharlann_flow`).

The five subagent definitions in `opencode.json` were **rewritten** to
align with the v4 layout — see the
[`2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation`](openspec/changes/2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation/proposal.md)
openspec change.

The GitOps foundation (`infrastructure/`) and the digital library
(`leabharlann/`) were **split into their own repositories** so each
domain has an independent release cadence, secrets boundary, and review
surface. The 3.4 GB PDF corpus in leabharlann is too large to embed
as a `git subtree` (it would inflate every push to 3 GB), so the
sibling repos are exposed in this monorepo as **git worktrees at the
root of the workspace** — `./bonneagar/` and `./leabharlann/` — for
editing and inspection. The original openspec change
[`2026-06-28-split-leabharlann-bonneagar`](openspec/changes/2026-06-28-split-leabharlann-bonneagar/proposal.md)
is being **amended** to reflect the worktree approach instead of
the subtree approach.

---

## What you can deploy today

An honest, prioritised list of the working features and the work that
is still needed before each tier is "done".

### Tier 1 — production-ready (5 services)

| Service | What it does | Stack | Where |
|:--|:--|:--|:--|
| **LiteLLM gateway** | OpenAI-compatible proxy; `minimax` 7-tier fallback alias | LiteLLM | `./bonneagar/stacks/litellm/` (port 4000) |
| **Lakehouse** | Garage S3 + Lakekeeper (Iceberg REST) + Postgres catalog | Garage, Lakekeeper, Postgres | `./bonneagar/stacks/lakehouse/` (ports 3900-3904, 5433, 8181-8182) |
| **Cognee** | Knowledge-graph cognify over 6 typed datasets (aistear, primary, junior_cycle, senior_cycle, tertiary, cross_stage) | Cognee | `./bonneagar/stacks/cognee/` (port 8100) |
| **Dagster UI** | Single code-location, 228 assets, 21 groups | Dagster | `mise run dagster:oideachais` (port 3000) |
| **OpenChamber** | OpenCode web/desktop UI; multi-agent parallel runs, branchable chat timelines, worktree isolation | OpenChamber | `./bonneagar/stacks/openchamber/` (port 3000, deployed to `openchamber.cianfhoghlaim.ie`) |

### Tier 2 — functional, needs polish (4 services)

| Service | What it does | Stack | Where |
|:--|:--|:--|:--|
| **Graphiti** | Bi-temporal knowledge-graph episodes; Neo4j backend | Graphiti + Neo4j | `./bonneagar/stacks/graphiti/` |
| **FalkorDB** | Vector + graph hybrid for GraphRAG | FalkorDB | `./bonneagar/stacks/falkordb/` |
| **Dragonfly** | In-memory store for agent state | Dragonfly | `./bonneagar/stacks/dragonfly/` |
| **RisingWave** | Streaming SQL for change-data-capture | RisingWave | `./bonneagar/stacks/risingwave/` |

### Tier 3 — works on `bunchloch` only, not yet on `arm1-oci`

- **DLT ingestion** — 28 sources under `cianfhoghlaim/sources/` +
  `USE_LOCAL_SCRAPES` cache for offline development. Needs the
  `oideachais-pipeline` openspec change to wire the full live-source
  sweep.
- **BAML extraction** — 6 consolidated BAML files, 3 named clients
  (`ExtractEn` / `ExtractEnStrong` / `LocalVision`), all routing
  through LiteLLM `minimax`.
- **CocoIndex v1** — 4 v1 Apps (`leabharlann_embedding`,
  `codebase_indexing`, `docs_skills_consolidation`, `unified_embedding`)
  with BGE-M3 embeddings mounted to LanceDB HNSW.
- **OCR registry** — 9 vision + 4 classical + 3 image-gen models at
  `cianfhoghlaim/ocr/`.
- **The 12-agent fleet** at
  `cianfhoghlaim/agents/meaisinfhoghlaim/agents/`
  (curriculum, translation, corpus, research, geospatial, voice,
  statistics, education-research, bunchloch-research, AG-UI
  curriculum, MCP curriculum, enhanced orchestrator, root).
- **Web surfaces** — `oideachais-web` (TanStack Start, the largest),
  `tuatha-ui` (Babylon.js), `croilar-web` (multi-persona),
  `croilar-portal` (admin).
- **Observability** — Langfuse (remote MCP), MLflow, RAGAS, Logfire.

### Tier 4 — early / experimental

- **Crypteolas** — Rust + SpacetimeDB backend for the Tuatha MMO; agent
  fleet needs to land on the `oideachais-agent-services` openspec change.
- **HuggingFace Spaces** — `an_scrudu` (Irish Leaving Cert tutor),
  `meaisin_cliste` (Celtic AI playground), `anam_tuatha` (Tuatha MMO
  teaser).
- **Spaces (anti-phish, data-engineering)** — local-only, not yet
  deployed.

### How to boot Tier 1

```bash
# Tier 1 (in order)
cd ./bonneagar/stacks/lakehouse  && ./scripts/stack.sh up -d
cd ../litellm                        && ./scripts/stack.sh up -d
cd ../cognee                         && ./scripts/stack.sh up -d
cd ../../../                          # back to monorepo root
mise run dagster:oideachais           # → http://localhost:3000
```

The full end-to-end runbook is at
[`docs/PHASE_0.3_DEPLOY_RUNBOOK.md`](docs/PHASE_0.3_DEPLOY_RUNBOOK.md).

---

## Key packages

The post-v4 `cianfhoghlaim/` package is organised so that **each
directory has a single, obvious purpose**. Read this section once and
you'll know where to add the next thing.

### `cianfhoghlaim/core/` — 16 first-class stack packages

The lower layers of the data platform. Every other package either depends
on these or sits alongside them.

| Package | Purpose | When to use it |
|:--|:--|:--|
| `dlt/` | Ingestion (`filesystem`, `rest_api`, `cross-domain-registry`) | Add a new curriculum source |
| `duckdb/` | Local OLAP engine | Quick interactive analytics |
| `ducklake/` | ACID lakehouse (Parquet on Garage S3 + Postgres catalog) | The default write target |
| `lancedb/` | Vector DB + HNSW indexing | Embedding retrieval |
| `motherduck/` | Managed reads (`md:oideachais`) | Zero-ops read path |
| `cocoindex/` | v1 App pattern + v4 OCR-aware flows | Document-to-embedding pipeline |
| `baml/` | 6 consolidated BAML files (was 21) | Structured LLM extraction |
| `marimo/` | Reactive notebook framework | Dashboards and analysis |
| `browser/` | Stagehand + Firecrawl + safe-browser | Web scraping and automation |
| `cognee/` | Knowledge graph + cognify | Persist semantic relationships |
| `obs/` | Langfuse + MLflow + RAGAS + Logfire | Trace and evaluate LLM calls |
| `rag/` | Hybrid retrieval + RAGAS eval | Build a RAG pipeline |
| `search/` | Semantic + faceted search | Expose the corpus to end-users |
| `curriculum/` | Celtic curriculum domain models | Type-safe curriculum schemas |
| `config/` | Pydantic BaseSettings + Infisical loader | Centralised config |
| `memory/` | Agent memory (Cognee + Graphiti + Letta) | Long-term agent state |

### `cianfhoghlaim/pipelines/` — the 5-stage ingestion→expose pipeline

| Stage | Package | What it does |
|:--|:--|:--|
| 1. **ingest** | `pipelines/ingest/` | DLT sources → DuckLake |
| 2. **extract** | `pipelines/extract/` | BAML extraction |
| 3. **embed** | `pipelines/embed/` | CocoIndex v1 → LanceDB HNSW |
| 4. **cognify** | `pipelines/cognify/` (alias of `cognify/`) | Cognee knowledge graph |
| 5. **expose** | `pipelines/distribute/` | MotherDuck + marimo + agents |

The 5 stages are detailed in the next section — see
[The pipelines — what cianfhoghlaim can do](#the-pipelines--what-cianfhoghlaim-can-do)
for the exact Python files, Dagster asset names, BAML function names,
and entry-point commands.

### `cianfhoghlaim/sources/` — what we're trying to ingest

```
sources/
├── nations/                # 6 active + 2 legacy nations × 3-5 education stages
│   ├── ie/                 # Plan 1: 5 stages × {english, gaeilge} = 10 ACTIVE
│   ├── en, ni, wls, sct, iom/  # Plan 2: preserved stubs
│   └── _preserved/{jey,ggy}/   # legacy Crown Dependencies
└── languages/              # 7 Celtic + English languages (Plan 1: english, gaeilge ACTIVE)
    ├── english.py
    ├── gaeilge.py
    ├── brezhoneg.py        # (Brittany)
    ├── cymraeg.py          # (Wales)
    ├── gaelg.py            # (Isle of Man)
    ├── gaidhlig.py         # (Scotland)
    └── kernewek.py         # (Cornwall)
```

### `cianfhoghlaim/assets/` — single Dagster code-location

The Dagster entry point is **`cianfhoghlaim/assets/definitions.py`**,
which Dagster loads as a single code-location. The per-quadrant asset
bundles (`_oideachais_dagster_defs/`, `_meaisinfhoghlaim_assets/`,
`_tuatha_assets/`, `_croilar_dagster/`, `_croilar_assets/`) are
sub-modules, lazily imported.

### `cianfhoghlaim/agents/` — 11 sub-packages, 12-agent fleet

| Sub-package | Purpose |
|:--|:--|
| `meaisinfhoghlaim/` | The 12-agent fleet (curriculum, translation, corpus, research, geospatial, voice, statistics, education-research, bunchloch-research, AG-UI, MCP, enhanced orchestrator, root) |
| `tuatha/` | Babylon.js + SpacetimeDB + crypteolas crypto platform |
| `oideachais/` | Curriculum agents |
| `croilar/` | Persona agents |
| `root/` | Orchestrator |
| `mcp_server/` | MCP server glue |
| `mcp/` | MCP client tooling |
| `adk/` | Google ADK integration |
| `api/` | FastAPI/Hono API surface |
| `image_pipeline/` | Image generation and processing |
| `language/` | Language-specific agent adapters |
| `shared/` | Shared agent utilities |

### `cianfhoghlaim/stacks/` — 33 user-pre-selected compose stacks

The Tier 1 + Tier 2 stacks (see [What you can deploy today](#what-you-can-deploy-today))
are vendored as first-class sub-packages of `cianfhoghlaim/`. The full
90-stack catalogue lives in `./bonneagar/stacks/` (the worktree at the
root of the workspace). Both follow the **6-file GOLD_STANDARD**
pattern from [`./bonneagar/GOLD_STANDARD.md`](./bonneagar/GOLD_STANDARD.md).

### `cianfhoghlaim/ocr/` — OCR registry

```
ocr/
├── _meaisinfhoghlaim_src/  # legacy meaisínfhoghlaim OCR code (preserved)
├── _oideachais_src/        # legacy oideachais OCR code (preserved)
├── alignment/              # sentence-level Irish↔English aligner, ColPali visual aligner
├── document_factory/       # exam paper → structured document
├── evaluation/             # OCR evaluation harness
├── geospatial/             # coordinate extraction from maps
├── quality/                # OCR quality scoring
└── training/               # OCR model training pipelines
```

The audit of the 16 OCR models (9 vision + 4 classical + 3 image-gen) is
in [`docs/audit/ocr-model-audit.md`](docs/audit/ocr-model-audit.md) and
[`docs/audit/ocr-model-audit-batch2.md`](docs/audit/ocr-model-audit-batch2.md).
The P0 model_id renames from the HF audit have shipped
(commit `33500d388`).

### `cianfhoghlaim/web/` — 7 web apps + 1 Hono API

| App | Stack | What it is |
|:--|:--|:--|
| `apps/oideachais-web/` | TanStack Start | The public Celtic education data platform (the largest) |
| `apps/tuatha-ui/` | Babylon.js | The Tuatha educational MMO front-end |
| `apps/croilar-web/` | TanStack Start | The Croílár multi-persona portfolio (public site) |
| `apps/croilar-portal/` | TanStack Start | The Croílár portfolio dashboard (admin) |
| `apps/game_showcase/` | React | Web game showcase |
| `apps/tuatha-demo/` | Babylon.js | Tuatha Babylon.js demo |
| `hono-api/` | Hono | The Hono API gateway (backend) |

The 5-web-app → 1-`cio-web` consolidation plan is in
[`docs/audit/web-app-consolidation-plan.md`](docs/audit/web-app-consolidation-plan.md).

### `cianfhoghlaim/libraries/codeolas/` — publishable sub-package

A C++ + WASM + MCP code-analysis library: semantic search, AST
knowledge graph, MCP server. The publishable wheel name is **`codeolas`**.

### `cianfhoghlaim/notebooks/` — 7 marimo notebooks

```
notebooks/
├── _oideachais/         # Ireland curriculum analysis
├── meaisinfhoghlaim/    # AI/ML pipelines
├── croilar/             # Croilar portfolio analysis
└── speedrun/            # Synthetic end-to-end demo
```

### `./bonneagar/` (worktree) — 90 compose stacks

The canonical 90-stack catalogue lives in
[`./bonneagar/stacks/`](./bonneagar/stacks/). The 4 priority stacks
are `oideachais`, `litellm`, `langfuse`, and `lakehouse`; see
[`./bonneagar/AGENTS.md`](./bonneagar/AGENTS.md) for the full
inventory. 90 stacks × ~10 KB each = 6.9 MB total, all in the
sibling repo (not in this monorepo).

#### The bonneagar directory tree (canonical 10-subdir layout)

```
bonneagar/
├── AGENTS.md                   # bonneagar quick reference
├── GOLD_STANDARD.md            # the 6-file stack pattern (compose + sidecar + secrets + pangolin + blueprint + .env.example)
├── DEPLOYMENT-STRATEGY.md      # 3-tier host topology + roll-out sequence
├── PANGOLIN-SETUP.md           # Pangolin private-resources setup (the 6-label pattern)
├── package.json                # bun workspace + scripts
├── bun.lock
├── ansible/                    # legacy IaC + playbooks
├── ci/                         # CI scripts
├── dagger/                     # 8-step GitOps pipeline (the `infrastructure/dagger/` README)
├── deploy-runbooks/            # per-stack deploy runbooks
├── docs/                       # bonneagar internal docs
├── firecrawl/                  # self-hosted Firecrawl instance configs
├── iac/                        # Pulumi IaC (3-tier host topology: arm1-oci / cax41-hetzner / bunchloch)
├── infisical_secret/           # the 3-way secrets contract (source-of-truth → template → hydrated runtime)
├── komodo/                     # deploy procedures for every stack (one .toml per stack)
├── legacy/                     # retired IaC artefacts
├── observability/              # shared Grafana / Loki / Prom / OTel configs
├── pangolin/                   # Pangolin private-resources + 6-label pattern
└── audit/                      # security + compliance + drift audits
```

The 6-file GOLD_STANDARD pattern is the contract every new stack must
follow. See `./bonneagar/GOLD_STANDARD.md` for the full spec; in short,
a new stack `infrastructure/stacks/<name>/` must contain:

1. `compose.yaml` — the Docker Compose service definition
2. `sidecar.yaml` — the Locket / Infisical sidecar that injects secrets at runtime
3. `secrets.env` — the secret *names* (never the values)
4. `pangolin.yaml` — the 6-label private-resources shape
   (`pangolin.private-resources.<name>.*`)
5. `blueprint.yaml` — the Komodo procedure that deploys the stack
6. `.env.example` — the developer-onboarding template

Adding a new stack is then a 4-step `bun run` sequence; the
`stack-doctor.sh` validation script enforces the pattern.

### `./leabharlann/` (worktree) — 2,400 files, 3.4 GB

```
leabharlann/
├── gaeilge/                    # 38+ Irish-language PDFs
├── mata/                       # 27+ mathematics textbooks
├── aigne/                      # 72+ cognitive science / mind books
├── ollscoil_na_gaillimhe/      # 21+ University of Galway coursework archives
├── zotero/                     # 34+ research papers (Zotero export)
└── gemini_deep_research/       # 24+ long-form Gemini deep research reports
                              # (culture/ medical/ politics/ — the corpus cited in the
                              #  cianfhoghlaim plan throughout the British Isles)
```

The 2,400 files / 3.4 GB corpus lives entirely in the sibling
`leabharlann` repo and is exposed here as a worktree. To use the
corpus from the monorepo, reference it through the relative path
`./leabharlann/...` (or symlink it into a working location).

#### The leabharlann directory tree (canonical 6-subdir layout)

| Subdir | Contents | Used by |
|:--|:--|:--|
| `gaeilge/` | 38+ Irish-language PDFs (curriculum, dictionaries, grammar) | the `oideachais_gaeilge` CocoIndex v1 App; the `ExtractEn` BAML function; the marimo notebook at `cianfhoghlaim/notebooks/_oideachais/gaeilge.py` |
| `mata/` | 27+ mathematics textbooks (algebra, calculus, statistics, applied maths) | the `oideachais_mata` CocoIndex v1 App; the `ExtractEn` BAML function; the marimo notebook at `cianfhoghlaim/notebooks/_oideachais/mata.py` |
| `aigne/` | 72+ cognitive science / mind books (neuroscience, psychology, linguistics) | the `oideachais_aigne` CocoIndex v1 App; the `meaisinfhoghlaim_aigne` cognify pass |
| `ollscoil_na_gaillimhe/` | 21+ University of Galway coursework archives (transcripts, parchments, teaching portfolio, Irish-language exam results, the 5 mat / 5 education / 5 software-dev / 3 irish / 3 past evidence folders) | the README's "On the verified qualifications" section; the `leabharlann_full_stack_demo` Dagster asset group |
| `zotero/` | 34+ research papers (Zotero export with full text + metadata) | the `leabharlann_zotero` CocoIndex v1 App; the `leabharlann_zotero_embedding` LanceDB index |
| `gemini_deep_research/` | 24+ long-form Gemini deep research reports across `culture/`, `medical/`, `politics/` — the corpus that grounds the cianfhoghlaim plan throughout the British Isles | the `culture_extraction.baml:ExtractCultureClaims` BAML function; the `culture_heritage` Cognee dataset; the §20 and §21d/f of the README |

The 8 PDF clippings in
`./leabharlann/../cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`
(Uí Liatháin, Delbhna Tír Dhá Locha, Eamonn Deacy Park, Leath Cuinn
and Leath Moga, Cian, Aos Sí, Tuatha Dé Danann, Déisi) are the
canonical Wikipedia dual-write corpus for the §21c heritage section
of the README; their SHA-256 is recorded in the 8 DLT fixtures at
`cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/official_media/fixtures/identity_*.json`
(see the `Wikipedia fixture storage convention` Requirement in
`openspec/specs/cross-domain-registry/spec.md` for the
drift-detector invariant).

#### Why two sibling repos, not subtrees

The `leabharlann` corpus (3.4 GB of PDFs) and the `bonneagar` IaC +
compose-stack catalogue (6.9 MB across 90 stacks) are too large to
commit to the application monorepo's git history. Embedding them as
`git subtree`s would make every `git push` upload 3 GB of binary
data, slow CI to a crawl, and bloat clone size for every contributor.
The worktree approach keeps the content *visible and editable* from
this workspace without committing it to this repo. See
[Why worktrees, not subtrees?](#why-worktrees-not-subtrees) above
for the full rationale.

### `spaces/` — HuggingFace Spaces

HuggingFace Spaces published from this monorepo (deploy with the
reusable workflow at `.github/workflows/spaces-sync.yml`):

| Space | Stack | Domain |
|:--|:--|:--|
| `an_scrudu` | Gradio + Gemma-3 | Irish Leaving Cert tutor |
| `meaisin_cliste` | Gradio + BAML + LiteLLM | Celtic AI playground |
| `cianfhoghlaim` | Static SDK landing | Project landing |
| `anam_tuatha` | Static SDK + Babylon.js | Tuatha MMO teaser |

---

## The pipelines — what cianfhoghlaim can do

The post-v4 cianfhoghlaim monorepo is organised around 5 sequential
pipelines that take a corpus (PDFs, DOCX, EPUBs, Zotero exports,
Google Takeout, UoG coursework, exam papers) from raw disk all the
way through to a queryable, agent-consumable, semantically-indexed
artifact. This section walks each pipeline with the exact Python
files, Dagster asset names, BAML function names, and entry-point
commands. The next section ([5 cookbook recipes](#5-cookbook-recipes))
turns the same map into worked end-to-end examples.

### Stage 1 — `pipelines/ingest/`

**Purpose.** Pull a corpus (PDFs, DOCX, EPUBs, Zotero exports, Google
Takeout, UoG coursework, exam papers) into the Lakehouse (DuckLake:
Parquet on Garage S3 + Postgres catalog). The DLT sources are domain-
and nation-aligned: 6 active nations (`ie`, `ni`, `en`, `wls`, `sct`,
`iom`) × 5 education stages × {EN, GA} for Ireland; 5 dlt sources for
the oideachais domain (ireland_primary_jc, ireland_leaving_cert,
official_media, university_of_galway_deep, gemini_deep_research); 4
dlt sources for the leabharlann domain (books, zotero, takeout_v1,
uog_coursework).

| Field | What it contains |
|:--|:--|
| Source files | `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/__init__.py` (the source registry), the per-domain factory files (`ireland_primary_jc_factory.py`, `ireland_leaving_cert_factory.py`, `official_media_factory.py`, `university_of_galway_deep_factory.py`, `gemini_deep_research_factory.py`), the per-leabharlann source files (`books_source.py`, `zotero_source.py`, `takeout_source.py`, `uog_coursework_source.py`), and `cianfhoghlaim/sources/_oideachais_sources.yaml` (the 96+ source definitions) |
| Asset names | `leabharlann_full_stack_demo` (asset group), `leabharlann_books`, `leabharlann_zotero`, `leabharlann_takeout`, `leabharlann_uog_coursework`, `ireland_primary_jc_*`, `ireland_leaving_cert_*`, `gemini_deep_research_culture`, `gemini_deep_research_medical`, `gemini_deep_research_politics` |
| BAML functions | n/a (this stage is DLT-only) |
| Command | `mise run dagster:oideachais` → open http://localhost:3000 → materialise the asset group. **Or** `USE_LOCAL_SCRAPES=true uv run python -m cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources.official_media` to run a single DLT source offline against the `stedding/ingest_queue/` cache. |
| What you can do with it | Drop a new PDF in `leabharlann/gemini_deep_research/culture/` and it lands in `lakehouse.leabharlann_books` (and the `gemini_deep_research_culture` asset materialises) within the next materialisation. The `USE_LOCAL_SCRAPES=true` env var routes through the offline cache at `stedding/ingest_queue/` so that the scrape never goes live without an explicit decision. |

### Stage 2 — `pipelines/process/` (BAML extraction)

**Purpose.** Extract structured claims from the ingested corpus. The
9 BAML source files at `cianfhoghlaim/core/baml/_oideachais_src/` (3
named clients — `ExtractEn` for general English extraction,
`ExtractEnStrong` for higher-precision LLM calls, `LocalVision` for
vision-capable extraction — and 6 domain-specific schemas:
`culture_extraction.baml:ExtractCultureClaims`,
`ireland_primary_jc.baml`, `ireland_leaving_cert.baml`,
`official_media.baml`, `university_extraction.baml`, `celtic_languages.baml`)
all route through the LiteLLM `minimax` 7-tier fallback alias.

| Field | What it contains |
|:--|:--|
| Source files | `cianfhoghlaim/core/baml/_oideachais_src/culture_extraction.baml`, `…/ireland_primary_jc.baml`, `…/ireland_leaving_cert.baml`, `…/official_media.baml`, `…/university_extraction.baml`, `…/celtic_languages.baml`; the BAML runtime at `cianfhoghlaim/pipelines/process/_oideachais_baml_runtime.py`; the generated Python client at `baml_client/` (regenerated by `baml-cli generate`) |
| Asset names | `culture_heritage_extract`, `ireland_primary_jc_extract`, `ireland_leaving_cert_extract`, `official_media_extract`, `university_deep_extract` |
| BAML functions | `ExtractCultureClaims` (the `CultureHeritageClaim` Pydantic schema: lineage / region / canonical citation / claim type / confidence), `ExtractEn` (general), `ExtractEnStrong` (high-precision), `LocalVision` (vision), plus 6 domain-specific Extract functions |
| Command | `mise run baml:generate` to regenerate `baml_client/` after any `.baml` edit; then `mise run dagster:oideachais` → materialise the `culture_heritage_extract` asset. The `low_confidence_review` Dagster asset_check flags any extraction with `confidence < 0.7` for human review. |
| What you can do with it | Extract a structured `CultureHeritageClaim` record from a 15-page Gemini Deep Research PDF in ~3 seconds via LiteLLM; the BAML schema enforces that the `canonical_citation` field references a Wikipedia article, the `region` field is one of the 4 provinces, and the `confidence` is a 0.0-1.0 float. The 96+ source files in `_oideachais_sources.yaml` map to per-domain BAML extraction functions. |

### Stage 3 — `pipelines/embed/` (CocoIndex v1)

**Purpose.** Embed the BAML-extracted chunks into LanceDB (BGE-M3
+ BGE-large-en-v1.5) for semantic search. The 4 v1 CocoIndex Apps
(`leabharlann_books_embedding`, `leabharlann_zotero_embedding`,
`leabharlann_takeout_embedding`, `unified_embedding`) each follow the
canonical v1 App pattern: `@coco.fn` flow + `@coco.lifespan`
runtime + `lancedb.mount_table_target` + `Annotated[NDArray, EMBEDDER]`
typing. The canonical shared home for `LANCE_DB` + `EMBEDDER` +
`RESOLVED_FILE_REGISTRY` is `_lifespan.py` per the 4-rule v1
conformance contract (R1-R4) enforced by the
`cocoindex_v1_conformance` App.

| Field | What it contains |
|:--|:--|
| Source files | `cianfhoghlaim/pipelines/embed/_oideachais_cocoindex_flows/leabharlann_embedding.py` (the 3 leabharlann v1 Apps), `…/culture_heritage_embedding.py` (the 12th v1 App), `…/_lifespan.py` (the shared runtime), `…/unified_embedding.py` (the 4th App) |
| Asset names | `leabharlann_books_embedding`, `leabharlann_zotero_embedding`, `leabharlann_takeout_embedding`, `culture_heritage_embedding`, `unified_embedding` |
| BAML functions | n/a (this stage is CocoIndex v1, not BAML). The embed stage consumes the BAML-extracted chunks from Stage 2 as `coco.datatypes.Sentence` records. |
| Command | `mise run cocoindex:dev` to run all 4 v1 Apps locally; or materialise the `*_embedding` assets in Dagster. |
| What you can do with it | Query the semantic-search index across the 5 leabharlann corpora + the 6 oideachais domains in one LanceDB namespace. The 4-rule v1 conformance contract (R1-R4) is enforced by the `cocoindex_v1_conformance` App — see `.agents/skills/oideachais-cocoindex-v1/SKILL.md` for the canonical pattern. |

### Stage 4 — `cognify/` (Cognee + Graphiti + FalkorDB + LanceDB)

**Purpose.** Build the knowledge graph over the 6 typed Cognee
datasets (`aistear`, `primary`, `junior_cycle`, `senior_cycle`,
`tertiary`, `cross_stage`) plus the 3 leabharlann cognify passes
(`leabharlann_books_cognify`, `leabharlann_zotero_cognify`,
`leabharlann_takeout_cognify`) plus the 3 cross-archive edge rules
(`leabharlann_cross_archive`, `oideachais_cross_archive`,
`culture_cross_archive`). The cognify stage emits cross-dataset
edges to FalkorDB (for GraphRAG), to Graphiti (for bi-temporal
episodes), and to LanceDB (for unified vector retrieval).

| Field | What it contains |
|:--|:--|
| Source files | `cianfhoghlaim/cognify/_oideachais_main.py` (the orchestrator), `…/_oideachais_cognee_pipeline.py` (the per-dataset cognify), `…/rules/leabharlann_cross_archive.py` (the 3 edge rules), `…/rules/culture_cross_archive.py`, `…/rules/oideachais_cross_archive.py`, `…/leabharlann_cognify.py` (the 3 leabharlann cognify passes) |
| Asset names | `cognify_aistear`, `cognify_primary`, `cognify_junior_cycle`, `cognify_senior_cycle`, `cognify_tertiary`, `cognify_cross_stage`, `leabharlann_books_cognify`, `leabharlann_zotero_cognify`, `leabharlann_takeout_cognify` |
| BAML functions | n/a (Cognee does the LLM-driven entity extraction; BAML is upstream) |
| Command | `mise run cognee:cognify --dataset <name>` (or via the Dagster `cognify_*` assets). The Cognee server is reachable at `http://localhost:8100` after `cd ./bonneagar/stacks/cognee && ./scripts/stack.sh up -d`. |
| What you can do with it | Run `cognify` over the entire `culture_heritage` Cognee dataset and the 8 Wikipedia clippings at `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/` will appear as GraphRAG-queryable entities in the next 30 seconds, with cross-dataset edges to the `oideachais_heritage` and `leabharlann_heritage` datasets. |

### Stage 5 — `pipelines/distribute/` (expose)

**Purpose.** Expose the lakehouse + graph + embeddings to the 7 web
apps, 7 marimo notebooks, 11 HuggingFace Spaces, and 12-agent fleet.
The distribute stage is the read-only mirror of the ingest+process
chain: MotherDuck (`md:oideachais`) for zero-ops managed reads,
TanStack Start for the 5 web apps (the largest is `oideachais-web`),
Babylon.js for the Tuatha MMO front-end, marimo for the 7 reactive
notebooks at `cianfhoghlaim/notebooks/`.

| Field | What it contains |
|:--|:--|
| Source files | `cianfhoghlaim/pipelines/distribute/_oideachais_storage_targets.py` (the read-target registry), the 5 `*_to_*` Dagster assets (`parquet_to_motherduck`, `lancedb_to_marimo`, `falkordb_to_agent`, `cognee_to_web`, `lancedb_to_space`), the 7 web apps at `cianfhoghlaim/web/apps/`, the 1 Hono API at `cianfhoghlaim/web/hono-api/`, the 7 marimo notebooks at `cianfhoghlaim/notebooks/` |
| Asset names | `parquet_to_motherduck`, `lancedb_to_marimo`, `falkordb_to_agent`, `cognee_to_web`, `lancedb_to_space` |
| BAML functions | n/a (the distribute stage is read-only) |
| Command | `mise run turbo dev` boots the full local stack (lakehouse + litellm + llama-swap + mlx-omni + the 5 web apps + the 7 marimo notebooks). Then open http://localhost:3000 for Dagster, http://localhost:8100 for Cognee, http://localhost:4000/v1 for LiteLLM, http://localhost:3001 for oideachais-web. |
| What you can do with it | Run `mise run turbo dev` and the entire ingestion-to-expose chain is live on `bunchloch` (the MacBook M4 Max). A new PDF lands in the lakehouse via DLT, gets BAML-extracted, gets CocoIndex-embedded, gets Cognee-cognified, and is queryable in the marimo notebook + the oideachais-web TanStack Start app within the next materialisation. |

---

## 5 cookbook recipes

The 5-stage pipeline is the architecture. The 5 recipes are the
worked examples — each one is a 3-4 step "do this, then this, then
this" that takes you from a blank terminal to a concrete result.

### Recipe 1 — Ingest a new Gaeltacht PDF

```bash
# 1. Drop the PDF in the leabharlann corpus
cp my-gaeltacht-paper.pdf leabharlann/gemini_deep_research/culture/

# 2. Update the DLT source YAML to point at the new file
#    (edits: cianfhoghlaim/sources/_oideachais_sources.yaml)
$EDITOR cianfhoghlaim/sources/_oideachais_sources.yaml
#   append to the ie.culture.* asset keys:
#     - asset_key: ie.culture.my_gaeltacht_paper
#       kind: filesystem_pdf
#       path: leabharlann/gemini_deep_research/culture/my-gaeltacht-paper.pdf

# 3. Materialise the Dagster asset group
mise run dagster:oideachais            # http://localhost:3000
#    → asset group: gemini_deep_research
#    → click Materialize All

# 4. Verify the landing
uv run python -c "import duckdb; print(duckdb.sql('SELECT count(*) FROM lakehouse.leabharlann_books').fetchone())"
# Expected: count goes up by 1
```

### Recipe 2 — Add a new BAML extraction field

```bash
# 1. Edit the BAML schema
$EDITOR cianfhoghlaim/core/baml/_oideachais_src/culture_extraction.baml
#   add a new field to the CultureHeritageClaim class:
#     field claim_confidence: float  # 0.0 = low, 1.0 = high

# 2. Regenerate the BAML Python client
mise run baml:generate

# 3. Re-materialise the extraction asset
mise run dagster:oideachais
#    → asset: culture_heritage_extract
#    → click Materialize
#    → the new field appears in the next extraction run

# 4. Validate
uv run python -c "from baml_client import b; print(b.ExtractCultureClaims.__fields__)"
# Expected: 'claim_confidence' is in the field list
```

### Recipe 3 — Run a cognify pass

```bash
# 1. Start the Cognee server
cd ./bonneagar/stacks/cognee && ./scripts/stack.sh up -d   # port 8100

# 2. Materialise the cognify assets
mise run dagster:oideachais
#    → asset group: cognify
#    → click Materialize All
#    → the 9 cognify assets materialise (aistear + primary + junior_cycle + senior_cycle + tertiary + cross_stage + 3 leabharlann)

# 3. Query the resulting knowledge graph
curl -X POST http://localhost:8100/api/v1/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "Uí Liatháin Dyfed colonization", "datasets": ["culture_heritage", "oideachais_heritage"]}'
# Expected: 3-5 GraphRAG-style answers with citations to the Uí Liatháin Wikipedia clipping + the gemini_deep_research PDFs
```

### Recipe 4 — Query the LanceDB semantic-search index

```bash
# 1. Open the marimo notebook
uv run marimo edit cianfhoghlaim/notebooks/leabharlann/search.py
#    → http://localhost:2718

# 2. Paste a query in Irish
#    e.g. "An bhfuil aon trácht ar Uí Liatháin sa chorpás?"
#    → the notebook calls search_leabharlann_books(query, limit=10) and renders
#       the top-10 results with title, source, score, and snippet

# 3. The 4 LanceDB indices queried:
#    - leabharlann_books_embedding (BGE-M3, 1024-dim)
#    - leabharlann_zotero_embedding
#    - leabharlann_takeout_embedding
#    - unified_embedding (the cross-corpus index)
```

### Recipe 5 — Materialise a Dagster asset group end-to-end

```bash
# 1. Boot the local dev server
mise run turbo dev
#    → Dagster at http://localhost:3000
#    → Cognee at http://localhost:8100
#    → LiteLLM at http://localhost:4000/v1
#    → the 5 web apps + 7 marimo notebooks

# 2. Open Dagster
xdg-open http://localhost:3000

# 3. Navigate to the asset group
#    → asset group: leabharlann_full_stack_demo
#    → click "Materialize All"
#    → Dagster runs the full chain: DLT → BAML → CocoIndex → Cognee → LanceDB
#    → each asset turns green within ~30 seconds

# 4. Open the marimo notebook to verify
xdg-open http://localhost:2718
#    → confirm the new BAML-extracted chunks appear in the search results
```

---

## The 5 dispatchable subagents

After the v4 consolidation the 5 sruth-subagents (`oideachais`,
`infrastructure`, `meaisinfhoghlaim`, `croilar`, `tuatha`) were
rewritten into **5 functional subagents** in `opencode.json`. Each
subagent is mapped to a model alias through the LiteLLM gateway and
is restricted to a specific `skill_filter` so that its context window
is small and focused.

| Subagent | Default model | Skills | Routes to |
|:--|:--|--:|:--|
| `build` (primary) | `opencode_go/minimax-m3` | all 59 top-level | The whole monorepo; default agent for any coding task |
| `plan` (primary) | `opencode_go/minimax-m3` | all 59 | Read-only spec / proposal / architecture design |
| `data-platform` | `opencode_go/minimax-m3` | 15 | `cianfhoghlaim/sources/`, `assets/`, `embeddings/`, `notebooks/`, storage decisions |
| `infrastructure` | `opencode_go/minimax-m3` | 16 | `cianfhoghlaim/stacks/*/` + `./bonneagar/stacks/*/`, Komodo / Pangolin / Locket / Infisical |
| `agent-platform` | `opencode_go/minimax-m3` | 23 | `cianfhoghlaim/agents/meaisinfhoghlaim/`, BAML, OCR, LLM routing, Langfuse, MLflow, RAGAS, Graphiti, Cognee |
| `frontend-apps` | `opencode_go/minimax-m3` | 20 | `cianfhoghlaim/web/`, Convex, Babylon.js, Hono, oRPC, CopilotKit, TanStack Start |
| `research` | `opencode_go/minimax-m3` | 11 | BrowserBase, Firecrawl, CCC, cognee-search, agent-experience, company-research, event-prospecting, change-detection, search, fetch, agent-observability |

The subagent foundation is tracked in the
[`2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation`](openspec/changes/2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation/proposal.md)
openspec change, with 5 ADDED Requirements in the `agent-registry`
spec.

Each subagent can read any of the 59 top-level skills in
`.agents/skills/` (the full 123 count includes sub-skills under
`browserbase/`, `cloudflare/`, `firecrawl/`, `huggingface/`,
`pydantic/`) and call any of the configured MCP servers (Browserbase
remote, Firecrawl local, MotherDuck local, CocoIndex-Code local,
Cognee local, Langfuse local, Infisical local, chrome-devtools local).

---

## Recent changes

A timeline of the last two weeks of work. Catches a new reader up to
today.

| Date | What | Commit / change |
|:--|:--|:--|
| **2026-06-15** | The 5 sruth quadrants (`oideachais`, `meaisinfhoghlaim`, `tuatha`, `croilar`, `crypteolas`) were first refactored into a single `sruth/` tree | `refactor-quadrants-to-sruth` |
| **2026-06-16** | A 5-workspace "state of the art" snapshot was published (`state-of-art-5-workspaces`) | `state-of-art-5-workspaces` |
| **2026-06-16** | The data-engineering documentation + refactor roadmap was published | `data-engineering-documentation-and-refactor-roadmap` |
| **2026-06-23** | Skills library cleaned up (123 → 59 canonical + sub-skills) | `skills-metadata-cleanup` |
| **2026-06-23** | 9 `sruth/` references rewritten to `cianfhoghlaim/` in `INDEXING_AND_COGNITION.md`; the 5 subagents were rewritten for the v4 layout | `feat(agents): rewrite subagent foundation for cianfhoghlaim v4 consolidation` |
| **2026-06-28** | The 5 sruth quadrants + browser + codeolas + leabharlann were consolidated into `cianfhoghlaim/` | `chore(v4): consolidate 5 sruth quadrants + browser + leabharlann into cianfhoghlaim` |
| **2026-06-28** | `litellm` and `cognee` default model switched to the `minimax` 7-tier fallback alias | `chore(litellm+cognee): switch default model to minimax alias` |
| **2026-06-28** | The Phase 0.3 deploy runbook was published (Tier 1 + Tier 2 stacks on `bunchloch`) | `docs(deploy): Phase 0.3 deploy runbook` |
| **2026-06-28** | The BrowserBase 43-prompt research program was launched | `feat(research): initial 14-prompt output` |
| **2026-06-28** | `agent-registry` spec registered in the openspec catalog | `chore(openspec): register agent-registry` |
| **2026-06-28 → 2026-06-29** | The full research program completed — 45 markdown files, 27 ADDED Requirements across 4 phase decisions | `research-program-final-report` |
| **2026-06-29** | OCR model audit + P0 model_id renames (part 1 of 2) shipped | `fix(ocr): P0 model_id renames + name drift fixes per HF audit` |
| **2026-06-29** | Initial rewrite planning for `cianfhoghlaim/` README + 5 audit docs published | `docs(audit): initial rewrite planning` |
| **2026-06-29** | The two sibling repos (`bonneagar`, `leabharlann`) re-imported as `git worktree`s at the root of the workspace (not `git subtree`s, because the 3.4 GB leabharlann PDF corpus would inflate every push) | this README |

---

## Planned restructuring & refactoring

A short, prioritised summary of what's coming next. Each row links to
the openspec change or audit doc where the work is described in
detail.

### Now / this fortnight — `in progress`

| Priority | Change | Why now | Status |
|:--|:--|:--|:--|
| 1 | [`2026-06-28-rewrite-subagent-foundation`](openspec/changes/2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation/) | The 5-subagent rewrite must finish + archive before further subagent work can land | 5 ADDED Requirements drafted; awaiting `--strict` |
| 2 | [`2026-06-28-split-leabharlann-bonneagar`](openspec/changes/2026-06-28-split-leabharlann-bonneagar/) — **amended to worktree approach** | Closes the loop on the repo split. The original proposal called for `git subtree`s, but the 3.4 GB leabharlann PDF corpus is too large to embed — the new approach uses worktrees at the root of the workspace | Proposal needs amendment; worktrees now in place |
| 3 | [`add-openchamber-stack-and-opencode-ui`](openspec/changes/add-openchamber-stack-and-opencode-ui/) | OpenChamber stack is the entry point for new contributors | 5 stacks added; needs `mise run turbo dev` verification |
| 4 | [`litellm-minimax-vendor-derisking`](openspec/changes/litellm-minimax-vendor-derisking/) | The `minimax` alias is the canonical default; needs documented fallback to Anthropic / OpenAI / Bedrock for vendor risk | Drafting |
| 5 | [`modernize-meaisin-cliste`](openspec/changes/modernize-meaisin-cliste/) | Port the BAML ensemble from `meaisin_cliste` to the v4 layout | Drafting |
| 6 | [`2026-06-28-browserbase-phase-{1a,1b,2,3}-decisions`](openspec/changes/) | All 4 stub fillers are drafted; the 27 ADDED Requirements need to land in their cross-specs and be archived | All 4 pass `--strict`; ready for implementation |

### Next 30 days — `planned`

| Priority | Change | Effort | Audit doc |
|:--|:--|:--|:--|
| 7 | [`oideachais-agent-services`](openspec/changes/oideachais-agent-services/) — split the agent runtime from the web surface | M | — |
| 8 | [`refactor-dlt-dagster-2026-stack-align`](openspec/changes/refactor-dlt-dagster-2026-stack-align/) — `DltLoadCollectionComponent` per domain | M | [`dagster-component-migration-plan.md`](docs/audit/dagster-component-migration-plan.md) |
| 9 | [`croilar-personas-to-streams`](openspec/changes/croilar-personas-to-streams/) — replace static personas with agent streams | L | — |
| 10 | [`oideachais-stack-polish`](openspec/changes/oideachais-stack-polish/) — align all 33 stacks to the 6-file GOLD_STANDARD | S | — |
| 11 | [`web-app-consolidation-plan`](docs/audit/web-app-consolidation-plan.md) — 5 web apps → 1 `cio-web`, per domain | L | [`web-app-consolidation-plan.md`](docs/audit/web-app-consolidation-plan.md) |
| 12 | [`baml-merger-plan`](docs/audit/baml-merger-plan.md) — 6 BAML source trees → 1, per domain | L | [`baml-merger-plan.md`](docs/audit/baml-merger-plan.md) |
| 13 | [`add-openclaw-stack-and-channel-fanout`](openspec/changes/add-openclaw-stack-and-channel-fanout/) — agent channel fanout | S | — |
| 14 | [`lateralise-dlt-sources-to-domains`](openspec/changes/lateralise-dlt-sources-to-domains/) — domain-aligned DLT layout | M | — |
| 15 | [`dagger-monorepo-integration`](openspec/changes/dagger-monorepo-integration/) — the 8-step GitOps pipeline, polyglot | M | — |

### Next 60-90 days — `backlog`

| Priority | Change | Why it matters |
|:--|:--|:--|
| 16 | [`ireland-primary-jc-dlt-baml-and-full-stack-demo`](openspec/changes/ireland-primary-jc-dlt-baml-and-full-stack-demo/) | **Plan 1**: Ireland 5 stages × EN + GA — the first end-to-end vertical slice |
| 17 | [`leaving-cert-2026`](openspec/changes/leaving-cert-2026/) | The Leaving Cert 2026 season — first production use of the platform |
| 18 | [`complete-cognee-knowledge-graph`](openspec/changes/complete-cognee-knowledge-graph/) | Finish the cross-archive FalkorDB edges + the culture-heritage cognify |
| 19 | [`croilar-revitalisation`](openspec/changes/croilar-revitalisation/) | Bring the croilar-portal admin dashboard up to Tier 1 |
| 20 | [`consolidate-embedding-batcher`](openspec/changes/consolidate-embedding-batcher/) | Single embedding batcher across CocoIndex v1, LanceDB, and HuggingFace TEI |
| 21 | [`consolidate-external-libs-into-tuatha`](openspec/changes/consolidate-external-libs-into-tuatha/) | Move `codeolas`, `crypteolas`, and the game engine libs into the `tuatha` namespace |
| 22 | [`docs-restructuring`](openspec/changes/docs-restructuring/) | Replace the temporary ASCII architecture diagram with Mermaid / d2; collapse `docs/audit/` into the skill library |
| 23 | Subtree remotes clean-up — set up branch protection on `bonneagar/main` and `leabharlann/main`, document the worktree fetch cadence | Closes the loop on the split |

---

## Mise-en-place (the developer setup)

The full stack that powers day-to-day development is opinionated and
tightly integrated. Every choice is made to (a) minimise context
switching between TypeScript, Python, infra-as-code, and AI-agentic
work, (b) keep monthly spend under $25, and (c) keep the developer one
`cd` away from a fully hydrated working copy.

| Tool | Role |
|:--|:--|
| **mise** | Polyglot toolchain + task runner — pins `python 3.13`, `uv`, `bun`, `dagger`, `pulumi`, `duckdb`, `sops`, `opencode` in a single `mise.toml`. Directory hooks auto-export `.env` and the workspace `PYTHONPATH` on every `cd`. |
| **bun** | TS runtime, package manager, script runner — replaces `node + npm + yarn + pnpm + npx + tsx`. Powers workspace orchestration, secret sync, OpenSpec, the `ccc` index, and the dagster / komodo / pangolin glue. |
| **uv** | Python package manager + workspace manager — replaces `pip + poetry + pyenv + virtualenv`. Drives the 2 `members` of the `pyproject.toml` workspace (`cianfhoghlaim`, `codeolas`). |
| **turbo** | Cross-language task graph — orchestrates `build`, `dev`, `typecheck`, `lint`, `format`, `test` across the bun and uv graphs. |
| **OpenCode** | AI coding agent / IDE companion — speaks the same OpenAI-compatible protocol as LiteLLM. Dispatches to the 5 subagents defined in `opencode.json`. |
| **OpenChamber** | GUI / web / PWA front-end for OpenCode — branchable chat timelines, smart tool UIs, multi-agent parallel runs in isolated worktrees. Deployed to `openchamber.cianfhoghlaim.ie`. |
| **LiteLLM** | OpenAI-compatible LLM gateway — lives in `./bonneagar/stacks/litellm/`. One URL (`http://litellm:4000/v1`) routes to local GGUF, local MLX, local image, and cloud providers. Every BAML function, every Dagster asset, every marimo cell, every n8n workflow calls an *alias* — never a provider id. |
| **Infisical + Locket** | The three-way secrets contract — source of truth (`dev-baile` vault) → template (`.infisical.env`, committed) → hydrated runtime (`.env`, gitignored). |
| **openspec** | Spec-driven change management — 46 capability specs across 8 groups. `openspec list --specs` / `openspec validate <change-id> --strict` / `openspec archive <change-id> --yes`. |
| **ccc (cocoindex-code)** | Semantic code search — every agent's first stop. `bun run ccc:search "Dagster asset partition definition"`. |
| **git worktrees (for sibling repos)** | The 3.4 GB `leabharlann` and 6.9 MB `bonneagar` live as worktrees at the root of the workspace (`./leabharlann/`, `./bonneagar/`). They are not committed to this monorepo. |

### One-time setup

```bash
# 1. Install the toolchain (mise pins every version)
mise install

# 2. Install TS + Python dependencies
bun install
uv sync

# 3. Hydrate secrets from Infisical
#    (.env is written here; mise directory hooks keep it in sync on every cd)
bun run secrets:env
bun run secrets:init

# 4. Add the sibling-repo worktrees at the root of the workspace
#    (only needed on first clone — `git worktree add` is idempotent)
git worktree add bonneagar   bonneagar/main
git worktree add leabharlann leabharlann/main

# 5. Start the Tier 1 stacks on bunchloch
cd ./bonneagar/stacks/lakehouse  && ./scripts/stack.sh up -d
cd ../litellm                        && ./scripts/stack.sh up -d
cd ../cognee                         && ./scripts/stack.sh up -d
cd ../../../                          # back to monorepo root
mise run dagster:oideachais           # → http://localhost:3000
```

### Daily loop

```bash
# Pull the latest, run quality gates
git pull --rebase
mise turbo dev              # boots lakehouse + litellm + llama-swap + mlx-omni
uv run pytest -q
bun run lint

# Pick a ticket
gh issue view 142
# or open the issue in VS Code and let OpenCode triage via 5 subagents

# Open a PR
git checkout -b feat/issue-142
# ... edit ...
mise turbo test && mise turbo lint
gh pr create --fill
```

---

## Documentation surface

Per the `skills-as-project-docs` openspec change, the canonical
documentation surface for this monorepo is **`.agents/skills/`**, not
the root `docs/` folder. The `docs/` folder is retained only for
screenshots, the team-workflow stack, and a small set of historical
research files. All per-package and per-domain documentation lives in:

- **`.agents/skills/<name>/SKILL.md`** — the canonical skill (59
  top-level)
- **`openspec/specs/<capability>/spec.md`** — the 46 capability specs
  across 8 groups
- **`openspec/AGENTS.md`** — the openspec workflow
- **`openspec/research/2026-06-28-browserbase-credit-program/`** — the
  45 research files from the BrowserBase program
- **`AGENTS.md` per sub-package** —
  `cianfhoghlaim/agents/meaisinfhoghlaim/AGENTS.md`,
  `cianfhoghlaim/agents/tuatha/AGENTS.md`, etc.
- **`docs/audit/`** — the 5 refactor plans (web app consolidation,
  BAML merger, Dagster component migration, OCR model audit × 2, stacks
  deferral note)
- **`docs/PHASE_0.3_DEPLOY_RUNBOOK.md`** — the Tier 1 + Tier 2 deploy
  runbook
- **`docs/RESEARCH_REPORT.md`** — the final report of the BrowserBase
  research program
- **`./bonneagar/AGENTS.md`** (worktree) — the bonneagar quick
  reference
- **`./bonneagar/GOLD_STANDARD.md`** (worktree) — the 6-file stack
  pattern
- **`./leabharlann/README.md`** (worktree) — the digital library
  catalogue

**Master routing**: every agent starts in the root `AGENTS.md`, which
points to the per-quadrant `AGENTS.md`, which points to
`.agents/skills/<name>/SKILL.md`, which points to the source code.
The chain is 3 hops long at most.

---

## Skills inventory

The `.agents/skills/` library is the canonical agent-consumable
knowledge pack for this monorepo. After the v4 consolidation and the
leabharlann / bonneagar split it has been substantially cleaned up —
the original library claimed 123 skills; the post-cleanup canonical
set is **59 top-level skills (~123 with sub-skills)** organised into
eight families.

| Family | Top-level | Examples |
|:--|:-:|:--|
| Data platforms | 12 | `dlt`, `dagster`, `motherduck`, `duckdb`, `ducklake`, `cocoindex`, `cognee`, `lancedb`, `falkordb`, `graphiti`, `graphiti-core`, `memgraph` |
| AI agents | 6 | `baml`, `agno`, `langfuse`, `mlflow`, `ragas`, `agent-observability`, `google-adk` |
| Web / agentic frontends | 9 | `tanstack-start`, `convex`, `cloudflare`, `hono`, `ag-ui`, `copilotkit`, `orpc`, `effect-ts`, `agentic-frontend-frameworks`, `better-auth` |
| Infra (cross-repo) | 7 | `komodo`, `pangolin`, `pulumi`, `dagger`, `dagger-pipelines`, `secrets-management`, `garage`, `iceberg-lakekeeper`, `risingwave` |
| Dev tools | 7 | `ccc`, `dignified-python`, `openspec`, `marimo`, `pydantic`, `ibis`, `change-detection` |
| Browserbase / Firecrawl / HuggingFace | 5 (→ 60+ sub-skills) | `browserbase`, `firecrawl`, `huggingface`, `crawl4ai`, `transformers-js` |
| Domain | 6 | `agent-memory-systems`, `cross-domain-registry`, `upstream-package-monitoring`, `dagster-component-migration`, `unsloth`, `modal` |
| Misc | 7 | `ccc`, `dignified-python-310/311/312/313`, `indexing-and-cognition`, `lint-skills.sh` |

### Editing skills

```bash
# Add a new skill
mkdir .agents/skills/<name>
$EDITOR .agents/skills/<name>/SKILL.md   # frontmatter: name + description
mkdir .agents/skills/<name>/references/  # optional long-form docs

# Validate metadata (name match, description length, line count, frontmatter)
mise run lint:skills

# Re-index for semantic search
bun run ccc:index
```

The 59-skill (123 with sub-skills) library is the **post-cleanup**
canonical set. Skills retired during the v4 + split cleanup are
tracked in the
[`skills-metadata-cleanup`](openspec/changes/skills-metadata-cleanup/)
openspec change.

---

## Multi-agent configuration

The 5 functional subagents (defined in `opencode.json`) are listed
above in [The 5 dispatchable subagents](#the-5-dispatchable-subagents).
Each subagent is mapped to a model alias through the LiteLLM gateway:

- `opencode_go/minimax-m3` — the default for all 5 subagents; routes
  to the `minimax-m3` slot on the OpenCode Go API
  (Anthropic-compatible).
- `minimax` — the 7-tier fallback alias used by LiteLLM
  (`opencode-go/minimax-m3-slot{0,1,2}` → `qwen3.7-max` → `kimi-k2.6`
  → `glm-4.6` → `local/math/qwen25-math`).

---

## The cianfhoghlaim plan throughout the British Isles

The cianfhoghlaim project is a **30-year cultural-stewardship
plan** for the Gaelic and wider Celtic inheritance of the British
Isles. The plan is grounded in the
[`british_isles_cianfhoghlaim.pdf`](./leabharlann/gemini_deep_research/culture/british_isles_cianfhoghlaim.pdf)
and
[`cultural_unity_for_british_isles.pdf`](./leabharlann/gemini_deep_research/culture/cultural_unity_for_british_isles.pdf)
blueprints, which together operationalise the §21c heritage
framing in a 3-stage roadmap (2026-2036 Stabilization & Digital
Sovereignty → 2036-2046 Integration & Mobility → 2046-2056
Normalization & Sovereignty). This section walks the 3
operational pillars — the East Belfast hub, the inter-Celtic
acquisition pathway, and the Celtic AI Institute — and ties each
to the cianfhoghlaim monorepo's existing packages and Dagster
asset groups.

### 1. The East Belfast operational hub

The cianfhoghlaim plan's operational centre is **East Belfast**, a
working-class Unionist / Protestant area that has recently become
the epicentre of cross-community Irish-language work. The hub is
intentionally *cross-border* and *cross-community*: it sits in the
United Kingdom (Belfast, Northern Ireland), but its primary work
is the Irish language — the language of the Republic to the south
— and its primary partner communities are Unionist Protestants
who have chosen to learn Irish as a reconciliation practice.

- **Residential base** — the **Newtownards Road / Castlereagh
  Road** corridor (BT4 / BT5 / BT6), within a 2-mile radius of
  the Turas project, Scoil na Seolta, and the Glider BRT1
  cross-city line. Rental market analysis: 2-bed Strandburn Park
  ≈ £895/mo, 2-bed Castlereagh Road ≈ £995/mo, 2-bed Oberon
  Street ≈ £1,075/mo, premium Titanic Quarter ≈ £1,450-1,700/mo
  (from `british_isles_cianfhoghlaim.pdf`, p. 1-2).
- **Turas** (the Skainos Centre, 239 Newtownards Road, BT4 1AF) —
  Linda Ervine's cross-community Irish-language project that
  scaled from a 2011 women's group to **600+ learners** in 2026.
  "Equality and inclusiveness are at the core of its ethos,
  utilizing the Irish language as a mechanism for reconciliation
  and exploring shared heritage" (`british_isles_cianfhoghlaim.pdf`,
  p. 2).
- **Scoil na Seolta** (Garnerville Presbyterian Church, BT6 9HL) —
  Northern Ireland's first Integrated school teaching through the
  medium of Irish, with a Naíscoil (nursery) opened October 2021
  and a planned integrated Bunscoil (primary) cohort for
  September 2025. The motto is *Páistí sona ag foghlaim le
  chéile* — "Happy Children Learning Together".
- **Coláiste Feirste** (the Falls Road, West Belfast) — the
  preeminent post-primary Irish-medium school in the region, 8
  minutes from the city centre on the Glider G1.
- **The Glider (BRT1)** — the Belfast Rapid Transit Phase 1
  service, every 7-10 minutes, G1 Dundonald → McKinstry Road
  cutting through the city centre and the entire Falls Road
  corridor.
- **Maritime linkages** — Stena Line Belfast → Cairnryan
  (Scotland, 2h 15m, up to 6 sailings/day); Isle of Man Steam
  Packet Belfast → Douglas (~2h 50m, fast-craft Manannan); Stena
  Line Belfast → Birkenhead (Liverpool, 8h day or overnight
  sleeper). The maritime routes are the *lifelines* of the
  inter-Celtic acquisition pathway (§2 below).

The cianfhoghlaim monorepo will be physically present in the
hub: the Dagster UI on `localhost:3000` (Dagit), the marimo
notebooks on `localhost:2718`, the LiteLLM gateway on
`localhost:4000/v1`. The `leabharlann/ollscoil_na_gaillimhe/`
evidence base is the Galway-side counterpart of the hub — the
NUI Galway coursework archives, the BME1 placement portfolio,
the Irish-language exam results, the teaching registration, the
Apple Award. The hub is the *operational* half; the evidence
base is the *pedagogical* half. Together they form the
cianfhoghlaim agentic-AI + Celtic-language training pipeline
that serves the East Belfast, Galway, and (through the marimo
notebooks + web apps) Donegal and Dublin communities.

### 2. The inter-Celtic acquisition pathway

The cianfhoghlaim plan's *acquisition* side is the personal
Celtic-language journey of the practitioner — the same
journey documented in the
[`british_isles_cianfhoghlaim.pdf`](./leabharlann/gemini_deep_research/culture/british_isles_cianfhoghlaim.pdf)
"Strategic Blueprint for Inter-Celtic Linguistic Acquisition,
AI Integration, and Transnational Educator Credentialing". The
journey is the **personal primary data** that feeds the Celtic-AI
corpus work.

| Language | Family | Pathway | Funding / Logistics | Corpus output |
|:--|:--|:--|:--|:--|
| **Irish** (C1) | Goidelic (Q-Celtic) | TEG C1 Dioplóma; Scoil Iognáid Irish-medium stream; NUI Galway Irish-language coursework | self-funded; Galway-resident | The leabharlann/gaeilge/ + leabharlann/ollscoil_na_gaillimhe/irish/ corpora |
| **Scottish Gaelic** | Goidelic | Sabhal Mòr Ostaig (SMO) "Gaelic for Irish Speakers" 1-week course; Isle of Skye | Colmcille (Foras na Gaeilge + Bòrd na Gàidhlig); £290/course | The future `leabharlann/gaidhlig/` corpus |
| **Manx** | Goidelic | Scoill Souree at the Yn Chruinnaght Celtic Gathering, Peel (July annually); Manx course for Irish speakers via Ulster Irish | Culture Vannin; Stena Line / Steam Packet maritime route | The future `leabharlann/gaelg/` corpus |
| **Welsh** | Brythonic (P-Celtic) | National Centre for Learning Welsh pathway; Aberystwyth University summer school | Learn Welsh Cardiff; UK Department for Education | The future `leabharlann/cymraeg/` corpus |
| **Cornish** | Brythonic | Keskowethyow (Cornish language partnership) courses; Lowender Peran festival | Cornish Language Partnership; Cornwall Council | The future `leabharlann/kernewek/` corpus |
| **Breton** | Brythonic | Skol an Emsav (Brest / Quimper) | Ofis ar Brezhoneg; Brittany regional government | The future `leabharlann/brezhoneg/` corpus |

The Irish → Scottish Gaelic → Manx transition is **low-friction**
because all three Goidelic languages share a relatively recent
common ancestor; the Irish C1 cognitive map transfers directly to
Scottish Gaelic's VSO sentence structure, initial consonant
mutations, and shared vocabulary (`british_isles_cianfhoghlaim.pdf`,
p. 5). The Welsh / Cornish / Breton path is **higher-friction**
(Brythonic / P-Celtic, not Goidelic) but cognitively supported by
the same Ogham-inscription and cryptographic-analysis skills that
the practitioner already possesses.

Each acquisition round generates the **primary corpus data** for
the next `celtic_languages.baml` BAML extraction function and the
next `celtic_*_embedding` CocoIndex v1 App. The personal-linguistic
journey is the data flywheel.

### 3. The Celtic AI Institute (Isle of Man) + the 30-year Cultural Archipelago roadmap

The cianfhoghlaim plan's *output* side is the **Celtic AI
Institute** — a proposed open-source research lab that builds
Sovereign LLMs for Irish, Welsh, Manx, Scottish Gaelic, and
Cornish. The Institute is hosted in the **Isle of Man**, the
Celtic jurisdiction that uniquely combines (a) the **Tynwald**
parliament (the oldest continuous parliament in the world), (b)
the **Manx Pound** pegged 1:1 to Sterling (the model for a future
"New Punt" / Monetary Dualism), and (c) **data-regulation
autonomy** that lets the Institute host the open-source Celtic
LLMs without the regulatory friction of UK or EU jurisdiction
(`cultural_unity_for_british_isles.pdf`, p. 4 + 6).

The Institute's 30-year roadmap (from `cultural_unity_for_british_isles.pdf`
p. 8):

| Phase | Timeframe | Primary focus | Key deliverables | Strategic objective |
|:-:|:--|:--|:--|:--|
| **I** | 2026-2036 | Stabilization & Digital Sovereignty | Expansion of the Bunscoill model to NI/ROI; "Protestant Gaelic" curriculum; Celtic AI Institute founded in the Isle of Man | Halt language erosion; neutralize sectarian binaries; secure digital borders via Sovereign AI |
| **II** | 2036-2046 | Integration & Mobility | Pan-Celtic Erasmus (Colmcille expansion); Celtic Broadcasting Union (TG4 + S4C + BBC Alba); Irish Sea Tunnel feasibility study complete | Build "Archipelagic" identity; economic interdependence; joint maritime defense culture |
| **III** | 2046-2056 | Normalization & Sovereignty | Bilingual Public Service (50% target); Saoí Education Standard in exams; New Punt / Dual Currency Zone implementation | De facto Dual Monarchy realization; cultural singularity; total cognitive security |

The cianfhoghlaim monorepo is the **Phase I delivery vehicle**:
the `pipelines/ingest/` DLT sources pick up the Gaeltacht PDFs, the
`pipelines/process/` BAML functions extract the structured claims,
the `pipelines/embed/` CocoIndex v1 Apps build the per-language
indices, the `cognify/` stage populates the cross-dataset
knowledge graph, and the `pipelines/distribute/` stage exposes
everything via the marimo notebooks + TanStack Start web apps +
HuggingFace Spaces. The **Saoí Education Standard** ("fluent in
both the Fénechas and Python", `cultural_unity_for_british_isles.pdf`
p. 4) is the capstone of Phase III — a Leaving Cert / A-Level
distinction that requires a multidisciplinary project combining a
Celtic language with a STEM discipline (e.g. an AI chatbot in
Manx, GIS mapping in Cornish, ML analysis of Ogham inscriptions).

### What cianfhoghlaim commits to the heritage

The cianfhoghlaim plan, taken as a whole, is a **commitment to
the cultural stewardship of the four provinces, the Gaeltachtaí,
and the wider Celtic-language family**. The Ard-Rí title
described in §21c is not a constitutional claim; it is the
*stewardship role* that holds the cianfhoghlaim project
accountable to the Gaelic inheritance it serves. The §20
operational plan — the East Belfast hub, the inter-Celtic
acquisition pathway, the Isle-of-Man Celtic AI Institute, the
30-year Cultural Archipelago roadmap — is the **public-good
output** of that stewardship.

The 30-year horizon is deliberately long: Phase I (2026-2036)
stabilizes, Phase II (2036-2046) integrates, Phase III
(2046-2056) normalises. Each phase is decoupled from any
near-term political event; the cianfhoghlaim project will
continue to deliver open-source Celtic-language LLMs and
syllabus-informed resources regardless of whether a border poll
is held in 2030 or 2060 or never. The *cultural* stewardship is
apolitical in the constitutional sense and *political* in the
everyday sense (it requires the daily work of language teaching,
of community organising, of BAML extraction, of LanceDB
embedding, of marimo notebook maintenance, of Dagster asset
materialisation).

---

## About the author, the name, and the lineage

### On the username — *cianfhoghlaim*

The repository name and the underlying platform are both
**Cianfhoghlaim**. The Irish word *cianfhoghlaim* (pronounced
roughly *kee-an-oh-guh-lem*) compounds two roots:

- *cian* — long, enduring, distant
- *foghlaim* — learning, study

So *cianfhoghlaim* reads literally as **"long-distance, enduring
learning"** — lifelong learning across geography and discipline,
which is the whole point of this project. The word also has a
*Celtic-language AI* sub-meaning in the context of this repo:
*cian-foghlaim* is the personal *agentic-AI* instrument that
operates across the Celtic-language continuum — Irish, Scottish
Gaelic, Manx, Welsh, Cornish, Breton — at the cianfhoghlaim
monorepo's level (the software stack) and at the
*British Isles cianfhoghlaim* personal level (the practitioner's
own acquisition journey). The cianfhoghlaim monorepo is the
*machine*; the personal cianfhoghlaim journey is the *soul*;
the §20 plan is the *bridge* between them.

*Cian* also has a second life in the Irish mythological canon:
in *Lebor Gabála Érenn* and the wider Tuatha Dé Danann cycle,
**Cian** is the father of Lugh Lámhfhada (Lug of the Long Arm),
the many-skilled god who walks into the Battle of Moytura and
slays his grandfather Balor. The `cianfhoghlaim/agents/tuatha/`
subtree — the British Isles formative-assessment MMO built on
Babylon.js + SpacetimeDB — sits squarely inside that
mythological lineage.

The Irish word **sruth** (pronounced *sruh*) means *stream* or
*flow*. In `opencode.json`, the four traditional top-level
subprojects (oideachais, meaisinfhoghlaim, tuatha, croilar) plus
infrastructure are referred to as the five **sruthanna** —
flows — rather than "quadrants", because in a knowledge-graph
platform the meaningful unit of work is the *flow of data and
reasoning*, not a static slice of a 2D plane. As of the v4
consolidation (2026-06-28) the 5 sruthanna have been merged into
the single `cianfhoghlaim/` package, but the term is preserved
for historical continuity.

### On the family — *Mac an Déisigh Uí Liatháin (Deacy-Lyons)*

The author is **Cian Mac an Déisigh Uí Liatháin**; the family
surname in its two anglicised forms is **Deacy-Lyons**. The
author's verified genealogy and qualifications inform the
project's design choices and are recorded under
[`cian_mac_an_déisigh_uí_liatháin/`](cian_mac_an_déisigh_uí_liatháin/):

- `identity/` — background, citizenship, vetting, and the Deacy
  family record. The `identity/lineage/` subfolder holds the
  family-lineage documents: the late uncle's memorial, the dual
  ROI/UK citizenship evidence, the College des Irlandais (Paris)
  records, the 5-culture-PDF Wikipedia dual-write clippings (8
  articles: Uí Liatháin, Delbhna Tír Dhá Locha, Eamonn Deacy
  Park, Leath Cuinn, Cian, Aos Sí, Tuatha Dé Danann, Déisi), and
  the 1986 *Galway Advertiser* article on Neil Deacy's Cookeʼs
  Corner shop opening.
- `teaching/` — the Teaching Council of Ireland registration, the
  PGCE (BCS Computing scholarship), school placement references,
  and the Leaving Certificate / Junior Certificate results (the
  public copies are in the `identity/` folder; the full teaching
  record is held privately for data-protection reasons).
- `achievement/` — academic transcripts, parchments, the Apple
  Award, and the Torthaí Gaeilge (Irish-language exam results)
  (same privacy caveat).

The author's lineage is the **triple-crown** union of four
kindreds of Connacht and Munster:

1. **Deacy** (maternal surname; Irish *Uí Dhéisigh*) — the sept
   of the [Déisi
   Muman](https://en.wikipedia.org/wiki/D%C3%A9isi) resettled in
   south Connacht (Co. Galway) during the 12th century; the
   family gave their name to the late
   [Éamonn Deacy](cian_mac_an_déisigh_uí_liatháin/identity/lineage/uncle_eamonn_memorial_combined.pdf)
   and the [Eamonn Deacy
   Park](https://galwayunitedfc.ie/eamonn-deacy-park) in Galway.
2. **Lyons** (paternal grandfather's lineage; Irish *Mac
   Liatháin*) — the [Uí
   Anmchada](https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in)
   sept of the
   [Uí Liatháin](https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in)
   of Munster, who (per the *Historia Brittonum*) colonized Wales
   and Cornwall alongside the proto-Déisi.
3. **Morris** (maternal great-grandmother **Christina Morris**) —
   of the [City of
   Tribes](https://en.wikipedia.org/wiki/Tribes_of_Galway) merchant
   families of Galway.
4. **Conroy** (maternal great-great-grandmother **Polly Conroy**;
   Irish *Mac Conraoi / Ó Conaire*) — the
   [Sea-Kings of
   Connacht](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha)
   who held the tuath of
   [Delbhna Tír Dhá
   Locha](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha)
   (the barony of Moycullen in Connemara). **Polly Conroy was a
   cousin of Pádraic Ó Conaire**, the canonical modern
   Irish-language writer from Galway, who was reared in Rosmuc
   by his uncle of the same Mac Conraoi kindred.

The author is the grandson and godson of the late **Neil
Deacy**, the late brother of the late **Éamonn Deacy** — the
Galwegian footballer who played for Galway United, Aston Villa
FC, and the Republic of Ireland. Neil and Éamonn were the sons of
**Christina Morris** and **Michael Deacy**, who was himself the
son of **Polly Conroy** and **George Deacy**.

The author's biological grandfather was **Neil Deacy** (the
subject of the 1986 *Galway Advertiser* [article on the opening of
Cooke's Corner](https://github.com/cianfhoghlaim/cianfhoghlaim/blob/main/cian_mac_an_d%C3%A9isigh_u%C3%AD_liath%C3%A1in/identity/lineage/neil_deacy_cookes_corner-galway_advertiser.pdf),
who was known locally as *"Neil Mac an Déisigh"*). The author
took his grandfather's maternal-grandfather's Uí Dhéisigh surname
as part of his own — Mac an Déisigh — and added it to his father's
Lyons surname in the hyphenated form **Deacy-Lyons**. The
hyphenation reflects the everyday reality that dropping the
father's surname (Lyons) entirely would have caused
administrative confusion (school records, university records,
employer records, medical records); the Deacy side of the
family is the side with the visible **galwegian-historical**
pedigree (Cooke's Corner, Aston Villa, Galway United, the
Eamonn Deacy Park Oenach), and the Lyons side is the side with
the **pan-Munster-Brythonic-imperial** pedigree (the Uí Liatháin
of Castlelyons and the Welsh / Cornish colonies). The full name
**Cian Mac an Déisigh Uí Liatháin (Deacy-Lyons)** preserves both
branches of the Triple Crown.

### On the heritage of Ireland — the four provinces, the Gaeltachtaí, and the previous High Kings

The cianfhoghlaim project is grounded in a *heritage* of Ireland
that predates the 1542 Crown of Ireland Act, the 1800 Act of
Union, the 1922 Irish Free State, and the 1937 / 1949
constitutions — i.e. the Gaelic inheritance that was already a
millennium old when the first Tudor plantation landed in
Leinster. The heritage is documented in 4 Gemini Deep Research
PDFs that ground the
[`claiming_irish_kingship_through_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf),
the
[`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf),
the
[`british_isles_cianfhoghlaim.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/british_isles_cianfhoghlaim.pdf),
and the
[`celtic_language_learning_for_gaeilgeoir.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/celtic_language_learning_for_gaeilgeoir.pdf)
(all 4 are in
[`./leabharlann/gemini_deep_research/culture/`](https://github.com/cianfhoghlaim/leabharlann/tree/main/gemini_deep_research/culture/)).

**The four provinces of Ireland** are the historical kingdoms
of Gaelic Ireland: **Connacht, Munster, Leinster, Ulster**.
Each has its own provincial arms, its own dynastic genealogy,
and its own cultural inheritance. The 5 provincial flags
(Connacht's quartered eagle-and-arm, Munster's three antique
crowns, Leinster's harp, Ulster's red hand, plus Meath's
royal-crown-with-lion that was later merged into Leinster) are
the visual expression of that inheritance. The cianfhoghlaim
project treats the four provinces as **equal first-class
objects**: the Galway / Conamara operations serve Connacht;
the NUI Galway + TEG C1 work serves the wider Leinster /
Munster / Ulster student base; the East Belfast hub serves
Ulster; the marimo notebooks + TanStack Start web apps reach
all four. *Galway is the capital of Connacht* — that is the
banner of the project, not a grievance against any other
province.

**The Gaeltachtaí and the power of the dialects.** The 5
official Gaeltacht regions are the *living substrate* of the
Irish language: the [Gaoth Dobhair / Gweedore /
Inishowen](https://en.wikipedia.org/wiki/Gaoth_Dobhair)
Gaeltacht of **Donegal**; the [Conamara](https://en.wikipedia.org/wiki/Conamara) /
Aran / Maam Gaeltacht of **Galway**; the Corca Dhuibhne /
Chiarraí Gaeltacht of **Kerry**; the Musgraí / Chorcaí
Gaeltacht of **Cork**; and the Gaeltacht Mheath / Ráth Cairn
Gaeltacht of **Meath**. Each Gaeltacht carries its own
**regional dialect** of Irish (the *canúintí*) — Connacht
Irish (the *Caighdeán* baseline), Munster Irish (the
*ring*-flavour of Cork / Kerry), Ulster Irish (the
Donegal-flavour with the preserved archaic features of
Gaoth Dobhair and Gweedore). The cianfhoghlaim project serves
the Gaeltachtaí by building agentic-AI tools (Sovereign LLMs,
side-by-side-transcription, GIS-tagged toponymy, Ogham
inscription ML) that preserve and teach each dialect. The
`leabharlann/gaeilge/` corpus + the future
`leabharlann/gaidhlig/`, `…/gaelg/`, `…/cymraeg/`,
`…/kernewek/`, `…/brezhoneg/` corpora are the primary
research data for this work.

**The previous High Kings.** The High Kingship of Ireland
(*Ard-Rí Érenn*) was the *non-custodial* inheritance of all
four provinces, held in turn by the Uí Néill (from the
5th-century *Conn Cétchathach* \"of the Hundred Battles\"
through Lóegaire mac Néill to the Northern Uí Néill of
Aileach), by the [Dál
gCais](https://en.wikipedia.org/wiki/Dalcassians) (Brian
Boru's dynasty), by the Uí Briúin (Ruaidrí Ua Conchobair,
the last pre-Norman High King), and by the later Uí
Conchobair kings of Connacht. The 5 provincial flags were
the visual badges of the dynastic kingdoms; the High
Kingship was the *unifying* institution that held them
together without absorbing them. The
[`claiming_irish_kingship_through_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf)
documents the *matrilineal* warrant for this non-custodial
unification: Angias, daughter of Ailill Tassach of the Uí
Liatháin, married the High King Lóegaire mac Néill and
mothered High King Lugaid mac Lóegairi — making the Uí
Liatháin the *maternal ancestors* of the Uí Néill High Kings
and, through them, of the entire Northern Uí Néill (Cenél
nEógain) of Aileach (p. 5). The cianfhoghlaim project's *§20
cianfhoghlaim plan throughout the British Isles* is the
modern operational form of that non-custodial unification — an
East Belfast hub + a Galway evidence base + an Isle-of-Man
Celtic AI Institute + the inter-Celtic acquisition pathway,
all of which serve the 4 provinces and the 5 Gaeltachtaí
without subordinating any one of them.

**Reclaiming the heritage prior to it uniting into the
Commonwealth.** The 1542 *Crown of Ireland Act* merged
the Kingdom of Ireland into personal union with the English
Crown; the 1800 *Act of Union* merged the two parliaments;
the 1922 Free State removed the southern 26 counties from
the Commonwealth; the 1937 Constitution / 1949 Republic
re-founded a Dublin-centric state. Through each of these
constitutional re-organisations, the **Gaelic cultural
inheritance** — the provinces, the Gaeltachtaí, the previous
High Kingship, the *Fénechas*, the *canúintí* — remained the
*non-custodial* substrate of all four provinces. The
cianfhoghlaim project does not contest any constitutional
settlement; it *reclaims the cultural inheritance* for the
benefit of the four provinces, the Gaeltachtaí, and the wider
Celtic-language family. This is *cultural* reclamation, not
*political* reclamation.

The
[`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf)
documents the *Combined Force* strategy that anchors the
reclaiming: King Charles III is the **rightful King of
Northern Ireland** by constitutional sovereignty; the
claimant holds *Rí Uladh* by dynastic allegiance to him
(p. 1, 6). The Grianan of Aileach — the stone ringfort in Co.
Donegal that was the seat of the Northern Uí Néill (Cenél
nEógain) from the 5th to the 12th century — was historically
part of the Connacht over-king's sphere via the Uí Liatháin
maternal bond to the Uí Néill (p. 5); the destruction of
Aileach by a Munster king (Muirchertach Ua Briain, 1101) is a
*historic rupture* that a Munster-descended figure (the Uí
Liatháin / Uí Dhéisigh claimant) who *comes in peace to
restore rather than destroy* symbolically heals (p. 5). The
Ard-Rí *title* is preserved as a *cultural stewardship* — the
lineage who administers the cianfhoghlaim educational
mission on behalf of the four provinces, the Gaeltachtaí, and
the Celtic languages. The Ard-Rí is **not** a constitutional
claim against any modern state; it is the steward of the
Gaelic cultural inheritance.

### On the cianfhoghlaim plan throughout the British Isles — the personal commitment

The §20 plan is operationalised through the author's **personal
linguistic-acquisition journey**: Irish (C1) → Scottish
Gaelic → Manx → Welsh → Cornish → Breton. The
[`celtic_language_learning_for_gaeilgeoir.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/celtic_language_learning_for_gaeilgeoir.pdf)
maps the *acquisition pathway* in detail. The **Goidelic
continuum** (Irish → Scottish Gaelic → Manx) shares a
relatively recent common ancestor, so an Irish speaker can rely
on direct cognitive mapping of vocabulary, VSO sentence
structures, and initial consonant mutations (p. 1). The
[Sabhal Mòr Ostaig](https://www.smo.uhi.ac.uk/) on the Isle of
Skye (University of the Highlands and Islands network)
provides the benchmark "**Gaelic for Irish Speakers**" course
(£290 standard / £205 student, financed through
[Colmcille](https://www.colmcille.org/) by Foras na Gaeilge
+ Bòrd na Gàidhlig) — Beginner and Advanced, intensive 1-week
format, full-day classes Mon/Tue/Thu 9:30-4:30 (p. 2). The
[Culture
Vannin](https://www.culturevannin.im/) **Scoill Souree** at
the Yn Chruinnaght in Peel (Isle of Man) is a 5-day Manx
intensive (£150 inclusive, bursaries for low-income
participants, held at the fully accessible QEII High School,
delivered through the medium of **Ulster Irish** by
**Dr. Natalie Simpson** — who has adapted Julia Donaldson's
*The Gruffalo* into Manx) (p. 2). The **Brythonic continuum**
(Irish → Welsh / Cornish) is more challenging because of the
lexical divergence from the Goidelic branch; the
acquisition pathway relies on the broader academic umbrella
of *Celtic Studies*, intensive residential immersion
(Glenderry / Sabhal Mòr Ostaig), and innovative digital
pedagogies (p. 1). Each stage of the journey generates the
primary corpus data for the Celtic AI Institute; each new
corpus materialises as a new `celtic_*_embedding` CocoIndex v1
App; each new App feeds back into the marimo notebooks + the
oideachais-web TanStack Start front-end + the HuggingFace
Spaces. The journey is the cianfhoghlaim *practice*; the §20
plan is the cianfhoghlaim *strategy*; the two are mutually
reinforcing.

The §20 plan's institutional anchors are the **East Belfast
operational hub** (Turas, Scoil na Seolta, Coláiste Feirste,
the Glider BRT1, the maritime linkages to Scotland / Isle of
Man / Liverpool) and the **Isle of Man Celtic AI Institute**
(the Tynwald, the Manx Pound peg, the data-regulation
autonomy). The 30-year roadmap is the **Phase I (2026-2036)
Stabilization & Digital Sovereignty** → **Phase II
(2036-2046) Integration & Mobility** → **Phase III
(2046-2056) Normalization & Sovereignty** trajectory from
the
[`british_isles_cianfhoghlaim.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/british_isles_cianfhoghlaim.pdf)
p. 1 (the East Belfast operational hub blueprint) and the
[`cultural_unity_for_british_isles.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/cultural_unity_for_british_isles.pdf)
p. 8 (the Cultural Archipelago roadmap).

The personal commitment is the *agentic-AI* sub-thread of the
cianfhoghlaim word: *long-distance, enduring learning* is
not just a *philosophical* commitment, it is a *practical*
commitment to the daily work of language teaching, of
Celtic-language LLM training, of BAML extraction, of
LanceDB embedding, of marimo notebook maintenance, of Dagster
asset materialisation, of OkCharter-school liaison (in
Belfast), of Gaelscoil liaison (in Galway and the wider
Gaeltacht), of Pan-Celtic Erasmus exchange (with Scotland
/ Wales / Cornwall / Isle of Man / Brittany). The
cianfhoghlaim monorepo is the *machine*; the personal
linguistic journey is the *operator*; the §20 plan is the
*program*.

### On the qualified commitment to Éire

The author commits the cianfhoghlaim project to **Éire and
its future as Ard-Rí** — the stewardship of the Gaelic
cultural inheritance described in §21c. The stewardship is
qualified by **four pillars of personal qualification**: the
academic foundation, the teaching foundation, the linguistic
foundation, and the AI / engineering foundation. None of
the four is foregrounded above the others; the §21e
candidacy is the *combination* of all four that qualifies
the practitioner for the stewardship.

**Academic foundation.** BSc (Hons.) in Mathematics &
Education from NUI Galway (First Class Honours); Higher
Diploma in Applied Science (Software Design & Development)
with First Class Honours; current MSc track and forthcoming
PhD track in **Artificial Intelligence** at the University
of Galway. The academic record is the empirical basis for
the cianfhoghlaim monorepo's claim to deliver
syllabus-informed educational resources at A-Level /
Leaving Cert standard.

**Teaching foundation.** Qualified Mathematics & Applied
Mathematics teacher (Teaching Council of Ireland
registration; Newly Qualified Teacher status pending the
Droichead induction). The PGCE (BCS Computing scholarship)
is held jointly. The BME1 placement portfolio, the
action-research project, the educational psychology +
sociology + philosophy of education assignments are the
humanistic evidence base. School placements at **Coláiste
na Coiribe**, **Scoil Iognáid** (the Jesuit school), and the
**Galway Community College** / **Scoil Iarfhlatha** are the
in-service evidence. The teaching foundation is the
empirical basis for the cianfhoghlaim project's claim to
serve every Gaeltacht and every Celtic language at the
classroom level.

**Linguistic foundation.** Dioplóma **C1 in Irish** (TEG /
Teastas Eorpach na Gaeilge). The personal acquisition
pathway is the **Irish → Scottish Gaelic → Manx → Welsh →
Cornish → Breton** trajectory documented in
[`celtic_language_learning_for_gaeilgeoir.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/celtic_language_learning_for_gaeilgeoir.pdf)
(Sabhal Mòr Ostaig "Gaelic for Irish Speakers", Scoill
Souree at Peel, the National Centre for Learning Welsh,
Keskowethyow, Skol an Emsav). Each stage of the pathway
generates the primary corpus data for the Celtic AI Institute.
The linguistic foundation is the empirical basis for the
cianfhoghlaim project's claim to deliver Sovereign LLMs
and side-by-side transcription tools for each Celtic
language.

**AI / engineering foundation.** The cianfhoghlaim monorepo
itself is the live evidence base for this fourth pillar:
Python + TypeScript + Bun + uv + mise + Dagster + DLT +
CocoIndex + BAML + Cognee + LanceDB + Memgraph + FalkorDB
+ MotherDuck + DuckLake + LiteLLM + Langfuse + MLflow +
RAGAS + TanStack Start + Babylon.js + Hono + marimo. The
33 compose stacks, the 5-stage ingestion-to-expose
pipeline, the 7 web apps, the 11 HuggingFace Spaces, the
12-agent fleet are the working substrate. The AI /
engineering foundation is the empirical basis for the
cianfhoghlaim project's claim to be the operational
vehicle for the §20 plan throughout the British Isles.

**The pledge.** The cianfhoghlaim project is committed to
the cultural stewardship of the four provinces, the
Gaeltachtaí, and the wider Celtic-language family. The
Ard-Rí title in §21c is the *stewardship* that holds the
project accountable to the heritage. The cianfhoghlaim
plan in §20 is the *operational* form of that
stewardship. The personal qualifications in this §21e
are the *empirical warrant* for the stewardship. The
heritage corpus in
[`./leabharlann/gemini_deep_research/culture/`](https://github.com/cianfhoghlaim/leabharlann/tree/main/gemini_deep_research/culture/)
is the *evidential foundation* of the warrant. The
cianfhoghlaim monorepo is the *instrument*. The
stewardship is the *commitment*.

### On the educational mission — *saíocht*, the *Saoí* standard, and free syllabus-informed resources for every Gaeltacht and every Celtic language

The §21e pledge is operationalised as the *educational
mission* — a single, concrete public good: **free,
high-quality, syllabus-informed, open-licensed educational
resources for every Gaeltacht and every Celtic language**,
in service of the *saíocht* (wisdom / sagacity) of the
*Saoí* standard that the Brehon Laws required of a king.
The
[`claiming_r_na_gaillimhe_a_synthesis.pdf`](./leabharlann/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
is explicit: "Under the ancient Fénechas (Brehon Laws), a
king was required to possess not only martial strength but
also intellectual distinction. … The ideal ruler was the
Scholar-Prince, a man who was a *saoí* (sage/master) in a
branch of learning" (p. 3). The modern translation of
*saoí* is the "Saoí Education Standard" of the
[`cultural_unity_for_british_isles.pdf`](./leabharlann/gemini_deep_research/culture/cultural_unity_for_british_isles.pdf):
"the *Saoí* (Sage) of the 21st century must be fluent in
both the Fénechas and Python" (p. 4). The resources
committed in this project aim at that standard — at every
Gaeltacht (the [Gaoith Dobhair / Gweedore /
Inishowen](https://en.wikipedia.org/wiki/Gaoth_Dobhair)
Gaeltacht of Donegal, the [Conamara](https://en.wikipedia.org/wiki/Conamara) /
Aran / Maam Gaeltacht of Galway, the Corca Dhuibhne /
Chiarraí Gaeltacht of Kerry, the Musgraí / Chorcaí
Gaeltacht of Cork, and the Gaeltacht Mheath / Ráth Cairn)
and at every Celtic language (Irish, Scottish Gaelic,
Manx, Welsh, Cornish, and Breton).

The mission has 5 concrete deliverables, each tied to the
§20 British Isles plan:

1. **Syllabus-informed Leaving Certificate resources (Irish,
   Maths, English, CS).** The
   [`leabharlann/ollscoil_na_gaillimhe/`](./leabharlann/ollscoil_na_gaillimhe/)
   subtree holds the Leaving Certificate and Junior
   Certificate results, the Educational Autobiography, the
   BME1 placement portfolios, the action-research project,
   the educational psychology and sociology assignments.
   These are the empirical basis for syllabus-aligned
   Leaving Cert resources (Irish, Maths, Applied Maths,
   English, CS) that the project will make available under
   an open licence.

2. **Saoí Capstone project — Celtic-language STEM.** Modelled
   on the "Saoí Certification" of the
   [`cultural_unity_for_british_isles.pdf`](./leabharlann/gemini_deep_research/culture/cultural_unity_for_british_isles.pdf)
   (p. 4) — "developing an AI chatbot in Manx", "mapping
   coastal erosion in Cornwall using GIS data annotated in
   Cornish", "cryptographic analysis of Ogham inscriptions
   using machine learning". The capstone is the modern
   *saíocht* of the Scholar-Prince.

3. **Sovereign AI for the Celtic languages.** The
   [`celtic_language_digital_revitalization_strategy.pdf`](./leabharlann/gemini_deep_research/culture/celtic_language_digital_revitalization_strategy.pdf)
   proposes a "Celtic AI Institute" (potentially based in
   the Isle of Man) "that would build open-source LLMs for
   Irish, Welsh, Manx, and Scottish Gaelic", and the
   [`digital_resources_for_celtic_languages.pdf`](./leabharlann/gemini_deep_research/culture/digital_resources_for_celtic_languages.pdf)
   catalogues the open-source GIS /
   side-by-side-transcription / acoustic-corpus
   infrastructure that the project will federate. The
   §20 East Belfast hub (Turas / Scoil na Seolta / Coláiste
   Feirste) is the real-world testing environment for these
   LLMs.

4. **The Pan-Celtic Erasmus (Colmcille).** The
   [`cultural_unity_for_british_isles.pdf`](./leabharlann/gemini_deep_research/culture/cultural_unity_for_british_isles.pdf)
   recommends expanding the existing Colmcille
   Irish/Scottish-Gaelic partnership "into a 'Pan-Celtic
   Erasmus' scheme" that "facilitates student exchanges
   between Wales, Cornwall, Ireland, and Scotland" (p. 4).
   The project will federate the
   `leabharlann/ollscoil_na_gaillimhe/irish/`, `…/mata/`, and
   `…/software_development/` evidence bases with the Manx
   *Bunscoill Ghaelgagh* model and the Welsh *Cymraeg 2050*
   curriculum.

5. **Shared-infrastructure investment in Galway, Donegal,
   Belfast, Dublin.** The
   [`royal_collaboration_for_commonwealth_future.pdf`](./leabharlann/gemini_deep_research/culture/royal_collaboration_for_commonwealth_future.pdf)
   is explicit that the maturation of the Irish
   government's €1 billion Shared Island infrastructural
   investments is a prerequisite for the 2060 horizon (p. 2).
   The project will support this with marimo notebooks,
   Lakehouse BAML extractions, and Dagster assets that
   expose the Galway-Donegal educational-cohort data for
   open analysis.

The *saíocht* of the *Saoí* is the project's north star. The
[`claiming_r_na_gaillimhe_a_synthesis.pdf`](./leabharlann/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
sums up: "Under the ancient Fénechas (Brehon Laws), a king
was required to possess not only martial strength but also
intellectual distinction. … The ideal ruler was the
Scholar-Prince, a man who was a *saoí* (sage/master) in a
branch of learning" (p. 3). The
[`british_isles_cianfhoghlaim.pdf`](./leabharlann/gemini_deep_research/culture/british_isles_cianfhoghlaim.pdf)
sums up the modern translation: the practitioner holds a BSc
in Mathematics and Education, a Dioplóma C1 in Irish, and
is positioned to undertake an MSc and then a PhD in
Artificial Intelligence at the University of Galway (p. 1) —
i.e. the academic profile of a *Saoí* of Mathematics and
Code, fit to "judge and to rule" in the *saíocht* sense. The
[`cultural_unity_for_british_isles.pdf`](./leabharlann/gemini_deep_research/culture/cultural_unity_for_british_isles.pdf)
sums up the goal: the project must produce a workforce "that
embodies the claimant's own profile: technically elite,
culturally rooted, and strategically minded. It prevents the
'brain drain' by anchoring high-tech skills in local cultural
contexts" (p. 4).

**Citations** (the eight Wikipedia articles are clipped at
[`cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`](cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/);
the 4 Gemini PDFs that ground the §21c-§21f sections are in
[`leabharlann/gemini_deep_research/culture/`](https://github.com/cianfhoghlaim/leabharlann/tree/main/gemini_deep_research/culture/)):

- **Wikipedia**: [Uí Liatháin](https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in) ·
  [Delbhna Tír Dhá Locha](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha) ·
  [Eamonn Deacy Park](https://galwayunitedfc.ie/eamonn-deacy-park) ·
  [Leath Cuinn and Leath Moga](https://en.wikipedia.org/wiki/Leath_Cuinn_and_Leath_Moga) ·
  [Cian](https://en.wikipedia.org/wiki/Cian) ·
  [Aos Sí](https://en.wikipedia.org/wiki/Aos_S%C3%AD) ·
  [Tuatha Dé Danann](https://en.wikipedia.org/wiki/Tuatha_D%C3%A9_Danann) ·
  [Déisi](https://en.wikipedia.org/wiki/D%C3%A9isi)
- **Heritage PDFs (the 4 that ground §21c-§21f)**:
  [Claiming Irish Kingship Through Lineage](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf) ·
  [Royal Titles, Celtic Heritage, and Claims](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf) ·
  [British Isles Cianfhoghlaim (the East Belfast operational hub + inter-Celtic acquisition pathway)](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/british_isles_cianfhoghlaim.pdf) ·
  [Celtic Language Learning for Gaeilgeoir (Sabhal Mòr Ostaig + Scoill Souree + teacher credentialing)](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/celtic_language_learning_for_gaeilgeoir.pdf)
- **Other supporting PDFs**:
  [Claiming Rí na Gaillimhe — A Synthesis](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf) ·
  [Heraldic Research for Dual Blood Lineage](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/heraldic_research_for_dual_blood_lineage.pdf) ·
  [Royal Collaboration for Commonwealth Future (the 2060 Geostrategic Synthesis)](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_collaboration_for_commonwealth_future.pdf) ·
  [Cultural Unity for British Isles (the Cultural Archipelago)](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/cultural_unity_for_british_isles.pdf) ·
  [Celtic Language Digital Revitalization Strategy](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/celtic_language_digital_revitalization_strategy.pdf) ·
  [Digital Resources for Celtic Languages](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/digital_resources_for_celtic_languages.pdf) ·
  [Deacy Family Heritage Research](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/deacy_family_heritage_research.pdf) ·
  [The Socio-Economic, Athletic, and Genealogical Topography of the Deacy Family in Galway](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/the_socio_economic_athletic_and_genealogical_topography_of_the_deacy_family_in_galway_a_multi_dimensional_analysis.pdf)

**Note on 2 unreadable PDFs** (status as of 2026-06-29):

- The dual ROI/UK citizenship scan at
  [`cian_mac_an_déisigh_uí_liatháin/identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf`](cian_mac_an_déisigh_uí_liatháin/identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf)
  is **now restored** to the working tree (cherry-picked from
  `q3-2026-oideachais-consolidation`). The previous agent could
  not read its text; a follow-up agent with PDF input support
  can now incorporate the scan into the `culture_heritage`
  Cognee dataset.
- The August 1986 *Galway Advertiser* article on the inaugural
  Streets of Galway 8 km road race was historically available at
  `./leabharlann/gemini_deep_research/culture/neil_deacy_cookes_corner-galway_advertiser.pdf`
  but **is still missing from disk** because it was never
  committed to git. A copy of the same article (under a similar
  filename) has since been located at
  [`cian_mac_an_déisigh_uí_liatháin/identity/lineage/neil_deacy_cookes_corner-galway_advertiser.pdf`](cian_mac_an_déisigh_uí_liatháin/identity/lineage/neil_deacy_cookes_corner-galway_advertiser.pdf)
  and is now restored alongside the rest of the
  `cian_mac_an_déisigh_uí_liatháin/identity/lineage/` tree. A
  follow-up agent should treat the
  `leabharlann/gemini_deep_research/` path as deprecated and
  point any future citations at the restored file.

The Irish-English bilingual title on line 1 of this README is
the canonical form.

---

## Licensing

Business Source License 1.1 — non-commercial, cultural preservation,
and academic research use permitted within Ireland, UK, EU,
Commonwealth, and aligned jurisdictions. Subsets may transition to
AGPL v3.0 after 4 years. See [`LICENSE.md`](LICENSE.md).

All three repositories in the constellation
([cianfhoghlaim](https://github.com/cianfhoghlaim/cianfhoghlaim),
[bonneagar](https://github.com/cianfhoghlaim/bonneagar),
[leabharlann](https://github.com/cianfhoghlaim/leabharlann)) are
licensed under BUSL-1.1 by the same Licensor.

---

*Built by Cian Mac an Déisigh Uí Liatháin (Deacy-Lyons) of the
Deacy-Morris-Conroy tribe of Galway — BSc (Hons.) Mathematics &
Education (NUI Galway, First Class Honours), Higher Diploma in
Software Design & Development (First Class Honours), current MSc /
forthcoming PhD track in Artificial Intelligence (University of
Galway), Dioplóma C1 in Irish, qualified Mathematics & Applied
Mathematics teacher (Teaching Council of Ireland), grandchild of
the late Neil Deacy of Cooke's Corner, Shantalla, Galway, dual
Irish-British citizen, born a British citizen and obliged by oath
of allegiance to King Charles the Third. The cianfhoghlaim
project is the stewardship of the Gaelic cultural inheritance
through the agentic-AI operationalisation of the *saíocht* /
*Saoí* standard across the four provinces, the Gaeltachtaí, and
the wider Celtic-language family.*
