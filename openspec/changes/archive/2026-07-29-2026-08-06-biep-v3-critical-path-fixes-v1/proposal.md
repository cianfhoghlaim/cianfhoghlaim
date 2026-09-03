## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

# 2026-08-06-biep-v3-critical-path-fixes-v1

## Why

The lakehouse + DLT + CocoIndex + BAML + Dagster stack surfaced 10 critical-path
silent failures during the post-BIEP-v3 audit. These block the BIEP v3 stack
from going to production:

1. `notebooks/_shared/db.py:26` `LAKEHOUSE_URI_DEFAULT = "md:oideachais"` (24+ call-sites)
2. `cocoindex/_shared/_lifespan.py:107` `EMBED_MODEL = "bge-large-en-v1.5"` (every docstring says `bge-m3`)
3. 4 BIEP v3 MotherDuck Flights exist on disk but NOT registered in `motherduck/flights/config.yaml`
4. `motherduck/flights/lc_pdf_sync_flight.py:122` uses `md:oideachais`
5. 6 missing jurisdiction loaders in `dlt/british_isles/_cross/registry_loader.py`
6. `BIEPSubjectComponent.build_defs()` always returns empty `Definitions()`
7. 5 sensors all return `SkipReason` unconditionally
8. Dagster group names use `/` (Dagster 1.13.1 rejects)
9. `dg.toml` references nonexistent `assets.definitions`
10. The end-to-end PDF → BAML → DuckLake → CocoIndex chain is non-functional

This change fixes all 10. Lives in the `cianfhoghlaim` + `bonnegar` repos.

## What changes

### 1. Canonical namespace renames (md:oideachais → md:cianfhoghlaim)

- `notebooks/_shared/db.py:26` — `LAKEHOUSE_URI_DEFAULT = "md:oideachais"` → `"md:cianfhoghlaim"`
- `motherduck/flights/lc_pdf_sync_flight.py:122` — `duckdb.connect("md:oideachais")` → `"md:cianfhoghlaim"`
- `dlt/api_sources/youtube_videos.py:40,377` — `dataset_name="oideachais.youtube"` → `"cianfhoghlaim.youtube"`
- 5 legacy api_sources imports updated to `from cianfhoghlaim.dlt.destinations_cianfhoghlaim import get_dlt_destination`
- `tests_pkg_temp/_oideachais/dlt_utils/test_destinations_namespaced.py:33,39,122`
- docs updated

### 2. Default embedder typo fix

`cocoindex/_shared/_lifespan.py:107` — `EMBED_MODEL = "bge-large-en-v1.5"` → `"bge-m3"` (the multilingual 1024-d embedder that every docstring claims). Rename env var `OIDEACHAIS_EMBED_MODEL` → `CIANFHOGHLAIM_EMBED_MODEL`.

### 3. 4 BIEP v3 flights registered in config.yaml

Create 4 Python shim files + register in `motherduck/flights/config.yaml`:

- `motherduck/flights/ireland_full_coverage_flight.py` (cron `0 2 * * *`)
- `motherduck/flights/england_full_coverage_flight.py` (cron `0 3 * * *`)
- `motherduck/flights/sct_wls_ni_flight.py` (cron `0 4 * * *`)
- `motherduck/flights/crown_dependencies_flight.py` (cron `30 4 * * *`)

Each shim executes the corresponding `.sql` file via `duckdb.sql(...)`.

### 4. 6 missing jurisdiction loaders

Add to `dlt/british_isles/_cross/registry_loader.py`:

- `load_scotland_subjects()` — SQA 50 subjects × 3 levels
- `load_wales_subjects()` — WJEC 80 subjects × 2 levels
- `load_northern_ireland_subjects()` — CCEA 35 subjects × 2 levels
- `load_jersey_subjects()` — 30 × 4 levels
- `load_guernsey_subjects()` — 30 × 4 levels
- `load_isle_of_man_subjects()` — 30 × 4 levels

Extend `seed_registry()` to iterate the 6 new loaders.

### 5. Components + sensors made real

`orchestration/components/biep_subject_component.py:59-76` — replace
the `Definitions()` placeholder with real Definitions built from
registry rows via the 4 generic asset modules.

5 sensors at `orchestration/sensors/{ncca,sqa,wjec,ccea,jcq}_registry_sensor.py` —
replace `SkipReason` with a real poll + `RunRequest` emission.

### 6. Dagster group names + `dg.toml`

- `orchestration/defs/2_materials/{ireland,england}/**/*.py` — replace
  `/` with `_` in all `group_name=` decorators
- `dg.toml:21-29` — point `module_name` to `orchestration.definitions`
- `orchestration/definitions.py:55-65` — remove the silent `except: return Definitions()`

### 7. End-to-end chain fix

- Fix `from cianfhoghlaim.baml_client import b` (the right namespace is `baml_client` directly)
- Update the canonical `BAML_AVAILABLE` flag in all 4 generic asset modules
- Wire `EnsembledExtractor` into the 4 modules (replace the `+ 0` placeholder)
- Wire the real DuckLake writes (replace the `logger.info` stub)
- Wire the real RAGAS vote (replace the heuristic)

## Dependencies

```yaml
Blocked by: none
Blocked by (soft): 2026-08-04-lakehouse-storage-cleanup-v1
Affected repos: cianfhoghlaim + bonnegar
```

## Acceptance gates

- `notebooks/_shared/db.py:connect_md("md:cianfhoghlaim")` returns 200 OK
- `dg check yaml` passes (no `/` in group names)
- `dg list components` shows the 4 components + 4 sub-classes
- `mise run lakehouse:smoke-test` passes
- The 4 BIEP v3 flights execute on their cron schedules
- `seed_registry()` seeds 1,560 rows (Ireland 544 + England 276 + 380 SCT/WLS/NI + 360 Crown)

## Cross-references

- `baml_src/clients.baml` (the existing client config)
- `dlt/common/destinations_cianfhoghlaim.py` (the canonical destination)
- `orchestration/components/biep_subject_component.py` (the abstract Component)
- `motherduck/flights/config.yaml` (the flight registry)
- `.agents/skills/ibis/SKILL.md` (the canonical ibis contract)
