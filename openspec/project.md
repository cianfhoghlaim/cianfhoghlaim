# Cianfhoghlaim Project Conventions

## Project Overview

A bilingual (EN/GA) agentic educational platform covering 5 stages of the
Irish education system: Aistear, Primary, Junior Cycle, Senior Cycle, and
Tertiary. Powered by BAML extraction, Cognee + LanceDB + DuckLake
knowledge graph, Agno + Google ADK agents, and a TanStack Start /
CopilotKit AG-UI front-end. The monorepo is a **bun + uv + turbo polyglot
orchestration** of a single consolidated `cianfhoghlaim/` package and
33 user-pre-selected selfhosted Docker Compose stacks (with the remaining
57 staying at `infrastructure/stacks/`).

**Plan 1 (active):** Ireland (early childhood / primary / junior cycle /
senior cycle / Leaving Cert) in EN + GA, plus the leabharlann corpus
(6 subdirs × 225 docs on disk; `identity/` is empty and the dlt source
no-ops gracefully), plus the new `oideachais-email-triage` capability
that ingests the user's personal + professional email from 4 accounts
(DKIT.ie M365, 2 Gmail, Hotmail) via Mailcow + a MBOX DLT source +
BAML classification + CocoIndex embedding + Google ADK `email_triage`
agent + a marimo notebook.
**Plan 2 (preserved):** UK 4-nation + Isle of Man — full education sources.
**Plan 3 (preserved):** UK 4-nation + IoM — 7 domains (law, medicine,
culture, government, intelligence, statistics, geospatial).
**Legacy:** Jersey + Guernsey (Crown Dependencies).

> See `openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/`
> for the v4 consolidation plan that produced this single-package layout.

## Subproject (1 consolidated package)

| Subproject | Path | Wheel / Workspace | Purpose | README | AGENTS.md |
|:--|:--|:--|:--|:--|:--|
| `cianfhoghlaim` | `cianfhoghlaim/` | `cianfhoghlaim` (uv) + `codeolas` (uv sub-package) | Consolidated Celtic education + multi-nation + multi-language data platform | [README](../cianfhoghlaim/README.md) | [AGENTS](../cianfhoghlaim/AGENTS.md) |

> **NOTE:** Source schema layout is provisional — refactor after Plan 1 informs
> best CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.

## Capability Areas (34 specs, 8 groups)

### Cianfhoghlaim core (11 specs — Plan 1 active)

| Capability | Description | Status |
|:--|:--|:--|
| `oideachais-pipeline` | Celtic education curriculum pipeline (Dagster + DLT + DuckLake + LanceDB + BAML, 5 stages); sources at `cianfhoghlaim/sources/nations/ie/education/{early_childhood,primary,junior_cycle,senior_cycle,leaving_cert}/` (EN + GA); Plan 1 active | Active |
| `oideachais-leabharlann` | 6 dlt sources (aigne + gaeilge + gemini_deep_research + mata + ollscoil_na_gaillimhe + zotero) at `cianfhoghlaim/pipelines/ingest/leabharlann/`; 3 v1 CocoIndex Apps (`leabharlann_books_embedding`, `leabharlann_zotero_embedding`, `leabharlann_takeout_embedding`) at `cianfhoghlaim/core/cocoindex/leabharlann_flow.py`; 7 Dagster assets at `cianfhoghlaim/assets/definitions.py` | Active |
| `oideachais-baml-schemas` | 6 consolidated BAML files (`clients.baml`, `curriculum.baml`, `culture.baml`, `document.baml`, `gaois.baml`, `code_intel.baml`) at `cianfhoghlaim/core/baml/`; 3 extraction clients (ExtractEn, ExtractEnStrong, LocalVision) | Active |
| `oideachais-cognify-knowledge-graph` | 5-stage cross-stage cognify + 3 leabharlann cognify datasets + 3 cross-archive FalkorDB edge types; rules at `cianfhoghlaim/cognify/rules/` | Active |
| `oideachais-semantic-search` | Cross-corpus LanceDB HNSW search (BGE-M3 multilingual + BGE-large-en-v1.5 English) at `cianfhoghlaim/core/lancedb/` | Active |
| `oideachais-marimo-dashboards` | 11 Marimo notebooks (5 educational stages + Ireland curriculum analysis + 6 leabharlann subdir analyses + cross-domain) at `cianfhoghlaim/notebooks/` | Active |
| `ireland-primary-jc-dlt-baml` | Ireland Primary + Junior Cycle dlt + BAML loop | Active |
| `official-media-pipeline` | Instagram-export → British-Isles government source enrichment (DLT + BAML `ClassifyOfficialMedia` + 4-lookup resolver + Dagster `group_name="official_media"`); 3 jurisdictions in PR 1 (IE/NI/EN), the `official-media-pipeline` change | Active |
| `official-media-fediverse` | Pure Python library for Mastodon webfinger + Bluesky xrpc resolution + Wikipedia REST + Companies House / CRO lookup; reusable by the side-loadable-app phase (the `official-media-fediverse` change) | Active |
| `official-media-marimo` | Marimo mission control + TanStack Start route + Cognee dataset `oideachais_official_media` with 4 edge types + strong-stance footer card; the `official-media-marimo` change | Active |
| `upstream-package-monitoring` | 3 CocoIndex v1 Apps (`upstream_blog_monitor`, `upstream_api_surface`, `cocoindex_v1_conformance`) at `cianfhoghlaim/core/cocoindex/`; 4 Firecrawl monitor configs + 1 n8n webhook bridge + 5 Dagster assets + 1 breaking-change sensor for the motherduck / dlthub / lancedb / cocoindex upstream surface | Active |
| `oideachais-email-triage` | 4-account MBOX DLT source (`leabharlann_email_inbox`) + `email.baml` BAML (ClassifyEmail / ExtractEmailThread / LinkEmailToResearch) + 4th v1 CocoIndex App `leabharlann_inbox_embedding` + 5 new Dagster assets + Google ADK `email_triage` agent (port 7778) + marimo notebook `email_inbox_triage.py` (primary manual surface) + openclaw WebChat email sub-UI (secondary) + Mailcow stack with 4 per-account IMAP credentials (DKIT.ie M365, 2 Gmail, Hotmail) + 3 new Cognee cross-archive edge types; the `2026-06-29-leabharlann-email-inbox-pipeline` change | Active |

### Meaisínfhoghlaim sub-tree (3 specs)

| Capability | Description | Status |
|:--|:--|:--|
| `meaisinfhoghlaim-platform` | 16 sub-packages at `cianfhoghlaim/core/{dlt,duckdb,ducklake,lancedb,motherduck,cocoindex,baml,marimo,browser,cognee,obs,rag,search,curriculum,config,memory}/` + 4 heartbeat Dagster assets + single Dagster code-location `cianfhoghlaim/assets/definitions.py` | Active |
| `meaisinfhoghlaim-agent-frameworks` | 12 specialised agents (Root, Curriculum, Translation, Corpus, Geospatial, Statistics, Research, Education Research, Bunchloch Research, Curriculum Comparison, AGUI Curriculum, MCP Curriculum) at `cianfhoghlaim/agents/meaisinfhoghlaim/` | Active |
| `meaisinfhoghlaim-ocr-htr` | **11 OCR vision models** (`unsloth/gemma-4-{31B-it,26B-A4B-it,E4B-it,E2B-it}-GGUF` + `unsloth/Qwen3.6-{27B-GGUF,27B-MLX-8bit,35B-A3B-GGUF,35B-A3B-UD-MLX-4bit}` + `unsloth/GLM-4.6V-Flash-GGUF`) at `cianfhoghlaim/ocr/models/registry.py` + **4 classical OCR Docker stacks** (`stacks/{dots-ocr,docling-serve,olmocr,paddleocr}/`) + 6 backends (litellm, mlx, transformers, ollama, openai, anthropic) + evaluation harness at `cianfhoghlaim/ocr/evaluation/compare.py` running ~220 evals (11 vision × 4 classical × Ireland syllabus + 6 leabharlann subdirs) | Active |

### Tuatha sub-tree (1 spec)

| Capability | Description | Status |
|:--|:--|:--|
| `tuatha-platform` | Celtic educational MMO (Babylon.js + Rust + SpacetimeDB) + crypteolas crypto platform (legacy snapshot at `cianfhoghlaim/docs/legacy/crypteolas/`) + BAML UI/image extraction; TanStack Start frontend at `cianfhoghlaim/web/apps/tuatha-ui/`; Babylon.js client at `cianfhoghlaim/web/apps/tuatha-demo/` | Active |

### Croílár sub-tree (4 specs)

| Capability | Description | Status |
|:--|:--|:--|
| `croilar-portfolio` | Public TanStack Start site at `cianfhoghlaim/web/apps/croilar-web/` — multi-persona (aleyum, cianfhoghlaim, carlcashman) | Active |
| `croilar-data-engineering` | Dagster + DLT + CocoIndex + BAML pipelines for croilar personas at `cianfhoghlaim/assets/_croilar_dagster/` | Active |
| `croilar-cv-extraction` | BAML extraction of the author's CV / achievements / teaching PDFs at `cianfhoghlaim/assets/_croilar_assets/` | Active |
| `croilar-stream-registry` | The 5 aleyum→croilar alias collapses (ALEYUM_→STREAMS_, aleyum.duckdb→croilar.duckdb, etc.) + `StreamSettings` Pydantic BaseSettings + `sruth/croilar/config/sources.yaml` registry | Active |

### Agent + Observability + Frontend (5 specs)

| Capability | Description | Status |
|:--|:--|:--|
| `agent-memory-systems` | Cognee + Graphiti + LanceDB + FalkorDB + Memgraph agent memory at `cianfhoghlaim/core/{cognee,memory}/` | Active |
| `indexing-and-cognition` | CCC v1 code search (16 Apps at `cianfhoghlaim/core/cocoindex/`) + Cognee 7-cluster knowledge graph + OpenCode agent/MCP registry | Active |
| `agent-registry` | OpenCode agent + skill + MCP registry (7 agents, 9 MCPs, 89 skills across data-platform/infrastructure/agent-platform/frontend-apps/research) per `openspec/specs/agent-registry/spec.md`; replaces the legacy 5 sruth-subagents + croilar-devtools MCP at `openspec/changes/2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation/` | Active |
| `agent-observability` | Langfuse + MLflow + RAGAS + Logfire at `cianfhoghlaim/core/obs/` | Active |
| `agentic-frontend-frameworks` | TanStack Start + CopilotKit + AG-UI + Hono + Convex at `cianfhoghlaim/web/` | Active |
| `dagger-pipelines` | Polyglot CI/CD via Dagger (Python + TS) — 5 separate `dagger-*` specs merged into 1 (8-step GitOps) | Active |

### Infrastructure + Tooling (7 specs)

| Capability | Description | Status |
|:--|:--|:--|
| `infrastructure-stacks` | **88 selfhosted Docker stacks at `bonneagar/stacks/`** (the 6-file GOLD_STANDARD pattern: `compose.yaml` + `sidecar.yaml` + `secrets.env` + `pangolin.yaml` + `blueprint.yaml` + `.env.example`) + the IaC TypeScript client at `bonneagar/iac/komodo/` + the root manifest at `bonneagar/package.json` + the 5-group model (infrastructure / data-engineering / agent-platform / language-model / user-facing-web / ci) + stack-doctor (the CI gate) + Pangolin + Infisical + Locket + Komodo | Active |
| `infrastructure-stacks-documentation` | Per-stack docs at `cianfhoghlaim/docs/stacks/<name>.md` (the 4-section template: Purpose + Why-GitOps + Cross-references + Tags); the contract is enforced by `scripts/stack-doctor.sh` (the CI gate fails if a stack is missing its doc); the `infrastructure-stacks-documentation` SKILL.md is the agent entry point | Active |
| `data-engineering-pipeline-documentation` | The 4 canonical ops dirs (bonneagar/, cianfhoghlaim/assets/, cianfhoghlaim/docs/stacks/, bonneagar/komodo/) + the per-area READMEs | Active |
| `spaces-cicd-pipeline` | Reusable GH Action at `infrastructure/ci/spaces-sync.yml` for publishing any `spaces/*/` dir to a HF Space (gradio / docker / static SDKs) | Active |
| `celtic-data-engineering-pipeline` | dbt-duckdb at `cianfhoghlaim/pipelines/process/_dbt_project/` + marimo statistical-analysis notebooks at `cianfhoghlaim/notebooks/meaisinfhoghlaim/` | Active |
| `gradio-ensemble-pattern` | `cianfhoghlaim/agents/image_pipeline/ensemble_gradio.py` (multi-model Gradio `Interface`) + `spaces/_common/hf_hub_push.py` (HF Hub upload) | Active |
| `chunkhound-code-search` | Semantic code search with MVCC | Active |
| `documentation` | Canonical `docs/` structure (8 numbered domains), frontmatter schema, Cognee ingestion | Active |
| `celtic-asset-generation` | **4 successive INDEPENDENT asset gen pipelines** at `cianfhoghlaim/assets/asset_generation/`: `official_documents/{syllabus,exam_papers,marking_schemes}/` → `subject_assets/{chemistry_lab,geography_landscape,biology_specimens,physics_apparatus}/` → `language_assets/{gaeilge,cymraeg,gaidhlig,gaelg,kernewek,brezhoneg}_assets.py` → `exporters/{babylon,godot,unity,unreal}.py` | Active |

### Team Workflow (3 specs)

| Capability | Description | Status |
|:--|:--|:--|
| `workflow-automation` | n8n + LLM pipelines (OpenCode Go API) | Active |
| `task-management` | Vikunja kanban + Gantt + list + team sharing | Active |
| `scheduling` | cal-diy team + per-member booking pages | Active |

## Conventions

All specs MUST respect constraints from `docs/context/00-core/CONSTRAINTS.md`:

1. **Database:** Single-threaded DuckDB, MVCC LanceDB
2. **Embeddings:** Batch minimum 100 texts
3. **Irish language:** Use specialized models (UCCIX, GaBERT)
4. **BAML:** Schema validation required for LLM extraction
5. **Secrets:** Infisical is the source of truth; Locket injects at runtime; never commit `.env`
6. **Image registry:** `ghcr.io/cianfhoghlaim/`, pinned to `<major>.<minor>.<patch>`, never `:latest`
7. **Multi-arch:** Every in-repo image built for `linux/amd64,linux/arm64`

## Requirement Language

- Use **SHALL** for normative requirements
- Use **SHOULD** for recommendations
- Use **MAY** for optional features

## Scenario Format

```markdown
#### Scenario: Descriptive name
- **GIVEN** initial context
- **WHEN** action occurs
- **THEN** expected result
```

## File Locations

- Specs: `openspec/specs/<capability>/spec.md` (34 canonical specs)
- Changes: `openspec/changes/<change-id>/`
- Archives: `openspec/changes/archive/YYYY-MM-DD-<change-id>/`
- Historical research: `docs/openspec/` (point-in-time, do not edit)
- Agent skills: `.agents/skills/<skill-name>/SKILL.md`
- Docker stacks: `infrastructure/stacks/<category>/<name>/`
- Canonical docs: `docs/0*-<domain>/<topic>.md` (frontmatter required)
- Doc index: `docs/00_index.md`
- Doc archive: `docs/archive/YYYY-MM-DD-<subtree>/`

## Review Process

1. Create proposal in `changes/<change-id>/`
2. Validate with `openspec validate <change-id> --strict`
3. Request review
4. Implement after approval
5. Archive after deployment

## Current In-Flight Changes

(Updated as changes move through the workflow. The 4 stale changes
`author-archive-gemini-and-uos-ingestion`, `cianfhoghlaim-oideachais-baml-first`,
`state-of-art-5-workspaces`, `team-workflow-stack` were archived on
2026-06-16 by the `openspec-consolidation-and-readme-refresh` change.)

| Change | Status |
|:--|:--|
| `consolidate-external-libs-into-tuatha` | in-flight (2/68 tasks) |
| `croilar-devtools-hub` | in-flight (6/55 tasks) |
| `croilar-personas-to-streams` | in-flight (6/45 tasks) |
| `croilar-portfolio` | in-flight (18/34 tasks) |
| `croilar-revitalisation` | in-flight (11/69 tasks) |
| `dagger-monorepo-integration` | in-flight (0/22 tasks) |
| `docs-restructuring` | in-flight (28/30 tasks) |
| `docs-skills-consolidation-pipeline` | in-flight (0/26 tasks) |
| `fix-existing-stacks` | in-flight (15/22 tasks) |
| `ireland-primary-jc-dlt-baml-and-full-stack-demo` | in-flight (0/22 tasks) |
| `leaving-cert-2026` | scaffold (0/28 tasks) |
| `monorepo-restructure-v2` | in-flight (19/20 tasks) |
| `official-media-pipeline` | scaffold (0/45 tasks) |
| `openspec-consolidation-and-readme-refresh` | **this change** (Phase 1+2 done; Phase 3+4 in-flight) |
