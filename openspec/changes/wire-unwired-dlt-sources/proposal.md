# wire-unwired-dlt-sources — Add 12 Dagster asset wrappers

## Why

Of the ~60 `@dlt.source` functions in `oideachais/dlt_sources/`,
**11 sources have no Dagster asset wrapper** and therefore never
materialise into DuckLake:

### UK (4 sources unwired)
| File | Function | URL |
|---|---|---|
| `dlt_sources/uk/england/school_info.py` | `gias_source` | `get-information-schools.service.gov.uk` |
| `dlt_sources/uk/scotland/insight_benchmarking.py` | `insight_source` | `insight-guides.scotxed.net` |
| `dlt_sources/uk/scotland/simd.py` | `simd_source` | `gov.scot/...simd-2020/` |
| `dlt_sources/uk/wales/estyn.py` | `estyn_source` | `estyn.gov.wales` |

### Crown Dependencies (2 sources unwired)
| File | Function | URL |
|---|---|---|
| `dlt_sources/crown_dependencies/channel_islands.py` | `jersey_source` | `gov.je/Education/*` |
| `dlt_sources/crown_dependencies/channel_islands.py` | `guernsey_source` | `gov.gg/education*` |

(IoM's `isle_of_man_source` IS wired via `dagster_defs/assets/uk_education_assets.py:iom_curriculum`.)

### Ireland (5 sources unwired — aistear was wired in C3.1)
| File | Function | Notes |
|---|---|---|
| `dlt_sources/ireland/primary.py` | `ireland_primary_source` | 4 resources; BAML `ExtractPrimaryFramework` invoked |
| `dlt_sources/ireland/junior_cycle.py` | `ireland_junior_cycle_source` | 3 resources; BAML `ExtractJCSpec` invoked |
| `dlt_sources/ireland/tertiary.py` | `tertiary_courses` | 5 resources; pure cache-only |
| `dlt_sources/ireland/local_documents.py` | `local_education_documents_source` | 5 resources; filesystem-only |
| `dlt_sources/ireland/parallel_corpus.py` | `parallel_corpus_source` | 4 resources; Gaois/Tearma/Logainm/Duchas |

### Documented in STATUS.md / REFACTORING.md
- REFACTORING.md item #1 ("Primary + Junior Cycle British Isles
  dlt + BAML loop") explicitly calls out: *"the BAML extraction
  is unreachable"*
- STATUS.md:35 confirms the `primary.baml` and `junior_cycle.baml`
  functions are wired to dlt sources but no Dagster asset
  consumes the dlt source output

## What

Add 11 simple `@asset` wrappers in a single new file
`oideachais/dagster_defs/assets/wire_unwired_dlt_sources.py`,
following the same `leaving_cert/dlt_assets.py` pattern (plain
`@asset` + `dlt.pipeline(...)` + `safe_dlt_run(pipeline, source)`).

Each asset:
1. Reads from the corresponding dlt source
2. Writes 1 row per dlt resource to a per-source DuckLake dataset
3. Uses `safe_dlt_run` for thread-safety
4. Has a `@asset_check` asserting at least 1 row loaded
   (the existing `aistear_documents_row_count_check` pattern)
5. Has `compute_kind="dlt"` and a `group_name` per the
   `cross-domain-registry` spec

The 11 new assets:

```python
@asset(group_name="uk_education", compute_kind="dlt")
def england_gias(context) -> MaterializeResult:
    from oideachais.dlt_sources.uk.england.school_info import gias_source
    ...

@asset(group_name="uk_education", compute_kind="dlt")
def scotland_insight(context) -> MaterializeResult: ...
@asset(group_name="uk_education", compute_kind="dlt")
def scotland_simd(context) -> MaterializeResult: ...
@asset(group_name="uk_education", compute_kind="dlt")
def wales_estyn(context) -> MaterializeResult: ...

@asset(group_name="crown_dependencies_education", compute_kind="dlt")
def jersey_education(context) -> MaterializeResult: ...
@asset(group_name="crown_dependencies_education", compute_kind="dlt")
def guernsey_education(context) -> MaterializeResult: ...

@asset(group_name="ie_education", compute_kind="dlt")
def ireland_primary_dlt(context) -> MaterializeResult: ...
@asset(group_name="ie_education", compute_kind="dlt")
def ireland_junior_cycle_dlt(context) -> MaterializeResult: ...
@asset(group_name="ie_education", compute_kind="dlt")
def ireland_tertiary_dlt(context) -> MaterializeResult: ...
@asset(group_name="ie_education", compute_kind="dlt")
def ireland_local_documents_dlt(context) -> MaterializeResult: ...
@asset(group_name="ie_education", compute_kind="dlt")
def ireland_parallel_corpus_dlt(context) -> MaterializeResult: ...
```

## Impact

### Affected files
- **NEW:** `oideachais/dagster_defs/assets/wire_unwired_dlt_sources.py` (~250 lines)
- **MODIFIED:** `oideachais/dagster_defs/definitions.py` (register the 11 new assets)
- **MODIFIED:** `oideachais/dagster_defs/asset_checks.py` (add 11 row_count checks)

### Affected specs
- MODIFIED `oideachais-pipeline` — the rule that every dlt
  source in `dlt_sources/` MUST have a corresponding Dagster
  asset wrapper that materialises its tables. The 12 newly-wired
  sources now comply.

### Backward compatibility
- The dlt sources are unchanged
- The 12 new assets are additive (no existing assets modified)
- The new assets follow the same `safe_dlt_run` + `get_dlt_destination`
  pattern, so no concurrency conflicts with existing assets
- The new asset keys follow the `uk.education.{nation}.{source}`
  and `ie.education.{stage}` conventions from
  `cross-domain-registry/SKILL.md`

## Non-Goals

- No new dlt source code changes
- No new BAML functions
- No new sensors (the existing `uk_dfe_statistics_sensor`,
  `scotland_sqa_sensor`, `wales_curriculum_sensor` cover the
  change-detection use case for the wired sources; the unwired
  sources use simpler on-demand materialisation)
- No cross-nation comparison (separate openspec change)

## Risk Assessment

- **Risk: the unwired sources fail when actually invoked.** Mitigation:
  the 12 new assets use the same `safe_dlt_run` + `get_dlt_destination`
  pattern as the working assets; the dlt sources themselves are
  unchanged. If a dlt source has a runtime error, the asset
  materialisation fails with a clear Dagster error.
- **Risk: 12 new assets cause Dagster performance issues.**
  Mitigation: each asset is a simple `@asset` (not `@multi_asset`
  or `@dlt_assets`); the assets are independent and can be
  materialised in parallel; the per-asset `@asset_check` is
  minimal overhead.
- **Risk: the `parallel_corpus.py` source needs the Gaois TMX
  cache at `$GAOIS_TMX_PATH`.** Mitigation: the source has
  graceful degradation (returns empty results when cache is
  missing); the asset_check `parallel_corpus_row_count_check`
  reports the row count, which may be 0 in dev environments.

## Validation

1. `from oideachais.dlt_sources.uk.england.school_info import gias_source` succeeds
2. `from oideachais.dlt_sources.crown_dependencies.channel_islands import jersey_source, guernsey_source` succeeds
3. `from oideachais.dlt_sources.ireland.primary import ireland_primary_source` succeeds
4. `from oideachais.dlt_sources.ireland.junior_cycle import ireland_junior_cycle_source` succeeds
5. `from oideachais.dlt_sources.ireland.tertiary import tertiary_courses` succeeds
6. `from oideachais.dlt_sources.ireland.local_documents import local_education_documents_source` succeeds
7. `from oideachais.dlt_sources.ireland.parallel_corpus import parallel_corpus_source` succeeds
8. `from oideachais.dlt_sources.uk.scotland.insight_benchmarking import insight_source` succeeds
9. `from oideachais.dlt_sources.uk.scotland.simd import simd_source` succeeds
10. `from oideachais.dlt_sources.uk.wales.estyn import estyn_source` succeeds
11. `uv run --package oideachais python -c "import dagster_defs.definitions"` still loads
12. `uv run --package oideachais python -c "from oideachais.dagster_defs.assets.wire_unwired_dlt_sources import WIRE_UNWIRED_DLT_ASSETS, WIRE_UNWIRED_DLT_CHECKS; print(f'Assets: {len(WIRE_UNWIRED_DLT_ASSETS)}; Checks: {len(WIRE_UNWIRED_DLT_CHECKS)}')"` shows 11 assets + 11 checks
13. `openspec validate wire-unwired-dlt-sources --strict` passes
