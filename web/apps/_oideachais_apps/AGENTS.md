# Oideachais Quadrant — Agent Instructions

> **The Celtic Education Lakehouse Engine.** The offline-first ELT
> engine and lakehouse that powers the entire `cianfhoghlaim` stack.

> **v4 consolidation note (2026-06-28):** The `sruth/oideachais/`
> directory was migrated into `cianfhoghlaim/` per
> `openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/`.
> The data platform now lives at `cianfhoghlaim/{core,pipelines,sources,assets}/`
> with a **single Dagster code-location** (`assets/definitions.py`),
> a **single package** (`cianfhoghlaim`), and one `pyproject.toml`.
> This file remains as the per-app routing reference; the canonical
> home for the platform is now `cianfhoghlaim/`.

## Priority quick reference

The 8 priority skills, the 4 priority commands, the 4 priority
compose ports, and the 4 priority openspec specs at a glance.
**Read this first**; the rest of the file is the full BAML ×
DLT × Dagster × CocoIndex matrix routing.

### Priority skills (9 of 108)

| Skill | When to load |
|:--|:--|
| [`baml`](../.agents/skills/baml/SKILL.md) | BAML extraction schemas (`sruth/oideachais/baml_src/`) |
| [`dagster`](../.agents/skills/dagster/SKILL.md) | Dagster asset patterns + `dg` CLI + the 5 KCG code-locations |
| [`dlt`](../.agents/skills/dlt/SKILL.md) | DLT source patterns (filesystem / rest_api / cross-domain-registry) |
| [`cognee`](../.agents/skills/cognee/SKILL.md) | Cognee cognify (5-stage curriculum KG + temporal + improve()) |
| [`lancedb`](../.agents/skills/lancedb/SKILL.md) | HNSW vector search + the v1 App pattern |
| [`motherduck`](../.agents/skills/motherduck/SKILL.md) | MotherDuck storage pattern (managed / BYOB / DuckLake / own-compute) + MCP |
| [`oideachais-storage`](../.agents/skills/oideachais-storage/SKILL.md) | The KCG storage mental model (DuckLake 1.0 + Lance Namespace) |
| [`oideachais-pipeline`](../.agents/skills/oideachais-pipeline/SKILL.md) | The canonical lakehouse pipeline (DLT + Dagster + CocoIndex + BAML) |
| [`oideachais-cocoindex-v1`](../.agents/skills/oideachais-cocoindex-v1/SKILL.md) | CocoIndex v1 App canonical pattern + 4-rule conformance contract + `_lifespan.py` shared home (REFACTORING.md item 12 enforcement precondition) |

### ccc + openspec commands

```bash
bun run ccc:search "Dagster asset partition definition"  # semantic code search
openspec list --specs                                    # 32 specs total
openspec validate <change-id> --strict                   # MUST pass before commit
openspec archive <change-id> --yes                       # after deploy
```

### Priority compose ports (the oideachais stack)

| Service | Port | Healthcheck |
|:--|--:|:--|
| `dagster` | 3335 | `/server_info` |
| `api` | 8000 | `/health` |
| `frontend` | 3080 | `/` |
| `agent_os` | 7777 | `/health` |
| `adk_agents` | 7778 | `/health` |

### Priority openspec specs for oideachais

| Spec | One-liner |
|:--|:--|
| `oideachais-pipeline` | Celtic education curriculum pipeline (Dagster + DLT + DuckLake + LanceDB + BAML) |
| `oideachais-leabharlann` | 4 dlt sources + 3 v1 CocoIndex Apps |
| `oideachais-baml-schemas` | 9 BAML files + 3 extraction clients |
| `oideachais-cognify-knowledge-graph` | 5-stage cross-stage cognify + 3 leabharlann cognify + 3 cross-archive FalkorDB edges |

## Overview

`sruth/oideachais/` is the **Celtic education data platform** quadrant of the
Cianfhoghlaim monorepo. It is a uv workspace member that contains:

- **DLT ingestion** — 30+ Irish sources, 4 UK nations, 3 Crown Dependencies,
  4 leabharlann corpora (books, zotero, takeout, UoG)
- **Dagster orchestration** — 21 asset modules covering the 5 educational
  stages (Aistear, Primary, JC, SC, Tertiary) and the leabharlann
  full-stack demo
- **BAML extraction** — 9 BAML files (`baml_src/`) with 3 extraction
  clients (ExtractEn, ExtractEnStrong, LocalVision)
- **CocoIndex flows** — 8 v0 flows + 3 new v1 leabharlann flows
- **Cognee + FalkorDB knowledge graph** — 5-stage cross-stage cognify +
  3 leabharlann cognify datasets + 3 cross-archive edge types
- **Marimo dashboards** — 11 reactive Python notebooks at
  `sruth/oideachais/notebooks/`
- **FastAPI** — at `sruth/oideachais/api/main.py` with the AG-UI streaming
  endpoints

The re-export shims to `sruth/meaisinfhoghlaim/`:

- `sruth/oideachais/agents/{adk,agno}/` — application-layer agent facades
  (front-end CopilotKit / AG-UI). The actual model-layer agents live in
  `sruth/meaisinfhoghlaim/agents/`.
- `sruth/oideachais/ocr/` — application-layer OCR wrapper (the
  `author_archive_ocr.py` and `pylaia_comparison.py` modules). The
  actual model-layer OCR models live in `sruth/meaisinfhoghlaim/ocr/`.
- `sruth/oideachais/memory/` — application-layer Cognee + Graphiti wrappers.
- `sruth/oideachais/graph/` — application-layer FalkorDB + Memgraph clients.
- `sruth/oideachais/knowledge_graph/` — application-layer
  `cross_stage_cognify` (the 5-stage curriculum knowledge graph).

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new education-domain dlt source for any nation (IE / EN / SCT / WLS / NI / IOM / JEY / GGY) | `sruth/oideachais/dlt_sources/domains/education/{nation}/{source}.py` (the canonical location, per `cross-domain-registry/SKILL.md`; replaces the legacy `dlt_sources/uk/`, `dlt_sources/ireland/`, and `dlt_sources/crown_dependencies/` paths) |
| Add a new medicine or law domain dlt source | `sruth/oideachais/dlt_sources/domains/{medicine|law}/{nation}/{source}.py` |
| Add a new leabharlann source | `sruth/oideachais/dlt_sources/leabharlann/` (the 4 dlt sources) |
| Add a new culture-heritage source (the 6th domain) | `sruth/oideachais/dlt_sources/domains/culture/{nation}/{source}.py` (e.g. `ie/heritage_source.py`); see `openspec/specs/cross-domain-registry/SKILL.md` for the Wikipedia dual-write convention |
| Add a new BAML extraction function | `baml_src/` (the 28 BAML files incl. `culture_extraction.baml`, plus `_archive/` for deferred consumers) + `baml_src/clients.baml` for the canonical client registry |
| Add a new Dagster asset | `sruth/oideachais/dagster_defs/assets/` (40+ modules, including `culture_heritage_assets.py` with 4 assets + `low_confidence_review` asset check) |
| Add a new CocoIndex v1 App | `sruth/oideachais/cocoindex_flows/leabharlann_embedding.py` (the 3 v1 Apps) or `docs_skills_consolidation.py`; the 12th v1 App is `culture_heritage_embedding.py`. See `.agents/skills/oideachais-cocoindex-v1/SKILL.md` for the canonical pattern. The shared `@coco.lifespan` + 3 ContextKeys live in `sruth/oideachais/cocoindex_flows/_lifespan.py` — import from there instead of re-declaring (REFACTORING.md item 12). |
| Add a new Cognee cognify pass | `sruth/oideachais/cognee_integration/` (6 adapters incl. `culture_cognify.py` for the `culture_heritage` dataset); see `.agents/skills/oideachais-leabharlaim/SKILL.md` for the 3 leabharlann cognify passes |
| Add a new cross-archive edge rule | `sruth/oideachais/cognify_rules/leabharlann_cross_archive.py` (3 rules) or `author_archive_cross_corpus.py` (8 rules); the culture-heritage cross-dataset edges live in `culture_cognify.py:CROSS_DATASET_EDGES`. See `.agents/skills/oideachais-leabharlann/SKILL.md` for the leabharlann 3-edge contract |
| Add a new Marimo dashboard | `sruth/oideachais/notebooks/` + `sruth/oideachais/notebooks/dashboards/` |
| Add a new FastAPI route | `sruth/oideachais/api/routes/` (6 route modules) |
| Add a new Dagster sensor | `sruth/oideachais/dagster_defs/sensors/` (5 sensor modules) |
| Add a new Dagster `dg` Component | `sruth/oideachais/dagster_defs/components/` (3 KCG components: `celtic_dlt_source`, `celtic_lancedb_hnsw`, `celtic_cocoindex_v1`). Use `dg scaffold defs MyComponent my_component/`. |
| Add a new LanceDB HNSW index | `sruth/oideachais/lancedb/indexing.py` (4 helpers: `build_hnsw_index`, `build_ivf_pq_index`, `build_scalar_index`, `optimize_index`) |
| Add a new Graphiti episode | `sruth/oideachais/graph/graphiti_client.py` (the `graphiti_client` async context manager; falls back to FalkorDB Lite) |
| Use a DuckLake 1.0 feature | `sruth/oideachais/dlt_utils/ducklake_options.py` (3 SQL helpers: `set_data_inlining_row_limit`, `set_sorted_by`, `set_bucket_partition`) |
| Use a MotherDuck hosting option | `sruth/oideachais/dlt_utils/motherduck_options.py` (3 helpers: `fully_managed_destination`, `byob_destination`, `byoc_destination`) |
| Migrate a v0 CocoIndex flow to v1 | `sruth/oideachais/cocoindex_flows/_v0_archive/` (the 10 deprecated v0 modules) — see `.agents/skills/oideachais-cocoindex-v1/SKILL.md` for the v0→v1 migration pattern (the 11 v1 Apps cover the equivalent use cases) |
| Update the BAML × dlt × Dagster matrix | `sruth/oideachais/STATUS.md` (single source of truth) |
| Add a new refactoring backlog item | `sruth/oideachais/REFACTORING.md` |
| Add a new agent for the front-end | `sruth/oideachais/agents/{adk,agno}/` (shims) or `sruth/meaisinfhoghlaim/agents/` (model layer) |

## openspec specs that govern oideachais

The 7 openspec specs for the oideachais quadrant are:

- `oideachais-pipeline` — canonical lakehouse pipeline
- `oideachais-leabharlann` — 4 dlt sources + 3 v1 CocoIndex Apps
- `oideachais-baml-schemas` — 9 BAML files + 3 extraction clients
- `oideachais-cognify-knowledge-graph` — Cognee + FalkorDB cross-archive
- `oideachais-semantic-search` — LanceDB HNSW search
- `oideachais-marimo-dashboards` — 11 Marimo notebooks
- `ireland-primary-jc-dlt-baml` — Ireland Primary + JC dlt + BAML loop

Plus the shared specs (4):

- `agent-memory-systems` — Cognee + Graphiti + LanceDB + FalkorDB + Memgraph
- `agent-observability` — Langfuse + MLflow + RAGAS + Logfire + Datadog
- `agentic-frontend-frameworks` — TanStack Start + CopilotKit + AG-UI
- `dagger-pipelines` — Polyglot CI/CD via Dagger

When adding a new feature, the canonical workflow is:

1. **Open an openspec change** at `openspec/changes/<change-id>/` with a
   `proposal.md` + `tasks.md` + spec deltas
2. **Validate with `openspec validate <change-id> --strict`**
3. **Implement** the feature
4. **Archive the change** with `openspec archive <change-id> --yes`

## Related skills (in `.agents/skills/`)

- `dagster/SKILL.md` — Dagster asset patterns
- `dlt/SKILL.md` — DLT source patterns
- `baml/SKILL.md` — BAML schema patterns
- `cocoindex/SKILL.md` — CocoIndex v1 patterns
- `cognee/SKILL.md` — Cognee cognify patterns
- `lancedb/SKILL.md` — LanceDB + RAG patterns
- `falkordb/SKILL.md` — FalkorDB graph patterns
- `duckdb/SKILL.md` — DuckDB / DuckLake patterns
- `motherduck/SKILL.md` — MotherDuck patterns
- `dignified-python/SKILL.md` — Python style guide
- `marimo/SKILL.md` — Marimo notebook patterns
- `ccc/SKILL.md` — semantic code search

## Cross-references

- [`../../README.md`](../../README.md) — the platform overview
- [`../../STATUS.md`](../../STATUS.md) — the single source of truth for
  the BAML × dlt × Dagster × CocoIndex matrix
- [`../../REFACTORING.md`](../../REFACTORING.md) — the refactor backlog
- [`../../agents/meaisinfhoghlaim/AGENTS.md`](../../agents/meaisinfhoghlaim/AGENTS.md) — the
  model-layer quadrant
- [`../../agents/tuatha/AGENTS.md`](../../agents/tuatha/AGENTS.md) — the MMO + crypto quadrant
- [`../../web/apps/croilar-web/AGENTS.md`](../../web/apps/croilar-web/AGENTS.md) — the portfolio quadrant
- [`../../../openspec/AGENTS.md`](../../../openspec/AGENTS.md) — openspec workflow
- [`../../../AGENTS.md`](../../../AGENTS.md) — root agent instructions

## Feedback loop (project → openspec → skill)

Per the `skills-as-project-docs` openspec change, this quadrant
participates in the formal feedback loop:

1. **When an openspec change is archived**, the canonical skill
   gets a "Post-archive update: YYYY-MM-DD-..." note in its
   "Pair this skill with" section.
2. **When this quadrant changes a BAML extraction / DLT source
   / Dagster asset**, the corresponding skill (`baml/SKILL.md`,
   `dlt/SKILL.md`, `dagster/SKILL.md`) gets a 1-line addition
   to its "When to use this skill" section.
3. **When this quadrant's `STATUS.md` / `REFACTORING.md` /
   README.md changes**, the
   `data-engineering-pipeline-documentation/SKILL.md` gets a
   link to the new content.

The lint script `mise run lint:skills` enforces the 4 metadata
rules (frontmatter, name match, description length, line count)
on every skill in `.agents/skills/`.
