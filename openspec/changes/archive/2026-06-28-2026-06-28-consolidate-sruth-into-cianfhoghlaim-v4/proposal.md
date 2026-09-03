# Consolidate sruth/* into cianfhoghlaim/v4 — single layered root with 33 selfhosted stacks

## Why

The Cianfhoghlaim monorepo has accumulated 6 `sruth/*` quadrants (`oideachais/`, `meaisinfhoghlaim/`, `tuatha/`, `croilar/`, `codeolas/`, `crypteolas/`) plus a separate `infrastructure/browser/` package plus a 90-stack `infrastructure/stacks/` directory plus a top-level `leabharlann/` corpus directory. The proliferation of top-level paths makes it hard to:

1. **Discover** what is part of the platform vs what is third-party.
2. **Refactor** shared concerns (BAML extraction, CocoIndex embedding, OCR routing) — they are copy-pasted across quadrants.
3. **Onboard** new developers — the 4-quadrant + 90-stack mental model is too many moving parts.
4. **Activate** Ireland + leabharlann simultaneously — code lives in 6 different packages.

The user has pre-selected 33 critical selfhosted stacks to be consolidated at `cianfhoghlaim/stacks/` (already populated). The remaining 57 stacks (out of 90) are deferred or kept at `infrastructure/stacks/`. The `sruth/*` quadrants are now consolidated into a single layered `cianfhoghlaim/` root with 16 stack packages, 5 pipeline stages, and a `sources/languages/` (or `sources/nations/`) hierarchy.

This change also acknowledges that the source-schema layout (sources/languages vs sources/nations vs cross-tagged) is **provisional** — it will be refactored after Plan 1 (Ireland + leabharlann) informs the best CocoIndex + DLT + DuckDB + DuckLake + Lance patterns for multi-nation + multi-language + multimodal processing.

## What Changes

### 1. Create layered `cianfhoghlaim/` root directory

```
cianfhoghlaim/
├── core/           # 16 stack packages first-class
│   ├── dlt/        # dlt destination + source factories
│   ├── duckdb/
│   ├── ducklake/
│   ├── lancedb/    # HNSW + hybrid search
│   ├── motherduck/
│   ├── cocoindex/  # ocr_aware_flow.py + leabharlann_flow.py
│   ├── baml/       # 6 consolidated BAML files
│   ├── marimo/
│   ├── browser/    # promoted from infrastructure/browser/
│   ├── cognee/
│   ├── obs/        # langfuse + mlflow + logfire shims
│   ├── rag/        # hybrid search (BGE-M3 + BGE-large)
│   ├── search/     # ccc + cognee
│   ├── curriculum/ # LC subjects + celtic + samplaí
│   ├── config/     # streams + settings + sources.yaml
│   └── memory/     # graphiti + falkordb + memgraph
├── pipelines/      # 5-stage pipeline spine
│   ├── browser/
│   ├── ingest/     # leabharlann/* + sources/*
│   ├── distribute/ # s3 + lance + ducklake
│   ├── process/    # cocoindex + ocr + baml + federated + streaming
│   └── expose/     # motherduck + marimo + agents
├── sources/        # language-first (Plan 1) — refactorable later
│   ├── languages/  # 7 Celtic languages × full
│   │   ├── gaeilge.py         # Plan 1 ACTIVE (teanglann + gaois)
│   │   ├── cymraeg.py         # Plan 2 preserved (gov.wales)
│   │   ├── gaidhlig.py        # Plan 2 preserved (hiddenheritages.ai)
│   │   ├── gaelg.py           # Plan 2 preserved (cultrix)
│   │   ├── kernewek.py        # Plan 2 preserved (kernowek / Kernewek)
│   │   └── brezhoneg.py       # Plan 2 preserved (ofis-bzh)
│   └── nations/    # 8 nations × 8 domains (cross-tagged)
│       ├── ie/education/{early_childhood,primary,junior_cycle,senior_cycle,leaving_cert}/{english,gaeilge}.py
│       ├── en/education/{early_childhood,primary,secondary}/  # Plan 2
│       ├── ni/education/{early_childhood,primary,secondary}/  # Plan 2
│       ├── wls/education/{early_childhood,primary,secondary}/ # Plan 2
│       ├── sct/education/{early_childhood,primary,secondary}/ # Plan 2
│       ├── iom/education/{early_childhood,primary,secondary}/ # Plan 2
│       ├── {en,ni,wls,sct,iom}/{law,medicine,culture,government,intelligence,statistics,geospatial}/  # Plan 3
│       └── _preserved/{jey,ggy}/  # legacy stubs (Crown Dependencies)
├── assets/         # 4 successive independent asset gen pipelines
│   ├── asset_generation/
│   │   ├── official_documents/{syllabus,exam_papers,marking_schemes}/
│   │   ├── subject_assets/{chemistry_lab,geography_landscape,biology_specimens,physics_apparatus}/
│   │   ├── language_assets/{gaeilge,cymraeg,gaidhlig,gaelg,kernewek,brezhoneg}_assets.py
│   │   └── exporters/{babylon,godot,unity,unreal}.py
│   ├── components/ # 3 KCG Components (DltSource, LancedbHnsw, CocoindexV1)
│   ├── resources/  # 19 ConfigurableResources consolidated
│   ├── definitions.py  # single Dagster code-location
│   └── leabharlann.py  # 7 leabharlann assets
├── agents/         # 12 meaisinfhoghlaim + 4 tuatha + ADK shims + image_pipeline
│   ├── api/
│   ├── tuatha/
│   ├── shared/
│   └── image_pipeline/
├── notebooks/      # 26+ marimo notebooks preserved
│   ├── ireland_curriculum_analysis.py  # Plan 1 NEW
│   ├── speedrun/  # 9 tuatha notebooks
│   ├── {music,teaching,cv,research}/  # croilar streams
│   └── leabharlann/{aigne,gaeilge,gemini_deep_research,mata,ollscoil_na_gaillimhe,zotero}_analysis.py  # Plan 1
├── stacks/         # 33 pre-selected stacks (already populated by user)
├── web/            # 4 TanStack apps + 6 component packages + hono-api
├── ocr/            # 11 vision + 3 image gen + 4 classical Docker
│   ├── models/     # 11 vision models (Gemma-4×4 + Qwen3.6×4 + GLM-4.6V)
│   ├── backends/   # litellm + mlx-omni + llama-swap + 4 classical Docker
│   ├── evaluation/compare.py  # vision vs classical harness
│   ├── document_factory/  # PDF factory + 5 converters
│   ├── alignment/  # ColPali + Irish G2P + Canuint
│   ├── training/   # HTR + LLM + TTS + modal_finetune
│   ├── quality/
│   └── geospatial/
├── embeddings/     # 14+ CocoIndex v1 Apps consolidated
├── cognify/        # 5-stage cognify pipeline
├── leabharlann/    # 6 subdirs (aigne, gaeilge, gemini_deep_research, mata, ollscoil_na_gaillimhe, zotero)
├── libraries/
│   └── codeolas/   # publishable sub-package
├── docs/legacy/    # WoW + Hades II + standalone crypteolas snapshot
├── tests/
├── scripts/
└── ops/
```

### 2. Migrate `sruth/*` → `cianfhoghlaim/`

- `sruth/oideachais/` → split into `cianfhoghlaim/core/{dlt,duckdb,ducklake,lancedb,motherduck,cocoindex,baml,marimo,browser,obs,rag,search,curriculum,config}/` + `sources/languages/{gaeilge,...}.py` + `sources/nations/ie/education/{early_childhood,primary,junior_cycle,senior_cycle,leaving_cert}/{english,gaeilge}.py` + `assets/{components,resources,leabharlann,definitions}.py` + `ocr/{document_factory,alignment,training,quality,geospatial}/` + `embeddings/` + `cognify/`
- `sruth/meaisinfhoghlaim/` → `cianfhoghlaim/{agents/,ocr/{models,backends}/,core/baml/,notebooks/,marimo/}`
- `sruth/tuatha/` → `cianfhoghlaim/{agents/tuatha/,assets/asset_generation/,notebooks/speedrun/,core/baml/culture.baml,embeddings/culture_heritage.py}` + `docs/legacy/{wow,Hades II}/`
- `sruth/croilar/` → `cianfhoghlaim/{agents/api/,web/apps/{croilar-web,croilar-portal}/,web/packages/{auth,db,ui,i18n,config,analytics}/,web/hono-api/,agents/mcp_server/,notebooks/{music,teaching,cv,research}/,agents/image_pipeline/,web/apps/game_showcase/,agents/shared/}`
- `sruth/codeolas/` → `cianfhoghlaim/libraries/codeolas/` + `embeddings/{code_embedding,file_graph_embedding}.py`
- `sruth/crypteolas/` patterns (excluding `dlt_sources/defi/`, `baml_src/{crypto_extraction,vulnerability_assessment,protocol_analysis}.baml`) → `cianfhoghlaim/{pipelines/{ingest,process}/,core/{cognee,cocoindex}/,agents/mcp_server/,web/apps/croilar-demo/}`. EXCLUDED financial DeFi sources.
- `infrastructure/browser/` → `cianfhoghlaim/core/browser/` (full 20-dir `sruth_browser/` package)
- `/leabharlann/` → `cianfhoghlaim/leabharlann/` (moved as-is, 6 subdirs × 216 documents)

### 3. Update monorepo manifests

- **Root `pyproject.toml`**: collapse 7 workspace members → 1 (`cianfhoghlaim` itself).
- **Root `package.json`**: collapse workspaces → `["cianfhoghlaim/web/apps/*", "cianfhoghlaim/web/packages/*", "cianfhoghlaim/web/hono-api"]`.
- **`dg.toml`**: collapse 6 code-locations → 1 (`module_name = "cianfhoghlaim.assets.definitions"`).
- **`mise.toml`**: drop per-quadrant `cd sruth/*` aliases; add `cianfhoghlaim` aliases.
- **`turbo.json`**: keep but reference `cianfhoghlaim/{core,pipelines,sources,assets,agents,notebooks}/`.

### 4. Update documentation

- `openspec/project.md`: rewrite subproject table — 4 quadrants → 1 `cianfhoghlaim/` with 16 sub-packages.
- `openspec/AGENTS.md`: update quadrant map, AGENTS.md paths, spec delta examples.
- `AGENTS.md` (root): update quadrant routing tables, file paths.
- 4 quadrant AGENTS.md files: `sruth/oideachais/AGENTS.md` → `cianfhoghlaim/core/AGENTS.md` (or split per sub-package).

### 5. Preserve explicit assets

- **Crown Dependencies**: `sources/_preserved/{jey,ggy}/` (legacy stubs, NOT deleted).
- **WoW + Hades II**: `docs/legacy/{wow,Hades II}/` with origin READMEs.
- **Crypteolas standalone snapshot**: `docs/legacy/crypteolas/` (broken `definitions.py` preserved as historical).
- **preserve-intent dirs**: `ocr/{document_factory,training,modal_finetune,alignment,quality,geospatial}/` + `core/curriculum/{subjects,celtic,samplaí}/` + `pipelines/process/{federated,streaming}/` + `agents/image_pipeline/` + `web/apps/game_showcase/` — all preserved.

### 6. Plan 1 activation (post-consolidation)

- Plan 1 = Ireland + leabharlann, 6,000 BB min, 25 parallel browsers, 48h push window.
- Will use `core/cocoindex/ocr_aware_flow.py` + `core/cocoindex/leabharlann_flow.py` (NEW) to integrate OCR + CocoIndex.
- OCR evaluation harness `ocr/evaluation/compare.py` runs 11 vision × 4 classical × Ireland syllabus + leabharlann corpus = ~220 evals.
- Analytics dashboards: `notebooks/ireland_curriculum_analysis.py` (NEW) + `notebooks/leabharlann/{aigne,gaeilge,gemini_deep_research,mata,ollscoil_na_gaillimhe,zotero}_analysis.py` (6 NEW).
- Educational asset gen: 4 successive independent pipelines (official_documents → subject_assets → language_assets → exporters).
- BrowserBase research AFTER Plan 1 — uses `core/browser/` + `pipelines/ingest/` + Ireland sources.

## Impact

| Surface | Before | After |
|:--|:--|:--|
| Top-level dirs | `sruth/`, `infrastructure/`, `leabharlann/` | `cianfhoghlaim/` (1 root) |
| Top-level subdirs | 4 quadrants + browser + stacks | 16 `core/` packages + 5 `pipelines/` stages + 7+ `sources/` files + 4 `assets/` subdirs + 4 `agents/` subdirs + 6 `ocr/` subdirs + 2 `leabharlann/` subdirs |
| Workspace members (uv) | 7 | 1 (`cianfhoghlaim`) |
| Bun workspaces | 6 | 3 (`cianfhoghlaim/web/{apps,packages,hono-api}`) |
| Dagster code-locations | 6 | 1 (`cianfhoghlaim.assets.definitions`) |
| BAML files | 21 | 6 (consolidated) |
| Selfhosted stacks activated | 90 | 33 (user pre-selected subset) |
| OCR vision models | 9 (9×6 registry) | 11 (Gemma-4×4 + Qwen3.6×4 + GLM-4.6V) |
| Classical OCR Docker stacks | 0 (4 unused) | 4 first-class (olmocr + docling-serve + dots-ocr + paddleocr) |
| CocoIndex OCR-aware flows | 0 | 2 (`ocr_aware_flow.py` + `leabharlann_flow.py`) |
| Asset gen pipelines | 0 | 4 successive independent |
| Source files (Plan 1) | 0 | 10 (5 Ireland education levels × 2 languages) |
| Leabharlann docs | 216 (orphaned at root) | 216 (consolidated under `cianfhoghlaim/leabharlann/`) |
| Marimo notebooks | 26+ (across 4 quadrants) | 26+ (consolidated in `cianfhoghlaim/notebooks/`) |
| Plan 1 BB minutes | 0 | 6,000 |