# Cianfhoghlaim Project Conventions

> **STALE PATHS WARNING (added 2026-08-26):** the capability tables below
> (Subproject + Capability Areas) were written against the pre-v7
> directory layout (`core/`, `assets/`, `pipelines/`, `cognify/`,
> `sources/nations/`) and have not been updated for the current flattened
> layout. Verified current top-level locations: `dlt_sources/` (not
> `pipelines/ingest/` or `sources/nations/`), `cocoindex_flows/` (not
> `core/cocoindex/`), `orchestration/` (not `assets/definitions.py`),
> `baml_src/` (not `core/baml/`), `.agents/skills/` (not a `cognify/`
> tree). The spec COUNT below ("38 specs") is also stale — the live
> count is 101 (`openspec list --specs`). The capability DESCRIPTIONS
> (what each thing does) are likely still directionally accurate; the
> PATHS inside them are not verified and should not be trusted without
> checking. A full per-row path audit is tracked as follow-up work, not
> done here — see the 2026-08-26 data-side-remediation session notes.

## Project Overview

A bilingual (EN/GA) agentic educational platform covering 5 stages of the
Irish education system: Aistear, Primary, Junior Cycle, Senior Cycle, and
Tertiary. Powered by BAML extraction, Cognee + LanceDB + DuckLake
knowledge graph, Agno + Google ADK agents, and a TanStack Start /
CopilotKit AG-UI front-end. The monorepo is a **bun + uv + turbo polyglot
orchestration of a single consolidated Python package (the repo itself, post-v7) and
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

**Plan 1.5 (NEW per `rewrite-cianfhoghlaim-leaving-cert-v2`; Brown
Ajah theming REMOVED 2026-07-09):** The
`cianfhoghlaim-leaving-cert-portal` TanStack Start app + the 8 NCCA
LC subject ADK specialists + the `retro-game-asset-pipeline` (2D + 3D
asset generator via TRELLIS.2 + SAM-3D-Objects + FIBO) + the
`ncca-leaving-cert-root-pdfs` (5 NCCA root-level programme PDFs).
The map is an accurate British Isles map split into 6 subnations
(Éire + Northern Ireland + Scotland + England + Wales + Isle of Man).
The public theming is professional + minimal; the mythology /
historical-sources theming is deferred to BIEP-v2 (post full British
Isles educational pipelines) per the
`2026-07-09-remove-brown-ajah-theming-v1` change. Cian of the Tuatha Dé
Danann (the operator) tries to heal the land and language through
education.

**Plan 2 (preserved):** UK 4-nation + Isle of Man — full education sources.
**Plan 3 (preserved):** UK 4-nation + IoM — 7 domains (law, medicine,
culture, government, intelligence, statistics, geospatial).
**Legacy:** Jersey + Guernsey (Crown Dependencies).

> See `openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/`
> for the v4 consolidation plan that produced this single-package layout.

## Subproject (1 consolidated package)

| Subproject | Path | Wheel / Workspace | Purpose | README | AGENTS.md |
|:--|:--|:--|:--|:--|:--|
| `cianfhoghlaim` | `.` (repo root — `pyproject.toml`'s `[tool.hatch.build.targets.wheel] packages = ["."]`, corrected 2026-08-26; the pre-v7 `cianfhoghlaim/cianfhoghlaim/` package dir no longer exists) | `cianfhoghlaim` (uv) | Consolidated Celtic education + multi-nation + multi-language data platform | [README](../README.md) | [AGENTS](../AGENTS.md) |

> **NOTE:** Source schema layout is provisional — refactor after Plan 1 informs
> best CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.

## Capability Areas (101 specs live per `openspec list --specs`, 2026-08-26 — the "38 specs, 8 groups" grouping below is the original pre-v7 categorisation and has not been reconciled against the current 101; treat group membership as approximate)

### Cianfhoghlaim core (14 specs — Plan 1 active)

| Capability | Description | Status |
|:--|:--|:--|
| `oideachais-pipeline` | Celtic education curriculum pipeline (Dagster + DLT + DuckLake + LanceDB + BAML, 5 stages); sources at `sources/nations/ie/education/{early_childhood,primary,junior_cycle,senior_cycle,leaving_cert}/` (EN + GA); Plan 1 active | Active |
| `oideachais-leabharlann` | 6 dlt sources (aigne + gaeilge + gemini_deep_research + mata + ollscoil_na_gaillimhe + zotero) at `pipelines/ingest/leabharlann/`; 3 v1 CocoIndex Apps (`leabharlann_books_embedding`, `leabharlann_zotero_embedding`, `leabharlann_takeout_embedding`) at `core/cocoindex/leabharlann_flow.py`; 7 Dagster assets at `assets/definitions.py` | Active |
| `oideachais-baml-schemas` | 6 consolidated BAML files (`clients.baml`, `curriculum.baml`, `culture.baml`, `document.baml`, `gaois.baml`, `code_intel.baml`) at `core/baml/`; 3 extraction clients (ExtractEn, ExtractEnStrong, LocalVision) | Active |
| `oideachais-cognify-knowledge-graph` | 5-stage cross-stage cognify + 3 leabharlann cognify datasets + 3 cross-archive FalkorDB edge types; rules at `cognify/rules/` | Active |
| `oideachais-semantic-search` | Cross-corpus LanceDB HNSW search (BGE-M3 multilingual + BGE-large-en-v1.5 English) at `core/lancedb/` | Active |
| `oideachais-marimo-dashboards` | 11 Marimo notebooks (5 educational stages + Ireland curriculum analysis + 6 leabharlann subdir analyses + cross-domain) at `notebooks/` | Active |
| `ireland-primary-jc-dlt-baml` | Ireland Primary + Junior Cycle dlt + BAML loop | Active |
| `official-media-pipeline` | Instagram-export → British-Isles government source enrichment (DLT + BAML `ClassifyOfficialMedia` + 4-lookup resolver + Dagster `group_name="official_media"`); 3 jurisdictions in PR 1 (IE/NI/EN), the `official-media-pipeline` change | Active |
| `official-media-fediverse` | Pure Python library for Mastodon webfinger + Bluesky xrpc resolution + Wikipedia REST + Companies House / CRO lookup; reusable by the side-loadable-app phase (the `official-media-fediverse` change) | Active |
| `official-media-marimo` | Marimo mission control + TanStack Start route + Cognee dataset `oideachais_official_media` with 4 edge types + strong-stance footer card; the `official-media-marimo` change | Active |
| `upstream-package-monitoring` | 3 CocoIndex v1 Apps (`upstream_blog_monitor`, `upstream_api_surface`, `cocoindex_v1_conformance`) at `core/cocoindex/`; 4 Firecrawl monitor configs + 1 n8n webhook bridge + 5 Dagster assets + 1 breaking-change sensor for the motherduck / dlthub / lancedb / cocoindex upstream surface | Active |
| `oideachais-email-triage` | 4-account MBOX DLT source (`leabharlann_email_inbox`) + `email.baml` BAML (ClassifyEmail / ExtractEmailThread / LinkEmailToResearch) + 4th v1 CocoIndex App `leabharlann_inbox_embedding` + 5 new Dagster assets + Google ADK `email_triage` agent (port 7778) + marimo notebook `email_inbox_triage.py` (primary manual surface) + openclaw WebChat email sub-UI (secondary) + Mailcow stack with 4 per-account IMAP credentials (DKIT.ie M365, 2 Gmail, Hotmail) + 3 new Cognee cross-archive edge types; the `2026-06-29-leabharlann-email-inbox-pipeline` change | Active |
| `oideachais-university-deep-extraction` | Per-university website deep extraction (BAML `university_extraction.baml` with 4 classes + 4 functions + 3 new deterministic evals; reusable DLT factory + Pydantic config; case-study Galway DLT source; 5 Dagster assets `uog_{pre_research,bulk_scrape,extract_courses,extract_modules,extract_programmes}`; 2 new v1 CocoIndex Apps `UniversityCoursesApp` + `UniversityModulesApp`; 1 Cognee cross-archive edge `UoGArtifact-MATCHES-CourseDescriptor`; 1 marimo notebook with 4 tabs; the `university-of-galway-deep-extraction` change) | Active |
| `british-isles-education-pipeline` | 6 Irish Leaving Certificate priority subjects (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science) + gov.ie education circulars; NCCA + SEC + gov.ie DLT sources; 5 `baml/education/lc_extraction/*.baml` + `circular_extraction.baml`; 7 v1-conformant CocoIndex flows (6 subjects + government_circulars); 42 lc5/lc6 Dagster assets + 2 gov.ie circular assets; 6 per-subject marimo notebooks + cross-subject competency notebook + gov.ie circulars cross-archive notebooks; 4 MotherDuck Dives (syllabus topics, exam paper difficulty, marking scheme complexity, education circulars); 1 daily MotherDuck Flight (`lc_pdf_sync_flight`); Garage S3 PDF storage (`s3://garage/oideachais/leaving_cert/<subject>/<lang>/<year>/<file>.pdf`); cross-nation extension (Scotland / Wales / England / NI / Crown Dependencies) deferred to v2; the `2026-07-06-british-isles-education-pipeline-v1` change | Active |
| `apple-photos-ingestion` | 5th leabharlann corpus (Apple Photos export via osxphotos); 3 new v1 CocoIndex Apps (`apple_photos_metadata`, `apple_photos_chunks`, `apple_photos_geospatial` GeoParquet); 5 new Dagster assets + 2 routing assets + 1 cross-frame velocity asset; 2 destination flows (document scans → paperless-ngx via docling-serve; vehicle photos → vehicle_observations via paddleocr + dots-ocr); privacy gate `LEABHARLANN_PHOTOS_INCLUDE_GPS` (default false) | Active |
| `agent-platform-cluster` | 8-stack agent-platform cluster (lakehouse + litellm + langfuse + mlflow + logfire + cognee + graphiti + lancedb) + 3 agent surfaces (openclaw + openchamber + hermes); omnibus Komodo procedure `deploy-agent-platform-cluster-bunchloch` with `--skip` flags; Hermes (NousResearch/hermes-agent v0.17.0) as the 3rd vertex; M3 chokepoint through LiteLLM | Active |
| `dlthub-platform-integration` | dltHub Platform CLI (`dlthub 1.28+`) workspace rooted at the repo root; 8 production AI workbench toolkits installed into Claude Code (`init` + `rest-api-pipeline` + `sql-database-pipeline` + `filesystem-pipeline` + `dlthub-platform` + `data-exploration` + `data-quality` + `transformations`) from the vendored `dlthub-ai-workbench/` marketplace; `fastmcp-slim[server]` for the dlt-workspace MCP server; deployment manifest at `__deployment__.py` with `@run.pipeline("name")` decorated batch jobs under `__all__` (first job: `government_circulars_ingest`); the `dlthub run` (batch) / `dlthub serve` (interactive) hygiene rule; diagnostic runbook at `docs/agents/dlthub-run-vs-serve.md` capturing the 5 most common CLI errors; the `2026-07-06-wire-dlthub-platform-toolkits-and-deployment` change | Active |

### Meaisínfhoghlaim sub-tree (3 specs)

| Capability | Description | Status |
|:--|:--|:--|
| `meaisinfhoghlaim-platform` | 16 sub-packages at `core/{dlt,duckdb,ducklake,lancedb,motherduck,cocoindex,baml,marimo,browser,cognee,obs,rag,search,curriculum,config,memory}/` + 4 heartbeat Dagster assets + single Dagster code-location `assets/definitions.py` | Active |
| `meaisinfhoghlaim-agent-frameworks` | 12 specialised agents (Root, Curriculum, Translation, Corpus, Geospatial, Statistics, Research, Education Research, Bunchloch Research, Curriculum Comparison, AGUI Curriculum, MCP Curriculum) at `agents/meaisinfhoghlaim/` | Active |
| `meaisinfhoghlaim-ocr-htr` | **11 OCR vision models** (`unsloth/gemma-4-{31B-it,26B-A4B-it,E4B-it,E2B-it}-GGUF` + `unsloth/Qwen3.6-{27B-GGUF,27B-MLX-8bit,35B-A3B-GGUF,35B-A3B-UD-MLX-4bit}` + `unsloth/GLM-4.6V-Flash-GGUF`) at `ocr/models/registry.py` + **4 classical OCR Docker stacks** (`stacks/{dots-ocr,docling-serve,olmocr,paddleocr}/`) + 6 backends (litellm, mlx, transformers, ollama, openai, anthropic) + evaluation harness at `ocr/evaluation/compare.py` running ~220 evals (11 vision × 4 classical × Ireland syllabus + 6 leabharlann subdirs) | Active |

### Tuatha sub-tree (1 spec)

| Capability | Description | Status |
|:--|:--|:--|
| `tuatha-platform` | Celtic educational MMO (Babylon.js + Rust + SpacetimeDB) + crypteolas crypto platform (legacy snapshot at `docs/legacy/crypteolas/`) + BAML UI/image extraction; TanStack Start frontend at `web/apps/tuatha-ui/`; Babylon.js client at `web/apps/tuatha-demo/` | Active |

### Croílár sub-tree (4 specs)

| Capability | Description | Status |
|:--|:--|:--|
| `croilar-portfolio` | Public TanStack Start site at `web/apps/croilar-web/` — multi-persona (aleyum, cianfhoghlaim, carlcashman) | Active |
| `croilar-data-engineering` | Dagster + DLT + CocoIndex + BAML pipelines for croilar personas at `assets/_croilar_dagster/` | Active |
| `croilar-cv-extraction` | BAML extraction of the author's CV / achievements / teaching PDFs at `assets/_croilar_assets/` | Active |
| `croilar-stream-registry` | The 5 aleyum→croilar alias collapses (ALEYUM_→STREAMS_, aleyum.duckdb→croilar.duckdb, etc.) + `StreamSettings` Pydantic BaseSettings + `config/sources.yaml` registry | Active |

### Agent + Observability + Frontend (5 specs)

| Capability | Description | Status |
|:--|:--|:--|
| `agent-memory-systems` | Cognee + Graphiti + LanceDB + FalkorDB + Memgraph agent memory at `core/{cognee,memory}/` | Active |
| `indexing-and-cognition` | CCC v1 code search (16 Apps at `core/cocoindex/`) + Cognee 7-cluster knowledge graph + OpenCode agent/MCP registry | Active |
| `agent-registry` | OpenCode agent + skill + MCP registry (7 agents, 9 MCPs, 89 skills across data-platform/infrastructure/agent-platform/frontend-apps/research) per `openspec/specs/agent-registry/spec.md`; replaces the legacy 5 sruth-subagents + croilar-devtools MCP at `openspec/changes/2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation/` | Active |
| `agent-observability` | Langfuse + MLflow + RAGAS + Logfire at `core/obs/` | Active |
| `agentic-frontend-frameworks` | TanStack Start + CopilotKit + AG-UI + Hono + Convex at `web/` | Active |
| `dagger-pipelines` | Polyglot CI/CD via Dagger (Python + TS) — 5 separate `dagger-*` specs merged into 1 (8-step GitOps) | Active |

### Infrastructure + Tooling (9 specs)

| Capability | Description | Status |
|:--|:--|:--|
| `infrastructure-stacks` | **88 selfhosted Docker stacks at `bonneagar/stacks/`** (the 6-file GOLD_STANDARD pattern: `compose.yaml` + `sidecar.yaml` + `secrets.env` + `pangolin.yaml` + `blueprint.yaml` + `.env.example`) + the unified IaC TypeScript client at `bonneagar/iac/` (Komodo + Pangolin Integrations API + Infisical) + the root manifest at `bonneagar/package.json` + the 5-group model (infrastructure / data-engineering / agent-platform / language-model / user-facing-web / ci) + stack-doctor (the CI gate) + Pangolin + Infisical + Locket + Komodo | Active |
| `infrastructure-stacks-documentation` | Per-stack docs at `docs/stacks/<name>.md` (the 4-section template: Purpose + Why-GitOps + Cross-references + Tags); the contract is enforced by `scripts/stack-doctor.sh` (the CI gate fails if a stack is missing its doc); the `infrastructure-stacks-documentation` SKILL.md is the agent entry point | Active |
| `data-engineering-pipeline-documentation` | The 4 canonical ops dirs (bonneagar/, cianfhoghlaim/assets/, docs/stacks/, bonneagar/komodo/) + the per-area READMEs | Active |
| `bonneagar-iac-merge` | The unified TypeScript IaC at `bonneagar/iac/` that orchestrates the 3 systems (Komodo + Pangolin + Infisical) into a single codebase; 3 typed clients (KomodoClient 18 methods, PangolinClient 12 methods using the Enterprise Edition **Integrations API** at `${PANGOLIN_URL}/v1` + `/api/v1/integration/...`, InfisicalClient 10 methods using `@infisical/sdk`); 4 source-discoverers (auto-derive from the 91 stacks); 15 CLI commands (plan, deploy, bootstrap, teardown, health + 10 sync commands); fixes the 4 known blockers from `DEPLOYMENT-STRATEGY.md` (Newt-Pangolin version mismatch, 3 manual Pangolin resources, 401 PANGOLIN_API_KEY, locket `${INFISICAL_CLIENT_ID}` literal); the `iac:bootstrap` flag `--with-blueprint-import` uses the Pangolin bulk-import API for the initial resource creation | Active |
| `bonneagar-komodo-gitops` | The canonical Komodo GitOps pattern for the `bonneagar/` fleet: 3 resource-syncs — `komodo/resource-syncs/{arm1-oci,bunchloch,cross-cutting}.toml` — that auto-pull from `forgejo.cianfhoghlaim.ie/cliste/kings_college_galway` on every commit (interval 60s, `on_pull: true`, `delete: false`, `managed: true`); the IaC at `iac/` is slimmed to the orchestration layer (only `iac:bootstrap` + 6 sync commands: secrets, resources, variables, action-recipients, olm, health); the pre-v5 `iac:sync:procedures` + `iac:sync:resource-syncs` commands are removed (procedures + stacks are owned by the resource-syncs); the 8-phase `iac:bootstrap` state machine registers the 3 resource-syncs in Phase 7; the 2-host topology (`arm1-oci` + `bunchloch`) is enforced; Hetzner is Pulumi-only (per the v5 user decision) | Active |
| `spaces-cicd-pipeline` | Reusable GH Action at `infrastructure/ci/spaces-sync.yml` for publishing any `spaces/*/` dir to a HF Space (gradio / docker / static SDKs) | Active |
| `documentation` | Canonical `docs/` structure (8 numbered domains), frontmatter schema, Cognee ingestion | Active |
| `celtic-asset-generation` | **4 successive INDEPENDENT asset gen pipelines** at `assets/asset_generation/`: `official_documents/{syllabus,exam_papers,marking_schemes}/` → `subject_assets/{chemistry_lab,geography_landscape,biology_specimens,physics_apparatus}/` → `language_assets/{gaeilge,cymraeg,gaidhlig,gaelg,kernewek,brezhoneg}_assets.py` → `exporters/{babylon,godot,unity,unreal}.py` | Active |
| `agent-platform-cluster` | 8-stack agent-platform cluster (lakehouse + litellm + langfuse + mlflow + logfire + cognee + graphiti + lancedb) + 3 agent surfaces (openclaw + openchamber + hermes); omnibus Komodo procedure `deploy-agent-platform-cluster-bunchloch` with `--skip` flags; Hermes (NousResearch/hermes-agent v0.17.0) as the 3rd vertex; M3 chokepoint through LiteLLM | Active |
| `apple-photos-ingestion` | 5th leabharlann corpus (Apple Photos export via osxphotos); 3 new v1 CocoIndex Apps (`apple_photos_metadata`, `apple_photos_chunks`, `apple_photos_geospatial` GeoParquet); 5 new Dagster assets + 2 routing assets + 1 cross-frame velocity asset; 2 destination flows (document scans → paperless-ngx via docling-serve; vehicle photos → `vehicle_observations` via paddleocr + dots-ocr); privacy gate `LEABHARLANN_PHOTOS_INCLUDE_GPS` (default false) | Active |
| `british-isles-education-pipeline` | 6 Irish LC priority subjects (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science) + gov.ie circulars — NCCA + SEC + gov.ie DLT + BAML + 7 v1 CocoIndex flows + 42 Dagster assets + 6 marimo notebooks + 4 MotherDuck Dives + daily Flight | Active |
| `oideachais-university-deep-extraction` | Per-university website deep extraction (BAML + DLT + Dagster + CocoIndex v1 + marimo + Cognee cross-archive) — the reusable template for any British Isles university | Active |
| `dagster-5-layer-component-architecture` | 5 KCG-specific Dagster Components (`CelticIngestionComponent` / `CelticMaterialsComponent` / `CelticModelLifecycleComponent` / `CelticAssetGenerationComponent` / `CelticAgentOpsComponent`) at `cianfhoghlaim/dagster/components/layer{1..5}_*.py` + 5-layer `defs/<1..5>_<layer>/` YAML tree + 260+ assets organised into 5 hierarchical groups (`1_ingestion/*`, `2_materials/*`, `3_model_lifecycle/*`, `4_asset_generation/*`, `5_agent_ops/*`) + Dagster 1.13+ Declarative Automation (`AutomationCondition.eager() | .cron(...)`) + Virtual Assets (`is_virtual=True` on the 17 L3 CocoIndex v1 Apps) + State-Backed Components (the 5 L1 high-churn sources NCCA/SEC/CCEA/SQA/WJEC with `state_refresh_interval="monthly"`) + R1–R4 conformance enforced at scaffold time + L5 Agent Operations (12 agents × 5 emitted assets = 60 new L5 assets, with RisingWave event stream at `risingwave.cianfhoghlaim.ie:4566` + Letta memory + Langfuse traces dropped); the 5-layer rewrite supersedes the legacy 3 KCG Components (`celtic_dlt_source`, `celtic_cocoindex_v1`, `celtic_lancedb_hnsw`); the `2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture` change | Active |

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

- Specs: `openspec/specs/<capability>/spec.md` (48 canonical specs)
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

**Do not hardcode this list — it goes stale within days on this repo's
change velocity.** The table that lived here (last refreshed
2026-07-06, still showing `2026-07-02-*` entries as "in-flight" that
were archived weeks ago) was removed 2026-08-26 for exactly that
reason. Use one of these instead:

```bash
uv run openspec list           # active changes + task completion + age
uv run openspec list --specs   # all specs + requirement counts
```

See also `openspec/ACTIVE_ROADMAP.md` for the curated summary (also
subject to the same staleness risk — check its own "Status" line's
date against today before trusting it).
| `rewrite-cianfhoghlaim-leaving-cert-v2` | umbrella in-flight (55/206 tasks) |
