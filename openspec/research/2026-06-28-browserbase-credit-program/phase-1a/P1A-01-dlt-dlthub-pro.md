# P1A-01 — dlt + dlthub-pro (Phase 1A, Data Plane)

**Date:** 2026-06-28
**Phase:** 1A (Data Plane Foundations)
**Budget:** ~180 credits
**Subagent:** data-platform

## TL;DR

`dlt` (Data Load Tool) is the ingestion backbone for every Cianfhoghlaim data source. The 5-stage PDF pipeline + leabharlann corpus (2,395 documents) + 28 dlt sources all funnel through it. `dlthub-pro` adds managed transformations, hub profiles, and data-quality rules. Together they replace the bespoke ETL scripts that historically lived in `sruth/oideachais/dlt_sources/` and predate the v4 consolidation.

The **canonical Cianfhoghlaim dlt pattern** is:

```python
@dlt.resource(primary_key="content_hash", write_disposition="merge")
def official_media() -> Iterator[Dict[str, Any]]:
    """Load official-media sources into Lakehouse Iceberg tables."""
    for url in sources:
        yield {"content_hash": hash(url), "url": url, ...}
```

Combined with `@dlt.hub.transformation` decorators + Lakehouse Iceberg destination (Garage S3 + Lakekeeper).

## Code (where dlt lives in Cianfhoghlaim)

| Path | Purpose |
|:--|:--|
| `cianfhoghlaim/dlt_sources/` | 28 DLT sources (Ireland, NI, EN, SCT, WLS, IOM, JEY, GGY) |
| `cianfhoghlaim/dlt_sources/ireland/sec.py` | Ireland SEC (Secondary Education) exam materials |
| `cianfhoghlaim/dlt_sources/uk/ucas/` | UCAS end-of-cycle datasets |
| `cianfhoghlaim/dlt_sources/leabharlann/` | Leabharlann corpus (PDFs, audio, video) |
| `cianfhoghlaim/dagster_defs/assets/ingestion/` | Dagster `@asset` wrappers around dlt resources |
| `cianfhoghlaim/cognify/rules/` | Cross-stage cognify rules that consume dlt outputs |

**Canonical example** (`oideachais/dlt_sources/official_media/__init__.py`):

```python
import dlt
from typing import Iterator, Dict, Any

@dlt.resource(
    primary_key="content_hash",
    write_disposition="merge",
    name="official_media_jurisdictions",
)
def jurisdictions() -> Iterator[Dict[str, Any]]:
    """Load 8 jurisdictions × 24 active parties = 192 jurisdictions."""
    for j in JURISDICTIONS:
        yield {"id": j["iso"], "name": j["name"], "tier": j["tier"]}
```

**Dagster integration** (`oideachais/dagster_defs/assets/ingestion/__init__.py`):

```python
from dagster_dlt import dlt_assets, DagsterDltResource

@dlt_assets(
    dlt_source=official_media_source(),
    dlt_pipeline=official_media_pipeline(),
    name="official_media",
    group_name="ingestion",
)
def official_media_assets(context, dlt_pipeline_resource: DagsterDltResource):
    yield from dlt_pipeline_resource.run(context=context)
```

## Env (deployed configuration)

| Env var | Value | Source |
|:--|:--|:--|
| `DESTINATION__LAKEHOUSE__CREDENTIALS__AWS_ACCESS_KEY_ID` | `${GARAGE_ACCESS_KEY}` | Locket (Infisical → env) |
| `DESTINATION__LAKEHOUSE__CREDENTIALS__AWS_SECRET_ACCESS_KEY` | `${GARAGE_SECRET_KEY}` | Locket |
| `DESTINATION__LAKEHOUSE__CREDENTIALS__ENDPOINT_URL` | `http://lakehouse.lakehouse:3900` | docker-compose network |
| `DLTHUB_API_KEY` | `infisical://dev-baile/dlthub/api_key` | Locket |
| `USE_LOCAL_SCRAPES` | `false` | compose default; `true` for offline stedding ingest |

The Lakehouse destination is configured via `dlt.destinations.postgres` (Iceberg catalog) + `dlt.destinations.filesystem` (Parquet on Garage S3).

## CCC anchors (where this code lives)

```
dlt source patterns:        cianfhoghlaim/dlt_sources/
official_media:             cianfhoghlaim/dlt_sources/official_media/
dlt_dagster integration:    cianfhoghlaim/dagster_defs/assets/ingestion/
leabharlann 28-source fanout: cianfhoghlaim/dlt_sources/leabharlann/
cognify rules:              cianfhoghlaim/cognify/rules/
hub transformations:        cianfhoghlaim/dlt_sources/*/_hub.py
data-quality checks:        cianfhoghlaim/dlt_sources/*/_checks.py
```

Use these CCC search terms to find more:
```
"@dlt.resource"               → 28 source files
"@dlt.hub.transformation"     → 2 transformation files
"DagsterDltResource"          → Dagster integration point
"primary_key=\"content_hash\"" → merge-write pattern (deduplication)
```

## Drift log

| Date | Event | Action |
|:--|:--|:--|
| 2025-Q3 | Original bespoke ETL scripts in `sruth/oideachais/dlt_sources/` (9 scripts) | Migrated to `dlt` resource pattern |
| 2026-01 | Dagster integration via `dagster-dlt` package | `dlt_assets` decorator wraps each source |
| 2026-03 | v1 Lakehouse Iceberg destination | Replace Parquet-on-S3-only with Iceberg ACID |
| 2026-06-04 | OpenSpec change `celtic-data-engineering-pipeline` archived | Status: 12 requirements, validated |
| 2026-06-28 | v4 consolidation: `sruth/oideachais/dlt_sources/` → `cianfhoghlaim/dlt_sources/` | Pure rename (no API changes) |

The current `dlt` version is pinned via `pyproject.toml`:
```toml
[project.dependencies]
dlt = ">=1.7.0,<2.0.0"
dagster-dlt = ">=0.25.0,<1.0.0"
```

## Anti-patterns (don't do this)

1. **Don't use absolute imports inside dlt sources.** Always `from .shared import ...` relative. The v3 code had `from oideachais.dlt_sources.shared import ...` which broke when the package was renamed to `cianfhoghlaim`.
2. **Don't put DLT secrets in `dlt.secrets.toml`** (plain text). Use the `infisical://dev-baile/<svc>/<key>` Locket-canonical form via the Locket sidecar pattern.
3. **Don't use `@dlt.resource` with `write_disposition="replace"`** for sources that accumulate over time (e.g., examinations.ie year-on-year). Use `merge` with a `primary_key` so re-ingestion is idempotent.
4. **Don't import dlt inside Dagster asset modules.** Import at module top so Dagster can introspect the asset graph at build time.
5. **Don't use `requests` directly for HTTP in dlt sources.** Use `dlt.sources.helpers.requests` for retry/backoff handling — it's already configured for the LLM-aware rate limits.
6. **Don't skip the `content_hash` primary_key.** It's how the Iceberg catalog deduplicates re-ingests; without it, every refresh creates duplicate rows.

## Decision matrix (Phase 1A conclusion)

| Decision | Choice | Rationale |
|:--|:--|:--|
| Storage destination | Iceberg on Garage S3 (via Lakekeeper catalog) | ACID + time-travel + Parquet compat |
| Write mode | `merge` with `content_hash` PK | Idempotent re-ingest |
| Dagster integration | `@dlt_assets` decorator | Native asset graph + sensor hooks |
| Source organisation | `cianfhoghlaim/dlt_sources/<nation>/<kind>/<source>.py` | 28 sources fan out cleanly |
| Secrets | Locket + Infisical | No `.env` in git |
| Local dev | `USE_LOCAL_SCRAPES=true` | Routes to `stedding/ingest_queue/` for offline development |
| Hub transformations | `@dlt.hub.transformation` | 2 cross-stage transforms (BAML-annotated + cognify-ready) |
| Data quality | `@dlt.hub.transformation` + `_checks.py` | Per-source assertions (PK, freshness, schema) |

## Anti-pattern priority for Phase 1A-02

When researching Dagster next, look for:
- `MultiPartitionsDefinition` (subject × material_type) used in `MultiPartitionsDefinition` exam materials asset
- `AssetCheckResult` (the 5-cognee-graph-model health check at `cognify/rules/asset_checks.py`)
- `dg CLI` (Dagster's new code-location command — replaces `dagit`)
- `AssetSpec`/`AssetMaterialization` API for declarative assets

## Files to read next

- `oideachais/dagster_defs/definitions.py` (1 file, 200 lines) — full asset registry
- `oideachais/dlt_sources/ireland/sec.py` (canonical example)
- `cognify/rules/asset_checks.py` — Dagster asset check patterns
- `docs/skills/dlt/SKILL.md` — canonical dlt skill (BAML extraction patterns)
