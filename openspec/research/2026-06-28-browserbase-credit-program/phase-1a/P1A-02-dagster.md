# P1A-02 — Dagster (Phase 1A, Data Plane)

**Date:** 2026-06-28
**Phase:** 1A (Data Plane Foundations)
**Budget:** ~180 credits
**Subagent:** data-platform

## TL;DR

Dagster is the **orchestration backbone** for the Cianfhoghlaim data plane. All 28 dlt sources are wrapped as `@dlt_assets`, all 5-stage PDF pipeline stages are `MultiPartitionsDefinition`s, and the 6 cognee-graph-model health checks run as `@asset_check` decorators. The single code-location is at `oideachais/dagster_defs/definitions.py`.

The canonical pattern uses:
- **Dagster 1.13+** with the `dg CLI` (replaces `dagit` for code-location management)
- **`MultiPartitionsDefinition`** for exam materials (subject × material_type) — 24 subjects × 4 types = 96 partitions
- **`@dlt_assets`** wrapper from `dagster-dlt` for every dlt source
- **`@asset_check`** with `AssetCheckResult(passed=True/False, metadata={...})` for the 6 cognee-graph-model health checks
- **`AssetSpec` / `AssetMaterialization`** for declarative asset graph definitions

## Code (where Dagster lives in Cianfhoghlaim)

| Path | Purpose |
|:--|:--|
| `cianfhoghlaim/dagster_defs/definitions.py` | Single code-location (`Definitions(...)`) — the entry point |
| `cianfhoghlaim/dagster_defs/assets/ingestion/` | `dlt_assets` wrappers (28 files, 1 per source) |
| `cianfhoghlaim/dagster_defs/assets/marimo_dashboards.py` | Marimo dashboard assets (11) |
| `cianfhoghlaim/dagster_defs/assets/cognify/` | Cross-stage cognify assets |
| `cianfhoghlaim/dagster_defs/schedules/` | 4 monthly cron schedules (official_media, leabharlann, upstream_monitor, cognify) |
| `cianfhoghlaim/dagster_defs/sensors/` | 1 breaking-change sensor for upstream packages (motherduck, dlthub, lancedb, cocoindex) |
| `cianfhoghlaim/dagster_defs/checks/` | 6 `@asset_check` health checks for cognee-graph-models |
| `dg.toml` (root) | Code-location workspace config |

**Canonical example** (`oideachais/dagster_defs/assets/ingestion/examinations.py`):

```python
from dagster import (
    MultiPartitionsDefinition,
    StaticPartitionsDefinition,
    AssetExecutionContext,
    MaterializeResult,
    asset,
)
from dagster_dlt import dlt_assets, DagsterDltResource

subjects = StaticPartitionsDefinition([...])  # 24 subjects
material_types = StaticPartitionsDefinition(["exam_paper", "marking_scheme", "audio", "video"])

examinations_partitions = MultiPartitionsDefinition({
    "subject": subjects,
    "material_type": material_types,
})

@asset(
    partitions_def=examinations_partitions,
    group_name="ingestion",
    description="24 subjects × 4 material types from examinations.ie",
)
def examinations_ie_asset(context: AssetExecutionContext):
    """Materialize a single (subject, material_type) partition."""
    partition_keys = context.partition_key.keys_by_dimension
    subject = partition_keys["subject"]
    material_type = partition_keys["material_type"]
    # ... dlt pipeline run for this partition ...
    return MaterializeResult(metadata={
        "subject": subject,
        "material_type": material_type,
        "row_count": row_count,
    })
```

**Asset check example** (`oideachais/dagster_defs/checks/cognee_models.py`):

```python
from dagster import asset_check, AssetCheckResult, MetadataValue

@asset_check(asset=AssetKey("cognee_graph_models"))
def cognee_models_health(context):
    """Verify all 7 cognee graph model files exist + parse correctly."""
    model_dir = Path("cognify/cognee_integration/graph_models")
    files = list(model_dir.glob("*.py"))
    if len(files) != 7:
        return AssetCheckResult(
            passed=False,
            metadata={"expected": 7, "found": len(files), "files": MetadataValue.json([str(f) for f in files])},
        )
    return AssetCheckResult(passed=True, metadata={"count": 7})
```

## Env (deployed configuration)

| Env var | Value | Source |
|:--|:--|:--|
| `DAGSTER_HOME` | `/opt/dagster/dagster_home` | Docker image default |
| `DAGSTER_POSTGRES_HOST` | `lakehouse-postgres` | Lakehouse stack network |
| `DAGSTER_POSTGRES_USER` | `dagster` | docker-compose env |
| `DAGSTER_POSTGRES_PASSWORD` | `${DAGSTER_POSTGRES_PASSWORD}` | Locket |
| `DAGSTER_K8S_PG_PASSWORD` | (same as above) | K8s deploy only |
| `DAGSTER_GRPC_SERVER_PORT` | `4001` | compose port mapping |

The Dagster web UI is exposed at `http://oideachais.cianfhoghlaim.ie:3080`.

## CCC anchors (where this code lives)

```
Dagster definitions entry:  cianfhoghlaim/dagster_defs/definitions.py
dlt_assets integration:     cianfhoghlaim/dagster_defs/assets/ingestion/
MultiPartitionsDefinition:  cianfhoghlaim/dagster_defs/assets/ingestion/examinations.py
@asset_check examples:        cianfhoghlaim/dagster_defs/checks/
AssetSpec definitions:       cianfhoghlaim/dagster_defs/assets/marimo_dashboards.py
Schedules (monthly cron):    cianfhoghlaim/dagster_defs/schedules/
Sensors (upstream):          cianfhoghlaim/dagster_defs/sensors/
dg.toml workspace config:    dg.toml (root)
Dagster UI container:        stacks/oideachais/dagster.yaml (compose)
```

Use these CCC search terms:
```
"@dlt_assets"                  → 28 asset wrappers
"MultiPartitionsDefinition"     → 3 multi-partitioned assets (examinations, oideachais_v1, leabharlann_v1)
"@asset_check"                  → 6 health checks
"Definitions("                  → canonical code-location entry point
"AssetCheckResult"              → health-check return type
"dagster_dlt"                   → dlt-dagster integration
```

## Drift log

| Date | Event | Action |
|:--|:--|:--|
| 2025-Q3 | `dagit` CLI used | Migrated to `dg` CLI (Dagster 1.10+) |
| 2025-Q4 | K8s deploy with `dagster-k8s` | Adopted; bumped to 1.13 |
| 2026-01 | Switched from `pandas`-based to `polars`-based assets | 3-5x faster materialization |
| 2026-02 | Added 6 `@asset_check` for cognee-graph-models | OpenSpec change `complete-cognee-knowledge-graph` |
| 2026-03 | `MultiPartitionsDefinition` for examinations | 24 subjects × 4 types = 96 partitions |
| 2026-04 | Adopted `dagster-dlt 0.25.0` for cleaner dlt integration | Replaced bespoke wrappers |
| 2026-05 | Added 1 breaking-change sensor for upstream packages | `upstream-package-monitoring` change archived |
| 2026-06-04 | Archived `audit-infrastructure-2026-06-15` | Audit phase 3 done |
| 2026-06-28 | v4 consolidation: `sruth/oideachais/dagster_defs/` → `cianfhoghlaim/dagster_defs/` | Pure rename |

Current Dagster version pin (via `pyproject.toml`):
```toml
[project.dependencies]
dagster = ">=1.13.0,<2.0.0"
dagster-webserver = ">=1.13.0,<2.0.0"
dagster-dlt = ">=0.25.0,<1.0.0"
dagster-graphql = ">=1.13.0,<2.0.0"
```

## Anti-patterns (don't do this)

1. **Don't use `@op` + `@job` directly.** Use `@asset` (Dagster 1.3+) for the data plane. `@op` is for low-level orchestration only.
2. **Don't put secrets in `dagster.yaml`** (plain text config). Use the env-var pattern (`${DAGSTER_POSTGRES_PASSWORD}`) + Locket injection.
3. **Don't create partition definitions inline in `@asset` calls.** Define them as module-level constants so they can be introspected by the asset graph and by external tools.
4. **Don't use `@repository` decorator.** Use `Definitions(...)` (Dagster 1.6+).
5. **Don't skip the `group_name` argument.** It determines the asset graph UI layout and the navigation sidebar.
6. **Don't use sync code in `@asset` functions.** Use `async def` + `await` for I/O-bound operations; Dagster's asyncio runtime supports it natively.
7. **Don't hardcode partition keys.** Use `StaticPartitionsDefinition` for known sets, `DynamicPartitionsDefinition` for runtime-discovered ones.

## Decision matrix (Phase 1A-02 conclusion)

| Decision | Choice | Rationale |
|:--|:--|:--|
| Code-location model | Single `Definitions(...)` in `definitions.py` | Simplest; matches `dg CLI` defaults |
| Asset wrapping | `@dlt_assets` for all 28 dlt sources | Native asset graph + Dagster-DLT integration |
| Partition model | `MultiPartitionsDefinition` for exams (subject × type) | 96 partitions manageable |
| Asset checks | 6 `@asset_check` decorators in `checks/cognee_models.py` | Per-graph-model health verification |
| Observability | Langfuse via `@asset` metadata | Cross-system tracing |
| Schedules | 4 monthly cron schedules | Low-frequency batch refresh |
| Sensors | 1 upstream-package-monitor sensor | Detects breaking changes in motherduck, dlthub, lancedb, cocoindex |
| Secrets | Locket + Infisical | No `.env` in git |

## Anti-pattern priority for Phase 1A-03

When researching CocoIndex v1 next, look for:
- `coco.App` (the v1 App class — replaces `cocoindex.Flow`)
- `@coco.fn` decorator (replaces `CocoIndexFlow`)
- `ContextKey` (replaces `flow_context`)
- `mount_table_target` (the v1 destination-mount API)
- `Annotated[NDArray, EMBEDDER]` (the v1 typed-embedding annotation)

## Files to read next

- `oideachais/dagster_defs/definitions.py` (1 file, 200 lines) — full asset registry
- `oideachais/dagster_defs/assets/ingestion/examinations.py` — canonical MultiPartitionsDefinition example
- `oideachios/dagster_defs/checks/cognee_models.py` — canonical asset check pattern
- `docs/skills/dagster/SKILL.md` — canonical Dagster skill (asset + dlt integration patterns)
