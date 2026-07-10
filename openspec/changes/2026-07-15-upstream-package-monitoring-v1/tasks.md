# Tasks

- [x] 1. Read the `upstream-package-monitoring` spec and audit existing
  CocoIndex, Firecrawl, and n8n infrastructure.
- [x] 2. Verify the three existing upstream CocoIndex v1 Apps
  (`upstream_blog_monitor`, `upstream_api_surface`,
  `cocoindex_v1_conformance`) AST-parse cleanly.
- [x] 3. Add four Firecrawl monitor entrypoints at
  `cianfhoghlaim/scripts/upstream/`:
  - [x] `motherduck_monitor.py`
  - [x] `dlthub_monitor.py`
  - [x] `lancedb_monitor.py`
  - [x] `cocoindex_monitor.py`
- [x] 4. Add the FastAPI n8n webhook bridge at
  `cianfhoghlaim/api/routes/upstream_webhook.py`.
- [x] 5. Add the Dagster breaking-change sensor at
  `cianfhoghlaim/orchestration/sensors/upstream_breaking_change_sensor.py`.
- [x] 6. Verify all changed upstream-monitoring Python files AST-parse
  cleanly.
- [x] 7. Add this OpenSpec change with a Phase 1 completion spec delta
  and validate it strictly.
