# Kings' College Galway || Coláiste na Déisigh

> *A unified Celtic education platform, infrastructure mesh, and AI research laboratory by Cian Mac an Déisigh Uí Liatháin (Deacy-Lyons) as the first part of cianfhoghlaim.ie*

[![Polyglot](https://img.shields.io/badge/polyglot-bun_%2B_uv_%2B_turbo-blue)](#)
[![Dagster](https://img.shields.io/badge/dagster-228_assets-4B8BBE)](oideachais/)
[![License](https://img.shields.io/badge/license-BSL_1.1-green)](LICENSE.md)

---

## What this is

A polyglot monorepo (`bun + uv + turbo`) that ingests the curriculums and exam papers of the British Isles, makes them interactive and bilingual through self-hosted AI, and serves as the personal research-and-deployment platform of Cian Mac an Déisigh Uí Liatháin. Six cooperating quadrants + an infrastructure mesh:

| Quadrant | Path | One-liner | Core stack |
|:--|:--|:--|:--|
| [`oideachais/`](oideachais/) | Curriculum, exam, marking-scheme extraction; BAML × DLT × Dagster × CocoIndex × Cognee | Dagster + DLT + DuckLake + LanceDB + BAML + LiteLLM |
| [`meaisinfhoghlaim/`](meaisinfhoghlaim/) | Model lifecycle + 12 specialised agents + 10 OCR models + 6 Celtic languages | llama-swap + llama.cpp + MLX + Bria FIBO |
| [`croilar/`](croilar/) | Multi-persona portfolio & DevTools Hub | Convex + Hono + TanStack + BetterAuth + Dagster + DLT |
| [`tuatha/`](tuatha/) | Celtic Educational MMO + crypteolas crypto platform | Babylon.js + Dagster + BAML + SpacetimeDB + x402 |
| [`leabharlann/`](leabharlann/) | Digital library: Zotero, Takeout, BAML metadata, CocoIndex v1 embedding | CocoIndex v1 + Zotero + BAML |
| [`infrastructure/`](infrastructure/) | Multi-cloud zero-trust mesh; LLM gateway; team-workflow (n8n+Vikunja+cal-diy) | Pulumi + Komodo + Pangolin + Locket + Infisical + LiteLLM |
| [`spaces/`](spaces/) | HuggingFace Spaces (gradio / docker / static SDKs) | HF Spaces + GitHub Actions |
| [`.agents/skills/`](.agents/skills/) | 123 skill definitions — agent-consumable knowledge of the monorepo | markdown + frontmatter |

The **3-way interaction** that makes the engine work:

```
┌─────────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐
│  oideachais/        │    │  meaisinfhoghlaim/    │    │  infrastructure/     │
│  Dagster assets     │───>│  llama-swap :8080     │<───│  LiteLLM gateway     │
│  BAML extraction    │    │  mlx-omni :10240      │    │   :4000              │
│  CocoIndex v1       │    │  invokeai :9090       │    │  Locket sidecar      │
│  Cognee cognify     │    │  HF cache (124 GB)    │    │  Infisical vault     │
└─────────────────────┘    └──────────────────────┘    └──────────────────────┘
```

- `oideachais/` **calls** the LiteLLM gateway at `http://litellm:4000/v1` through `LiteLLMResource` (Dagster) and `client LiteLLM` (BAML).
- The gateway **routes** to `llama-swap` (GGUF), `mlx-omni` (MLX), `invokeai` (image), or cloud providers.
- `meaisinfhoghlaim/` **feeds** backends with converted GGUF models and runs `llama-swap` on M4 Max 48GB.
- `infrastructure/` **secures** connections with PocketID SSO + Pangolin; **observes** with Langfuse + MLflow; **injects** secrets via Locket.

---

## Mise-en-place (the developer setup)

The full stack that powers day-to-day development is opinionated and tightly integrated. Every choice is made to (a) minimise context switching between TypeScript, Python, infra-as-code, and AI-agentic work, (b) keep monthly spend under $25, and (c) keep the developer one `cd` away from a fully hydrated working copy.

| Tool | Role | Why we chose it |
|:--|:--|:--|
| **mise** | Polyglot toolchain + task runner | Pins `python 3.13`, `uv`, `bun`, `dagger`, `pulumi`, `duckdb`, `sops`, `opencode` in a single `mise.toml`. Directory hooks auto-export `.env` and the workspace `PYTHONPATH` on every `cd`. |
| **bun** | TS runtime, package manager, script runner | One tool replaces `node + npm + yarn + pnpm + npx + tsx`. Powers workspace orchestration, secret sync, OpenSpec, the `ccc` index, the dagster / komodo / pangolin glue. |
| **uv** | Python package manager + workspace manager | Replaces `pip + poetry + pyenv + virtualenv`. Native PEP 723, lockfile, uv-workspace member resolution. Drives the four `members` of the `pyproject.toml` workspace. |
| **turbo** | Cross-language task graph | Orchestrates `build`, `dev`, `typecheck`, `lint`, `format`, `test` across the bun and uv graphs. Reachable through `mise turbo <task>`. |
| **OpenCode** | AI coding agent / IDE companion | Speaks the same OpenAI-compatible protocol as LiteLLM. Dispatches to the 5 specialised subagents (`explorer`, `data-engineer`, `ai-engineer`, `frontend-dev`, `devops-architect`) defined in `opencode.json`. |
| **OpenChamber** | GUI / web / PWA front-end for OpenCode | Optional VS Code extension / desktop app / self-hostable web UI wrapping the OpenCode CLI with branchable chat timelines, smart tool UIs, multi-agent parallel runs in isolated worktrees, GitHub-native flows. Install: `code --install-extension FedaykinDev.openchamber`. |
| **LiteLLM** | OpenAI-compatible LLM gateway | One URL (`http://litellm:4000/v1`) routes to local GGUF, local MLX, local image, and cloud providers. Every BAML function, every Dagster asset, every marimo cell, every n8n workflow calls an *alias* — never a provider id. |
| **HuggingFace GGUF** | Local model format | Q4_K_M quantised GGUFs are small (~4-6 GB per 7 B model) and run on the M4 Max 48 GB via `llama-swap`. Cache at `stedding/huggingface/{hub,gguf,mlx}/`. |
| **openspec** | Spec-driven change management | 32 capability specs, 4 shared. `openspec list --specs` / `openspec validate <change-id> --strict` / `openspec archive <change-id> --yes`. |
| **.agents/skills/** | Agent-consumable knowledge library | 123 skills, indexed by 5 subagents via `ccc` semantic search. Per-skill `SKILL.md` with frontmatter + use-cases + cross-references. |

### How they fit together

```
┌────────────────────────────┐    ┌──────────────────────────────┐    ┌──────────────────────────────┐
│  Visual Studio Code        │    │  OpenCode (agent)            │    │  OpenCode Go API             │
│  ── editor + tasks         │───>│  ── sub-agent dispatcher     │───>│  ── 6-model lineup           │
│  ── integrated terminal    │    │  ── 5 specialised subagents  │    │  ── deepseek-v4-pro direct   │
│  ── debug + MCP clients    │    │  ── 123 .agents/skills/      │    │  ── minimax-m2.5 / m3 plan   │
└──────────────┬─────────────┘    └──────────────┬───────────────┘    └──────────────┬───────────────┘
               │                                │                                 │
               │ mise → bun / uv               │ chat/completions                │
               ▼                                ▼                                 ▼
┌────────────────────────────┐    ┌──────────────────────────────┐    ┌──────────────────────────────┐
│  mise.toml toolchain       │    │  LiteLLM gateway :4000       │    │  HuggingFace GGUF cache      │
│  python 3.13, bun, uv,     │    │  ── llama-swap :8080 (GGUF)  │◀───│  stedding/huggingface/       │
│  dagger, pulumi, opencode  │    │  ── mlx-omni :10240 (MLX)    │    │  28 models, ~124 GB safetensors│
│  ── dir hooks + tasks      │    │  ── OpenCode Go passthrough  │    │  + 30 GB GGUF + 15 GB MLX    │
└────────────────────────────┘    └──────────────────────────────┘    └──────────────────────────────┘
```

### .agents/skills/ — the agent-consumable knowledge library

`.agents/skills/` holds **123 skill definitions** in markdown with frontmatter (name, description, when-to-load trigger). Each skill is a compact, agent-consumable knowledge packet for one specific task:

```bash
bun run ccc:search "Dagster asset partition definition"  # semantic code search
openspec list --specs                                    # 32 specs total
openspec validate <change-id> --strict                   # MUST pass before commit
openspec archive <change-id> --yes                       # after deploy
```

| Skill family | Count | Examples |
|:--|:-:|:--|
| Data platforms | 12 | `dlt`, `dagster`, `motherduck`, `duckdb`, `ducklake`, `cocoindex`, `cognee`, `lancedb`, `falkordb`, `graphiti`, `graphiti-core`, `memgraph` |
| AI agents | 8 | `baml`, `agno`, `pydantic-ai`, `langfuse`, `mlflow`, `ragas`, `agent-observability`, `agent-fleet-orchestration` |
| Celtic | 6 | `celtic-language-ai`, `celtic-asset-generation`, `celtic-ocr-evaluation`, `irish-llm-on-device`, `british-isles-formative-assessment`, `pent-elemental-cosmology` |
| Web | 7 | `tanstack-start`, `agentic-frontend-frameworks`, `copilotkit`, `convex`, `cloudflare`, `hono`, `ag-ui` |
| Infra | 8 | `docker-compose`, `komodo`, `pangolin`, `kubernetes`, `pulumi`, `dagger`, `stack-ops`, `kcg-convergence` |
| Dev tools | 6 | `ccc`, `ccc` (semantic search), `dignified-python`, `openspec`, `mise-en-place`, `opencode` |
| Domain | 14 | `agentic-frontend-frameworks`, `agent-memory-systems`, `kcg-leabharlann-pipeline`, `celtic-asset-generation`, `cross-domain-registry` |

The lint script `mise run lint:skills` enforces the 4 metadata
rules (frontmatter, name match, description length, line count)
on every skill in `.agents/skills/`.

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

# 4. Start the local LLM gateway + HF GGUF swapper
cd infrastructure/stacks/litellm    && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../meaisinfhoghlaim             && docker compose -f compose.yaml -f sidecar.yaml up -d
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

## Core patterns and software

### [`oideachais/`](oideachais/) — the Lakehouse Engine

The Celtic education data platform. Ingests 100+ British Isles curriculum sources (IE, EN, SCT, WLS, NI, IOM, JEY, GGY) into a unified DuckLake 1.0 lakehouse, extracts structured data via BAML, embeds with CocoIndex v1, cognifies with Cognee + Graphiti + FalkorDB.

| Pattern | Implementation | Use |
|:--|:--|:--|
| **DLT ingestion** | `oideachais/dlt_sources/domains/{education,law,medicine}/{nation}/` (the canonical `{nation}/{domain}` layout per `cross-domain-registry`) | Add a new curriculum source |
| **BAML extraction** | `oideachais/baml_src/*.baml` (9 BAML files, 3 clients: `ExtractEn`, `ExtractEnStrong`, `LocalVision`) | Define a structured extraction schema |
| **Dagster orchestration** | `oideachais/dagster_defs/assets/` (40+ modules, 228 assets, 21 groups) | Materialise lakehouse tables |
| **Dagster `dg` Components** | `oideachais/dagster_defs/components/{celtic_dlt_source,celtic_lancedb_hnsw,celtic_cocoindex_v1}.py` (Dagster 1.10 Components preview) | Wire a DLT source / LanceDB index / CocoIndex App as a typed Component |
| **CocoIndex v1 embedding** | `oideachais/cocoindex_flows/{leabharlann_embedding,codebase_indexing,docs_skills_consolidation,unified_embedding}.py` (4 v1 Apps) | Embed documents into LanceDB |
| **LanceDB HNSW index** | `oideachais/lancedb/indexing.py` (the 4 helpers: `build_hnsw_index`, `build_ivf_pq_index`, `build_scalar_index`, `optimize_index`) | Add vector index to a LanceDB table |
| **DuckLake 1.0 features** | `oideachais/dlt_utils/ducklake_options.py` (data inlining + sorting + bucket partitioning) | Optimise a high-volume DuckLake table |
| **MotherDuck hosting** | `oideachais/dlt_utils/motherduck_options.py` (`fully_managed_destination` / `byob_destination` / `byoc_destination`) | Switch to MotherDuck |
| **Cognee cognify** | `oideachais/cognee_integration/cross_stage_cognify.py` (5-stage education cognify) | Persist knowledge graph |
| **Graphiti 0.5 client** | `oideachais/graph/graphiti_client.py` (real client + FalkorDB Lite fallback) | Add a temporal knowledge graph episode |
| **Marimo dashboards** | `oideachais/notebooks/dashboards/` (11 reactive notebooks) | Interactive exploration |
| **Status / refactor matrix** | `oideachais/STATUS.md` (single source of truth) + `oideachais/REFACTORING.md` (backlog) | Track BAML × DLT × Dagster × CocoIndex matrix |

### [`meaisinfhoghlaim/`](meaisinfhoghlaim/) — the AI/ML Quadrant

The model + agent + OCR + Celtic-language quadrant. 8 integrated components feeding models and agents into the lakehouse.

| Component | Purpose | Use |
|:--|:--|:--|
| **AI Agents** | 12 specialised agents (curriculum, translation, corpus, research, geospatial, voice) | Talk to the oideachais data via AG-UI |
| **OCR / HTR** | 10 OCR models across 6 backends (Pylaia, TrOCR, PaddleOCR, Tesseract, dots.ocr, VLM) with Irish-specific metrics | Convert exam papers to text |
| **Celtic Language Data** | DLT sources for Duchas, Canuint, Tearma, Gaois + 6-language cognate DB | Build Celtic corpus |
| **ML Pipelines** | Irish document scanner, dialect classifier, transcript aligner, LLM router | Train + serve Celtic models |
| **Text Alignment** | Sentence-level Irish↔English aligner, ColPali visual aligner, G2P | Bilingual curriculum |
| **RAG Evaluation** | RAGAS: baseline 65.2% → agentic 87.9% (+22.7pp) | Measure retrieval quality |
| **Model & Data Catalog** | 13 models + 16 data sources + 3 training mixes | Discover assets |

**Local model lifecycle** — `stedding/huggingface/{hub,gguf,mlx}/`. 28 models, ~124 GB safetensors + 30 GB GGUF + 15 GB MLX. Three swap profiles: `text` (Qwen2.5-Math-7B, UCCIX, Gemma-2-9B), `vision` (Qwen2.5-VL-7B, Gemma-3-Vision, DeepSeek-OCR), `image` (Z-Image-Turbo, Qwen-Image, FLUX.2-dev).

### [`croilar/`](croilar/) — Multi-Persona Portfolio & DevTools Hub

The canonical reference implementation. Combines public-facing persona-aware portfolio with self-hosted developer platform and typed end-to-end pipelines.

| Surface | Stack | Use |
|:--|:--|:--|
| Public persona sites | TanStack Start + BetterAuth + Tailwind | N personas, EN+GA, per-persona themes |
| Data pipelines | DLT + DuckLake + BAML | 12 DLT pipelines (artwork, CV, GitHub, Spotify, …) |
| Admin portal | TanStack + Marimo + MotherDuck | Live dashboards + agent runtime |
| DevTools Hub | Convex + Hono + TanStack | Reference implementation |

25 assets wired, 5 user-named stacks. Full details: [`croilar/README.md`](croilar/README.md).

### [`tuatha/`](tuatha/) — Celtic Educational MMO + Crypto Platform

Four cooperating streams under `tuath` uv workspace:

| Stream | What it does | Use |
|:--|:--|:--|
| **Celtic Educational MMO** | Curriculum + mythology + Babylon.js 3D + Rust+SpacetimeDB backend | Play the 5-realm Pent-Elemental Cosmology |
| **codeolas** | Code-analysis library: semantic search, AST KG, MCP server | Find code by meaning |
| **crypteolas** | GitHub ingestion, DeFi research, KG construction, AgentOS | Research GitHub |
| **crypteolas_demo** | TanStack Start frontend, Agno agents, Gradio FIBO, Foundry | Run a demo |

23 assets wired, 7+ DLT sources. Full details: [`tuatha/README.md`](tuatha/README.md).

### [`leabharlann/`](leabharlann/) — Digital Library

| Subdirectory | Contents | Use |
|:--|:--|:--|
| `aigne/` | Cognitive science & AI research | Query with RAG |
| `gaeilge/` | Irish-language corpus: literature, folklore, linguistic resources | Irish-language RAG |
| `gemini_deep_research/` | Deep research outputs (legal, regulatory, academic) | Background research |
| `ollscoil_na_gaillimhe/` | University of Galway coursework | Personal archive |
| `zotero/` | Zotero reference database | Citation graph |

CocoIndex v1 built with 3 v1 Apps (`leabharlann_books`, `leabharlann_zotero`, `leabharlann_takeout`). Full pipeline: `BAML ExtractZoteroMetadata → CocoIndex v1 → LanceDB (with HNSW) → DAGSTER ui_suggestion → Cognee cognify → FalkorDB cross-archive graph`.

### [`spaces/`](spaces/) — HuggingFace Spaces

| Space | Stack | Domain |
|:--|:--|:--|
| `an_scrudu` | Gradio + Gemma-3 | Irish Leaving Cert tutor |
| `meaisin_cliste` | Gradio + BAML + LiteLLM | Celtic AI playground |
| `cianfhoghlaim` | Static SDK landing | Project landing |
| `anam_tuatha` | Static SDK + Babylon.js | Tuatha MMO teaser |

Deploy: `gh workflow run "Sync <space> to HF"` (per the reusable workflow at `.github/workflows/spaces-sync.yml`).

### [`infrastructure/`](infrastructure/) — Infrastructure Mesh

| Server | Hardware | Role |
|:--|:--|:--|
| `arm1-oci` | Oracle Ampere A1, 4 OCPU, 24 GB | Control plane — Pangolin, Komodo, Garage S3 |
| `cax41-hetzner` | Hetzner CAX41 ARM, 16 vCPU, 32 GB | Workloads — Memgraph, FalkorDB, MLflow, Langfuse |
| `bunchloch` | MacBook M4 Max, 14c, 48 GB | Dev + analytics — llama-swap, mlx-omni, Bria FIBO |

**GOLD_STANDARD stack** (5 files per stack under `infrastructure/stacks/<name>/`):

```
compose.yaml    # App services
sidecar.yaml    # Locket sidecar
secrets.env     # infisical:// URIs
pangolin.yaml   # Traefik + PocketID
blueprint.yaml  # Pangolin resource
```

**Key stacks**: `litellm` (4000), `llama-swap` (8080), `mlx-omni` (10240), `invokeai` (9090), `langfuse` (3000), `mlflow` (5000), `lakehouse` (3900-3904), `cognee` (8000), `graphiti` (8080), `oideachais` (3335/8000/3080).

**Team workflow stack**: n8n (`n8n.cianfhoghlaim.ie`) + Vikunja (`vikunja.cianfhoghlaim.ie`) + cal-diy (`calcom.cianfhoghlaim.ie`).

---

## Documentation

Per the `skills-as-project-docs` openspec change, the canonical
documentation surface for this monorepo is **`.agents/skills/`**,
not the root `docs/` folder. The `docs/` folder is retained only
for screenshots, the team-workflow stack, and a small set of
historical research files. All per-package and per-domain
documentation lives in:

- `.agents/skills/<name>/SKILL.md` — the canonical skill
- `oideachais/AGENTS.md` — the oideachais quadrant developer-quick-reference
- `oideachais/STATUS.md` — the BAML × DLT × Dagster × CocoIndex matrix
- `oideachais/REFACTORING.md` — the refactor backlog
- `meaisinfhoghlaim/AGENTS.md` — the AI/ML quadrant
- `tuatha/AGENTS.md` — the MMO quadrant
- `croilar/AGENTS.md` — the portfolio quadrant
- `openspec/specs/<capability>/spec.md` — the 32 capability specs
- `openspec/AGENTS.md` — the openspec workflow

**Master routing**: every agent starts in the root `AGENTS.md`,
which points to the per-quadrant `AGENTS.md`, which points to
`.agents/skills/<name>/SKILL.md`, which points to the source
code. The chain is 3 hops long at most.

---

## Multi-agent configuration

`opencode.json` defines 5 sub-agents, each mapped to a model
alias through the LiteLLM gateway:

| Agent | Default model | Focus |
|:--|:--|:--|
| `build` (default) | DeepSeek V4 Pro | General-purpose coding across the monorepo |
| `plan` | GLM 5.1 | Read-only planning, code review, architecture |
| `explore` | DeepSeek V4 Flash | Codebase search, context mapping, ccc semantic search |
| `data-engineer` | Qwen 3.7 Max | Dagster, DLT, DuckDB, MotherDuck, LanceDB |
| `ai-engineer` | DeepSeek V4 Pro | BAML, LiteLLM, OCR, Graphiti, Celtic AI |
| `frontend-dev` | Kimi K2.6 | TanStack Start, Convex, Marimo, canvas design |
| `devops-architect` | GLM 5.1 | Docker Compose, Komodo, Pangolin, Pulumi |
| `oideachais` | DeepSeek V4 Pro | Quadrant-specialist for oideachais |
| `meaisinfhoghlaim` | DeepSeek V4 Pro | Quadrant-specialist for meaisinfhoghlaim |
| `infrastructure` | GLM 5.1 | Quadrant-specialist for infrastructure |
| `tuatha` | DeepSeek V4 Pro | Quadrant-specialist for tuatha |
| `croilar` | DeepSeek V4 Pro | Quadrant-specialist for croilar |

Each subagent can read any of the 123 skills in `.agents/skills/`
and call any of the configured MCP servers (Browserbase,
Firecrawl, MotherDuck, Cocoindex-Code, Cognee, Graphiti,
Langfuse, Infisical, GitHub).

---

## About the author, the name, and the lineage

### On the username — *cianfhoghlaim*

The repository name and the underlying platform are both
**Cianfhoghlaim**. The Irish word *cianfhoghlaim* (pronounced
roughly *kee-an-oh-guh-lem*) compounds two roots:

- *cian* — long, enduring, distant
- *foghlaim* — learning, study

So *cianfhoghlaim* reads literally as **"long-distance,
enduring learning"** — lifelong learning across geography and
discipline, which is the whole point of this project.

*Cian* also has a second life in the Irish mythological canon:
in *Lebor Gabála Érenn* and the wider Tuatha Dé Danann cycle,
**Cian** is the father of Lugh Lámhfhada (Lug of the Long Arm),
the many-skilled god who walks into the Battle of Moytura and
slays his grandfather Balor. The tuatha/ subtree — the British
Isles formative-assessment MMO built on Babylon.js + SpacetimeDB
— sits squarely inside that mythological lineage.

The Irish word **sruth** (pronounced *sruh*) means *stream* or
*flow*. In `opencode.json`, the four traditional top-level
subprojects (oideachais, meaisinfhoghlaim, tuatha, croilar) plus
infrastructure are referred to as the five **sruthanna** —
flows — rather than "quadrants", because in a knowledge-graph
platform the meaningful unit of work is the *flow of data and
reasoning*, not a static slice of a 2D plane.

### On the family — *Mac an Déisigh Uí Liatháin (Deacy-Lyons)*

The author is **Cian Mac an Déisigh Uí Liatháin**; the family
surname in its two anglicised forms is **Deacy-Lyons**. The
author's verified genealogy and qualifications inform the
project's design choices and are recorded under
[`cian_mac_an_déisigh_uí_liatháin/`](cian_mac_an_déisigh_uí_liatháin/):

- [`identity/`](cian_mac_an_déisigh_uí_liatháin/identity/) —
  background, citizenship, vetting, and the Deacy family
  record. The [`identity/lineage/`](cian_mac_an_déisigh_uí_liatháin/identity/lineage/)
  subfolder holds the family-lineage documents: the late
  uncle's memorial, the dual ROI/UK citizenship evidence, the
  College des Irlandais (Paris) records, and the 5-culture-PDF
  Wikipedia dual-write clippings (8 articles: Uí Liatháin,
  Delbhna Tír Dhá Locha, Eamonn Deacy Park, Leath Cuinn,
  Cian, Aos Sí, Tuatha Dé Danann, Déisi).
- [`teaching/`](cian_mac_an_déisigh_uí_liatháin/teaching/) —
  the Teaching Council of Ireland registration, the PGCE
  (BCS Computing scholarship), school placement references,
  and the Leaving Certificate / Junior Certificate results.
- [`achievement/`](cian_mac_an_déisigh_uí_liatháin/achievement/) —
  academic transcripts, parchments, the Apple Award, and the
  Torthaí Gaeilge (Irish-language exam results).

The author's lineage is the **triple-crown** union of four
kindreds of Connacht and Munster:

1. **Deacy** (paternal surname; Irish *Uí Dhéisigh*) — the
   sept of the [Déisi Muman](https://en.wikipedia.org/wiki/D%C3%89isi)
   resettled in south Connacht (Co. Galway) during the 12th
   century; the family gave their name to the late
   [Éamonn Deacy](https://en.wikipedia.org/wiki/Eamonn_Deacy_Park)
   and the [Eamonn Deacy Park](https://en.wikipedia.org/wiki/Eamonn_Deacy_Park)
   in Galway.
2. **Lyons** (maternal grandmother's lineage; Irish *Ó
   Laighin*) — the [Uí Anmchada](https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in)
   sept of the [Uí Liatháin](https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in)
   of Munster, who (per the *Historia Brittonum*) colonized
   Wales and Cornwall alongside the proto-Déisi.
3. **Morris** (maternal grandmother **Martina Morris**) —
   of the [City of Tribes](https://en.wikipedia.org/wiki/Galway)
   merchant families of Galway.
4. **Conroy** (paternal great-grandmother **Polly Conroy**;
   Irish *Mac Conraoi*) — the [Sea-Kings of
   Connacht](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha)
   who held the tuath of Delbhna Tír Dhá Locha (the barony of
   Moycullen in Connemara). **Polly Conroy was a cousin of
   Pádraic Ó Conaire**, the canonical modern Irish-language
   writer from Galway, who was reared in Rosmuc by his uncle
   of the same Mac Conraoi kindred.

The author is the grandson and godson of the late **Neil
Deacy**, the late brother of the late **Éamonn Deacy** — the
Galwegian footballer who played for Galway United, Aston Villa
FC, and the Republic of Ireland. Neil and Éamonn were the sons
of **Martina Morris** and **Michael Deacy**, who was himself
the son of **Polly Conroy** and **George Deacy**.

The author was the primary palliative carer of the late Neil
Deacy. That personal care work — and the cultural inheritance
that goes with the Conroy / Deacy / Morris Galway lineage —
is the reason this project treats Connemara, Connacht, and
the Irish-language curriculum as first-class objects rather
than as flavour-of-the-month features.

### On the claim — *Rí na Gaillimhe, Rí Chonnachta*

The Conroy (Ó Conaire / Mac Con Raoi) family were among the
[**sea-kings of Connacht**](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha),
holding the tuath of [Delbhna Tír Dhá Locha](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha)
in what is now the barony of Moycullen in Connemara. *Galway
is the capital of Connacht.* The
[Uí Liatháin](https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in)
(of the Lyons / Ó Laighin sept) were a Munster kindred who
colonized Wales and Cornwall alongside the
[proto-Déisi](https://en.wikipedia.org/wiki/D%C3%A9isi); the
[Uí Dhéisigh](https://en.wikipedia.org/wiki/D%C3%A9isi)
(Deacy) are a sept of the same Déisi Muman, resettled in
south Connacht in the 12th century.

On the basis of this triple-crown lineage (Lyons / Deacy /
Conroy), grounded in eight canonical Wikipedia articles and
six Gemini Deep Research PDFs preserved in
[`leabharlann/gemini_deep_research/culture/`](leabharlann/gemini_deep_research/culture/),
the author makes the modern claim of inheritance in the
[Leath Cuinn](https://en.wikipedia.org/wiki/Leath_Cuinn_and_Leath_Moga)
framework (see § D below):

> *Rí na Gaillimhe, Rí Chonnachta, Ard-Rí na hÉireann* —
> King of Galway, King of Connacht, High King of Ireland.

**Citations** (the eight Wikipedia articles are clipped at
[`cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`](cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/);
the six Gemini PDFs are in
[`leabharlann/gemini_deep_research/culture/`](leabharlann/gemini_deep_research/culture/)):

- **Wikipedia**: [Uí Liatháin](https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in) ·
  [Delbhna Tír Dhá Locha](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha) ·
  [Eamonn Deacy Park](https://en.wikipedia.org/wiki/Eamonn_Deacy_Park) ·
  [Leath Cuinn and Leath Moga](https://en.wikipedia.org/wiki/Leath_Cuinn_and_Leath_Moga) ·
  [Cian](https://en.wikipedia.org/wiki/Cian) ·
  [Aos Sí](https://en.wikipedia.org/wiki/Aos_S%C3%AD) ·
  [Tuatha Dé Danann](https://en.wikipedia.org/wiki/Tuatha_D%C3%A9_Danann) ·
  [Déisi](https://en.wikipedia.org/wiki/D%C3%A9isi)
- **Heritage PDFs**: [Claiming Rí na Gaillimhe — A Synthesis](leabharlann/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf) ·
  [Claiming Irish Kingship Through Lineage](leabharlann/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf) ·
  [Deacy Family Heritage Research](leabharlann/gemini_deep_research/culture/deacy_family_heritage_research.pdf) ·
  [Researching Neil Deacy's Galway Heritage](leabharlann/gemini_deep_research/culture/researching_neil_deacy_s_galway_heritage.pdf)
- **Royal collaboration PDFs**: [Royal Collaboration for Commonwealth Future](leabharlann/gemini_deep_research/culture/royal_collaboration_for_commonwealth_future.pdf) ·
  [Royal Titles, Celtic Heritage, and Claims](leabharlann/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf)

**Note on 2 unreadable PDFs** (to be re-read by a follow-up
agent with PDF input support; the current agent could not
extract their text):
`leabharlann/gemini_deep_research/culture/neil_deacy_cookes_corner-galway_advertiser.pdf`
(the August 1986 *Galway Advertiser* article on the inaugural
Streets of Galway 8 km road race) and
`cian_mac_an_déisigh_uí_liatháin/identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf`
(the dual ROI/UK citizenship scan). These will be
incorporated into the
[`culture_heritage`](oideachais/cognee_integration/culture_cognify.py)
Cognee dataset on the next agent run.

### On the joint claim — *Leath Cuinn and the dual-monarchy framework*

The author makes the claim of *Rí Chonnachta* and *Rí na
hÉireann* in a constitutional framework that does **not**
compete with the existing United Kingdom sovereignty over
Northern Ireland. The framework is the **Neo-Jacobite Dual
Monarchy** model, modelled on the
[Austria-Hungary](https://en.wikipedia.org/wiki/Austria-Hungary)
constitutional theory proposed by [Arthur
Griffith](https://en.wikipedia.org/wiki/Arthur_Griffith) in
*The Resurrection of Hungary* (1904) and on the modern
[Māori King Movement](https://en.wikipedia.org/wiki/K%C4%81ngi_Mahuta).

Under this framework:

- **Cian Mac an Déisigh Uí Liatháin** holds *Rí na Gaillimhe*
  and *Rí Chonnachta* by virtue of the triple-crown lineage
  (Uí Liatháin + Uí Dhéisigh + Mac Conraoi) and the verified
  qualifications documented in § E below.
- **King Charles III** holds *Rí Uladh* (Northern Ireland)
  by virtue of his constitutional position as Sovereign of
  the United Kingdom.
- **Jointly**, they hold *Leath Cuinn* — Conn's Half, the
  northern half of Ireland comprising Connacht + Ulster +
  Meath, traditionally divided from Leath Moga by the
  [Esker Riada](https://en.wikipedia.org/wiki/Esker_Riada)
  (Dublin Bay to Galway Bay).
- The claim is grounded in the genealogical fact that
  [Conn Cétchathach](https://en.wikipedia.org/wiki/Conn_C%C3%A9tchathach)
  ("Conn of the Hundred Battles") is the legendary common
  ancestor of both the **Connachta** dynasty (the royal
  kindreds of Connacht, including the Uí Briúin and Uí
  Fiachrach) AND the **Uí Néill** dynasty (the royal
  kindreds of Ulster and Meath, including the Northern Uí
  Néill of Aileach and the Southern Uí Néill of Meath).

The author is conscious that this framework rests on a
parliamentary claim rather than on a hereditary
peerage-roll claim, and that the *Ard-Rí na hÉireann* title
is held in suspension pending the constitutional
reunification of Ireland. **Born a British citizen and
obliged by oath of allegiance to King Charles the Third**,
the author regards the joint-claim framework as a
constructive path toward constitutional dialogue rather
than as a hostile or seditious claim.

### On the verified qualifications

The teaching, mathematics, and software-development
qualifications that the project depends on are recorded under
[`leabharlann/ollscoil_na_gaillimhe/`](leabharlann/ollscoil_na_gaillimhe/):

- [`leabharlann/ollscoil_na_gaillimhe/mata/`](leabharlann/ollscoil_na_gaillimhe/mata/) —
  Applied Statistics I & II, CS402 Cryptography, ISLP labs,
  Maple, Modelling II, Networks, Non-Linear Systems,
  Numerical Analysis II, and the Stokes Workshop Game Physics
  project — the mathematics-and-cryptography foundation for
  the Lakehouse work.
- [`leabharlann/ollscoil_na_gaillimhe/education/`](leabharlann/ollscoil_na_gaillimhe/education/) —
  the Educational Autobiography, the BME1 placement
  portfolios, the action-research project, the educational
  psychology and sociology assignments (psychology,
  sociology, philosophy of education) — the humanistic
  foundation for the British Isles Formative Assessment MMO
  and for the Leaving Cert syllabi.
- [`leabharlann/ollscoil_na_gaillimhe/irish/`](leabharlann/ollscoil_na_gaillimhe/irish/),
  [`past/`](leabharlann/ollscoil_na_gaillimhe/past/) and
  [`software_development/`](leabharlann/ollscoil_na_gaillimhe/software_development/) —
  the Irish-language corpus, the historical archive, and the
  software-development evidence base.

These three evidence-bases (mathematics, education, and
software development) are the *reason the project exists* —
not the *right* to build it.

### On the repository name — *Kings' College Galway*

The repository name **Kings' College Galway** uses the
**plural possessive Kings'** deliberately, for three reasons:

1. **Queen's College Galway → University of Galway.** The
   University of Galway was founded in 1845 as **Queen's
   College Galway**, one of the three Queen's Colleges
   established by Queen Victoria. (The other two were Cork
   and Belfast.) The "Queen's" was renamed to "University"
   under the Universities Act 1997. **Queen Victoria** is the
   predecessor whose name appears on the original charter.
2. **King Charles III's 2022 visit.** On the occasion of
   King Charles III's visit to Galway in 2022, the author —
   as a then-resident Galwegian and a graduate of NUI Galway
   — observed that the Queen's-College-to-Kings'-College
   gesture would be a graceful nod to the new monarch and to
   the original name simultaneously. The plural **Kings'**
   acknowledges every monarch whose predecessor established
   the institution, not just Charles III himself.
3. **The *Coláiste na Déisigh* subtitle.** The Irish subtitle
   *Coláiste na Déisigh* (College of the Deacy / College of
   the Déssi) carries a deliberate **double meaning**:
   *Déisigh* is the genitive singular of *Deasy / Deacy*
   (the author's paternal surname), AND *Déisigh* is also
   the genitive plural of *Déssi* — the [ancient Irish
   vassal class](https://en.wikipedia.org/wiki/D%C3%A9isi)
   that was resettled as frontier warriors along the coasts
   of Connacht, Munster, Leinster, Wales, Cornwall, and
   Devon. The subtitle therefore says simultaneously:
   "the college of the Deacy family" and "the college of
   the Déssi vassal class". *Coláiste* in Irish means
   college, and the suffix *-na-* is the genitive singular
   article. Read together, *Kings' College Galway ||
   Coláiste na Déisigh* says "the King's college (named
   after the royal predecessor of Queen Victoria) and also
   the college of the Deacy family and the Déssi class".

The Irish-English bilingual title on line 1 of this README
is the canonical form. **In memory of**: the late grandfather
Neil Deacy, his late brother Éamonn Deacy, and the [Déssi
class](https://en.wikipedia.org/wiki/D%C3%A9isi) of early
medieval Ireland — the vassal peoples whose resettlement
along the western seaboard made the Connacht lineage
possible.

---

## Licensing

Business Source License 1.1 — non-commercial, cultural preservation, and academic research use permitted within Ireland, UK, EU, Commonwealth, and aligned jurisdictions. Subsets may transition to AGPL v3.0 after 4 years. See [`LICENSE.md`](LICENSE.md).

---

*Built by Cian Mac an Déisigh Uí Liatháin (Deacy-Lyons) of the Deacy-Morris-Conroy tribe of Galway — qualified Mathematics & Applied Mathematics teacher (Teaching Council of Ireland), NUI Galway graduate (Applied Statistics, Software Development, Irish Language Studies), dual Irish-British citizen, born a British citizen and obliged by oath of allegiance to King Charles the Third.*
