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

### `./leabharlann/` (worktree) — 2,400 files, 3.4 GB

```
leabharlann/
├── gaeilge/                   # 38+ Irish-language PDFs
├── mata/                      # 27+ mathematics textbooks
├── aigne/                     # 72+ cognitive science / mind books
├── ollscoil_na_gaillimhe/     # 21+ University of Galway coursework archives
├── zotero/                    # 34+ research papers (Zotero export)
└── gemini_deep_research/      # 24+ long-form Gemini deep research reports
```

The 2,400 files / 3.4 GB corpus lives entirely in the sibling
`leabharlann` repo and is exposed here as a worktree. To use the
corpus from the monorepo, reference it through the relative path
`./leabharlann/...` (or symlink it into a working location).

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

## About the author, the name, and the lineage

### On the username — *cianfhoghlaim*

The repository name and the underlying platform are both
**Cianfhoghlaim**. The Irish word *cianfhoghlaim* (pronounced roughly
*kee-an-oh-guh-lem*) compounds two roots:

- *cian* — long, enduring, distant
- *foghlaim* — learning, study

So *cianfhoghlaim* reads literally as **"long-distance, enduring
learning"** — lifelong learning across geography and discipline, which
is the whole point of this project.

*Cian* also has a second life in the Irish mythological canon: in
*Lebor Gabála Érenn* and the wider Tuatha Dé Danann cycle, **Cian** is
the father of Lugh Lámhfhada (Lug of the Long Arm), the many-skilled
god who walks into the Battle of Moytura and slays his grandfather
Balor. The `cianfhoghlaim/agents/tuatha/` subtree — the British Isles
formative-assessment MMO built on Babylon.js + SpacetimeDB — sits
squarely inside that mythological lineage.

The Irish word **sruth** (pronounced *sruh*) means *stream* or *flow*.
In `opencode.json`, the four traditional top-level subprojects
(oideachais, meaisinfhoghlaim, tuatha, croilar) plus infrastructure are
referred to as the five **sruthanna** — flows — rather than
"quadrants", because in a knowledge-graph platform the meaningful unit
of work is the *flow of data and reasoning*, not a static slice of a
2D plane. As of the v4 consolidation (2026-06-28) the 5 sruthanna have
been merged into the single `cianfhoghlaim/` package, but the term is
preserved for historical continuity.

### On the family — *Mac an Déisigh Uí Liatháin (Deacy-Lyons)*

The author is **Cian Mac an Déisigh Uí Liatháin**; the family surname
in its two anglicised forms is **Deacy-Lyons**. The author's verified
genealogy and qualifications inform the project's design choices and
are recorded under
[`cian_mac_an_déisigh_uí_liatháin/`](cian_mac_an_déisigh_uí_liatháin/):

- `identity/` — background, citizenship, vetting, and the Deacy family
  record. The `identity/lineage/` subfolder holds the family-lineage
  documents: the late uncle's memorial, the dual ROI/UK citizenship
  evidence, the College des Irlandais (Paris) records, and the
  5-culture-PDF Wikipedia dual-write clippings (8 articles: Uí
  Liatháin, Delbhna Tír Dhá Locha, Eamonn Deacy Park, Leath Cuinn,
  Cian, Aos Sí, Tuatha Dé Danann, Déisi).
- `teaching/` — the Teaching Council of Ireland registration, the
  PGCE (BCS Computing scholarship), school placement references, and
  the Leaving Certificate / Junior Certificate results (the public
  copies are in the `identity/` folder; the full teaching record is
  held privately for data-protection reasons).
- `achievement/` — academic transcripts, parchments, the Apple Award,
  and the Torthaí Gaeilge (Irish-language exam results) (same privacy
  caveat).

The author's lineage is the **triple-crown** union of four kindreds
of Connacht and Munster:

1. **Deacy** (maternal surname; Irish *Uí Dhéisigh*) — the sept of the
   [Déisi Muman](https://en.wikipedia.org/wiki/D%C3%89isi) resettled
   in south Connacht (Co. Galway) during the 12th century; the family
   gave their name to the late
   [Éamonn Deacy](https://en.wikipedia.org/wiki/Eamonn_Deacy_Park)
   and the [Eamonn Deacy
   Park](https://en.wikipedia.org/wiki/Eamonn_Deacy_Park) in Galway.
2. **Lyons** (paternal grandfather's lineage; Irish *Mac Liatháin*) —
   the [Uí Anmchada](https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in)
   sept of the
   [Uí Liatháin](https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in)
   of Munster, who (per the *Historia Brittonum*) colonized Wales and
   Cornwall alongside the proto-Déisi.
3. **Morris** (maternal great-grandmother **Christina Morris**) — of
   the [City of Tribes](https://en.wikipedia.org/wiki/Galway) merchant
   families of Galway.
4. **Conroy** (maternal great-great-grandmother **Polly Conroy**;
   Irish *Mac Conraoi / Ó Conaire*) — the
   [Sea-Kings of Connacht](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha)
   who held the tuath of
   [Delbhna Tír Dhá Locha](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha)
   (the barony of Moycullen in Connemara). **Polly Conroy was a cousin
   of Pádraic Ó Conaire**, the canonical modern Irish-language writer
   from Galway, who was reared in Rosmuc by his uncle of the same
   Mac Conraoi kindred.

The author is the grandson and godson of the late **Neil Deacy**, the
late brother of the late **Éamonn Deacy** — the Galwegian footballer
who played for Galway United, Aston Villa FC, and the Republic of
Ireland. Neil and Éamonn were the sons of **Christina Morris** and
**Michael Deacy**, who was himself the son of **Polly Conroy** and
**George Deacy**.

The author was the primary palliative carer of the late Neil Deacy.
That personal care work — and the cultural inheritance that goes with
the Conroy / Deacy / Morris Galway lineage — is the reason this
project treats Connemara, Connacht, and the Irish-language curriculum
as first-class objects rather than as flavour-of-the-month features.

### On the claim — *Rí na Gaillimhe, Rí Chonnachta*

The Conroy (Ó Conaire / Mac Con Raoi) family were among the
[**sea-kings of Connacht**](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha),
holding the tuath of
[Delbhna Tír Dhá Locha](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha)
in what is now the barony of Moycullen in Connemara. *Galway is the
capital of Connacht.* The
[Uí Liatháin](https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in) (of
the Lyons / Mac Liatháin sept) were a Munster kindred who colonized
Wales and Cornwall alongside the
[proto-Déisi](https://en.wikipedia.org/wiki/D%C3%89isi); the
[Uí Dhéisigh](https://en.wikipedia.org/wiki/D%C3%89isi) (Deacy) are a
sept of the same Déisi Muman, resettled in south Connacht in the 12th
century. The corpus-anchored PDF
[`claiming_r_na_gaillimhe_a_synthesis.pdf`](./leabharlann/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
draws the distinction sharply: the title *Rí na Gaillimhe* is not
synonymous with the English "King of Galway", because "King", when
applied to Irish territory after the Norman invasion of 1169, "carries
explicit feudal connotations … derived from the election of the tribe",
whereas *Rí* denotes the sacral relationship between ruler and *tuath*
under the *Fénechas* (Brehon Law), mated to the sovereignty goddess of
the land in the *banais ríghi* (wedding of kingship)
(`claiming_r_na_gaillimhe_a_synthesis.pdf`, p. 1-2). The claim of *Rí
na Gaillimhe* therefore bypasses the colonial structure of the
Anglo-Norman "City of the Tribes" and asserts an indigenous authority
that "predates the walls of Galway and the dominance of the Lynch
mayoralty" (p. 2).

The Triple Crown is rooted in three documented pillars: **the Uí
Liatháin (Lyons)** bring the imperial, royal, and maritime dimension —
they "launched massive raids and established colonies in Dyfed (Wales)
and Cornwall" in the 4th and 5th centuries, and through Angias
(daughter of Ailill Tassach of the Uí Liatháin, who married the High
King Lóegaire mac Néill) they are the *maternal* ancestors of the Uí
Néill High Kings of Tara
([`claiming_irish_kingship_through_lineage.pdf`](./leabharlann/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf),
p. 5); the **Uí Dhéisigh (Deacy)** bring the martial, territorial, and
"Oenach" dimension — the renaming of Terryland Park to [Eamonn Deacy
Park](https://en.wikipedia.org/wiki/Eamonn_Deacy_Park) in honour of the
Aston Villa and European Cup winner is "a modern secular equivalent
of the ancient inauguration rituals at sites like Tara or Lisbanagher …
the Oenach (assembly place) of the tribe"
([`claiming_irish_kingship_through_lineage.pdf`](./leabharlann/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf),
p. 7); and the **Mac Conraoi (Conroy)** bring the maritime and
mercantile dimension — the great-grandfather John Conroy operated a
"large fish business" on Quay Street, opposite McDonagh's, in what was
"the absolute epicenter of Galway's maritime trade" in the late 19th
century, and the etymological anglicization of *Mac Conraoi* to *King*
("due to the phonetic similarity to *Mac an Rí* — Son of the King")
embeds the title in the very name
([`deacy_family_heritage_research.pdf`](./leabharlann/gemini_deep_research/culture/deacy_family_heritage_research.pdf),
p. 2; [`claiming_irish_kingship_through_lineage.pdf`](./leabharlann/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf),
p. 5). The visual half of the claim is supplied by the **Connacht
arms** — "Party Per Pale Argent and Azure, in the first an eagle
dimidiated and displayed Sable, in the second issuant from the
partition an arm embowed and vested, the hand holding a sword erect,
all Argent" — which the
[`heraldic_research_for_dual_blood_lineage.pdf`](./leabharlann/gemini_deep_research/culture/heraldic_research_for_dual_blood_lineage.pdf)
interprets as a heraldic prophecy of the "Dual Blood": the
dimidiated Eagle is the Uí Liatháin / Lyons / Imperial half, the
Arm-and-Sword is the Uí Dhéisigh / Deacy / Martial half, and the
claimant "is these arms" (p. 2-3). The Deacy motto *Toujours Pret*
("Always Ready") and crest of "a dexter arm erect … holding a dagger"
mirror the Connacht arm; the Lyons motto *Noli Irritare Leones* and
the Lion of the Lyons crest mirror the Connacht Eagle (p. 4, 6).

On the basis of this triple-crown lineage (Lyons / Deacy / Conroy),
grounded in eight canonical Wikipedia articles and six Gemini Deep
Research PDFs preserved in
[`./leabharlann/gemini_deep_research/culture/`](./leabharlann/gemini_deep_research/culture/),
the author makes the modern claim of inheritance in the
[Leath Cuinn](https://en.wikipedia.org/wiki/Leath_Cuinn_and_Leath_Moga)
framework (see § D below):

> *Rí na Gaillimhe, Rí Chonnachta, Ard-Rí na hÉireann* — King of
> Galway, King of Connacht, High King of Ireland.

**Citations** (the eight Wikipedia articles are clipped at
`cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`;
the six Gemini PDFs are in
[`./leabharlann/gemini_deep_research/culture/`](./leabharlann/gemini_deep_research/culture/)):

- **Wikipedia**: [Uí Liatháin](https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in) ·
  [Delbhna Tír Dhá Locha](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha) ·
  [Eamonn Deacy Park](https://en.wikipedia.org/wiki/Eamonn_Deacy_Park) ·
  [Leath Cuinn and Leath Moga](https://en.wikipedia.org/wiki/Leath_Cuinn_and_Leath_Moga) ·
  [Cian](https://en.wikipedia.org/wiki/Cian) ·
  [Aos Sí](https://en.wikipedia.org/wiki/Aos_S%C3%AD) ·
  [Tuatha Dé Danann](https://en.wikipedia.org/wiki/Tuatha_D%C3%A9_Danann) ·
  [Déisi](https://en.wikipedia.org/wiki/D%C3%89isi)
- **Heritage PDFs**: [Claiming Rí na Gaillimhe — A Synthesis](./leabharlann/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf) ·
  [Claiming Irish Kingship Through Lineage](./leabharlann/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf) ·
  [Deacy Family Heritage Research](./leabharlann/gemini_deep_research/culture/deacy_family_heritage_research.pdf) ·
  [Researching Neil Deacy's Galway Heritage](./leabharlann/gemini_deep_research/culture/researching_neil_deacy_s_galway_heritage.pdf)
- **Royal collaboration PDFs**: [Royal Collaboration for Commonwealth Future](./leabharlann/gemini_deep_research/culture/royal_collaboration_for_commonwealth_future.pdf) ·
  [Royal Titles, Celtic Heritage, and Claims](./leabharlann/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf)

**Note on 2 unreadable PDFs** (status as of 2026-06-29):

- The dual ROI/UK citizenship scan at
  [`cian_mac_an_déisigh_uí_liatháin/identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf`](cian_mac_an_déisigh_uí_liatháin/identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf)
  is **now restored** to the working tree (cherry-picked from
  `q3-2026-oideachais-consolidation`). The previous agent could not
  read its text; a follow-up agent with PDF input support can now
  incorporate the scan into the `culture_heritage` Cognee dataset.
- The August 1986 *Galway Advertiser* article on the inaugural
  Streets of Galway 8 km road race was historically available at
  `./leabharlann/gemini_deep_research/culture/neil_deacy_cookes_corner-galway_advertiser.pdf`
  but **is still missing from disk** because it was never committed
  to git. A copy of the same article (under a similar filename) has
  since been located at
  [`cian_mac_an_déisigh_uí_liatháin/identity/lineage/neil_deacy_cookes_corner-galway_advertiser.pdf`](cian_mac_an_déisigh_uí_liatháin/identity/lineage/neil_deacy_cookes_corner-galway_advertiser.pdf)
  and is now restored alongside the rest of the
  `cian_mac_an_déisigh_uí_liatháin/identity/lineage/` tree. A
  follow-up agent should treat the `leabharlann/gemini_deep_research/`
  path as deprecated and point any future citations at the restored
  file.

### On the joint claim — *Leath Cuinn and the dual-monarchy framework*

The author makes the claim of *Rí Chonnachta* and *Rí na hÉireann* in
a constitutional framework that does **not** compete with the existing
United Kingdom sovereignty over Northern Ireland. The framework is the
**Neo-Jacobite Dual Monarchy** model, modelled on the
[Austria-Hungary](https://en.wikipedia.org/wiki/Austria-Hungary)
constitutional theory proposed by
[Arthur Griffith](https://en.wikipedia.org/wiki/Arthur_Griffith) in
*The Resurrection of Hungary* (1904) and on the modern
[Māori King Movement](https://en.wikipedia.org/wiki/K%C4%81ngi_Mahuta).

Under this framework:

- **Cian Mac an Déisigh Uí Liatháin** holds *Rí na Gaillimhe* and *Rí
  Chonnachta* by virtue of the triple-crown lineage (Uí Liatháin + Uí
  Dhéisigh + Mac Conraoi) and the verified qualifications documented
  in § E below.
- **King Charles III** holds *Rí Uladh* (Northern Ireland) by virtue
  of his constitutional position as Sovereign of the United Kingdom.
- **Jointly**, they hold *Leath Cuinn* — Conn's Half, the northern
  half of Ireland comprising Connacht + Ulster + Meath, traditionally
  divided from Leath Moga by the
  [Esker Riada](https://en.wikipedia.org/wiki/Esker_Riada) (Dublin Bay
  to Galway Bay).
- The claim is grounded in the genealogical fact that
  [Conn Cétchathach](https://en.wikipedia.org/wiki/Conn_C%C3%A9tchathach)
  ("Conn of the Hundred Battles") is the legendary common ancestor of
  both the **Connachta** dynasty (the royal kindreds of Connacht,
  including the Uí Briúin and Uí Fiachrach) AND the **Uí Néill**
  dynasty (the royal kindreds of Ulster and Meath, including the
  Northern Uí Néill of Aileach and the Southern Uí Néill of Meath).

The author is conscious that this framework rests on a parliamentary
claim rather than on a hereditary peerage-roll claim, and that the
*Ard-Rí na hÉireann* title is held in suspension pending the
constitutional reunification of Ireland. In the early-medieval sense
the *Ard-Rí na hÉireann* (literally "High King of Ireland") was the
Uí Néill over-king at Tara, and the title carries a constitutional
weight that the present claim deliberately leaves in suspension: the
*Crown of Ireland Act 1542* created the Kingdom of Ireland in
personal union with the English Crown, and the *1800 Act of Union*
merged the two parliaments — but the "distinct Crown of Ireland has
a ghostly legal existence" that this claim respectfully acknowledges
without attempting to revive
([`claiming_irish_kingship_through_lineage.pdf`](./leabharlann/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf),
p. 7). Under the Neo-Jacobite framework the British Monarch is
therefore the *De Jure* Sovereign of Northern Ireland and the
claimant is the *De Facto* Gaelic Lieutenant — a relationship modelled
on the "Princes of the Holy Roman Empire or the Maharajas of the
British Raj" and on Arthur Griffith's reading of
[Austria-Hungary](https://en.wikipedia.org/wiki/Austria-Hungary)
(`claiming_irish_kingship_through_lineage.pdf`, p. 4). The suspension
is *not* a renunciation; it is a constitutional courtesy parallel to
King Charles III's continued *Rí Uladh* claim, and the
[`royal_titles_celtic_heritage_and_claims.pdf`](./leabharlann/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf)
argues that the framework is in fact "viable" and "heals the shield"
of Connacht by allowing the Eagle (Britain) and the Arm (Ireland) to
coexist (p. 1, 6). **Born a British citizen and obliged by oath of
allegiance to King Charles the Third**, the author regards the
joint-claim framework as a constructive path toward constitutional
dialogue rather than as a hostile or seditious claim.

### On the verified qualifications

The teaching, mathematics, and software-development qualifications
that the project depends on are recorded under
[`./leabharlann/ollscoil_na_gaillimhe/`](./leabharlann/ollscoil_na_gaillimhe/):

- [`./leabharlann/ollscoil_na_gaillimhe/mata/`](./leabharlann/ollscoil_na_gaillimhe/mata/) —
  Applied Statistics I & II, CS402 Cryptography, ISLP labs, Maple,
  Modelling II, Networks, Non-Linear Systems, Numerical Analysis II,
  and the Stokes Workshop Game Physics project — the
  mathematics-and-cryptography foundation for the Lakehouse work.
- [`./leabharlann/ollscoil_na_gaillimhe/education/`](./leabharlann/ollscoil_na_gaillimhe/education/) —
  the Educational Autobiography, the BME1 placement portfolios, the
  action-research project, the educational psychology and sociology
  assignments (psychology, sociology, philosophy of education) — the
  humanistic foundation for the British Isles Formative Assessment
  MMO and for the Leaving Cert syllabi.
- [`./leabharlann/ollscoil_na_gaillimhe/irish/`](./leabharlann/ollscoil_na_gaillimhe/irish/),
  [`past/`](./leabharlann/ollscoil_na_gaillimhe/past/) and
  [`software_development/`](./leabharlann/ollscoil_na_gaillimhe/software_development/) —
  the Irish-language corpus, the historical archive, and the
  software-development evidence base.

These three evidence-bases (mathematics, education, and software
development) are the *reason the project exists* — not the *right*
to build it.

### On the repository name — *Kings' College Galway*

The repository name **Kings' College Galway** uses the **plural
possessive Kings'** deliberately, for three reasons:

1. **Queen's College Galway → University of Galway.** The University
   of Galway was founded in 1845 as **Queen's College Galway**, one
   of the three Queen's Colleges established by Queen Victoria. (The
   other two were Cork and Belfast.) The "Queen's" was renamed to
   "University" under the Universities Act 1997. **Queen Victoria** is
   the predecessor whose name appears on the original charter.
2. **King Charles III's 2022 visit.** On the occasion of King
   Charles III's visit to Galway in 2022, the author — as a
   then-resident Galwegian and a graduate of NUI Galway — observed
   that the Queen's-College-to-Kings'-College gesture would be a
   graceful nod to the new monarch and to the original name
   simultaneously. The plural **Kings'** acknowledges every monarch
   whose predecessor established the institution, not just Charles
   III himself.
3. **The *Coláiste na Déisigh* subtitle.** The Irish subtitle
   *Coláiste na Déisigh* (College of the Deacy / College of the Déssi)
   carries a deliberate **double meaning**: *Déisigh* is the genitive
   singular of *Deasy / Deacy* (the author's paternal surname), AND
   *Déisigh* is also the genitive plural of *Déssi* — the
   [ancient Irish vassal
   class](https://en.wikipedia.org/wiki/D%C3%89isi) that was resettled
   as frontier warriors along the coasts of Connacht, Munster,
   Leinster, Wales, Cornwall, and Devon. The subtitle therefore says
   simultaneously: "the college of the Deacy family" and "the college
   of the Déssi vassal class". *Coláiste* in Irish means college, and
   the suffix *-na-* is the genitive singular article. Read together,
   *Kings' College Galway || Coláiste na Déisigh* says "the King's
   college (named after the royal predecessor of Queen Victoria) and
   also the college of the Deacy family and the Déssi class".

   The **Deacy half** of the subtitle is grounded in a four-generation
   Galway commercial dynasty documented in the corpus PDFs. The
   great-grandfather John Conroy operated the Quay Street fish business
   "opposite McDonagh's" in the late 19th century; the Conroy
   enterprise "dominated the supply of fresh fish to the city's hotels,
   religious houses, and the British Army garrison"
   ([`deacy_family_heritage_research.pdf`](./leabharlann/gemini_deep_research/culture/deacy_family_heritage_research.pdf),
   p. 2). The matriarchal bridge from Conroy to Deacy is the marriage
   of Polly Conroy to George Deacy in c. 1910-1920; the High Street
   consolidation under their son Miko (Michael) Deacy, who trained Neil
   Deacy "in the ancient arts of filleting, curing, and barrelling";
   and the 1986 expansion of Neil and Peggy Deacy to Cookeʼs Corner,
   a "critical arterial junction" that "intercepted the commuter flow
   of residents traveling to and from the city"
   ([`deacy_family_heritage_research.pdf`](./leabharlann/gemini_deep_research/culture/deacy_family_heritage_research.pdf),
   p. 3; [`the_socio_economic_athletic_and_genealogical_topography_of_the_deacy_family_in_galway_a_multi_dimensional_analysis.pdf`](./leabharlann/gemini_deep_research/culture/the_socio_economic_athletic_and_genealogical_topography_of_the_deacy_family_in_galway_a_multi_dimensional_analysis.pdf),
   p. 3). Peggy Deacy's bilingual retail strategy — "Niall Mac an
   Déisigh éisc úra agus glasraí. Beidh Fáilte roimh mhuintir Chonamara
   ar an mbealach anoir agus siar" — explicitly addressed the
   Connemara Gaeltacht customer base and "transformed Cooke's Corner
   into a culturally safe harbor" (topography PDF, p. 3-4). The Deacy
   commercial footprint is completed by Eamonn "Chick" Deacy's
   international sporting legacy (League Championship 1981, European
   Cup 1982 with Aston Villa) and by the modern extension of the
   Deacy commercial family into the cultural and intellectual
   economy — most visibly Paul Deacy's ownership of Kenny's Bookshop
   and Art Gallery in Liosban
   ([`the_socio_economic_athletic_and_genealogical_topography_of_the_deacy_family_in_galway_a_multi_dimensional_analysis.pdf`](./leabharlann/gemini_deep_research/culture/the_socio_economic_athletic_and_genealogical_topography_of_the_deacy_family_in_galway_a_multi_dimensional_analysis.pdf),
   p. 5). The Deacy half of the subtitle therefore names a real,
   documented, multi-generational Galway mercantile and cultural
   lineage.

   The **Déssi half** of the subtitle is grounded in the ancient
   Irish vassal class resettled as frontier warriors under the
   *Tairired na nDéssi* foundation myth. The Déisi "rebel against
   the injustice of the High King Cormac mac Airt (blinding him in
   one eye) and were expelled from Tara" before migrating west
   across the Shannon and "carving out new kingdoms in Munster and
   Connacht"; the *Déisi Tuisceart* (Northern Déisi) became the
   *Dál gCais*, the dynasty of Brian Boru
   ([`claiming_r_na_gaillimhe_a_synthesis.pdf`](./leabharlann/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf),
   p. 5-6; [`royal_titles_celtic_heritage_and_claims.pdf`](./leabharlann/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf),
   p. 4). The motto of the Deacy / Deasy lineage — *Toujours Pret*
   ("Always Ready") — is interpreted as "a continuation of this
   doctrine" of conditional Déisi loyalty: "a permanent readiness to
   defend the honor of the tribe against central tyranny"
   (`royal_titles_celtic_heritage_and_claims.pdf`, p. 4). Read
   together, *Coláiste na Déisigh* therefore names both a
   contemporary Galway family and an ancient Irish vassal class;
   the *Coláiste* (college) half of the title is the umbrella that
   holds the *King's* college (named after Queen Victoria's
   predecessor) and the *Deacy* / *Déssi* lineage together as
   co-equal objects of intellectual and cultural study.

The Irish-English bilingual title on line 1 of this README is the
canonical form. **In memory of**: the late grandfather Neil Deacy, his
late brother Éamonn Deacy, and the
[Déssi class](https://en.wikipedia.org/wiki/D%C3%89isi) of early
medieval Ireland — the vassal peoples whose resettlement along the
western seaboard made the Connacht lineage possible.

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
Deacy-Morris-Conroy tribe of Galway — qualified Mathematics & Applied
Mathematics teacher (Teaching Council of Ireland), NUI Galway graduate
(Applied Statistics, Software Development, Irish Language Studies),
dual Irish-British citizen, born a British citizen and obliged by
oath of allegiance to King Charles the Third.*
