# Tasks: Geospatial British Isles Twin

## Stage 0 — Pre-flight
- [ ] T0.1 — Confirm change 1 (Celtic Mythology Content System) is merged
- [ ] T0.2 — Create the new spec dirs

## Stage 1 — 5 DLT sources
- [ ] T1.1 — Create `dlt/infrastructure/os_mastermap.py`
- [ ] T1.2 — Create `dlt/infrastructure/tailte_eireann_lidar.py`
- [ ] T1.3 — Create `dlt/infrastructure/met_office_datapoint.py`
- [ ] T1.4 — Create `dlt/infrastructure/met_eireann_mera.py`
- [ ] T1.5 — Create `dlt/infrastructure/crown_dependencies.py`
- [ ] T1.6 — Run `mise run dlt:infrastructure`

## Stage 2 — Shared geo utilities
- [ ] T2.1 — Create `notebooks/_shared/geo.py`
- [ ] T2.2 — Create `notebooks/_shared/spatial_grid.py`
- [ ] T2.3 — Add unit tests for both utilities

## Stage 3 — CocoIndex v1 embedding App
- [ ] T3.1 — Create `cocoindex_flows/biep_parity/geospatial_embedding.py`
- [ ] T3.2 — Run `mise run biep:v3:cocoindex-build`

## Stage 4 — Dagster asset layer
- [ ] T4.1 — Create `orchestration/defs/2_materials/infrastructure/geospatial_assets.py`
- [ ] T4.2 — Run `mise run biep:v3:infrastructure`

## Stage 5 — Marimo explorer
- [ ] T5.1 — Create `notebooks/37_geospatial_explorer.py`
- [ ] T5.2 — Run `mise run notebook:geospatial`

## Stage 6 — MotherDuck Dive
- [ ] T6.1 — Create `motherduck/dives/british_isles_geospatial_twin.py`
- [ ] T6.2 — Add `mise run dive:geospatial` task

## Stage 7 — Educational Geography Curriculum binding
- [ ] T7.1 — Create `notebooks/_shared/curriculum.py`
- [ ] T7.2 — Cross-reference the 5 geospatial layers to the 4 syllabuses
- [ ] T7.3 — Run `mise run notebook:geography-curriculum`
- [ ] T7.4 — Register the Educational Geography Agent

## Stage 8 — Validation + handoff
- [ ] T8.1 — Run `mise run lint:skills`
- [ ] T8.2 — Run `openspec validate 2026-09-22-geospatial-british-isles-twin-v1 --strict`
- [ ] T8.3 — Run `mise run sync:all`