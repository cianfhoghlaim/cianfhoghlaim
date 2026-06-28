# Tasks — Consolidate sruth/* into cianfhoghlaim/v4

## 1. Create OpenSpec change proposal + spec deltas
- [ ] 1.1 Create `openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/proposal.md` ✅
- [ ] 1.2 Create `openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/tasks.md` ✅
- [ ] 1.3 Add spec delta to `openspec/changes/.../specs/oideachais-pipeline/spec.md` — REQUIRES `oideachais.assets.{aistear,primary_curriculum,junior_cycle,senior_cycle,leaving_cert_syllabus,leaving_cert_exam_paper,leaving_cert_marking_scheme,leabharlann}` to live at `cianfhoghlaim.assets.*`
- [ ] 1.4 Add spec delta to `openspec/changes/.../specs/infrastructure-stacks/spec.md` — REQUIRES 33 user-selected stacks at `cianfhoghlaim/stacks/`
- [ ] 1.5 Add spec delta to `openspec/changes/.../specs/meaisinfhoghlaim-platform/spec.md` — REQUIRES OCR registry moved to `cianfhoghlaim.ocr.models.registry`
- [ ] 1.6 Add spec delta to `openspec/changes/.../specs/celtic-asset-generation/spec.md` — REQUIRES 4 successive independent asset gen pipelines
- [ ] 1.7 Add spec delta to `openspec/changes/.../specs/oideachais-leabharlann/spec.md` — REQUIRES `/leabharlann/` consolidated at `cianfhoghlaim/leabharlann/`
- [ ] 1.8 `openspec validate 2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4 --strict`

## 2. Create cianfhoghlaim/ layered directory structure
- [ ] 2.1 `mkdir -p cianfhoghlaim/{core/{dlt,duckdb,ducklake,lancedb,motherduck,cocoindex,baml,marimo,browser,cognee,obs,rag,search,curriculum,config,memory},pipelines/{browser,ingest,distribute,process,expose},sources/{languages,nations/_preserved},assets/{asset_generation/{official_documents,subject_assets,language_assets,exporters},components,resources},agents/{api,tuatha,shared,image_pipeline,mcp_server},notebooks/{speedrun,music,teaching,cv,research,leabharlann},ocr/{models,backends,evaluation,document_factory,alignment,training,quality,geospatial},embeddings,cognify,leabharlann,libraries/codeolas,docs/legacy/{wow,Hades II,crypteolas},tests,scripts,ops,web/{apps,packages,hono-api}}`

## 3. Migrate sruth/oideachais/ → cianfhoghlaim/
- [ ] 3.1 `mv sruth/oideachais/core/storage cianfhoghlaim/core/{duckdb,ducklake,lancedb}/` (split)
- [ ] 3.2 `mv sruth/oideachais/lancedb cianfhoghlaim/core/lancedb/`
- [ ] 3.3 `mv sruth/oideachais/cognee_integration cianfhoghlaim/cognify/`
- [ ] 3.4 `mv sruth/oideachais/cocoindex_flows cianfhoghlaim/embeddings/` (then split into `core/cocoindex/` + `embeddings/`)
- [ ] 3.5 `mv sruth/oideachais/dlt_sources cianfhoghlaim/pipelines/ingest/`
- [ ] 3.6 `mv sruth/oideachais/dlt_utils cianfhoghlaim/core/dlt/`
- [ ] 3.7 `mv sruth/oideachais/baml_src/*.baml cianfhoghlaim/core/baml/` (consolidate to 6 files)
- [ ] 3.8 `mv sruth/oideachais/document_factory cianfhoghlaim/ocr/document_factory/`
- [ ] 3.9 `mv sruth/oideachais/training cianfhoghlaim/ocr/training/`
- [ ] 3.10 `mv sruth/oideachais/modal_finetune cianfhoghlaim/ocr/training/modal_finetune/`
- [ ] 3.11 `mv sruth/oideachais/alignment cianfhoghlaim/ocr/alignment/`
- [ ] 3.12 `mv sruth/oideachais/federated cianfhoghlaim/pipelines/process/federated/`
- [ ] 3.13 `mv sruth/oideachais/streaming cianfhoghlaim/pipelines/process/streaming/`
- [ ] 3.14 `mv sruth/oideachais/subjects cianfhoghlaim/core/curriculum/subjects/`
- [ ] 3.15 `mv sruth/oideachais/celtic cianfhoghlaim/core/curriculum/celtic/`
- [ ] 3.16 `mv sruth/oideachais/samplaí cianfhoghlaim/core/curriculum/samplaí/`
- [ ] 3.17 `mv sruth/oideachais/quality cianfhoghlaim/ocr/quality/`
- [ ] 3.18 `mv sruth/oideachais/geospatial cianfhoghlaim/ocr/geospatial/`
- [ ] 3.19 `mv sruth/oideachais/dagster_defs/assets cianfhoghlaim/assets/` (split: `components/`, `resources/`, `definitions.py`, `leabharlann.py`, etc.)
- [ ] 3.20 `mv sruth/oideachais/dagster_defs/sensors cianfhoghlaim/pipelines/sensors/`
- [ ] 3.21 `mv sruth/oideachais/dagster_defs/components cianfhoghlaim/assets/components/`
- [ ] 3.22 `mv sruth/oideachais/dagster_defs/resources.py cianfhoghlaim/assets/resources.py`
- [ ] 3.23 `mv sruth/oideachais/dagster_defs/__init__.py cianfhoghlaim/assets/__init__.py` (single code-location root)
- [ ] 3.24 `mv sruth/oideachais/agents cianfhoghlaim/agents/adk/` (DEPRECATED marker)
- [ ] 3.25 `mv sruth/oideachais/agent_os cianfhoghlaim/agents/api/`
- [ ] 3.26 `mv sruth/oideachais/web cianfhoghlaim/web/apps/oideachais-web/`
- [ ] 3.27 `mv sruth/oideachais/mcp cianfhoghlaim/web/apps/oideachais-mcp-filesystem/`
- [ ] 3.28 `mv sruth/oideachais/dlt_sources/{ie,en,ni,sct,wls,iom,jey,ggy}/ cianfhoghlaim/sources/nations/{ie,en,ni,sct,wls,iom,_preserved/{jey,ggy}}/` (split by nation)
- [ ] 3.29 `mv sruth/oideachais/dlt_sources/gaois cianfhoghlaim/sources/languages/` (gaois → gaeilge.py etc.)
- [ ] 3.30 `mv sruth/oideachais/dlt_sources/leabharlann cianfhoghlaim/pipelines/ingest/leabharlann/`
- [ ] 3.31 Delete `sruth/oideachais/` (now empty)

## 4. Migrate sruth/meaisinfhoghlaim/ → cianfhoghlaim/
- [ ] 4.1 `mv sruth/meaisinfhoghlaim/agents cianfhoghlaim/agents/meaisinfhoghlaim/` (12-agent fleet)
- [ ] 4.2 `mv sruth/meaisinfhoghlaim/ocr cianfhoghlaim/ocr/` (then split into `models/` + `backends/` + `evaluation/`)
- [ ] 4.3 `mv sruth/meaisinfhoghlaim/dagster_defs/assets/healthchecks.py cianfhoghlaim/assets/healthchecks.py`
- [ ] 4.4 `mv sruth/meaisinfhoghlaim/baml_src cianfhoghlaim/core/baml/_meaisinfhoghlaim_src/` (then consolidate)
- [ ] 4.5 `mv sruth/meaisinfhoghlaim/marimo cianfhoghlaim/notebooks/meaisinfhoghlaim/`
- [ ] 4.6 `mv sruth/meaisinfhoghlaim/language cianfhoghlaim/agents/language/` (Celtic-language agents)
- [ ] 4.7 `mv sruth/meaisinfhoghlaim/services cianfhoghlaim/agents/shared/services/`
- [ ] 4.8 `mv sruth/meaisinfhoghlaim/evaluation cianfhoghlaim/ocr/evaluation/meaisinfhoghlaim/` (CER/WER eval)
- [ ] 4.9 `mv sruth/meaisinfhoghlaim/catalog cianfhoghlaim/core/baml/catalog/` (asset catalog)
- [ ] 4.10 `mv sruth/meaisinfhoghlaim/pipelines cianfhoghlaim/pipelines/process/llm_router.py` (only llm_router.py — delete duplicates)
- [ ] 4.11 Delete `sruth/meaisinfhoghlaim/` (now empty)

## 5. Migrate sruth/tuatha/ → cianfhoghlaim/
- [ ] 5.1 `mv sruth/tuatha/agents cianfhoghlaim/agents/tuatha/` (4 agents)
- [ ] 5.2 `mv sruth/tuatha/baml_src cianfhoghlaim/core/baml/_tuatha_src/` (then consolidate)
- [ ] 5.3 `mv sruth/tuatha/cocoindex_flows cianfhoghlaim/embeddings/_tuatha/` (then split)
- [ ] 5.4 `mv sruth/tuatha/dagster_assets cianfhoghlaim/assets/tuatha.py` (consolidated)
- [ ] 5.5 `mv sruth/tuatha/crypteolas cianfhoghlaim/core/crypteolas/` (deferred - phased)
- [ ] 5.6 `mv sruth/tuatha/knowledge_graph cianfhoghlaim/core/rag/knowledge_graph/`
- [ ] 5.7 `mv sruth/tuatha/asset_generation cianfhoghlaim/assets/asset_generation/_tuatha/`
- [ ] 5.8 `mv sruth/tuatha/fibo_generation cianfhoghlaim/assets/asset_generation/fibo/`
- [ ] 5.9 `mv sruth/tuatha/notebooks cianfhoghlaim/notebooks/speedrun/`
- [ ] 5.10 `mv sruth/tuatha/dlt_sources cianfhoghlaim/sources/languages/_tuatha/` (geospatial sources)
- [ ] 5.11 `mv sruth/tuatha/ui cianfhoghlaim/web/apps/tuatha-ui/`
- [ ] 5.12 `mv sruth/tuatha/api cianfhoghlaim/agents/api/routes/`
- [ ] 5.13 `mv sruth/tuatha/wow cianfhoghlaim/docs/legacy/wow/`
- [ ] 5.14 `mv sruth/tuatha/Hades II cianfhoghlaim/docs/legacy/Hades II/`
- [ ] 5.15 Delete `sruth/tuatha/` (now empty)

## 6. Migrate sruth/croilar/ → cianfhoghlaim/
- [ ] 6.1 `mv sruth/croilar/_shared cianfhoghlaim/core/config/_croilar/`
- [ ] 6.2 `mv sruth/croilar/config cianfhoghlaim/core/config/`
- [ ] 6.3 `mv sruth/croilar/agent_os cianfhoghlaim/agents/api/agent_os/`
- [ ] 6.4 `mv sruth/croilar/{baml,baml_src} cianfhoghlaim/core/baml/_croilar_src/`
- [ ] 6.5 `mv sruth/croilar/convex cianfhoghlaim/agents/api/convex/`
- [ ] 6.6 `mv sruth/croilar/dagster_assets cianfhoghlaim/assets/croilar/` (22 stream-driven assets)
- [ ] 6.7 `mv sruth/croilar/definitions.py cianfhoghlaim/assets/definitions_croilar.py` (merge into main `definitions.py`)
- [ ] 6.8 `mv sruth/croilar/hono-api cianfhoghlaim/web/hono-api/`
- [ ] 6.9 `mv sruth/croilar/mcp cianfhoghlaim/agents/mcp_server/`
- [ ] 6.10 `mv sruth/croilar/notebooks cianfhoghlaim/notebooks/croilar/`
- [ ] 6.11 `mv sruth/croilar/services cianfhoghlaim/agents/shared/`
- [ ] 6.12 `mv sruth/croilar/apps/web cianfhoghlaim/web/apps/croilar-web/`
- [ ] 6.13 `mv sruth/croilar/apps/portal cianfhoghlaim/web/apps/croilar-portal/`
- [ ] 6.14 `mv sruth/croilar/image-pipeline cianfhoghlaim/agents/image_pipeline/`
- [ ] 6.15 `mv sruth/croilar/game_showcase cianfhoghlaim/web/apps/game_showcase/`
- [ ] 6.16 `mv sruth/croilar/packages cianfhoghlaim/web/packages/`
- [ ] 6.17 Delete `sruth/croilar/{Dockerfile.dagster,dagster.yaml,compose.yaml,compose.dev.yaml,sidecar.yaml,mise.toml,secrets.env,wrangler.toml,dg.toml,definitions.py,__pycache__}` (root-level files redundant)
- [ ] 6.18 Delete `sruth/croilar/` (now empty)

## 7. Migrate sruth/codeolas/ → cianfhoghlaim/libraries/codeolas/
- [ ] 7.1 `mv sruth/codeolas/{core,chunking,search,graph,generators,mcp_server,cli,tests} cianfhoghlaim/libraries/codeolas/`
- [ ] 7.2 `mv sruth/codeolas/cocoindex_flows cianfhoghlaim/embeddings/_codeolas/` (then split into `embeddings/{code_embedding,file_graph_embedding}.py`)
- [ ] 7.3 `mv sruth/codeolas/dagster_assets cianfhoghlaim/assets/codeolas.py`
- [ ] 7.4 `mv sruth/codeolas/compose.{yaml,dev.yaml} cianfhoghlaim/stacks/codeolas/`
- [ ] 7.5 Delete `sruth/codeolas/` (now empty)

## 8. Migrate sruth/crypteolas/ patterns (excluding defi)
- [ ] 8.1 `mv sruth/crypteolas/pipelines/github_api cianfhoghlaim/pipelines/ingest/github_indexer.py`
- [ ] 8.2 `mv sruth/crypteolas/pipelines/cognee cianfhoghlaim/core/cognee/_crypteolas_pipelines/`
- [ ] 8.3 `mv sruth/crypteolas/pipelines/cocoindex cianfhoghlaim/core/cocoindex/_crypteolas_pipelines/`
- [ ] 8.4 `mv sruth/crypteolas/dlt_sources/{github,documentation,local} cianfhoghlaim/pipelines/ingest/` (NOT defi/)
- [ ] 8.5 `mv sruth/crypteolas/mcp_server cianfhoghlaim/agents/mcp_server/_crypteolas/`
- [ ] 8.6 `mv sruth/crypteolas/knowledge_graph cianfhoghlaim/core/cognee/_crypteolas_clients/`
- [ ] 8.7 `mv sruth/crypteolas/apps/crypteolas_demo cianfhoghlaim/web/apps/croilar-demo/`
- [ ] 8.8 **EXCLUDE** `sruth/crypteolas/dlt_sources/defi/` (okx, coingecko, bybit, binance, defillama, beaconchain, subgraphs)
- [ ] 8.9 **EXCLUDE** `sruth/crypteolas/baml_src/{crypto_extraction,vulnerability_assessment,protocol_analysis}.baml`
- [ ] 8.10 `mv sruth/crypteolas cianfhoghlaim/docs/legacy/crypteolas/` (preserve snapshot for reference)

## 9. Promote infrastructure/browser/ → cianfhoghlaim/core/browser/
- [ ] 9.1 `mv infrastructure/browser/sruth_browser cianfhoghlaim/core/browser/sruth_browser/` (full 20-dir package)
- [ ] 9.2 `mv infrastructure/browser/{compose.yaml,Dockerfile,Dockerfile.proxy,stagehand_proxy.py,pyproject.toml} cianfhoghlaim/core/browser/`
- [ ] 9.3 `mv infrastructure/browser/agent_os cianfhoghlaim/core/browser/agent_os/`
- [ ] 9.4 `mv infrastructure/browser/tests cianfhoghlaim/core/browser/tests/`
- [ ] 9.5 Delete `infrastructure/browser/` (now empty)

## 10. Move /leabharlann/ → cianfhoghlaim/leabharlann/
- [ ] 10.1 `mv leabharlann/{aigne,gaeilge,gemini_deep_research,mata,ollscoil_na_gaillimhe,zotero} cianfhoghlaim/leabharlann/`
- [ ] 10.2 Delete `leabharlann/` (now empty)

## 11. Update monorepo manifests
- [ ] 11.1 Rewrite root `pyproject.toml`: single workspace member `"cianfhoghlaim"` (drop `sruth/*`, `infrastructure/browser`)
- [ ] 11.2 Rewrite root `package.json`: workspaces = `["cianfhoghlaim/web/apps/*", "cianfhoghlaim/web/packages/*", "cianfhoghlaim/web/hono-api"]`
- [ ] 11.3 Rewrite `dg.toml`: single code-location `module_name = "cianfhoghlaim.assets.definitions"`
- [ ] 11.4 Patch `mise.toml`: drop `cd sruth/*` aliases; add `cianfhoghlaim` aliases
- [ ] 11.5 Patch `turbo.json`: `src` glob to `cianfhoghlaim/{core,pipelines,sources,assets,agents,notebooks,web}/**`

## 12. Update openspec documentation
- [ ] 12.1 Rewrite `openspec/project.md`: subproject table — 4 quadrants → 1 `cianfhoghlaim/` with 16 sub-packages
- [ ] 12.2 Update `openspec/AGENTS.md`: quadrant map, AGENTS.md paths, spec delta examples
- [ ] 12.3 Update 4 quadrant AGENTS.md files: path refs to `cianfhoghlaim/{core,sources,assets,agents,notebooks,ocr}/`
- [ ] 12.4 Update `AGENTS.md` (root): quadrant routing tables, file paths
- [ ] 12.5 Update root `README.md`: Monorepo Topology, file paths

## 13. Source schema refactor (Plan 1)
- [ ] 13.1 Create `cianfhoghlaim/sources/languages/{gaeilge,cymraeg,gaidhlig,gaelg,kernewek,brezhoneg}.py` (7 files, language-first)
- [ ] 13.2 Create `cianfhoghlaim/sources/nations/ie/education/{early_childhood,primary,junior_cycle,senior_cycle,leaving_cert}/{english,gaeilge}.py` (10 files, Plan 1 active)
- [ ] 13.3 Create `cianfhoghlaim/sources/nations/{en,ni,wls,sct,iom}/education/{early_childhood,primary,secondary}/` (15 stub files, Plan 2 preserved)
- [ ] 13.4 Create `cianfhoghlaim/sources/nations/{en,ni,wls,sct,iom}/{law,medicine,culture,government,intelligence,statistics,geospatial}/` (35 stub files, Plan 3 preserved)
- [ ] 13.5 Create `cianfhoghlaim/sources/_preserved/{jey,ggy}/` (2 legacy stub files)
- [ ] 13.6 Add cross-doc note: "Source schema layout is provisional — refactor after Plan 1 informs best CocoIndex + DLT + DuckDB + DuckLake + Lance patterns"

## 14. Plan 1 activation (post-consolidation)
- [ ] 14.1 Create `cianfhoghlaim/core/cocoindex/ocr_aware_flow.py` (NEW — CocoIndex flow with OCR backend + vision model selection)
- [ ] 14.2 Create `cianfhoghlaim/core/cocoindex/leabharlann_flow.py` (NEW — CocoIndex flow for leabharlann filesystem + Zotero)
- [ ] 14.3 Create `cianfhoghlaim/ocr/models/registry.py` (NEW — 11 vision models: Gemma-4×4 + Qwen3.6×4 + GLM-4.6V)
- [ ] 14.4 Create `cianfhoghlaim/ocr/evaluation/compare.py` (NEW — vision vs classical OCR harness)
- [ ] 14.5 Create `cianfhoghlaim/notebooks/ireland_curriculum_analysis.py` (NEW — Ireland education analytics dashboard)
- [ ] 14.6 Create `cianfhoghlaim/notebooks/leabharlann/{aigne,gaeilge,gemini_deep_research,mata,ollscoil_na_gaillimhe,zotero}_analysis.py` (6 NEW)
- [ ] 14.7 Create `cianfhoghlaim/assets/asset_generation/{official_documents,subject_assets,language_assets,exporters}/` (4 successive independent pipelines)
- [ ] 14.8 Create `cianfhoghlaim/core/baml/curriculum.baml` (NEW — Ireland education BAML extraction consolidated)
- [ ] 14.9 Create `cianfhoghlaim/core/baml/culture.baml` (NEW — Celtic languages BAML extraction consolidated)
- [ ] 14.10 Create `cianfhoghlaim/core/baml/document.baml` (NEW — OCR-aware document extraction)
- [ ] 14.11 Create `cianfhoghlaim/core/baml/gaois.baml` (NEW — teanglann + gaois asset generation)
- [ ] 14.12 Create `cianfhoghlaim/core/baml/code_intel.baml` (NEW — codeolas code extraction)

## 15. Run quality gates
- [ ] 15.1 `mise run lint` (lint all)
- [ ] 15.2 `mise run py:typecheck` (Python type check)
- [ ] 15.3 `mise run turbo typecheck` (TypeScript type check)
- [ ] 15.4 `openspec validate 2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4 --strict` (final)
- [ ] 15.5 `dg validate cianfhoghlaim` (Dagster code-location)

## 16. Hand off
- [ ] 16.1 Stop here for user to commit + push per "Landing the Plane" protocol
- [ ] 16.2 After commit: launch Plan 1 (Ireland + leabharlann BB research, 6,000 min)