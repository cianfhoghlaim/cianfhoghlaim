# Tasks: 2026-08-24-wave-4-ducklake-v1-hardening-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-08-24-wave-4-ducklake-v1-hardening-v1/proposal.md`
- [x] **T1.2**: Create `openspec/changes/2026-08-24-wave-4-ducklake-v1-hardening-v1/tasks.md` (this file)
- [x] **T1.3**: Create `openspec/changes/2026-08-24-wave-4-ducklake-v1-hardening-v1/specs/ducklake-v1-hardening/spec.md`

## Phase 2: Layer-grouped destinations (5 tasks)

- [ ] **T2.1**: Create `dlt_sources/common/destinations/__init__.py`
  - `named_destinations(name: str)` factory — the canonical KCG pattern
  - Registry of available destination names
  - Backward-compat re-exports for the 6 legacy destinations

- [ ] **T2.2**: Create `dlt_sources/common/destinations/ducklake.py`
  - `get_ducklake_destination(...)` — DuckLake + Postgres catalog + Garage S3
  - DuckLake 1.0 features: data_inlining, sort expressions, bucket partitioning
  - `ducklake_cianfhoghlaim_at_timestamp(ts)` + `at_version(v)` time-travel helpers
  - `ducklake_cianfhoghlaim_table_changes(table)` data change feed helper

- [ ] **T2.3**: Create `dlt_sources/common/destinations/motherduck.py`
  - `get_motherduck_destination(...)` — MotherDuck managed DuckLake
  - `CIANFHOGHLAIM_MOTHERDUCK_TOKEN` env var wire-up

- [ ] **T2.4**: Create `dlt_sources/common/destinations/filesystem.py`
  - `get_filesystem_destination(...)` — local FS + S3 + GCS + Azure
  - Supports Parquet + JSONL formats

- [ ] **T2.5**: Create `dlt_sources/common/destinations/iceberg.py`
  - `get_iceberg_destination(...)` — Iceberg REST catalog via Lakekeeper (:8181)

## Phase 3: Re-export shims (5 tasks)

- [ ] **T3.1**: Replace `dlt_sources/common/destinations_cianfhoghlaim.py` body with a re-export shim
  - `from dlt_sources.common.destinations import *` + `named_destinations` + `get_ducklake_destination`
- [ ] **T3.2**: Replace `dlt_sources/common/destinations_tuatha.py` body with a re-export shim
- [ ] **T3.3**: Replace `dlt_sources/common/named_destinations.py` body with a re-export shim
- [ ] **T3.4**: Replace `dlt_sources/_lakehouse/destinations.py` body with a re-export shim
- [ ] **T3.5**: Replace `dlt_sources/_lakehouse/personal_archive_destinations.py` body with a re-export shim

## Phase 4: DuckLake 1.0 features (4 tasks)

- [ ] **T4.1**: Implement `data_inlining_row_limit` for small tables
  - Apply to `media_personal.apple_photos_chunks`, `media_descriptors`,
    `corpus.government_circulars_embedding`, etc.
- [ ] **T4.2**: Apply `SORTED BY (subject, board, year, language)` to the 6 LC chunks tables
  - `leabharlann_books`, `leabharlann_zotero`, `leabharlann_takeout`,
    `leabharlann_zotero_raw`, `leabharlann_takeout_raw`, `leabharlann_books_raw`
- [ ] **T4.3**: Implement time-travel query helpers
  - `ducklake_cianfhoghlaim_at_timestamp(ts: str)` — returns a snapshot connection
  - `ducklake_cianfhoghlaim_at_version(v: int)` — returns a snapshot connection
  - Used by syllabus-version pinning pipelines (NCCA / SEC / CCEA / SQA / WJEC)
- [ ] **T4.4**: Implement data change feed helper
  - `ducklake_cianfhoghlaim_table_changes(table: str, since: datetime)` — returns a query result
  - Consumed by the Cognee cognify pipeline to keep the knowledge graph in sync

## Phase 5: Namespace consolidation (1 task)

- [ ] **T5.1**: Add a deprecation warning to each of the 6 legacy namespaces
  - `ducklake_oideachais`, `ducklake_educational`, `ducklake_crypteolas`,
    `ducklake_tertiary`, `ducklake_uog`, `ducklake_cie`
  - Print a deprecation warning at first import
  - Route to the consolidated `ducklake_cianfhoghlaim` namespace

## Phase 6: Verification (3 tasks)

- [ ] **T6.1**: `from dlt_sources.common.destinations import named_destinations` succeeds
- [ ] **T6.2**: `named_destinations("ducklake_cianfhoghlaim").destination_name == "ducklake"`
- [ ] **T6.3**: All 6 legacy destinations files still import cleanly (re-export shims)

## Phase 7: Commit + push (2 tasks)

- [ ] **T7.1**: Stage only Wave 4 files
- [ ] **T7.2**: Commit + push

## Total: 24 tasks across 7 phases

Estimated effort: ~6 weeks (per the master plan's Wave 4 estimate).
This PR delivers the framework + layer-grouped destinations + DuckLake
1.0 feature helpers. Subsequent PRs deploy the actual catalog
migration and Lakekeeper.
