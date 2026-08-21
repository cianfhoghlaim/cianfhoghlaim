# Cross-repo-sync: 2026-08-06-biep-v3-critical-path-fixes-v1

Per the AGENTS.md "OpenSpec Change Management" + v6 lockdown convention,
this file documents the 2-repo commit plan for this change.

## Affected repos

- `cianfhoghlaim` (this repo) — DLT + DuckDB + CocoIndex + BAML + Dagster + MotherDuck code
- `bonnegar` (separate repo) — IaC stack catalogue + Lakekeeper + Nimtable + Olake + LanceDB Viewer

## Commit plan

### Commit 1 (cianfhoghlaim repo)

```
1. Update notebooks/_shared/db.py:26
2. Update cocoindex_flows/_shared/_lifespan.py:107
3. Update motherduck/flights/lc_pdf_sync_flight.py:122
4. Update dlt/api_sources/youtube_videos.py:40,377
5. Update dlt/british_isles/_cross/registry_loader.py
   - add 6 jurisdiction loaders
   - update seed_registry()
6. Update orchestration/components/biep_subject_component.py:59-76
7. Update 5 orchestration/sensors/{ncca,sqa,wjec,ccea,jcq}_registry_sensor.py
8. Update orchestration/defs/2_materials/official_media/jurisdictions_assets.py
   - replace / with _ in group_name
9. Update orchestration/definitions.py:46
   - fix import path (post-v7 flatten)
```

### Commit 2 (bonneagar repo)

```
1. Run stacks/lakehouse/compose.yaml up -d
2. Smoke-test the 3 services (curl /health endpoints)
3. Delete stacks/olake/, stacks/nimtable/, stacks/lancedb-viewer/
4. Delete komodo/stacks/{olake,nimtable,lancedb-viewer}.toml
5. Update iac/sources/key-stacks.ts:55-85
6. Update docs/lakehouse/smoke-test-2026-08-09.md
```

## Order of operations

1. Commit 1 (cianfhoghlaim) lands first — provides the registry seed function
2. Commit 2 (bonneagar) lands second — depends on the registry having
   1,560 rows before the lakehouse smoke-test can verify the S3 buckets

## Push targets

- `origin/openspec/2026-07-25-refactor-batch-v1` (the wave branch)
