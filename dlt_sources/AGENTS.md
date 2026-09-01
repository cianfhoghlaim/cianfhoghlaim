# `dlt_sources/` — DLT ingestion layer + cross-jurisdiction registry

> **The canonical post-v7 Python sub-package for DLT sources + destinations + cross-jurisdiction registry + common helpers.**
>
> Pre-v7 this lived at `cianfhoghlaim/dlt/`; post-v7 flattening (2026-07-17) it's the canonical sibling location at the repo root. 1,905 `.py` files, 920 `@dlt.source` decorated functions, 13 top-level sub-trees.

## Priority quick reference

### Priority skills (3 of 53)

| Skill | When to load |
|:--|:--|
| [`dlt`](../../.agents/skills/dlt/SKILL.md) | The master routing skill — load this first for any DLT work |
| [`dlt-cli`](../../.agents/skills/dlt-cli/SKILL.md) | The `dlt init` + `dlt deploy` + `dlt pipeline` CLI surface |
| [`motherduck`](../../.agents/skills/motherduck/SKILL.md) | The MotherDuck connection options + MCP server |

### Priority commands

```bash
# The 6 CLI subcommands (dlt_sources/cli.py -> cianfhoghlaim-dlt)
uv run python -m dlt_sources.cli run-pipeline <name>     # Run a curated source by name
uv run python -m dlt_sources.cli list-sources            # List the 22 curated sources

# The Ireland BIEP v3 generic pipeline (the canonical reference)
python -c "from dlt_sources.british_isles.ireland.education.ireland_jurisdiction_pipeline import ireland_jurisdiction_pipeline; print(ireland_jurisdiction_pipeline.jurisdiction)"
# -> ireland

# The cross-jurisdiction registry
python -c "from dlt_sources.british_isles._cross.registry_loader import seed_registry; print(type(seed_registry()))"
# -> <class 'function'>
```

### Priority compose stacks

`lakehouse` (the DuckLake + Lance Namespace + Postgres + Garage S3 stack) + `motherduck` (the MotherDuck SaaS compute stack). Both live at `bonneagar/stacks/`.

### Priority openspec specs (1 of 48)

| Spec | One-liner |
|:--|:--|
| [`british-isles-education-pipeline`](../../openspec/specs/british-isles-education-pipeline/spec.md) | The flagship — 6 Irish LC priority subjects + gov.ie circulars — 7 v1 CocoIndex flows + 42 Dagster assets + 6 marimo notebooks + 4 MotherDuck Dives + daily Flight |

### Priority mise tasks

```bash
mise run cic:dlt:{dev,staging,prod}-pipeline  # Author-archive DLT targets
mise run biep:v3:registry:seed                # Seed the BIEP v3 registry
mise run biep:v3:lint                        # ibis-first contract lint
```

## Overview

`dlt_sources/` is the **DLT ingestion layer** of the Cianfhoghlaim
monorepo. It houses:

- **1,905+ `.py` files** containing **920+ `@dlt.source` decorated
  functions** + 4,900+ helper functions across **18 top-level
  sub-trees**:
  - **Geographic (KEEP ENGLISH — ISO/toponym conventions)**:
    - `british_isles/` (the BIEP focus: ireland + england + scotland +
      wales + ni + isle_of_man + jersey + guernsey + sct_wls_ni +
      crown_dependencies + `_cross/`)
    - `european_nations/` (40 nations × {education, government, law,
      medicine, statistics} via the universal template)
    - `european_union/` (EUR-Lex + CEDEFOP + ECDC + EMA + Eurostat +
      Eurydice + Commission press + ...)
    - `commonwealth/` (australia + canada (12 provinces + quebec/
      montreal) + india + new_zealand + nigeria (federal + 36 states)
      + south_africa)
    - `american_nations/` (brazil + mexico + united_states (CA) +
      venezuela)
  - **Domain-first (the new layout)**:
    - `law/<jurisdiction>/<geography>/` (59 directories — jurisdiction
      pipelines for legal sources)
    - `medicine/<jurisdiction>/<geography>/` (61 directories —
      jurisdiction pipelines for medical sources)
    - `education/<jurisdiction>/<geography>/` (61 directories — K-12 +
      secondary education pipelines)
    - `education/tertiary/<institution>/` (UoG + NUI + BI tertiary)
  - **Themed (the language/ split)**:
    - `lexicographic/` (11 source files + 3 helpers — Irish +
      Celtic lexicographic: ainm, canuint×5, duchas, gaois×2,
      logainm, tearma×2)
    - `cultural_heritage/` (6 source files + 2 helpers — folklore +
      mythology + heritage sites: celtic_mythology, duchas_corpus,
      heritage, hidden_heritages, local_documents×2)
    - `language_models/` (1 source file — Universal Dependencies
      treebanks; sister-repo-owned per INVARIANT 1)
  - **Official media (the 4-way split)**:
    - `official_media/british_crown/` (sct + wls feeds)
    - `official_media/channel_islands/` (ggy + iom + jsy feeds)
    - `official_media/companies/` (companies_house + cro feeds)
    - `official_media/fediverse/` (mastodon/activitypub feeds)
    - `official_media/hmgcc/`, `official_media/_resolver_live.py`,
      `official_media/allowlist.py`, `official_media/classifier.py`,
      `official_media/instagram_export.py`, `official_media/source_resolver.py`
  - **Cross-cutting helpers + shared infra**:
    - `destinations/` (CANONICAL top-level home for the layer-grouped
      destinations package — `_common.py` + `ducklake.py` +
      `motherduck.py` + `filesystem.py` + `iceberg.py`)
    - `common/` (25+ helpers — destinations (DEPRECATION SHIM), 
      endpoint_recovery, observability, http_client,
      motherduck_options, named_destinations (DEPRECATION SHIM), etc.)
    - `lakehouse/` (DuckLake bridge — renamed from `_lakehouse/`;
      `pool.py`, `options.py`, `personal_archive.py`,
      `cognify_health.py`)
  - **Pipeline + ops**:
    - `_jobs/` (CLI dispatcher for long-running scheduled jobs)
    - `apple_photos/` (the 5th leabharlann corpus via osxphotos)
    - `api_sources/` (generic non-jurisdictional API clients)
    - `filesystem/` (`raw_files/` rename in flight)
    - `media/` (5 sub-themes already distinct — kept as-is)
    - `crypteolas/`, `crypteolas_chain/`, `crypteolas_docs/`,
      `crypteolas_defi/` (the crypto credentials system)
    - `cv/`, `artwork/`, `labels/` (the portfolio split)
    - `media_text/`, `media_comics/`, `media_games/`,
      `media_personal/` (the media split)
    - `local_archive/` (the local archive sub-tree)
    - `tuatha_media_intel/` (the big media-intel pipeline)

## Themed sub-trees (Wave 1 — 2026-08-24)

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (master plan §3.2, §7.1). The previous `dlt_sources/language/`
grab-bag (16 source files + 5 helpers across 3 unrelated domains) was
split into 3 themed sub-trees, one concern per sub-tree:

| Sub-tree | Files | Domain |
|:--|--:|:--|
| `dlt_sources/lexicographic/` | 11 sources + 3 helpers | Word-form + translation + definition — the *lexicon* |
| `dlt_sources/cultural_heritage/` | 6 sources + 2 helpers | Folklore + monuments + archival — the *narrative corpus* |
| `dlt_sources/language_models/` | 1 source | Treebanks — a *training corpus* for ML, not a heritage source |

Each sub-tree has different ingestion cadence, destination, and embedding
strategy (per master plan §2.1.2).

### `lexicographic/` (the *lexicon*)

```
lexicographic/
├── ainm.py                     (Irish place-names — Ainm)
├── canuint.py + canuint_*.py   (Canúint — Irish dialect corpus × 5)
├── duchas.py                   (the Dúchas lexicon — Schools' Collection terminology)
├── gaois.py + gaois_combined.py
├── logainm.py                  (Logainm — Placenames Database of Ireland)
├── tearma.py + tearma_search.py
├── _canuint_helpers.py
├── _gaois_helpers.py
├── _tearma_helpers.py
└── AGENTS.md
```

Ingestion cadence: monthly. Destination: typed DuckLake tables.
Embedding strategy: keyword sparse.

### `cultural_heritage/` (the *narrative corpus*)

```
cultural_heritage/
├── celtic_mythology.py         (Celtic mythology corpus)
├── duchas_corpus.py            (Dúchas manuscript images + transcriptions, was duchas_images.py)
├── heritage.py                 (Heritage Council of Ireland — sites & monuments)
├── hidden_heritages.py
├── local_documents_by_subject.py
├── local_education_documents.py
├── _duchas_corpus_helpers.py   (was _duchas_images_helpers.py)
├── _local_documents_helpers.py
└── AGENTS.md
```

Ingestion cadence: archival. Destination: fulltext + BAML.
Embedding strategy: BGE-M3 dense.

### `language_models/` (the *training corpus*)

```
language_models/
├── universal_dependencies.py   (UD treebanks — CoNLL-U)
└── AGENTS.md
```

Ingestion cadence: snapshot releases. Destination: Arrow IPC for
training. Embedding strategy: syntax-aware.

> **Sister-repo ownership** (per master plan INVARIANT 1, bilingual
> carve rule): UD corpora are owned by the `ciancheiltis` sister repo.
> Pinned cross-repo reference: `ciar://ciancheiltis/datasets/ud_<lang>@v<N>`.

### Layer-grouped destinations (Wave 1)

The previous 3-way split (`common/destinations_cianfhoghlaim.py` +
`common/destinations_tuatha.py` + `lakehouse/destinations.py`) was
consolidated into a single layer-grouped package:

```
dlt_sources/destinations/        (CANONICAL — top-level)
├── __init__.py                  (named_destinations() factory + re-exports)
├── _common.py                   (credential validation + namespace defaults)
├── ducklake.py                  (DuckLake + Postgres catalog + Garage S3)
├── motherduck.py                (MotherDuck managed DuckLake)
├── filesystem.py                (local FS + S3 + GCS + Azure)
└── iceberg.py                   (Iceberg REST catalog via Lakekeeper :8181)
```

Re-export shims at the legacy paths (`common/destinations_*.py`,
`common/named_destinations.py`, `common/destinations/`,
`lakehouse/destinations.py`, `lakehouse/personal_archive_destinations.py`)
preserve backwards compatibility for at least one release cycle per
the `LEGACY_ALIASES.md` precedent.

The single DuckLake namespace is `ducklake_cianfhoghlaim` (per master
plan §1.1). The 6 → 10 legacy namespace aliases all route to this
consolidated namespace via the `DESTINATIONS` registry.

### Backwards-compat policy

Every themed sub-tree import path continues to work:

| New (canonical) | Legacy (shim) |
|:--|:--|
| `from dlt_sources.lexicographic import ainm, canuint, tearma` | `from dlt_sources.language import ainm, canuint, tearma` |
| `from dlt_sources.cultural_heritage import celtic_mythology, duchas_corpus` | `from dlt_sources.language import celtic_mythology, duchas_images` |
| `from dlt_sources.language_models import universal_dependencies` | `from dlt_sources.language import universal_dependencies` |
| `from dlt_sources.destinations import named_destinations` | `from dlt_sources.common.destinations import named_destinations` |
| `from dlt_sources.destinations import named_destinations` | `from dlt_sources.common.destinations_cianfhoghlaim import named_destinations` |

The `mise run lint:dlt-paths` CI gate (per master plan §1.10) fails
the build if any source `.py` file is added back to the deprecated
`dlt_sources/language/` directory (other than `__init__.py` shims).

## The BIEP v3 generic pipeline pattern

The canonical entry point for new BIEP v3 jurisdictions is
`dlt_sources/british_isles/_cross/jurisdiction_pipeline_base.py:33`
(`JurisdictionPipelineBase`). Subclass it, set `STAGE`, and implement
`build_pipeline_resource()`. The base class provides:

- `VALID_JURISDICTIONS` (8 BI nations)
- `VALID_STAGES` (5 educational stages)
- `WRITE_DISPOSITION = "merge"`
- `PRIMARY_KEY = ["content_hash"]`
- `subject_to_row(subject)` — converts a registry row to a DLT record
- `build_pipeline(name, dataset_name)` — assembles a DLT pipeline
- `build_pipeline_resource(pipeline)` — the subclass hook
- `run()` — executes the pipeline

The **10 jurisdiction pipeline files** are:
1. `british_isles/ireland/education/ireland_jurisdiction_pipeline.py`
   (the reference implementation; emits 544 Ireland cohorts)
2. `british_isles/england/education/england_jurisdiction_pipeline.py`
3. `british_isles/scotland/education/sct_jurisdiction_pipeline.py`
4. `british_isles/wales/education/wls_jurisdiction_pipeline.py`
5. `british_isles/northern_ireland/education/ni_jurisdiction_pipeline.py`
6. `british_isles/sct_wls_ni/education/sct_wls_ni_jurisdiction_pipeline.py`
7. `british_isles/isle_of_man/education/isle_of_man_jurisdiction_pipeline.py`
8. `british_isles/jersey/education/jersey_jurisdiction_pipeline.py`
9. `british_isles/guernsey/education/guernsey_jurisdiction_pipeline.py`
10. `british_isles/crown_dependencies/education/crown_dependencies_jurisdiction_pipeline.py`

The cross-jurisdiction registry lives at
`british_isles/_cross/registry_loader.py` — its `seed_registry()`
function returns the canonical cohort seed (1,990 rows across all 8
BI jurisdictions). The legacy `seed_registry()` definition at
`registry_loader.py:350` is dead code (overridden by the live one at
`:674`).

## The 3 critical conventions

1. **Always use relative imports** within `dlt_sources/`. The
   canonical pattern is `from .._shared.<file> import ...` for
   cross-file references. **Never** `from dlt_sources.x import ...`
   from within `dlt_sources/x/` — this creates an import cycle.

2. **Respect the ingestion cache** — set `USE_LOCAL_SCRAPES=true`
   to route all DLT extractions through the curated
   `stedding/ingest_queue/` snapshot fallback. This is the only way
   to iterate on the pipeline without draining API credits on
   Firecrawl + Crawl4AI + ChangeDetection.io.

3. **Zero absolute namespaces** in data pipelines. Never import
   `cianfhoghlaim.dlt.*` from within the data platform — always use
   the canonical sibling locations (`dlt_sources.*`).

## The destination contract

The canonical destination factory is now at the TOP LEVEL of the
package — `dlt_sources.destinations.named_destinations()` — per the
Wave 1 destination consolidation (master plan §3.2, §7.1):

```python
from dlt_sources.destinations import named_destinations

# The single consolidated DuckLake namespace
con = named_destinations("ducklake_cianfhoghlaim")

# Per-quadrant Postgres metadata schemas
con = named_destinations("ducklake_oideachais_quadrant")
con = named_destinations("ducklake_tuatha_quadrant")

# MotherDuck (cloud SaaS)
con = named_destinations("motherduck")

# Filesystem (local + S3 + GCS + Azure)
con = named_destinations("filesystem_local")
con = named_destinations("filesystem_s3")

# Iceberg REST catalog (via Lakekeeper :8181)
con = named_destinations("iceberg_rest")
```

The single DuckLake namespace is `"ducklake_cianfhoghlaim"` (per master
plan §1.1). The 6 → 10 legacy namespace aliases all route to this
consolidated namespace via the `DESTINATIONS` registry.

Legacy import paths continue to work via deprecation shims:

```python
# These all resolve to the same factory:
from dlt_sources.destinations import named_destinations
from dlt_sources.common.destinations import named_destinations
from dlt_sources.common.destinations_cianfhoghlaim import named_destinations
from dlt_sources.common.named_destinations import named_destinations
```

## The LEGACY_ALIASES.md migration story

The pre-v7 ISO 3-letter → snake_case rename waves (per
`2026-07-17-pipeline-directory-consolidation-v1`):

1. **European nations**: `alb` → `albania`, `cze` → `czechia`, ...
   (39 codes mapped)
2. **Commonwealth**: `aus` → `australia`, `can` → `canada`, ...
   (6 codes mapped)
3. **Canada provinces**: `ab` → `alberta`, `bc` → `british_columbia`,
   ... (13 codes mapped)
4. **Nigeria states**: `nga_abi` → `abia`, `nga_zam` → `zamfara`,
   ... (36 codes mapped)
5. **British Isles**: collapse dual naming — `en` → `england`,
   `ni` → `northern_ireland`, `sct` → `scotland`, `wls` → `wales`,
   `iom` → `isle_of_man`, `jey` → `jersey`, `ggy` → `guernsey`
6. **Americas**: `americas/` → `american_nations/`,
   `bra` → `brazil`, `mex` → `mexico`, `us` → `united_states`,
   `ven` → `venezuela`

All 6 renames are completed on disk. The doc's role is now purely
historical — there's no `import dlt.european_nations.alb` shim
remaining.

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new DLT source | The relevant jurisdiction sub-dir (`british_isles/<jurisdiction>/...`) |
| Add a new jurisdiction pipeline | Subclass `JurisdictionPipelineBase` at `british_isles/_cross/jurisdiction_pipeline_base.py:33` |
| Add a new common helper | `common/<helper>.py` (25 helpers + `cli.py`) |
| Add a new API source | `api_sources/<service>_source.py` |
| Add a new OCR/text extractor for BAML | (out of scope — that's `baml_src/`) |
| Add a new filesystem pipeline | `filesystem/<pipeline>.py` (10 utilities) |
| Add a new MotherDuck Dive target | See `motherduck/README.md` (this repo) |
| Add a new CocoIndex embedding | See `cocoindex/AGENTS.md` (this repo) |
| Run the BIEP v3 Ireland pipeline | `python -c "from dlt_sources.british_isles.ireland.education.ireland_jurisdiction_pipeline import ireland_jurisdiction_pipeline; ireland_jurisdiction_pipeline.run()"` |
| Diagnose a destination issue | `python -c "from dlt_sources.destinations import named_destinations; print(named_destinations('ducklake_cianfhoghlaim'))"` |
| Add a new lexicographic source | `dlt_sources/lexicographic/<source>.py` (then `from dlt_sources.lexicographic import <source>`) |
| Add a new cultural-heritage source | `dlt_sources/cultural_heritage/<source>.py` (then `from dlt_sources.cultural_heritage import <source>`) |
| Add a new language-models source | `dlt_sources/language_models/<source>.py` (then `from dlt_sources.language_models import <source>`) |
| Add a new destination layer | `dlt_sources/destinations/<layer>.py` + register in `dlt_sources/destinations/__init__.py:DESTINATIONS` |
| Use the legacy `language/` paths | The `dlt_sources/language/` shim re-exports from the 3 themed sub-trees — `from dlt_sources.language import ainm` works |

## Cross-references

- [`../README.md`](../README.md) — root README
- [`../AGENTS.md`](../AGENTS.md) — root agent instructions
- [`../openspec/AGENTS.md`](../openspec/AGENTS.md) — openspec workflow
- [`../openspec/specs/british-isles-education-pipeline/spec.md`](../openspec/specs/british-isles-education-pipeline/spec.md) — flagship BIEP spec
- [`../.agents/skills/dlt/SKILL.md`](../.agents/skills/dlt/SKILL.md) — DLT master routing skill
- [`../.agents/skills/motherduck/SKILL.md`](../.agents/skills/motherduck/SKILL.md) — MotherDuck connection options
- [`../cocoindex/AGENTS.md`](../cocoindex/AGENTS.md) — CocoIndex embedding layer
- [`../motherduck/README.md`](../motherduck/README.md) — MotherDuck Dives + Flights
- [`../orchestration/README.md`](../orchestration/README.md) — Dagster orchestration layer
- [`../dlt_sources/LEGACY_ALIASES.md`](LEGACY_ALIASES.md) — the v7 ISO-3 → snake_case rename map

## Schema introspection (NEW 2026-08-15)

The canonical way to introspect the 920 `@dlt.source` + ~4,900 `@dlt.resource` decorated functions across `dlt_sources/` is via the 5 helpers in `notebooks/_shared/schema.py`:

```python
from notebooks._shared.schema import (
    list_dlt_sources,                # returns 1963 rows (sources + resources)
    schema_introspect,               # returns BIEP DuckDB column metadata
    schema_introspect_full,          # DuckDB + LanceDB + BAML union
)
```

The helpers walk `dlt_sources/**/*.py` via AST parsing, extracting:

- `source_name` (the function name)
- `file_path` (relative to the repo root)
- `primary_key` (from the `@dlt.source(primary_key=...)` decorator)
- `destinations` (from `dlt.destinations.*(...)` calls)
- `dagster_asset` (the asset that wraps the source)

**To check if a DLT source is wired correctly** without running the full pipeline:

```bash
PYTHONPATH="$PWD/notebooks/_shared:$PWD" uv run python -c "
import sys, types
sys.modules['ibis'] = types.ModuleType('ibis')
import schema
for s in schema.list_dlt_sources():
    if 'ireland' in s['file_path']:
        print(s)
"
```

**Reuse the `JurisdictionPipelineBase`** at `british_isles/_cross/jurisdiction_pipeline_base.py:33` for any new jurisdiction pipeline — don't hand-roll a new pipeline class.

**The 619 empty placeholder YAMLs** in `orchestration/defs/1_ingestion/{american_nations,commonwealth,european_nations,...}/` are **audited as dead** (per the 2026-08-15 audit). They reference nations/stages that have already been absorbed into the v3 generic pipeline pattern. They are NOT loaded by `mise run dagster:dev` and can be safely deleted in the cleanup follow-up (issue #146).

---

**Last updated**: 2026-08-15 (added the schema introspection section + the 619-empty-YAML audit note).
**Owner**: Build agent.

## Data platform router

> **The single router for the 5 per-area data platform docs** is at [`DATA_PLATFORM_ROUTER.md`](DATA_PLATFORM_ROUTER.md). Co-located with this file; added by `openspec/changes/2026-08-13-skill-consolidation-and-extension-v1/`. Documents the 6 critical conventions (relative imports / `USE_LOCAL_SCRAPES` / zero absolute namespaces / R1-R4 conformance / MODEL_REGISTRY-only / factory pattern) that apply ACROSS all 5 sub-packages.