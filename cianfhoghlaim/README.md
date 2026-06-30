# cianfhoghlaim

> **Celtic education + multi-nation + multi-language data platform.**
> A single Python package (`cianfhoghlaim`) that fuses 8 NCCA Leaving
> Certificate subject pipelines, a 12-agent fleet (Agno + ADK +
> Pipecat + CopilotKit + Letta), the Cianfhoghlaim Educational MMO
> (`web/apps/cianfhoghlaim-mmo/`, 2D TanStack Start), and the Croílár
> multi-persona portfolio. Served from a single Dagster code-location
> (5-Layer Component architecture) and orchestrated by **3 sibling
> repos**: [`bonneagar`](https://github.com/cianfhoghlaim/bonneagar)
> (sovereign infrastructure), [`leabharlann`](https://github.com/cianfhoghlaim/leabharlann)
> (digital library corpus), and this monorepo (application).

---

## TL;DR

A working, deployable, self-hosted Celtic education platform:

- **8 NCCA subjects** (mathematics / applied_mathematics / chemistry /
  geography / history / english / gaeilge / computer_science) each
  with a per-subject 6-asset Dagster pipeline (syllabus → BAML
  extraction → quest pack → CocoIndex embedding → Cognee cognify →
  marimo dashboard) backed by **8 NCCA-aligned BAML quest packs**
  (`baml/education/subjects/qpack_*.baml`) and **8 ADK subject
  specialist agents** plus a root orchestrator.
- **A 2D TanStack Start educational MMO** (port 3080) that turns
  the per-subject quest packs into bilingual (EN + GA) in-game
  formative-assessment questions, with a hybrid `SkillTreeBadge`
  credential anchored daily on Base L2.
- **A 5-stage Dagster Component spine** (`dagster/defs/1_ingestion/
  .../5_agent_ops/`) wrapping DLT → BAML → CocoIndex → Cognee →
  marimo + 12-agent orchestration. Local dev: `mise run dagster:oideachais`.
- **A shared centralised data plane** (`bonneagar/stacks/lakehouse/`)
  for Garage S3 + Postgres + ClickHouse + Redis, consumed by
  langfuse / litellm / mlflow as pure app tiers.
- **A 116–217 doc research corpus** in
  [`leabharlann`](https://github.com/cianfhoghlaim/leabharlann),
  consumed into the pipeline via DLT filesystem sources.

The most recent architectural shifts (in commit-recent order):

1. **2026-07-30** — centralise-data-plane: langfuse / litellm / mlflow
   now share lakehouse PG (12 DBs), Garage (7 buckets), ClickHouse, Redis.
2. **2026-07-30** — `retro-educational-game-asset-pipeline-v1`: a new
   `retro-game-design-catalogue` capability spec + a 5th pipeline
   in `celtic-asset-generation` (`retro_design_patterns/`) feeding
   `s3://cianfhoghlaim-asset-v2/3d/` for the deferred MMO v2 Babylon.js
   client.
3. **2026-07-30** — 7-stack ops rewrite: `lakehouse / langfuse /
   litellm / llama-swap / mlflow / falkordb / graphiti` all migrated
   to the 6-file GOLD_STANDARD + the new dependency order
   (foundation → observability → memory → surfaces).
4. **2026-06-30** — 5-Layer Dagster Component architecture collapsed
   the 619-line legacy `definitions.py` to ~30 lines + a layered
   `dagster/defs/` tree (1_ingestion / 2_materials / 3_model_lifecycle
   / 4_asset_generation / 5_agent_ops).
5. **2026-06-28** — `sruth → cianfhoghlaim` v4 consolidation merged
   5 quadrants (`oideachais`, `meaisinfhoghlaim`, `tuatha`, `croilar`,
   `crypteolas`) into a single layered Python package.

---

## Architecture at a glance

```
           ┌─────────────────────────────────────────────────────────┐
           │  cianfhoghlaim  (this monorepo)                         │
           │  the application package + web apps + dagster + agents │
           └────────────────┬────────────────────────────────────────┘
                            │
        ┌───────────────────┼────────────────────┐
        │                                         │
        ▼                                         ▼
┌────────────────────────┐              ┌────────────────────────────────┐
│  bonneagar             │              │  leabharlann                   │
│  (sovereign GitOps)    │              │  (digital library corpus)     │
│  90+ Docker Compose    │              │  6 domains of PDFs + research  │
│  stacks; Locket-       │              │  consumed via DLT              │
│  injected secrets;     │              │  filesystem_sources.          │
│  Pangolin + WireGuard  │              │                                │
│  + Pocket ID + Komodo; │              │                                │
│  arm1-oci + bunchloch. │              │                                │
└────────────────────────┘              └────────────────────────────────┘
```

The **3 sibling repos** are independent Python / Pulumi / GitOps
projects, but they share a single mental model:

| Repo | Contains | Use it for |
|---|---|---|
| **[cianfhoghlaim](https://github.com/cianfhoghlaim/cianfhoghlaim)** | Python package + Dagster code-locations + 8 web apps + 12-agent fleet + 116-doc PDF corpus (subset) | Application code, agent prompts, BAML contracts, per-subject pipelines, the educational MMO |
| **[bonneagar](https://github.com/cianfhoghlaim/bonneagar)** | 90+ Compose stacks + Komodo procedures + Pangolin routes + Ansible + Pulumi + Locket sidecar pattern | Infrastructure; "where does langfuse.run actually live?" |
| **[leabharlann](https://github.com/cianfhoghlaim/leabharlann)** | Personal digital library: 6 domains (gaeilge / aigne / mata / ollscoil_na_gaillimhe / zotero / gemini_deep_research) of curated PDFs | Material corpus; "where do the actual syllabus documents live?" |

---

## Layout

The repository root. The 5-stage Dagster Component tree (in
`dagster/defs/`) is the architectural spine; every other top-level
directory hangs off it.

```
cianfhoghlaim/
├── baml/                       # BAML contracts (3-cluster taxonomy)
│   ├── education/              # NCCA subjects + stages + cross-nation + university
│   │   ├── subjects/           # 8 qpack_<subject>.baml (one per NCCA subject)
│   │   ├── stages/             # aistear / primary / junior_cycle / senior_cycle / tertiary
│   │   ├── cross_nation/
│   │   ├── pdfs/                # 116 NCCA syllabus + past-paper + marking-scheme PDFs
│   │   ├── university/
│   │   ├── statistics/
│   │   └── _shared/             # 5 curriculum-extraction support files
│   ├── celtic/                 # gaois / grammar / morphology / sources / curriculum
│   ├── processing/             # 23 .baml files for OCR / image-gen / extraction / generation
│   ├── clients.baml            # canonical LiteLLM + OpenCode Go + Llama-Swap clients
│   ├── clients_llama_swap.baml
│   ├── shared/                 # the platform-wide BAML shared helpers
│   └── baml.toml
│
├── cocoindex/                 # 12 v1 CocoIndex Apps + 4 schema indexes
│   ├── _lifespan.py             # canonical shared lifespan (per
│   │                          #    REFACTORING.md item 12)
│   ├── <subject>_embedding.py  # 8 NCCA subject embeddings (maths/chem/...)
│   ├── agent_registry.py / agents_md.py / apple_photos_chunks.py / apple_photos_metadata.py
│   ├── cocoindex_v1_conformance.py    # 4-rule R1-R4 conformance contract
│   └── language / culture_heritage / cv / artwork / codebase / filesystem / api / storage / docs_skills / cross_archive...
│
├── dlt/                       # DLT ingestion (per 6 domains)
│   ├── british_isles/          # 8 nations × 4 domains × 3-5 stages (Plan 1: ie ACTIVE)
│   ├── filesystem/             # leabharlann filesystem_sources
│   ├── language/               # canuint / duchas / tearma / gaeilge
│   ├── api_sources/            # github / linkedin / researchgate
│   ├── portfolio/              # artwork / cv / labels / teaching
│   ├── official_media/         # instagram + BAML resolver
│   └── law / medicine / site_analysis / statistics   (cross-nation)
│
├── dagster/                   # Single Dagster code-location (5-Layer Component)
│   ├── definitions.py          # 30-line bootstrap → dg.load_from_defs_folder()
│   ├── defs/                   # 5-Layer Component architecture
│   │   ├── 1_ingestion/        # CelticIngestionComponent (DLT sources)
│   │   ├── 2_materials/        # CelticMaterialsComponent + DbtProjectComponent (BAML extraction, OCR, embeddings)
│   │   ├── 3_model_lifecycle/  # CelticModelLifecycleComponent (12 v1 CocoIndex Apps)
│   │   ├── 4_asset_generation/ # CelticAssetGenerationComponent (5th pipeline: retro_design_patterns/)
│   │   ├── 5_agent_ops/        # CelticAgentOpsComponent (12-agent fleet × 5 assets each)
│   │   └── _shared/            # Component post-processing helpers
│   ├── components/             # The 5 KCG-specific Components (subclasses)
│   ├── sensors/                # directory-watch sensors + LLM/asset-staleness triggers
│   ├── schedules.py            # cron triggers + auto-materialization
│   └── resources/              # 19 ConfigurableResources consolidated
│
├── agents/                    # AI agent fleet
│   ├── adk/                    # 21 agent files: 8 NCCA subject + aux specialists (voice/vision/research/translation/mythology/geospatial/email_triage/...) + root_agent + enhanced_orchestrator
│   ├── agno/                   # legacy education_team.py (pre-ADK)
│   ├── tuatha/                 # Babylon.js + SpacetimeDB + crypteolas (the MMO v2 backend)
│   ├── api/                    # web API agents (deprecated path)
│   ├── tools/                  # shared agent tools (file_search, web_search, code_execution...)
│   ├── letta_client.py / pydantic_gateway.py / baml_integration.py / translation.py / vision.py / image_generation.py
│   ├── hitl_agent.py / hitl_state.py
│   └── routing_keywords.py     # 8-bucket keyword router for the root_agent
│
├── web/                        # 8 TanStack Start / TanStack apps + 6 shared packages + 1 hono-api
│   ├── apps/
│   │   ├── cianfhoghlaim-mmo/          # the 2D educational MMO (port 3080)
│   │   ├── oideachais-web/            # public-facing oideachais portal
│   │   ├── _oideachais_dashboard/     # internal dashboard (newly separated)
│   │   ├── _oideachais_apps/          # the consolidated oideachais web surface
│   │   ├── tuatha-ui/                 # Tuatha MMO UI
│   │   ├── tuatha-demo/              # demo front-end
│   │   ├── croilar-web/              # Croílár portfolio
│   │   ├── croilar-portal/           # Croílár portal
│   │   └── game_showcase/            # showcase + landing
│   ├── _croilar_shared/               # Croílár cross-app shared components
│   ├── packages/               # 6 shared packages (analytics/auth/config/db/i18n/ui)
│   └── hono-api/               # the canonical Hono backend
│
├── observability/             # Langfuse + MLflow + Logfire shim (consolidated
│                              #    by the cleanup-and-boot-stacks change)
├── storage/                   # FalkorDB + Cognee + Graphiti + LanceDB + Letta + research.py + letta_memory.py
├── notebooks/                 # 8 marimo notebooks (`leaving_cert/<subject>.py`) + dashboards/ + meaisinfhoghlaim/ + speedrun/
├── meaisinfhoghlaim/          # OCR (24 models) + alignment + document_factory + training + federated + evaluation + quality + geospatial + backends + datasets + config + ci
├── tuatha/                     # Babylon.js + SpacetimeDB + crypteolas (legacy Tuatha per the educational-mmo v1 redirect)
├── cian_mac_an_déisigh_uí_liatháin/   # author bio + education artefacts (NOT part of the v4 platform)
├── scripts/                    # CLI entry-points: ingest, extract, embed, cognify, expose, build, ccc reindex
├── tests/                      # pytest (unit + integration + 6 per-subject suites)
├── docs/                       # auto-published doc portal (infrastructure-stacks, ops, ui-inspiration)
├── spaces/                     # embedded sub-repos (data-engineering/, huggingface demos) — separate git repos
├── leaving_certificate/        # 116 raw NCCA PDFs across 8 subjects × {en, ga}
├── pyproject.toml             # single Python package boundary (`[tool.uv.sources]`)
├── README.md                   # this file
└── AGENTS.md                  # AI agent dispatch contract (read this first)
```

> **Note**: `core/` (the v3 proposal's 16-stack-package home) was **never
> created** — the v4 consolidation landed directly at the top level. If
> you're reading older openspec proposals that reference `core/dlt/` etc.,
> those are describing the planned shape that the v4 commit chose not
> to deliver. See
> `openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/`
> for the full decision rationale.

---

## The 8 NCCA subjects — per-subject pipeline

Every NCCA subject gets the same 6-asset Dagster pattern:

| # | Subject (EN) | Subject (GA) | Realm | Levels | BAML quest pack | Dagster asset folder | Specialist agent |
|:--|:--|:--|:--|:--|:--|:--|:--|
| 1 | Mathematics | Matamaitic | MATH | FL / OL / HL | `qpack_mathematics.baml` | `dagster/defs/.../mathematics/` | `math_agent` |
| 2 | Applied Mathematics | Matamaitic Fheidhmeach | APPM | HL only | `qpack_applied_mathematics.baml` | `defs/.../appm/` | `appm_agent` |
| 3 | Chemistry | Ceimic | CHEM | OL / HL | `qpack_chemistry.baml` | `defs/.../chemistry/` | `chem_agent` |
| 4 | Geography | Tíreolaíocht | GEOG | OL / HL | `qpack_geography.baml` | `defs/.../geography/` | `geog_agent` |
| 5 | History | Stair | HIST | OL / HL | `qpack_history.baml` | `defs/.../history/` | `hist_agent` |
| 6 | English | Béarla | ENGL | OL / HL | `qpack_english.baml` | `defs/.../english/` | `engl_agent` |
| 7 | Gaeilge | Gaeilge | GAEL | FL / OL / HL | `qpack_gaeilge.baml` | `defs/.../gaeilge/` | `gael_agent` |
| 8 | Computer Science | Ríomheolaíocht | COMP | OL / HL | `qpack_computer_science.baml` | `defs/.../computer_science/` | `comp_agent` |

Each subject is a 6-asset Dagster pattern (`dagster/defs/2_materials/`)
plus a per-language BAML contract (`baml/education/subjects/`) plus
a per-language CocoIndex embedding App (`cocoindex/<subject>_embedding.py`)
plus a marimo notebook (`notebooks/leaving_cert/<subject>.py`)
plus an ADK `LlmAgent` (`agents/adk/<subject>_agent.py`).

---

## The 5-stage Dagster `defs/` spine

The architectural backbone of every pipeline. Each layer is a
Dagster `Component` (`Celtic<Role>Component`):

| Layer | Folder | What lives there | Component |
|:--|:--|:--|:--|
| 1. **Ingestion** | `dagster/defs/1_ingestion/` | DLT sources: 8 nations × 4 domains DLT (curriculum, law, medicine, site_analysis, filesystem) | `CelticIngestionComponent` |
| 2. **Materials** | `dagster/defs/2_materials/` | BAML extraction (`baml_extraction/`), DBT bridge, embedding pivot, OCR comparison, **PDF processing** (133 leaving-cert PDFs × 5 converters × 24 OCR models) | `CelticMaterialsComponent` + `DbtProjectComponent` |
| 3. **Model Lifecycle** | `dagster/defs/3_model_lifecycle/` | 12 v1 CocoIndex Apps (`cocoindex_v1/`), 5-stage cognify pipeline (`cognify/`), cross-archive edges (`cross_archive/`) | `CelticModelLifecycleComponent` |
| 4. **Asset Generation** | `dagster/defs/4_asset_generation/` | 5 successive independent pipelines: official_documents / subject_assets / language_assets / exporters / **retro_design_patterns/** (the new 2026-07-30 addition). Plus marimo dashboards, TanStack pages, orpc routes | `CelticAssetGenerationComponent` |
| 5. **Agent Ops** | `dagster/defs/5_agent_ops/` | 8 NCCA subject ADK agents + agno + custom — each wired to LiteLLM + Letta + BAML + LanceDB | `CelticAgentOpsComponent` |

The Dagster UI at `http://localhost:3000` loads the entire tree via
`dg load_from_defs_folder()` (per the 2026-06-30
`dagster-ground-up-rewrite-5-layer-component-architecture` change
that collapsed the 619-line legacy `definitions.py` into a 30-line
bootstrap).

---

## The 12-agent fleet

A mixed-framework fleet (Agno + ADK + Pipecat + CopilotKit + Letta)
keyed off the 8 NCCA subjects + 3 cross-cutting specialists + 1 root
orchestrator:

- **8 NCCA subject agents** in `agents/adk/<subject>_agent.py`
  (math / appm / chem / geog / hist / engl / gael / comp) — each
  seeded with its `qpack_<subject>.baml` and per-subject LanceDB
  table.
- **1 root orchestrator** (`agents/adk/root_agent.py`) implementing
  the 8-bucket `ROUTING_KEYWORDS` map from
  `agents/routing_keywords.py` and dispatching to the right subject
  specialist.
- **3 cross-cutting specialists** for queries that span subjects:
  - `corpus_agent.py` / `mcp_curriculum_agent.py` — corpus-wide search
    across the leabharlann PDF cache
  - `curriculum_comparison_agent.py` — cross-subject comparisons
    (e.g., how a Statistics LO in Mathematics differs from a
    Statistics LO in Geography)
  - `research_assistant_agent.py` / `education_research_agent.py` —
    pedagogical research queries
- **Domain auxiliaries** (voice_agent, vision_agent, translation_agent,
  geospatial_agent, mythology_narrator_agent, bunchloch_research_agent,
  email_triage_agent, statistics_agent, quest_guide_agent, agui_curriculum_agent,
  celtic_tutor_agent) — frame-specialised helpers that any subject
  agent can delegate to.
- **1 Tuatha root** (`agents/adk/tuatha_root_agent.py` + `tuatha_config.py`)
  for the MMO game-side routes (in-game NPC dialogue, quest
  generation).

Default model is `litellm/anthropic/claude-sonnet-4` via the
centralised LiteLLM gateway (`bonneagar/stacks/litellm/`).

---

## Quick commands

```bash
# Verify the package
uv run python -c "import cianfhoghlaim; print(cianfhoghlaim.__version__)"
# → 0.1.0

# Launch the single Dagster UI (5-layer Component architecture)
mise run dagster:oideachais
# → http://localhost:3000

# Materialise the per-subject pipelines
dg launch --assets 'math_syllabus_raw,math_syllabus_structured,math_quest_pack,math_embedding,math_cognify,math_dashboard'

# Semantic code search (always use before grep)
bun run ccc:init     # first time only — creates .cocoindex_code/target_sqlite.db
bun run ccc:index    # rebuild the index after any major file move
bun run ccc:search "Dagster asset partition definition"

# Run OCR evaluation harness (24 OCR models × 5 converters)
uv run python -m cianfhoghlaim.ocr.evaluation.compare

# Validate an openspec change (MUST pass before commit)
bun run spec:validate retro-educational-game-asset-pipeline-v1 --strict
```

---

## Sub-project AGENTS.md routing

Three layers of agent instructions. **Read them in order:**

1. **Root** — `AGENTS.md` (the 5 priority skills, 4 priority commands,
   4 priority stacks, 4 priority openspec specs)
2. **Openspec workflow** — `openspec/AGENTS.md` (the 32 capability specs)
3. **Per-area dispatches** (each sub-package has its own AGENTS.md):
   - `agents/adk/AGENTS.md` — the ADK agent fleet
   - `agents/adk/callbacks/AGENTS.md` — agent middleware patterns
   - `dagster/AGENTS.md` (defs/ tree inspection)
   - `web/_oideachais_apps/AGENTS.md` — the oideachais web surface
   - `meaisinfhoghlaim/AGENTS.md` — OCR + alignment + alignment workers
   - `baml/AGENTS.md` — the BAML contract taxonomy
   - `cocoindex/AGENTS.md` — the v1 CocoIndex conformance contract

Plus the per-stack docs at `bonneagar/stacks/<name>/README.md` for
the 90+ Compose stacks and the **per-stack 4-section docs** at
`cianfhoghlaim/docs/stacks/<name>.md` (the 6-file GOLD_STANDARD).

---

## Recent major changes (chronological)

A condensed history. The full openspec change set lives at
`openspec/changes/` and the full git log at
`git log --oneline --decorate-all origin/main`.

| Date | Change | What |
|:--|:--|:--|
| **2026-07-30** | `retro-educational-game-asset-pipeline-v1` | New `retro-game-design-catalogue` spec + 5th pipeline in `celtic-asset-generation`. Reads retro educational games (Number Munchers, Oregon Trail, Carmen Sandiego) via headless libretro, segments with SAM3, extracts design patterns via Bolmo / Molmo2 / Qwen3-VL, then generates subject-conditioned 2D + 3D assets for the MMO. Output targets `s3://cianfhoghlaim-asset-v2/3d/`. |
| **2026-07-30** | `centralise-data-plane` (7-stack ops rewrite) | langfuse / litellm / mlflow migrated off per-stack Postgres/Minio/Redis/ClickHouse onto the shared `bonneagar/stacks/lakehouse/` instance. 12 databases + 7 buckets + ClickHouse + Redis now centralised. |
| **2026-07-29** | **v4 stack migration complete** (bonneagar) | All 90+ Compose stacks now canonical at `bonneagar/stacks/`. The `infrastructure/` + `cianfhoghlaim/stacks/` legacy locations removed. |
| **2026-06-30** | `dagster-ground-up-rewrite-5-layer-component-architecture` | The 619-line legacy `definitions.py` → 30-line bootstrap + layered `dagster/defs/` tree (1_ingestion / 2_materials / 3_model_lifecycle / 4_asset_generation / 5_agent_ops) using the Dagster 1.10 Components preview. |
| **2026-06-30** | `agent-platform-cluster-hermes-cocoindex` | The OpenClaw + OpenChamber + Hermes agent cluster + the unified v1 CocoIndex code-lookup agent. Single LiteLLM chokepoint for all LLM calls. |
| **2026-06-29** | `baml-reorganize-by-cluster` | 60+ BAML files reorganised into a 3-cluster taxonomy (`education/`, `celtic/`, `processing/`) with `_shared/` homes per cluster. |
| **2026-06-29** | `wire-baml-to-consolidated-pipelines` | All consumer docstrings/comments swept to point at the new cluster-relative BAML paths. |
| **2026-06-28** | `sruth → cianfhoghlaim` v4 consolidation | Merged 5 quadrants (`oideachais / meaisinfhoghlaim / tuatha / croilar / crypteolas`) + browser + 33 stacks into a single Python package. Top-level dirs became `baml/`, `cocoindex/`, `dlt/`, `dagster/`, `agents/`, `web/`, `meaisinfhoghlaim/`, `tuatha/` instead of `core/*`. |
| **2026-06-28** | `ncca-leaving-cert-syllabi-corpus` | 116 NCCA syllabus PDFs across 8 subjects × {en, ga} downloaded into `leaving_certificate/`. New BAML function `ExtractSyllabusStructure`. |
| **2026-06-28** | `cianfhoghlaim-educational-mmo-v1` | The MMO v1: 8 NCCA subject realms + 8 ADK agents + 1 root + `SkillTreeBadge` credential anchored daily on Base L2. The Tuatha theming dropped (preserved in `.agents/skills_backup/` as archaeology). |
| **2026-06-26** | `consolidate-cianfhoghlaim-pyproject-and-8-dirs` | Single `pyproject.toml` boundary across the consolidated v4 package. |
| Earlier | `celtic-asset-generation`, `cognee-knowledge-graph`, `croilar-portfolio`, `tuatha-mmo`, … | The 30+ archived changes live at `openspec/changes/archive/` and the 32 canonical capability specs at `openspec/specs/`. |

---

## Related repos

| Repo | Use it for |
|:--|:--|
| [**cianfhoghlaim/bonneagar**](https://github.com/cianfhoghlaim/bonneagar) | Infrastructure GitOps — 90+ Compose stacks, Komodo procedures, Pangolin routes, Ansible, Pulumi, the Locket secrets sidecar pattern. Start here when you need to **deploy** something. |
| [**cianfhoghlaim/leabharlann**](https://github.com/cianfhoghlaim/leabharlann) | The personal digital library corpus: 6 domains of curated PDFs. Start here when you want to **read** something. |
| Sub-embedded repos | `spaces/data-engineering/` is its own git repo (the data-engineering HuggingFace Space demo). Don't `git add` it from this repo — work directly in `spaces/data-engineering/`. |

---

## License

BUSL-1.1 — see [`LICENSE`](../LICENSE).

The sibling repos (`bonneagar`, `leabharlann`) also use BUSL-1.1.
Source-available; not an Open Source licence. Re-use permitted for
non-commercial purposes; commercial re-use requires written
agreement.
