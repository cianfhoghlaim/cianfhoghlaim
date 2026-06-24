# Oideachais Quadrant — Agent Instructions

> **The Celtic Education Lakehouse Engine.** The offline-first ELT
> engine and lakehouse that powers the entire `cianfhoghlaim` stack.

## Overview

`oideachais/` is the **Celtic education data platform** quadrant of the
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
  `oideachais/notebooks/`
- **FastAPI** — at `oideachais/api/main.py` with the AG-UI streaming
  endpoints

The re-export shims to `meaisinfhoghlaim/`:

- `oideachais/agents/{adk,agno}/` — application-layer agent facades
  (front-end CopilotKit / AG-UI). The actual model-layer agents live in
  `meaisinfhoghlaim/agents/`.
- `oideachais/ocr/` — application-layer OCR wrapper (the
  `author_archive_ocr.py` and `pylaia_comparison.py` modules). The
  actual model-layer OCR models live in `meaisinfhoghlaim/ocr/`.
- `oideachais/memory/` — application-layer Cognee + Graphiti wrappers.
- `oideachais/graph/` — application-layer FalkorDB + Memgraph clients.
- `oideachais/knowledge_graph/` — application-layer
  `cross_stage_cognify` (the 5-stage curriculum knowledge graph).

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new education-domain dlt source for any nation (IE / EN / SCT / WLS / NI / IOM / JEY / GGY) | `oideachais/dlt_sources/domains/education/{nation}/{source}.py` (the canonical location, per `cross-domain-registry/SKILL.md`; replaces the legacy `dlt_sources/uk/`, `dlt_sources/ireland/`, and `dlt_sources/crown_dependencies/` paths) |
| Add a new medicine or law domain dlt source | `oideachais/dlt_sources/domains/{medicine|law}/{nation}/{source}.py` |
| Add a new leabharlann source | `oideachais/dlt_sources/author_archive/` (the 4 dlt sources) |
| Add a new BAML extraction function | `baml_src/` (the 27 BAML files, plus `_archive/` for deferred consumers) + `baml_src/clients.baml` for the canonical client registry |
| Add a new Dagster asset | `oideachais/dagster_defs/assets/` (40+ modules) |
| Add a new CocoIndex v1 App | `oideachais/cocoindex_flows/leabharlann_embedding.py` (the 3 v1 Apps) or `docs_skills_consolidation.py` |
| Add a new Cognee cognify pass | `oideachais/cognee_integration/` (5 adapters) |
| Add a new cross-archive edge rule | `oideachais/cognify_rules/leabharlann_cross_archive.py` (3 rules) or `author_archive_cross_corpus.py` (8 rules) |
| Add a new Marimo dashboard | `oideachais/notebooks/` + `oideachais/notebooks/dashboards/` |
| Add a new FastAPI route | `oideachais/api/routes/` (6 route modules) |
| Add a new Dagster sensor | `oideachais/dagster_defs/sensors/` (5 sensor modules) |
| Migrate a v0 CocoIndex flow to v1 | `oideachais/cocoindex_flows/` — see the canonical pattern in `leabharlann_embedding.py` |
| Update the BAML × dlt × Dagster matrix | `oideachais/STATUS.md` (single source of truth) |
| Add a new refactoring backlog item | `oideachais/REFACTORING.md` |
| Add a new agent for the front-end | `oideachais/agents/{adk,agno}/` (shims) or `meaisinfhoghlaim/agents/` (model layer) |

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

- [`oideachais/README.md`](README.md) — the user-facing overview
- [`oideachais/STATUS.md`](STATUS.md) — the single source of truth for
  the BAML × dlt × Dagster × CocoIndex matrix
- [`oideachais/REFACTORING.md`](REFACTORING.md) — the refactor backlog
- [`meaisinfhoghlaim/AGENTS.md`](../meaisinfhoghlaim/AGENTS.md) — the
  model-layer quadrant
- [`tuatha/AGENTS.md`](../tuatha/AGENTS.md) — the MMO + crypto quadrant
- [`croilar/AGENTS.md`](../croilar/AGENTS.md) — the portfolio quadrant
- [`../openspec/AGENTS.md`](../openspec/AGENTS.md) — openspec workflow
- [`../AGENTS.md`](../AGENTS.md) — root agent instructions

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
