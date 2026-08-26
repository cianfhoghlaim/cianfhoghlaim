# Change: Geospatial British Isles Twin (OS MasterMap + Tailte Éireann + Met Office + Met Éireann + Crown Dependencies)

## Why

The British Isles Game Dev Data Pipeline research (~31KB) identifies 5
authoritative geospatial sources that together form a "digital twin" of
the British Isles:

- **OS MasterMap** (Ordnance Survey, vector buildings + UPRN/USRN)
- **Tailte Éireann LiDAR** (Irish national mapping agency, 0.13m DCHG)
- **Met Office DataPoint** (UK weather radar, 15-min cadence)
- **Met Éireann MERA + WDB** (Irish weather, GRIB2/NetCDF hourly)
- **Crown Dependencies** (MANNGIS, Jersey Digimap)

Currently NONE of these are wired to BIEP v3 or any other pipeline.
This change adds them as the new "infrastructure scanner subdomain"
of BIEP v3.

## What changes

- **Geospatial British Isles Twin** (NEW capability
  `geospatial-british-isles-twin`): 5 DLT sources + 3
  shared utilities + 1 CocoIndex v1 App + 1 Dagster asset
  module + 1 marimo explorer + 1 MotherDuck Dive.

- **Educational Geography Curriculum** (NEW capability
  `educational-geography-curriculum`): the 4 syllabuses
  (LC + A-Level + CfE + WJEC) cross-referenced to the
  geospatial layers (climate, geomorphology, settlement,
  economy, population).

- **BIEP v3 infrastructure scanner subdomain** (capability
  `british-isles-education-pipeline-v3`): 5 new DLT
  sources under `dlt/infrastructure/`.

## Out of scope

- The Babylon.js 3D visualisation layer (per ADR-2).
- The Web3 token layer.

## Dependencies

```markdown
## Dependencies

`Blocked by: 2026-09-01-celtic-mythology-content-system-v1` (the Geography Agent + GeoAI helpers are built there).

`Blocked by: 2026-08-09-biiep-v3-4-stage-ireland-education-rollout-v1`.

`Affected repos: cianfhoghlaim`
```

## Impact

- Affected specs:
  - NEW: `geospatial-british-isles-twin` (5 ADDED Requirements)
  - NEW: `educational-geography-curriculum` (4 ADDED Requirements)
  - `british-isles-education-pipeline-v3` (2 ADDED Requirements)
- Affected code/config:
  - `dlt/infrastructure/os_mastermap.py` (NEW)
  - `dlt/infrastructure/tailte_eireann_lidar.py` (NEW)
  - `dlt/infrastructure/met_office_datapoint.py` (NEW)
  - `dlt/infrastructure/met_eireann_mera.py` (NEW)
  - `dlt/infrastructure/crown_dependencies.py` (NEW)
  - `notebooks/_shared/geo.py` (NEW)
  - `notebooks/_shared/spatial_grid.py` (NEW)
  - `cocoindex_flows/biep_parity/geospatial_embedding.py` (NEW)
  - `orchestration/defs/2_materials/infrastructure/geospatial_assets.py` (NEW)
  - `notebooks/37_geospatial_explorer.py` (NEW)
  - `motherduck/dives/british_isles_geospatial_twin.py` (NEW)