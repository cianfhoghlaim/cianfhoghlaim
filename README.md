# Kings' College Galway || Coláiste na Déisigh

> *A unified Celtic education platform, infrastructure mesh, and AI research laboratory by Cian Mac an Déisigh Uí Liatháin.*

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

## Licensing

Business Source License 1.1 — non-commercial, cultural preservation, and academic research use permitted within Ireland, UK, EU, Commonwealth, and aligned jurisdictions. Transitions to AGPL v3.0 after 4 years. See [`LICENSE.md`](LICENSE.md).

---

*Built by Cian Mac an Déisigh Uí Liatháin — qualified Mathematics & Applied Mathematics teacher (Teaching Council of Ireland), NUI Galway graduate (Applied Statistics, Software Development, Irish Language Studies), dual Irish-British citizen.*
