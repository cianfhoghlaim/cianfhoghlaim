# `orchestration/` — Cianfhoghlaim Dagster Layer

> **The 5-layer Dagster Component Architecture for Cianfhoghlaim.** Houses `definitions.py` (the consolidated code-location) + the `defs/` tree (5 layers: Ingestion / Materials / Model Lifecycle / Asset Generation / Agent Operations) + the **`pipelines/`** tree (per-pipeline Components; canonical `dagster_dlt.DltLoadCollectionComponent` + `StateBackedComponent` per Wave 2 of the 2026-08-24 master refactor) + `automation/` (schedules + sensors) + the canonical `sync_health` asset.

## Routing

Load this AGENTS.md when:

- You need to add / modify a Dagster asset (5-layer model OR per-pipeline Component)
- You need to add / modify a Dagster schedule or sensor
- You need to run a Dagster asset or materialise the lakehouse
- You need to inspect the `sync_health` cron + Layer 6 drift reports
- You need to migrate a hand-rolled Python file to the canonical `pipelines/` Component shape

For platform-wide context, load [`../AGENTS.md`](../AGENTS.md).
For the canonical `pipelines/` tree authoring conventions, load
[`../openspec/changes/2026-08-24-master-refactor-v1/specs/dagster-pipeline-components/spec.md`](../openspec/changes/2026-08-24-master-refactor-v1/specs/dagster-pipeline-components/spec.md).

## Quick start

```bash
mise run dagster:dev                                       # Launch the consolidated Dagster UI on :3000
mise run sync:all                                          # Run all 7 sync layers
mise run sync:dagster                                      # Layer 6: validate Dagster assets via AST parsing + per-group breakdown
mise run pipelines:lint                                     # Wave 2: lint the canonical group_name on every per-pipeline Component
python3 scripts/sync/check_pipelines_yaml.py                # Wave 2: validate the canonical defs.yaml schema (DltLoadCollectionComponent)
python3 scripts/sync/scaffold_pipelines_tree.py             # Wave 2: regenerate the defs.yaml scaffold (per `@dlt.source` in dlt_sources/)
python3 scripts/sync/move_handrolled_files.py               # Wave 2: convert a hand-rolled orchestration/defs/<file>.py to a deprecation shim
python3 scripts/sync/migrate_pipeline_factory_to_dlt.py     # Wave 2: migrate a PipelineFactoryComponent defs.yaml to the canonical DltLoadCollectionComponent
```

## The two parallel trees

The `orchestration/` package houses **two parallel tree shapes**:

### 1. The horizontal `defs/` tree (the 5-layer Architecture, Wave 0+1)

```
orchestration/defs/
├── 1_ingestion/                                ─── the per-pipeline Component layer (L1)
├── 2_materials/                                ─── the BAML extraction layer (L2)
├── 3_model_lifecycle/                          ─── the CocoIndex v1 flow layer (L3)
├── 4_asset_generation/                         ─── the marimo + TanStack layer (L4)
└── 5_agent_ops/                                ─── the agent-ops layer (L5; nightly maintenance + observability)
```

190 assets across 192 `defs.yaml` files + 145 Python `@asset` decorators + 8 `@sensor` + 1 `@schedule` + 54 `@asset_check` (auto-detected by `mise run sync:dagster`).

### 2. The vertical `pipelines/` tree (per-pipeline Component, Wave 2)

```
orchestration/pipelines/
├── _shared/                                    ─── the canonical Cianfhoghlaim customisation helpers
│   ├── dagster_dlt_integration.py             ─── the canonical `translation:` callable
│   ├── state_helpers.py                       ─── the canonical `StateBackedComponent` wrapper
│   └── group_name_lint.py                     ─── the canonical `dg check yaml`-style linter
├── education/                                  ─── the per-pipeline Component tree
│   └── tertiary/                              ─── (UoG + NUI federation + British Isles)
│       └── uog/exam_papers/                   ─── each leaf has a `defs.yaml` + a Python `__init__.py`
│       └── uog/official_docs/
│       └── uog/personal_archive/
│       └── uog/students_union/
│       └── nui_federation/
│       └── british_isles/
├── law/                                        ─── the per-pipeline Component tree (Wave 2 scaffold)
├── medicine/                                   ─── the per-pipeline Component tree (Wave 2 scaffold)
├── media_intel/                                ─── the cross-medium media intel pipeline
├── raw_files/                                  ─── the raw file ingestion tree (zotero + takeout + leabharlann_books + …)
├── cv/                                         ─── the CV / résumé tree
├── artwork/                                    ─── the artwork metadata tree
├── labels/                                     ─── the label annotation tree
├── lexicographic/                              ─── the lexicographic metadata tree
├── cultural_heritage/                          ─── the cultural heritage tree
├── local_archive/                              ─── the local archive tree
├── media_text/                                 ─── the media text tree
├── media_comics/                               ─── the media comics tree
├── media_games/                                ─── the media games tree
├── media_personal/                             ─── the media personal archive tree
├── crypteolas_chain/                           ─── the crypteolas chain indexer tree
├── crypteolas_docs/                            ─── the crypteolas protocol docs tree
└── crypteolas_defi/                            ─── the crypteolas DeFi tree
```

609 per-pipeline `defs.yaml` files as of Wave 2 (canonical `dagster_dlt.DltLoadCollectionComponent` + `translation: orchestration.pipelines._shared.dagster_dlt_integration.kcg_default_translation`).

## The canonical per-pipeline Component shape

Per master plan §3.3 + the canonical `dagster-pipeline-components` spec, every per-pipeline Component under `orchestration/pipelines/<mirror>/<source>/defs.yaml` declares:

```yaml
type: dagster_dlt.DltLoadCollectionComponent
attributes:
  loads:
    - pipeline: orchestration.pipelines._shared.dagster_dlt_integration:build_dlt_pipeline|<source_module>
      source: <source_module>
      translation: orchestration.pipelines._shared.dagster_dlt_integration.kcg_default_translation
```

The `translation:` callable applies the canonical group_name + tags per master plan §7.2 (the Cianfhoghlaim naming map):

- `group_name: {layer}_{domain}_{nation}_{kind}` (e.g., `1_ingestion_education_ie_syllabus_gaeilge`)
- 5 tags: `cianfhoghlaim:domain`, `cianfhoghlaim:nation`, `cianfhoghlaim:subject`, `cianfhoghlaim:pipeline_kind`, `cianfhoghlaim:wave=2` (renamed from the legacy `kcg:` prefix on 2026-08-27; the legacy prefix is still accepted for one release cycle)

The 5 high-churn sources (NCCA + SEC + CCEA + SQA + WJEC) default to `LOCAL_FILESYSTEM` state (per `state_helpers.LOCAL_FILESYSTEM_DEFAULTS`); everything else defaults to `LEGACY_CODE_SERVER_SNAPSHOTS`.

## Key sources

| Path | Why it matters |
|:--|:--|
| `orchestration/definitions.py` | The consolidated code-location entry-point (loads both `defs/` + `pipelines/` + `_shared/` helpers + 8 deprecation shims at `defs/uog_*.py` + `defs/{nui_federation,british_isles_tertiary,media_intel}.py`) |
| `orchestration/defs/` | The horizontal 5-layer `defs/` tree (192 defs.yaml files; the Wave 0+1 legacy surface) |
| `orchestration/pipelines/` | The vertical per-pipeline Component tree (609 defs.yaml files; the Wave 2 canonical surface) |
| `orchestration/pipelines/_shared/dagster_dlt_integration.py` | The canonical `translation:` callable (the Cianfhoghlaim `kcg_default_translation` per master plan §7.2) |
| `orchestration/pipelines/_shared/state_helpers.py` | The canonical `StateBackedComponent` wrapper (`KCGStateBackedDltComponent`) + the `LOCAL_FILESYSTEM_DEFAULTS` set (the 5 high-churn sources) |
| `orchestration/pipelines/_shared/group_name_lint.py` | The canonical `dg check yaml`-style linter for the `{layer}_{domain}_{nation}_{kind}` group_name shape |
| `orchestration/components/` | The 5 Cianfhoghlaim custom Dagster Components (Declarative Automation + State-Backed) + the per-pipeline-kind handlers |
| `orchestration/resources.py` | The 24 `ConfigurableResource` subclasses (23 legacy + `BritishIslesStateResource` for the 5 high-churn sources) |
| `orchestration/dbt_translator.py` | The dbt-to-DuckLake bridge for BIEP v3 |

## Adjacent specs

- [`dagster-5-layer-component-architecture`](../openspec/specs/dagster-5-layer-component-architecture/spec.md) — the 5-layer model the `defs/` tree implements
- [`dagster-pipeline-components`](../openspec/changes/2026-08-24-master-refactor-v1/specs/dagster-pipeline-components/spec.md) — the canonical per-pipeline Component model the `pipelines/` tree implements (Wave 2)
- [`orchestration-vertical-pipelines`](../openspec/changes/2026-08-24-wave-2-orchestration-vertical-pipelines-v1/specs/orchestration-vertical-pipelines/spec.md) — the Wave 2 vertical pipeline tree + the `PipelineFactoryComponent` migration (the precursor to the canonical `DltLoadCollectionComponent`)
- [`knowledge-sync-loop`](../openspec/specs/knowledge-sync-loop/spec.md) — Layer 6 (sync:dagster) + cron + stale-skill alert + the `wave-status-panel` tab
- [`centralize-cross-cutting-docs`](../openspec/specs/centralize-cross-cutting-docs/spec.md) — the `lint:drift-docs` gate that audits this file

## DO NOT

- **Never** import raw `duckdb.connect()` in BIEP v3 paths — use `ibis.duckdb.connect("md:oideachais")` (the BIEP v3 contract is ibis-first).
- **Never** import `cianfhoghlaim.data_platform...` from within the data platform — always relative or local package imports.
- **Never** add a new asset without registering it in `orchestration/defs/<layer>/` (no top-level `orchestration/assets.py` file).
- **Never** add a new per-pipeline Component under `orchestration/pipelines/` without the canonical `dagster_dlt.DltLoadCollectionComponent` + `translation: orchestration.pipelines._shared.dagster_dlt_integration.kcg_default_translation` shape.
- **Never** add a `@dlt.source` decorated function to a dlt source whose module path is NOT in the canonical 18-domain tree (`law`, `medicine`, `education`, `lexicographic`, `cultural_heritage`, `local_archive`, `media_text`, `media_comics`, `media_games`, `media_personal`, `crypteolas_chain`, `crypteolas_docs`, `crypteolas_defi`, `raw_files`, `cv`, `artwork`, `labels`, `media_intel`).
- **Never** delete the legacy `orchestration/defs/uog_*.py` + `nui_federation.py` + `british_isles_tertiary.py` + `media_intel.py` deprecation shims — they remain in place per the constraint "Keep backward compat — leave `orchestration/defs/` as deprecation shim".

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`dagster`](../.agents/skills/dagster/SKILL.md) | Dagster 1.13+ Declarative Automation + Cianfhoghlaim Components |
| [`dagster-asset-sync`](../.agents/skills/dagster-asset-sync/SKILL.md) | Layer 6 of the knowledge-sync-loop (the `sync:dagster` task + the per-group breakdown) |
| [`dagster-dlt`](../.agents/skills/dagster-dlt/SKILL.md) | The canonical `dagster_dlt.DltLoadCollectionComponent` reference |
| [`ccc`](../.agents/skills/ccc/SKILL.md) | Semantic code search across the orchestration tree |
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | The single source of truth for models + schemas |
| [`cocoindex`](../.agents/skills/cocoindex/SKILL.md) | The CocoIndex v1 flow conventions + Live mode |
| [`motherduck`](../.agents/skills/motherduck/SKILL.md) | MotherDuck storage pattern (the BIEP lakehouse sink) |

## Data platform router

> **The single router for the 5 per-area data platform docs** is at [`../dlt_sources/DATA_PLATFORM_ROUTER.md`](../dlt_sources/DATA_PLATFORM_ROUTER.md). Documents the 6 critical conventions (relative imports / `USE_LOCAL_SCRAPES` / zero absolute namespaces / R1-R4 conformance / MODEL_REGISTRY-only / factory pattern) that apply ACROSS all 5 sub-packages.

## The 8 hand-rolled files (the deprecation shim contract)

Per Wave 2 task 2.6, the 8 hand-rolled files at `orchestration/defs/{uog_*.py, nui_federation.py, british_isles_tertiary.py, media_intel.py}` were converted to deprecation shims that re-export from `orchestration/pipelines/<mirror>/<source>/`. The legacy module's original content is preserved at `orchestration/defs/<file>.legacy.bak`. Sister repos and downstream consumers SHOULD import from the canonical `orchestration.pipelines.<path>` location; the shims will be removed in a future release.

## DuckLake v1.0 hardening (Wave 4 — `2026-08-24-wave-4-ducklake-v1-hardening-v1`)

Per Wave 4 of the 2026-08-24 master refactor plan, the DuckLake
lakehouse surface was hardened against the v1.0 spec with the
following 7 adoptions:

1. **Single namespace** (`ducklake_cianfhoghlaim`) — the 6 legacy
   namespaces (`ducklake_oideachais` / `ducklake_crypteolas` /
   `ducklake_croilar` / `ducklake_tuath` /
   `ducklake_meaisinfhoghlaim` / `ducklake_aleyum`) are
   consolidated via
   `scripts/sync/consolidate_ducklake_namespaces.py` (dry-run by
   default). Use `get_ducklake_namespace()` from
   `dlt_sources.destinations.ducklake` to ask the canonical
   accessor (do not hard-code the name).

2. **`data_inlining`** for 8 small tables
   (`SMALL_TABLES` in `dlt_sources.destinations.ducklake`).
   The `apply_data_inlining_to_table(...)` helper emits
   `ALTER TABLE ... SET (data_inlining_row_limit = 100)`.
   The `should_inline_table(...)` helper in
   `dlt_sources.british_isles._cross.jurisdiction_pipeline_base`
   decides per-row at write time.

3. **`SORTED BY (subject, board, year, language)`** on the 6 LC
   chunks tables (`SORTED_BY_TABLES`). The
   `apply_lc_chunks_sort(...)` helper in the BIEP jurisdiction
   base class wires the sort after each load. The
   `lc_chunks_sort_sql(...)` helper emits the canonical
   `ALTER TABLE ... SET SORTED BY (...)` SQL.

4. **Data change feed** via `ducklake_table_changes(...)` —
   consumed by the new sensor at
   `orchestration/sensors/ducklake_change_feed_sensor.py`. The
   `ducklake_cianfhoghlaim_table_changes(...)` helper emits the
   SQL; the sensor emits a Dagster `RunRequest` per change.

5. **Per-namespace encryption** (UoG student-data policy). The
   `ENCRYPTED_NAMESPACES` set + `set_namespace_encryption_sql(...)`
   + `namespace_encryption_info_sql(...)` helpers emit the
   `ALTER NAMESPACE ... SET (encryption_key_id = '...')` SQL.
   Verified via
   `SELECT encryption_key_id FROM ducklake_namespace_info`.

6. **Snapshot expiry policy** — 30 days for BIEP quadrants,
   7 days for media-intel + UoG personal-archive. Per-quadrant
   retention in `SNAPSHOT_RETENTION_BY_QUADRANT`; the new Dagster
   asset at `orchestration/assets/ducklake_maintenance.py`
   (`ducklake_expire_snapshots_multi_quadrant_asset`) emits one
   `CALL ducklake_expire_snapshots(...)` per quadrant nightly.

7. **Iceberg REST catalog (Lakekeeper)** for cross-engine
   compatibility at `:8181`. The
   `get_iceberg_rest_endpoint(...)` helper +
   `attach_as_iceberg_rest_sql(...)` emits the Iceberg REST URL
   (`http://lakekeeper:8181/catalog/v1/<warehouse>`). The new
   asset `ducklake_iceberg_rest_attach_verify_asset` HTTP-probes
   the endpoint nightly.

### The 3 new DuckLake maintenance assets (Wave 4)

- `orchestration/assets/ducklake_maintenance.py:ducklake_expire_snapshots_multi_quadrant_asset`
  — multi-quadrant snapshot expiry (Wave 4 §4.6).
- `orchestration/assets/ducklake_maintenance.py:ducklake_encryption_audit_asset`
  — verifies per-namespace `encryption_key_id` is set
  (Wave 4 §4.5).
- `orchestration/assets/ducklake_maintenance.py:ducklake_iceberg_rest_attach_verify_asset`
  — HTTP-probes the Lakekeeper Iceberg REST endpoint
  (Wave 4 §4.7).

### The new change feed sensor

- `orchestration/sensors/ducklake_change_feed_sensor.py:ducklake_change_feed_evaluate`
  — polls `ducklake_table_changes(...)` every 5 min, emits a
  `RunRequest` per change; consumed by the Cognee cognify pipeline
  + the daily cron sensor.

### The deprecation shim contract (Wave 4 §4.8)

`orchestration/storage/ducklake_client.py` is now a deprecation
shim that re-exports the canonical v1.0 surface from
`dlt_sources.destinations.ducklake` and emits a `DeprecationWarning`
when the legacy `DuckLakeClient` / `DuckLakeConfig` classes are
constructed. Sister repos and downstream consumers SHOULD import
from the canonical location; the shim classes will be removed
in a future release.

### The canonical namespace accessor

Every code path that needs the namespace should call
`dlt_sources.destinations.ducklake.get_ducklake_namespace()`
(returns `"ducklake_cianfhoghlaim"`) rather than hard-coding
the literal. Verified via the Wave 4 §4.1 verification path:

```bash
python -c "from dlt_sources.destinations.ducklake import get_ducklake_namespace; print(get_ducklake_namespace())"
# → ducklake_cianfhoghlaim
```

<!-- generated: 2026-08-26; do not hand-edit -->
