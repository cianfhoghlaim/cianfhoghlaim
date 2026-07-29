# 2026-08-06-biep-v3-critical-path-fixes-v1 — Tasks

## Pre-implementation
- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Canonical namespace renames (md:oideachais → md:cianfhoghlaim)

- [ ] Edit `notebooks/_shared/db.py:26` — `LAKEHOUSE_URI_DEFAULT = "md:oideachais"` → `"md:cianfhoghlaim"`
- [ ] Edit `motherduck/flights/lc_pdf_sync_flight.py:122` — `duckdb.connect("md:oideachais")` → `"md:cianfhoghlaim"`
- [ ] Edit `dlt/api_sources/youtube_videos.py:40,377` — `dataset_name="oideachais.youtube"` → `"cianfhoghlaim.youtube"`
- [ ] Edit `dlt/api_sources/{soundcloud_scraper,spotify_source,researchgate,linkedin,github}.py` — `from cianfhoghlaim.dlt.destinations_cianfhoghlaim import get_dlt_destination`
- [ ] Edit `tests_pkg_temp/_oideachais/dlt_utils/test_destinations_namespaced.py:33,39,122`
- [ ] Update docs

## Stage 2 — Default embedder typo fix

- [ ] Edit `cocoindex/_shared/_lifespan.py:107` — `EMBED_MODEL = "bge-large-en-v1.5"` → `"bge-m3"`
- [ ] Rename env var `OIDEACHAIS_EMBED_MODEL` → `CIANFHOGHLAIM_EMBED_MODEL`
- [ ] Update `observability/env_config.LANCEDB_URL`

## Stage 3 — 4 BIEP v3 flights registered in config.yaml

- [ ] Create `motherduck/flights/ireland_full_coverage_flight.py` (shim)
- [ ] Create `motherduck/flights/england_full_coverage_flight.py`
- [ ] Create `motherduck/flights/sct_wls_ni_flight.py`
- [ ] Create `motherduck/flights/crown_dependencies_flight.py`
- [ ] Edit `motherduck/flights/config.yaml` — register the 4 new flights

## Stage 4 — 6 missing jurisdiction loaders

- [ ] Add `load_scotland_subjects()` to `dlt/british_isles/_cross/registry_loader.py`
- [ ] Add `load_wales_subjects()`
- [ ] Add `load_northern_ireland_subjects()`
- [ ] Add `load_jersey_subjects()`
- [ ] Add `load_guernsey_subjects()`
- [ ] Add `load_isle_of_man_subjects()`
- [ ] Extend `seed_registry()` to iterate the 6 new loaders

## Stage 5 — Components + sensors made real

- [ ] Edit `orchestration/components/biep_subject_component.py:59-76` — replace `Definitions()` placeholder
- [ ] Edit `orchestration/sensors/ncca_registry_sensor.py` — replace `SkipReason`
- [ ] Edit `orchestration/sensors/sqa_registry_sensor.py`
- [ ] Edit `orchestration/sensors/wjec_registry_sensor.py`
- [ ] Edit `orchestration/sensors/ccea_registry_sensor.py`
- [ ] Edit `orchestration/sensors/jcq_registry_sensor.py`

## Stage 6 — Dagster group names + dg.toml

- [ ] Edit `orchestration/defs/2_materials/ireland/**` — replace `/` with `_` in `group_name=`
- [ ] Edit `orchestration/defs/2_materials/england/**` — same
- [ ] Edit `orchestration/defs/2_materials/sct_wls_ni/**` — same
- [ ] Edit `orchestration/defs/2_materials/crown_dependencies/**` — same
- [ ] Edit `dg.toml:21-29` — point `module_name` to `orchestration.definitions`
- [ ] Edit `orchestration/definitions.py:55-65` — remove the silent `except: return Definitions()`

## Stage 7 — End-to-end chain fix

- [ ] Fix `from cianfhoghlaim.baml_client import b` in 4 generic asset modules
- [ ] Update `BAML_AVAILABLE` flag
- [ ] Wire `EnsembledExtractor` into 4 modules (replace `+ 0` placeholder)
- [ ] Wire real DuckLake writes (replace `logger.info` stub)
- [ ] Wire real RAGAS vote (replace heuristic)

## Stage 8 — Spec delta + validation

- [ ] Write spec delta to
  `openspec/changes/2026-08-06-biep-v3-critical-path-fixes-v1/specs/infrastructure-stacks/spec.md`
- [ ] `openspec validate 2026-08-06-biep-v3-critical-path-fixes-v1 --strict`
- [ ] Commit + push
- [ ] Archive after merge: `openspec archive 2026-08-06-biep-v3-critical-path-fixes-v1 --yes`

## Post-implementation hand-off
- [ ] File any remaining bugs as GitHub issues
- [ ] Run `./scripts/sync_agent_docs.sh`