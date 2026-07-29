# `cocoindex/` — CocoIndex v1 embedding layer

> **The 94+ CocoIndex v1 Apps for the British-Isles Education Pipeline (BIEP v3) + 9 infrastructure indexes + corpus embeddings.**
>
> Embedder is `BAAI/bge-m3` (1024-d, multilingual) per `_shared/_lifespan.py:107`. The canonical home for the shared `@coco.lifespan` + 3 `ContextKey`s.

## Priority quick reference

### Priority skills (2 of 53)

| Skill | When to load |
|:--|:--|
| [`cocoindex`](../../.agents/skills/cocoindex/SKILL.md) | The v1 App canonical pattern + 4-rule R1-R4 conformance contract + `_lifespan.py` shared home |
| [`lancedb`](../../.agents/skills/lancedb/SKILL.md) | The LanceDB HNSW vector store (the canonical target for BIEP embeddings) |

### Priority commands

```bash
# The canonical CLI (must be invoked as `uv run cianfhoghlaim-cocoindex --help`)
# Once `__main__.py` lands: `python -m cocoindex --help`

# R1-R4 conformance audit
mise run cocoindex:conformance
# alias: uv run python -m cocoindex._shared.cli conformance

# Update a single App
mise run cocoindex:update -- <module>:<App>
# e.g. mise run cocoindex:update -- cianfhoghlaim.cocoindex.biep_parity.ireland_lc_mathematics_embedding:ireland_lc_mathematics_embedding

# Reindex the codebase (CCC)
mise run ccc:init       # first time only
mise run ccc:index      # rebuild the codebase index
mise run ccc:search "your query here"
```

### Priority compose stacks

`lancedb` (the LanceDB vector store) + `lakehouse` (the DuckLake + Lance Namespace + Postgres + Garage S3 stack). Both live at `bonneagar/stacks/`.

### Priority openspec specs (2 of 48)

| Spec | One-liner |
|:--|:--|
| [`british-isles-education-pipeline`](../../openspec/specs/british-isles-education-pipeline/spec.md) | The flagship — 7 v1 CocoIndex flows (6 LC + government_circulars) |
| [`indexing-and-cognition`](../../openspec/specs/indexing-and-cognition/spec.md) | CCC v1 code search + Cognee knowledge graph + OpenCode agent/MCP registry |

### Priority mise tasks

```bash
mise run lint:skills              # validate .agents/skills/ metadata (53/53 pass)
mise run cocoindex:conformance    # R1-R4 conformance audit
```

## Overview

`cocoindex/` is the **CocoIndex v1 App canonical home** of the
Cianfhoghlaim monorepo. It houses:

- **94 explicit `coco.App(...)` instances** + **378 CocoIndex Apps
  inside factory-generated dicts** (across `biep_parity/`'s
  Ireland JC + England A-Level + England GCSE factories).
- **190 `.py` files** with **306 `@coco.fn(` decorators**.
- **9 sub-trees**: `_shared/` + `biep_parity/` + `british_isles/` +
  `celtic/` + `commonwealth/` + `corpus/` + `european_nations/` +
  `european_nations_cross/` + `european_union/` + `american_nations/`
  + `infrastructure/` + `knowledge_graph/` + `media/` + `portfolio/`
  + `subjects/`.

## The R1-R4 conformance contract

`infrastructure/cocoindex_v1_conformance.py:13–31` enforces the
4-rule R1-R4 contract at scaffold time by static AST inspection of
every v1 App module:

| Rule | Meaning |
|:--|:--|
| **R1** | The App imports from `.._shared._lifespan` (or `..._shared._lifespan` for 3-deep dirs, etc.) — the canonical lifespan + ContextKeys home. |
| **R2** | No new `coco.ContextKey[` declared outside `_lifespan.py` without a `# R2-exempt: <reason>` comment. |
| **R3** | `app = coco.App(coco.AppConfig(...))` (or any name ending in `_app` / `_embedding` / `_App`) is at module scope (NOT inside a function body). |
| **R4** | At least one `@coco.fn(` decorator is present. |

On R1-R4 fail, `ConformanceViolation` is raised with the exact rule +
fix instructions.

## The shared lifespan (`_shared/_lifespan.py`)

The single `@coco.lifespan async def shared_lifespan(builder)`
plus 3 `ContextKey`s:

- `LANCE_DB` — the LanceDB connection (defaults to
  `rest://lakehouse-lance-namespace:8182` in dev mode)
- `EMBEDDER` — the `BAAI/bge-m3` 1024-d multilingual embedder
  (configurable via `CIANFHOGHLAIM_EMBED_MODEL` env var)
- `RESOLVED_FILE_REGISTRY` — the file-resolved registry for
  incremental processing

Every v1 App imports these:
```python
from .._shared._lifespan import shared_lifespan, LANCE_DB, EMBEDDER
```

## The 9 sub-trees

| Sub-tree | Purpose |
|:--|:--|
| `_shared/` | The canonical shared home (`_lifespan.py` + `cli.py` + `languages.py` + `caighdean_standardize.py` + `reranker.py` + `repo_embedding.py` + `repo_type_detector.py`) |
| `biep_parity/` | 14 explicit Apps + 88 Ireland JC factory Apps + 147 England A-Level factory Apps + 129 England GCSE factory Apps = **378 Apps in this dir** |
| `british_isles/` | Per-nation Apps for England (AQA/OCR/Edexcel/A-Level) + Ireland (5 ie_law modules + canuint + ireland_legal_embedding) |
| `celtic/` | Celtic-language family Apps: Gaeilge, UD Celtic, Gaois (NLI), Mythology, Multilingual, Curriculum |
| `commonwealth/` | Australia + Canada-Quebec + India + Nigeria + New-Zealand + South-Africa per-jurisdiction Apps |
| `corpus/` | The big shared-corpus Apps: `leabharlann_embedding` (38KB), `unified_embedding` (22KB), `university_embedding`, `government_circulars_embedding`, `duchas_embedding`, `local_documents_embedding`, `root_pdfs_embedding` |
| `european_nations/` | 40 per-country sub-dirs (`albania/`, ..., `ukraine/`); each has one `education_embedding.py` |
| `european_nations_cross/` | Cross-EU-wide Apps: `law_embedding`, `medicine_embedding`, `education_embedding` |
| `european_union/` | EU-wide: `official_embedding`, `eu_multilingual_alignment_embedding` |
| `american_nations/` | US-California (only nation currently populated); placeholder for BRA/MEX/VEN |
| `infrastructure/` | Codebase + API + filesystem + storage + config indexing + `cocoindex_v1_conformance.py` (the R1-R4 linter) + 2 smoke tests |
| `knowledge_graph/` | `youtube_kg_embedding`, `file_graph`, `multihop_search`, `terminology_linking` |
| `media/` | Apple Photos (4 variants) + OCR + Artwork + Computer-Vision embeddings |
| `portfolio/` | Personal `heritage_embedding` + `culture_heritage_embedding` |
| `subjects/` | Cross-subject competency + JC + LC + education_subject embeddings |

## The LanceDB namespace convention

All CocoIndex v1 Apps in this repo write to **LanceDB**. There is
**no Postgres, SQLite, Neo4j, FalkorDB, or Kafka target usage** in
`cocoindex/` — those are listed in the skill's "17 source/target
connectors" but none are actually wired on disk.

Confirmed LanceDB target table naming patterns:

| Owner | Pattern | Example |
|:--|:--|:--|
| BIEP v3 per-jurisdiction (LC) | `cianhoghlaim.<jurisdiction>.<stage>.<subject>.<level>_<lang>_chunks` | `cianhoghlaim.ireland.leaving_cycle.mathematics.untiered_en_chunks` |
| BIEP v3 per-jurisdiction (A-Level/GCSE) | `cianhoghlaim.<jurisdiction>.<stage>.<board>.<subject>_<...>_chunks` | `cianhoghlaim.england.a_level.aqa.mathematics_a_level_chunks` |
| BIEP v1 corpus | `cianhoghlaim.<vertical>.<sub>.<level>_<lang>` | `cianhoghlaim.lc.gaeilge.hl_ga`, `cianhoghlaim.government.circulars.des_2024_en` |
| Infrastructure indexes | bare names | `codebase_chunks`, `codebase_graph`, `codebase_graph_edges` |
| Compliance audit | `conformance_check_history` | the linter's own history table |

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new CocoIndex v1 App | `biep_parity/<jurisdiction>_<subject>_embedding.py` (model after `ireland_lc_mathematics_embedding.py`) |
| Add a new BIEP v3 jurisdiction factory | `biep_parity/<jurisdiction>_<stage>_apps.py` (model after `ireland_jc_apps.py`) |
| Add a new ContextKey | `_shared/_lifespan.py` (with `# R2-exempt:` comment if needed) |
| Modify the embedder | `_shared/_lifespan.py:107` (`EMBED_MODEL` env var) |
| Add a new infrastructure index | `infrastructure/<index>_indexing.py` (model after `codebase_indexing.py`) |
| Add a new conformance rule | `infrastructure/cocoindex_v1_conformance.py` |
| Run the R1-R4 audit | `mise run cocoindex:conformance` |
| Update a single App | `mise run cocoindex:update -- <module>:<App>` |
| Diagnose an embedder issue | `python -c "from cocoindex._shared._lifespan import EMBED_MODEL, EMBED_DIM; print(EMBED_MODEL, EMBED_DIM)"` |

## Cross-references

- [`../README.md`](../README.md) — root README
- [`../AGENTS.md`](../AGENTS.md) — root agent instructions
- [`../openspec/AGENTS.md`](../openspec/AGENTS.md) — openspec workflow
- [`../openspec/specs/british-isles-education-pipeline/spec.md`](../openspec/specs/british-isles-education-pipeline/spec.md) — flagship BIEP spec
- [`../.agents/skills/cocoindex/SKILL.md`](../.agents/skills/cocoindex/SKILL.md) — CocoIndex master skill
- [`../.agents/skills/lancedb/SKILL.md`](../.agents/skills/lancedb/SKILL.md) — LanceDB vector store
- [`../dlt_sources/AGENTS.md`](../dlt_sources/AGENTS.md) — the DLT ingestion layer
- [`../orchestration/README.md`](../orchestration/README.md) — the Dagster orchestration layer
- [`../motherduck/README.md`](../motherduck/README.md) — the MotherDuck Dives + Flights
- [`../LEGBACK_ALIASES.md`](LEGACY_ALIASES.md) — the v7 ISO-3 → snake_case rename map (historical)