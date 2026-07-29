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

- **1,905 `.py` files** containing **920 `@dlt.source` decorated
  functions** + 4,900+ helper functions across **13 top-level
  sub-trees**:
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
  - `common/` (25 helpers — destinations, endpoint_recovery,
    observability, http_client, motherduck_options, etc.)
  - `language/` (Celtic-language sources: Logainm, Téarma, Ainm,
    Gaois, Dúchas, Canúint)
  - `official_media/` (British Crown + Channel Islands government
    feeds)
  - `api_sources/` (generic non-jurisdictional API clients — Spotify,
    SoundCloud, YouTube, GitHub, LinkedIn, ResearchGate)
  - `filesystem/` (10 DLT filesystem pipeline utilities)
  - `jobs/` (long-running scheduled jobs — only `government_circulars_job.py`)
  - `portfolio/` (CV, teaching, artwork, labels)
  - `apple_photos/` (the 5th leabharlann corpus via osxphotos;
    empty stub awaiting the `apple-photos-ingestion` openspec change)

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

The canonical destination factory is
`common/destinations_cianfhoghlaim.py:191:get_dlt_destination()`:

```python
from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination

# Local DuckDB at ./data/cianfhoghlaim.duckdb
con = get_dlt_destination(mode="local")

# MotherDuck (cloud SaaS)
con = get_dlt_destination(mode="production")

# DuckLake (local + Iceberg-compatible)
con = get_dlt_destination(use_ducklake=True)
```

Namespace defaults to `"cianfhoghlaim"` (line 47). Tables land at
`cianfhoghlaim.<jurisdiction>.<stage>.<subject>.<variant>`.

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
| Diagnose a destination issue | `python -c "from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination; print(get_dlt_destination())"` |

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