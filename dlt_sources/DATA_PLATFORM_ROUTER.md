# `DATA_PLATFORM_ROUTER` — Single Router for the Cianfhoghlaim Data Platform

> **The canonical router for the 5 per-area `AGENTS.md` files that document the Cianfhoghlaim data platform surface.** Co-located with the per-area docs (at `dlt_sources/DATA_PLATFORM_ROUTER.md`, NOT in `.agents/skills/`) so it doesn't inflate the top-level skill count. Added by `openspec/changes/2026-08-13-skill-consolidation-and-extension-v1/`.

## What this file is

The Cianfhoghlaim data platform surface is split across 5
sub-packages — each with its own `AGENTS.md` / `README.md`
that documents one slice. This router file is the single
entrypoint that:

1. Links to each of the 5 per-area docs (so a new agent
   can find the right sub-package)
2. Documents the 6 critical conventions that apply
   ACROSS all 5 sub-packages (so a new agent doesn't have
   to re-discover them)
3. Provides the "I want to add X, where do I go?" routing
   table for the most common tasks

## The 5 per-area docs

| Sub-package | Canonical doc | Size | What it documents |
|:--|:--|--:|:--|
| `dlt_sources/` | [`./AGENTS.md`](AGENTS.md) | 251 lines | 1,957 `.py` files, 928 `@dlt.source`, 15 sub-trees (BIEP focus: 8 British Isles nations × 5 stages + 40 European nations + 6 Commonwealth + 4 Americas + 1 Cross-British Isles), the BIEP v3 generic pipeline pattern |
| `baml_src/` | [`../baml_src/AGENTS.md`](../baml_src/AGENTS.md) | — | 319 `.baml` files, 5 canonical `lc6` extraction functions (`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`, `ExtractMarkingSchemeGuideline`, `ExtractCrossLinguisticConcept`, `ExtractSyllabusDiagram`), 3 clients (`ExtractEn`, `ExtractEnStrong`, `LocalVision`) |
| `cocoindex/` | [`../cocoindex/AGENTS.md`](../cocoindex/AGENTS.md) | 214 lines | 94 explicit `coco.App(...)` instances + 378 factory Apps, 190 `.py` files, 9 sub-trees, the R1-R4 conformance contract, shared `_lifespan.py` (the `BAAI/bge-m3` 1024-d embedder) |
| `orchestration/` | [`../orchestration/AGENTS.md`](../orchestration/AGENTS.md) | — | ~833 Dagster assets, 5-layer Cianfhoghlaim Component architecture (Ingestion / Materials / Model Lifecycle / Asset Generation / Agent Operations), 6 jurisdictions (`ireland`, `england`, `scotland`, `wales`, `ni`, `isle_of_man`), the `JurisdictionAssetsBase` pattern |
| `meaisinfhoghlaim/` | [`../meaisinfhoghlaim/README.md`](../meaisinfhoghlaim/README.md) | — | 22 VISION_MODELS (subset view of `ocr_vision` family), 6 CLASSICAL_OCR backends, BIEP v2 4-path ensemble (`EnsembledExtractor`), 7 PDF converters, 4 alignment methods, Irish HTR dataset, M4-Max dispatch helper |

## The 6 critical conventions

Every sub-package on the data platform surface MUST follow
these 6 conventions. Drift from any of them is a CI gate
violation (enforced by `mise run lint:drift-docs`).

### 1. Always use relative imports within sub-packages

The canonical pattern is `from .._shared.<file> import ...`
for cross-file references within the same sub-package.
**Never** use absolute `from cianfhoghlaim.<area>.x import ...`
imports from inside the same area — this creates an import
cycle that crashes the Dagster orchestrator.

```python
# GOOD — relative
from .._shared.helpers import some_helper

# BAD — absolute (creates import cycle)
from dlt_sources._shared.helpers import some_helper
```

### 2. Respect the ingestion cache (`USE_LOCAL_SCRAPES=true`)

Before executing live web scrapes (Firecrawl on
`examinations.ie`, Crawl4AI on `ncca.ie`, etc.) that drain
API credits and risk rate limits, set:

```python
import os
os.environ['USE_LOCAL_SCRAPES'] = 'true'
```

This automatically routes extraction to the curated
`stedding/ingest_queue/` snapshot fallback. This is the
only way to iterate on the pipeline without draining API
credits.

### 3. Zero absolute namespaces in data pipelines

Never import `cianfhoghlaim.data_platform.*` from within
the data platform itself. Always use the canonical sibling
locations:

```python
# GOOD — sibling sub-package
from dlt_sources.british_isles.ireland.education.ireland_jurisdiction_pipeline import ireland_jurisdiction_pipeline

# BAD — absolute namespace (crashes Dagster)
from cianfhoghlaim.data_platform.ireland.education.ireland_jurisdiction_pipeline import ireland_jurisdiction_pipeline
```

Failing to follow this convention causes critical
`ModuleNotFoundError` crashes in the Dagster orchestrator.

### 4. R1-R4 CocoIndex conformance

Every CocoIndex v1 App MUST pass the 4-rule R1-R4
conformance contract enforced by
`cocoindex_flows/infrastructure/cocoindex_v1_conformance.py`:

| Rule | Meaning |
|:--|:--|
| **R1** | The App imports from `.._shared._lifespan` (or `..._shared._lifespan` for 3-deep dirs) |
| **R2** | No new `coco.ContextKey[` declared outside `_lifespan.py` without a `# R2-exempt:` comment |
| **R3** | `app = coco.App(coco.AppConfig(...))` (or any name ending in `_app` / `_embedding` / `_App`) is at module scope |
| **R4** | At least one `@coco.fn(` decorator is present |

Run the audit: `mise run cocoindex:conformance`. Failures
raise `ConformanceViolation` with the exact rule + fix
instructions.

### 5. MODEL_REGISTRY-only (no hardcoded model strings)

Every model choice (OCR/VLM, text LLM, embedder, rerank,
image-gen, voice, translation) MUST route through
`meaisinfhoghlaim.models.MODEL_REGISTRY` — never hardcode
a model string anywhere. The pre-commit hook blocks
commits that introduce hardcoded model strings:

```bash
mise run pre-commit-install  # install the hook (once)
mise run lint:registry      # audit agents/, baml_src/, notebooks/, web/, orchestration/, spaces/, meaisinfhoghlaim/
```

The audit walks these 6 paths via AST-aware regex against a
tight family-prefix whitelist and trips on any string not
in the canonical `MODEL_REGISTRY` key set.

### 6. Factory pattern for N nearly-identical Apps

When you need N nearly-identical CocoIndex Apps that differ
only by a config row (ISO code, subject, jurisdiction,
etc.), collapse them into 1 factory-driven module + N
1-line re-export shims. Canonical example:
`cocoindex_flows/european_nations/_factory.py` collapses 40
nation CocoIndex Apps into 1 factory + 40 shims
(~4,776 LOC reduction).

```python
# From cocoindex_flows/european_nations/_factory.py
@dataclass(frozen=True)
class NationConfig:
    iso3: str
    iso2: str
    app_slug: str
    display_name: str
    table_suffix: str

NATION_CONFIG: list[NationConfig] = [
    NationConfig("alb", "al", "alb", "Albania",  "alb.education_chunks"),
    NationConfig("aut", "at", "aut", "Austria",  "aut.education_chunks"),
    # ... 38 more rows
]

for _nation in NATION_CONFIG:
    _Chunk = _build_chunk_class(_nation)
    _process_fn = _build_process_fn(_nation, _Chunk)
    _main = _build_app_main(_nation, _Chunk, _process_fn)
    _app = coco.App(coco.AppConfig(name=f"{_nation.app_slug}_education_embedding", ...), _main)
    globals()[f"{_nation.app_slug}_education_embedding"] = _app
```

To add a new jurisdiction: append a `NationConfig` row to
`NATION_CONFIG`. The factory instantiates the new
`coco.App` at module import time and the L3 Component
`defs.yaml` picks it up automatically.

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new DLT source | The relevant jurisdiction sub-dir (`dlt_sources/british_isles/<jurisdiction>/...`) or jurisdiction-specific helper for the 8 BI nations |
| Add a new BIEP v3 jurisdiction pipeline | Subclass `JurisdictionPipelineBase` at `dlt_sources/british_isles/_cross/jurisdiction_pipeline_base.py:33` |
| Add a new BAML extraction function | `baml_src/<area>/` (319 `.baml` files; the 5 canonical `lc6` extraction functions are in `baml_src/curriculum/`) |
| Add a new CocoIndex v1 App | `cocoindex/<area>/<name>_embedding.py` (model after `ireland_lc_mathematics_embedding.py`) |
| Add a new BIEP v3 jurisdiction factory | `cocoindex_flows/biep_parity/<jurisdiction>_<stage>_apps.py` (model after `ireland_jc_apps.py`) |
| Add a new Dagster asset | The relevant 5-layer component: `orchestration/defs/{1_ingestion,2_materials,3_model_lifecycle,4_asset_generation,5_agent_ops}/` |
| Add a new jurisdiction asset wrapper | Subclass `JurisdictionAssetsBase` at `orchestration/defs/2_materials/_base/jurisdiction_assets_base.py:33` |
| Add a new OCR/VLM model | `meaisinfhoghlaim/models/registry.py:VISION_MODELS` (the 22-entry `ocr_vision` subset view of `MODEL_REGISTRY`) |
| Add a new classical OCR backend | `meaisinfhoghlaim/models/registry.py:CLASSICAL_OCR` + `bonneagar/stacks/ocr-classical/<name>/` |
| Add a new PDF converter | `meaisinfhoghlaim/document_factory/converters/<name>_converter.py` + register in `pdf_factory.py` |
| Add a new alignment method | `meaisinfhoghlaim/alignment/aligner.py:AlignmentMethod` (StrEnum) |
| Add a new filesystem pipeline | `dlt_sources/filesystem/<pipeline>.py` (10 utilities) |
| Add a new MotherDuck Dive target | `motherduck/README.md` (this repo) |
| Run the BIEP v3 Ireland pipeline | `python -c "from dlt_sources.british_isles.ireland.education.ireland_jurisdiction_pipeline import ireland_jurisdiction_pipeline; ireland_jurisdiction_pipeline.run()"` |
| Audit a DLT destination issue | `python -c "from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination; print(get_dlt_destination())"` |
| Diagnose an embedder issue | `python -c "from cocoindex_flows._shared._lifespan import EMBED_MODEL, EMBED_DIM; print(EMBED_MODEL, EMBED_DIM)"` |

## Cross-references

### Per-area canonical docs (the 5 entrypoints)

- [`dlt_sources/AGENTS.md`](AGENTS.md) — the DLT ingestion layer
- [`baml_src/AGENTS.md`](../baml_src/AGENTS.md) — the BAML extraction schemas
- [`cocoindex/AGENTS.md`](../cocoindex/AGENTS.md) — the CocoIndex v1 embedding layer
- [`orchestration/AGENTS.md`](../orchestration/AGENTS.md) — the Dagster orchestration layer
- [`meaisinfhoghlaim/README.md`](../meaisinfhoghlaim/README.md) — the OCR/HTR/alignment sub-package

### Skills (always-on reference docs)

- [`.agents/skills/centralized-registry/SKILL.md`](../.agents/skills/centralized-registry/SKILL.md) — the centralized model + schema + pipeline + stack registry (with §11 OCR/VLM Pipeline)
- [`.agents/skills/dlt/SKILL.md`](../.agents/skills/dlt/SKILL.md) — the master DLT routing skill
- [`.agents/skills/baml/SKILL.md`](../.agents/skills/baml/SKILL.md) — the BAML extraction pattern
- [`.agents/skills/cocoindex/SKILL.md`](../.agents/skills/cocoindex/SKILL.md) — the CocoIndex v1 master skill
- [`.agents/skills/dagster/SKILL.md`](../.agents/skills/dagster/SKILL.md) — the Dagster asset pattern
- [`.agents/skills/motherduck/SKILL.md`](../.agents/skills/motherduck/SKILL.md) — the MotherDuck connection options
- [`.agents/skills/lancedb/SKILL.md`](../.agents/skills/lancedb/SKILL.md) — the LanceDB HNSW vector store
- [`.agents/skills/INDEXING_AND_COGNITION.md`](../.agents/skills/INDEXING_AND_COGNITION.md) — the CCC + Cognee + MCP indexing surface (with §10 Code-search canonical entrypoint)

### OpenSpec specs (the canonical contract)

- [`british-isles-education-pipeline`](../openspec/specs/british-isles-education-pipeline/spec.md) — the flagship (6 Irish LC subjects + gov.ie circulars)
- [`centralized-model-registry`](../openspec/specs/centralized-model-registry/spec.md) — the model registry contract (with §11 OCR/VLM delta from `2026-08-13-skill-consolidation-and-extension-v1`)
- [`dagster-5-layer-component-architecture`](../openspec/specs/dagster-5-layer-component-architecture/spec.md) — the 5-layer Cianfhoghlaim Component architecture
- [`indexing-and-cognition`](../openspec/specs/indexing-and-cognition/spec.md) — CCC + Cognee + OpenCode registry

### Mise tasks (the developer shortcuts)

```bash
# Drift / health
mise run lint:skills               # validate .agents/skills/ metadata (67/67 pass as of 2026-08-13)
mise run lint:drift-docs           # validate every AGENTS.md number claim against ground truth
mise run lint:registry            # audit hardcoded model strings
mise run cocoindex:conformance    # R1-R4 conformance audit
mise run sync:all                  # run all sync layers (paths + ccc + cognee + skills + mcp + drift-docs + dagster)

# Orchestration
mise run dagster:oideachais        # launch the lakehouse Dagster UI

# Notebook
mise run notebook:control-panel    # open the 5-tab marimo control panel
```

---

**Last updated**: 2026-08-23 (CCC audit findings + 14 new per-subtree AGENTS.md + leabharlann_education_notes bridge + dagster-mlflow + cognee_health_check sensor — per `openspec/changes/2026-08-23-dlt-sources-ccc-audit-and-realignment-v1/`).
**Owner**: Build agent.

## Per-subtree inventory (CCC audit 2026-08-23)

| Subtree | .py | @dlt.source | @dlt.resource | Tangent served | AGENTS.md |
|:--|--:|--:|--:|:--|:--|
| `american_nations/` | 51 | 24 | 24 | 4 Americas jurisdictions (BR + MX + US + VE) | ✓ (new 2026-08-23) |
| `api_sources/` | 11 | 6 | 14 | Cross-corpus API sources (YouTube + Spotify + SoundCloud + GitHub + LinkedIn + ResearchGate + TG4 + Foghlaim) | ✓ (new) |
| `apple_photos/` | 1 | 1 | 2 | 5th leabharlann corpus (macOS Photos library) | ✓ (new) |
| `british_isles/` | 237 | 106 | 273 | BIEP v3 flagship (8 jurisdictions × 5 stages + 5 verticals) | ✓ (new) |
| `common/` | 28 | 3 | 4 | Cross-corpus helpers (destinations, registry, base classes) | README ✓ |
| `commonwealth/` | 633 | 292 | 292 | 6 Commonwealth jurisdictions (AU + CA + IN + NZ + NG + ZA) | ✓ (new) |
| `crypteolas/` | 15 | 18 | 49 | Tuatha's Crypteolas achievement ledger (defi + github + local + docs) | ✓ (new) |
| `european_nations/` | 859 | 407 | 407 | 40 European nations × 5 verticals via `_shared/nation_source.py` | ✓ (new) |
| `european_union/` | 27 | 19 | 18 | EU pilot + Ukraine depth upgrade | ✓ (new) |
| `filesystem/` | 17 | 8 | 39 | File system sources (leaving_cert + zotero + takeout + UoG) | ✓ (new) |
| `jobs/` | 2 | 0 | 1 | Dagster job entry points | ✓ (new) |
| `language/` | 25 | 11 | 45 | Celtic language sources (ainm + canuint + duchas + gaois + heritage + tearma + UD) | ✓ (new) |
| `media/` | 22 | 9 | 30 | Media sources (animation + comics + games + official + celtic_history + prose) | ✓ (new) |
| `official_media/` | 20 | 2 | 2 | Official media (Instagram + fediverse + companies_house + hmgcc + ggy) | ✓ (new) |
| `portfolio/` | 7 | 2 | 8 | Croilar portfolio (artwork + cv + labels + source + teaching) | ✓ (new) |
| **Total** | **1,957** | **928** | **1,188** | **15 subtrees, 1,116 source+resource decorators** | **14/15 + README** |

### Audit findings

1. **14 of 15 subtrees had no AGENTS.md** — gap-fill completed 2026-08-23.
2. **The `university_of_galway_deep.py` DLT source is orphaned** — not referenced from `ireland_jurisdiction_pipeline.py`. Spec delta added to BIEP v3 to wire it into the 5-phase pattern.
3. **No cross-repo bridge for leabharlann maths + CS notes** — added `dlt_sources/api_sources/leabharlann_education_notes.py` (the cross-repo bridge).
4. **dagster-mlflow plugin not wired** — added to `pyproject.toml` dependencies.
5. **No `cognee_health_check` sensor** — added `orchestration/sensors/cognee_health_check_sensor.py` + `orchestration/defs/1_ingestion/cognee_health/` + the `cognee_health_change_job`.

### Post-audit deployment

The Phase C (TG4 + Foghlaim), Phase B (Tuatha), Phase D (Apple Photos), Phase E (Hackathon) tangents all use this dlt_sources tree as their foundation. Per-corpus DuckLake schema isolation is deferred to per-tangent work (each tangent owns its own schema).
---

## Wave 1 themed sub-trees — appended 2026-08-24

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (master plan §3.2, §7.1), the canonical `dlt_sources/` surface
gained 3 new themed sub-trees (`lexicographic/`, `cultural_heritage/`,
`language_models/`) + the layer-grouped top-level `destinations/`
package. The old `language/` grab-bag was deprecated into a re-export
shim.

### The 3 new themed sub-trees

| Sub-tree | Files | Concern | Cadence | Destination | Embedding strategy |
|:--|--:|:--|:--|:--|:--|
| `lexicographic/` | 11 sources + 3 helpers | Word-form + translation + definition — the *lexicon* | Monthly | Typed DuckLake tables | Keyword sparse |
| `cultural_heritage/` | 6 sources + 2 helpers | Folklore + monuments + archival — the *narrative corpus* | Archival | Fulltext + BAML | BGE-M3 dense |
| `language_models/` | 1 source | Treebanks — a *training corpus* for ML, not a heritage source | Snapshot releases | Arrow IPC for training | Syntax-aware |

Each sub-tree has a self-contained `AGENTS.md` (added per master plan
§1.5). The canonical import surface:

```python
from dlt_sources.lexicographic import ainm, canuint, tearma, duchas, logainm, gaois
from dlt_sources.cultural_heritage import celtic_mythology, duchas_corpus, heritage, hidden_heritages
from dlt_sources.language_models import universal_dependencies
```

Legacy `language/` import paths continue to work via the
`dlt_sources/language/__init__.py` re-export shim for at least one
release cycle per the `LEGACY_ALIASES.md` precedent.

### The layer-grouped destinations package

The previous 3-way split (`common/destinations_cianfhoghlaim.py` +
`common/destinations_tuatha.py` + `lakehouse/destinations.py`) was
consolidated into a single layer-grouped package at the TOP LEVEL of
`dlt_sources/`:

```python
from dlt_sources.destinations import named_destinations

# The single consolidated DuckLake namespace
con = named_destinations("ducklake_cianfhoghlaim")

# Per-quadrant Postgres metadata schemas
con = named_destinations("ducklake_oideachais_quadrant")
con = named_destinations("ducklake_tuatha_quadrant")
con = named_destinations("ducklake_croilar_quadrant")
con = named_destinations("ducklake_agents_quadrant")
con = named_destinations("ducklake_media_quadrant")

# MotherDuck + filesystem + Iceberg
con = named_destinations("motherduck")
con = named_destinations("filesystem_local")
con = named_destinations("iceberg_rest")
```

Legacy import paths continue to work via deprecation shims:

```python
# All 3 of these resolve to the same factory:
from dlt_sources.destinations import named_destinations
from dlt_sources.common.destinations import named_destinations
from dlt_sources.common.destinations_cianfhoghlaim import named_destinations
```

### Sister-repo carve (INVARIANT 1)

The UD corpora (`language_models/universal_dependencies.py`) are
owned by the `ciancheiltis` sister repo per the bilingual carve rule
(master plan INVARIANT 1). Pinned cross-repo reference:
`ciar://ciancheiltis/datasets/ud_<lang>@v<N>`. The
`language_models/universal_dependencies.py` source is the
`cianfhoghlaim` mirror that re-publishes the corpora into the
consolidated `ducklake_cianfhoghlaim` DuckLake namespace.

### CI gate — `mise run lint:dlt-paths`

The `lint:dlt-paths` mise task (added per master plan §1.10) fails
the build if any source `.py` file exists in the deprecated
`dlt_sources/language/` directory (other than the `__init__.py` shim).
Run with `mise run lint:dlt-paths` (added 2026-08-24).
