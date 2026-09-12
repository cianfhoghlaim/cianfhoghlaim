# Geospatial British Isles Twin Capability

## Purpose

`geospatial-british-isles-twin` is the geospatial ingestion + render
surface for the British Isles educational MMO. It fuses OS MasterMap
+ Tailte Éireann + Met Office + Met Éireann + Crown Dependencies
data into a single spatial grid the tuatha-ui map can render at
zoom 0-18.

This capability is referenced by:
- `openspec/changes/2026-09-22-geospatial-british-isles-twin-v1`

## Requirements

### Requirement: Multi-source ingestion

The pipeline SHALL ingest from 5 sources: OS MasterMap (England +
Wales), Tailte Éireann (Ireland), Met Office (UK), Met Éireann
(IoM), Crown Dependencies (Jersey, Guernsey, IoM ordnance).

### Requirement: Spatial grid unification

The pipeline SHALL project all 5 sources to a unified spatial grid
(ETRS89 / EPSG:4258) at zoom 0-18 and emit Geoparquet files.

### Requirement: Climate overlay

The pipeline SHALL overlay current Met Office + Met Éireann data
(precipitation, temperature, wind) on the map tiles so the educational
content can render seasonal Celtic festival context.

### Requirement: Educational geography layer

The pipeline SHALL emit an `educational_geography` layer that maps
NCEA + SQA + WJEC + CCEA + JCQ + IoM + Jersey + Guernsey historic
sites (hillforts, monastic sites, Ogham stones) onto the map tiles.
