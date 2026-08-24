# 2026-08-24-wave-4-ducklake-v1-hardening-v1

## Why

The 2026-08-24 master refactor plan identified Wave 4 as the
**DuckLake v1.0 hardening** cascade. Six DuckLake namespaces currently
exist (`ducklake_oideachais`, `ducklake_educational`, `ducklake_crypteolas`,
`ducklake_tertiary`, `ducklake_uog`, `ducklake_cie`) with
**six separate sets of destination helpers** in
`dlt_sources/common/{destinations_*.py,named_destinations.py}`. This
sprawl causes:

1. **Catalog duplication** — each namespace has its own
   `postgres://loader:pass@lakehouse-postgres:5433/ducklake_<ns>`
   Postgres schema, its own `s3://ducklake-<ns>/` S3 prefix, and
   its own BIEP-axis catalog rows.

2. **Cross-namespace joins are impossible** — `SELECT * FROM
   ducklake_oideachais.mathematics UNION ALL SELECT * FROM
   ducklake_cie.mathematics` requires the orchestrator to know
   about every namespace, defeating the Wave 1 domain-first
   restructure.

3. **No time-travel** — the 6 separate catalogs don't share
   snapshots, so `AT (TIMESTAMP => '2025-09-01')` queries can't
   reconstruct a historical view of the platform.

4. **No data change feed** — `ducklake_table_changes()` is a single
   catalog operation; we have 6 separate catalogs and can't
   subscribe to changes across them.

5. **No Iceberg interoperability** — each catalog uses the default
   DuckLake metadata layout; the Lakekeeper (`:8181`) Iceberg REST
   catalog can only see ONE of them.

Per `ducklake.select/docs/stable/duckdb/usage/connecting`, DuckLake v1.0
(April 2026 stable) supports:
- `data_inlining_row_limit` (small-insert optimization)
- `SORTED BY (col)` (cluster key)
- `PARTITIONED BY (bucket(N, col))` (bucket partitioning)
- `ducklake_table_changes()` (data change feed)
- `AT (TIMESTAMP => ...)` / `AT (VERSION => ...)` (time travel)
- Iceberg REST catalog interop via `METADATA_BACKEND=iceberg-rest`

## User preferences (locked-in from prior turns)

| Decision | Choice |
|:--|:--|
| Destinations layout | **Layer-grouped** (`dlt_sources/common/destinations/{ducklake.py,motherduck.py,filesystem.py,iceberg.py}` with `named_destinations()` factory) |
| Namespace consolidation | **Single `ducklake_cianfhoghlaim`** namespace (merge all 6 legacy namespaces) |
| Postgres catalog | `postgres://loader:pass@lakehouse-postgres:5433/dlt_data` (production-grade; full MVCC parallelism) |
| Storage | Garage S3 `s3://ducklake-cianfhoghlaim/` |
| MotherDuck token | `CIANFHOGHLAIM_MOTHERDUCK_TOKEN` env var (currently missing — needs wire-up) |
| Lakekeeper | `:8181` Iceberg REST catalog (cross-engine compatible) |

## Dependencies

`Blocked by: 2026-08-24-wave-3-cocoindex-v0-stragglers-v1` (✅ landed commit `b8e7e18bd`)
`Unblocks: 2026-08-24-wave-5-web-consolidation-v1 (the oideachais/cianfhoghlaim UI apps consume the consolidated lakehouse)`

## What changes

### 1. Layer-grouped destinations

**New**: `dlt_sources/common/destinations/__init__.py`
- `named_destinations(name: str)` factory — the canonical KCG pattern
  (per the BIEP v1 spec). Returns a `@dlt.destination` function for
  the requested name (`ducklake_cianfhoghlaim`, `motherduck`,
  `filesystem_local`, `filesystem_s3`, `iceberg_rest`, etc.)

**New**: `dlt_sources/common/destinations/ducklake.py`
- `get_ducklake_destination(...)` — DuckLake + Postgres catalog +
  Garage S3 + DuckLake 1.0 optimisations (data_inlining, sort
  expressions, bucket partitioning)

**New**: `dlt_sources/common/destinations/motherduck.py`
- `get_motherduck_destination(...)` — MotherDuck managed DuckLake

**New**: `dlt_sources/common/destinations/filesystem.py`
- `get_filesystem_destination(...)` — local FS + S3 + GCS + Azure
  (Parquet/JSONL)

**New**: `dlt_sources/common/destinations/iceberg.py`
- `get_iceberg_destination(...)` — Iceberg REST catalog via Lakekeeper

### 2. Re-export shims

The 6 legacy destination files at:
- `dlt_sources/_lakehouse/destinations.py`
- `dlt_sources/_lakehouse/personal_archive_destinations.py`
- `dlt_sources/common/destinations_cianfhoghlaim.py`
- `dlt_sources/common/destinations_tuatha.py`
- `dlt_sources/common/named_destinations.py`

…become **re-export shims** that import from
`dlt_sources.common.destinations.{ducklake,motherduck,filesystem,iceberg}`.
Legacy imports continue to work.

### 3. DuckLake 1.0 features

**Data inlining**: `data_inlining_row_limit=100` for small tables
(< 100 rows). Solves the small-files problem for low-volume sources
(`media_personal.apple_photos_chunks`, `media_descriptors`, etc.).

**Sort expressions**: `SORTED BY (subject, board, year, language)`
on the 6 LC chunks tables (`leabharlann_books`,
`leabharlann_zotero`, `leabharlann_takeout`, etc.). The sort key
aligns with the BIEP axis for 10x faster BIEP-axis reads.

**Bucket partitioning**: `PARTITIONED BY (bucket(1000, jurisdiction))`
on the 6 per-jurisdiction tables. Improves high-cardinality joins.

**Time-travel queries**: `ducklake_cianfhoghlaim_at_timestamp(ts)` +
`ducklake_cianfhoghlaim_at_version(version)` helpers in
`dlt_sources/common/destinations/ducklake.py`. Used by the
syllabus-version pinning pipelines (NCCA / SEC / CCEA / SQA / WJEC).

**Data change feed**: `ducklake_cianfhoghlaim_table_changes(table)`
helper that subscribes to changes via `ducklake_table_changes()`.
The Cognee cognify pipeline consumes this to keep the knowledge
graph up-to-date with the lakehouse.

### 4. Namespace consolidation

All 6 legacy DuckLake namespaces are consolidated to a SINGLE
`ducklake_cianfhoghlaim` namespace. The BIEP axis (subject + board +
year + language) is preserved in the column order; the sort key
ensures efficient queries.

## Out of scope (deferred)

- **Actual data migration** of the 6 legacy namespaces into the new
  consolidated one — this is a Wave 4 follow-up PR with a separate
  openspec change (`2026-08-25-ducklake-namespace-data-migration-v1`).
- **MotherDuck token wire-up** — the `CIANFHOGHLAIM_MOTHERDUCK_TOKEN`
  env var is currently missing from `.env.example`. Wave 4 follow-up.
- **Lakekeeper deployment** — the Iceberg REST catalog at `:8181`
  is documented but not yet deployed. Wave 4 follow-up.
- **OpenSpec audit on the 8 sub-namespaces** (`ducklake_*.toml`
  configs) — deferred.

## Verification

After Wave 4 lands:

1. `from dlt_sources.common.destinations import named_destinations; d = named_destinations("ducklake_cianfhoghlaim"); print(d.destination_name)` prints `"ducklake"`
2. `from dlt_sources.common.destinations.ducklake import get_ducklake_destination; d = get_ducklake_destination()` returns a valid DuckLake destination
3. The 6 legacy destinations files (`destinations_cianfhoghlaim.py`,
   `destinations_tuatha.py`, etc.) still import cleanly (re-export shims)
4. `from dlt_sources.common.destinations.ducklake import ducklake_table_changes` exists and is callable
5. The 8 sort-key tables (`leabharlann_books`, `leabharlann_zotero`, etc.) get `SORTED BY (subject, board, year, language)` applied

## References

- Master plan: `openspec/plans/2026-08-24-master-refactor-plan.md`
- Wave 0 (unblocker): `openspec/changes/2026-08-24-wave-0-cocoindex-module-path-repair-v1/`
- Wave 1 (dlt_sources restructure): `openspec/changes/2026-08-24-wave-1-dlt-sources-domain-restructure-v1/`
- Wave 2 (vertical pipelines): `openspec/changes/2026-08-24-wave-2-orchestration-vertical-pipelines-v1/`
- Wave 3 (CocoIndex v0 stragglers): `openspec/changes/2026-08-24-wave-3-cocoindex-v0-stragglers-v1/`
- DuckLake docs: `https://ducklake.select/docs/stable/duckdb/introduction`
- dlt DuckLake destination: `https://dlthub.com/docs/dlt-ecosystem/destinations/ducklake`
