# cianfhoghlaim

> **The consolidated Cianfhoghlaim platform** (v4 consolidation, 2026-06-28).
> Celtic education + multi-nation + multi-language data platform, AI/ML
> services, Túatha educational MMO, and Croílár multi-persona portfolio —
> all in a single Python package, served from a single Dagster code-location
> and orchestrated by a single monorepo.

> **Provisional schema note:** The `sources/` and `core/cocoindex/` layouts
> below are provisional. Plan 1 (Ireland + leabharlann) will inform the best
> CocoIndex + DLT + DuckDB + DuckLake + Lance patterns; refactor after the
> first 216 leabharlann docs + 5×2 Ireland sources land. See
> `openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/`.

## Layout

```
cianfhoghlaim/
├── core/                # 16 first-class stack packages
│   ├── dlt/             # ingestion (filesystem, rest_api, cross-domain-registry)
│   ├── duckdb/          # local OLAP + DuckLake
│   ├── ducklake/        # ACID lakehouse (Parquet on Garage S3 + Postgres catalog)
│   ├── lancedb/         # vector DB + HNSW
│   ├── motherduck/      # managed reads (`md:oideachais`)
│   ├── cocoindex/       # v1 App pattern + NEW v4 OCR-aware flows
│   ├── baml/            # 6 consolidated BAML files (was 21)
│   ├── marimo/          # reactive notebook framework
│   ├── browser/         # ← NEW v4 (promoted from infrastructure/browser/)
│   ├── cognee/          # knowledge graph + cognify
│   ├── obs/             # Langfuse + MLflow + RAGAS + Logfire
│   ├── rag/             # hybrid retrieval + RAGAS eval
│   ├── search/          # semantic + faceted search
│   ├── curriculum/      # Celtic curriculum domain models
│   ├── config/          # Pydantic BaseSettings + Infisical loader
│   └── memory/          # agent memory (Cognee + Graphiti + Letta)
│
├── pipelines/           # 5-stage ingestion→expose pipeline
│   ├── ingest/          # dlt sources → DuckLake
│   ├── extract/         # BAML extraction
│   ├── embed/           # CocoIndex v1 → LanceDB HNSW
│   ├── cognify/         # Cognee knowledge graph
│   └── expose/          # MotherDuck + marimo + agents
│
├── sources/             # ← NEW v4 simplified
│   ├── nations/         # 6 active + 2 legacy nations × 3-5 education stages
│   │   ├── ie/          # Plan 1: 5 stages × {english, gaeilge} = 10 ACTIVE
│   │   ├── en, ni, wls, sct, iom/  # Plan 2: preserved stubs
│   │   └── _preserved/{jey,ggy}/   # legacy Crown Dependencies
│   └── languages/       # 7 Celtic + English languages (Plan 1: english, gaeilge ACTIVE)
│
├── assets/              # ← NEW v4 single Dagster code-location
│   ├── definitions.py   # single entry point (`dg` module_name = "cianfhoghlaim.assets.definitions")
│   └── asset_generation/  # 4 successive INDEPENDENT asset gen pipelines
│
├── agents/              # 8 subdirs
│   ├── meaisinfhoghlaim/  # 12-agent fleet (Agno + ADK + Pipecat + CopilotKit)
│   ├── tuatha/            # Babylon.js + SpacetimeDB + crypteolas
│   ├── oideachais/        # curriculum agents
│   ├── croilar/           # persona agents
│   ├── root/              # orchestrator
│   ├── mcp/               # MCP server glue
│   └── ...
│
├── notebooks/           # 7 marimo notebooks
│   ├── ireland_curriculum_analysis.py    # Plan 1
│   └── leabharlann/                      # 6 subdir analyses (Plan 1)
│
├── stacks/              # ← NEW v4 33 user-pre-selected compose stacks
│   └── ...
│
├── web/                 # 8 bun workspaces
│   ├── apps/{oideachais-web, tuatha-ui, croilar-web, croilar-portal, ...}/
│   ├── packages/
│   └── hono-api/
│
├── ocr/                 # ← NEW v4 OCR registry (was sruth/meaisinfhoghlaim/ocr/)
│   ├── models/registry.py    # 11 vision + 4 classical + 3 image gen
│   ├── evaluation/compare.py # harness skeleton
│   └── ...
│
├── embeddings/          # CocoIndex + LanceDB embeddings
├── cognify/             # Cognee cognify passes
│
├── leabharlann/         # ← NEW v4 (was /leabharlann/)
│   ├── aigne/                # 72 docs
│   ├── gaeilge/              # 38 docs
│   ├── gemini_deep_research/ # 24 docs
│   ├── mata/                 # 27 docs
│   ├── ollscoil_na_gaillimhe/ # 21 docs
│   └── zotero/               # 34 docs
│   # total: 216 docs
│
├── libraries/
│   └── codeolas/        # publishable sub-package (was sruth/codeolas/)
│
├── docs/legacy/         # preserve-intent snapshots
│   ├── wow/             # World of Warcraft snapshot
│   ├── hades_ii/        # Hades II snapshot
│   └── crypteolas/      # standalone crypteolas snapshot
│
├── tests/               # pytest
├── scripts/             # CLI entry points (ingest, extract, embed, cognify, expose)
└── ops/                 # observability + ops utilities
```

## Quick commands

```bash
# Import the package
uv run python -c "import cianfhoghlaim; print(cianfhoghlaim.__version__)"
# → 0.1.0

# Launch the single Dagster UI
mise run dagster:oideachais
# → http://localhost:3000 (single code-location: cianfhoghlaim.assets.definitions)

# Run OCR evaluation harness
uv run python -m cianfhoghlaim.ocr.evaluation.compare

# Run ccc semantic code search
bun run ccc:search "BAML extraction Ireland curriculum"

# Validate the openspec change
bun run spec:validate 2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4 --strict
```

## Sub-project AGENTS.md

- `agents/meaisinfhoghlaim/AGENTS.md` — 12-agent fleet
- `agents/tuatha/AGENTS.md` — Babylon.js + SpacetimeDB + crypteolas
- `web/apps/_oideachais_apps/AGENTS.md` — TanStack Start + Celtic education data platform
- `web/apps/croilar-web/AGENTS.md` — multi-persona portfolio

## Related

- `openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/` — the consolidation proposal
- `openspec/AGENTS.md` — openspec workflow
- `/AGENTS.md` — root agent instructions