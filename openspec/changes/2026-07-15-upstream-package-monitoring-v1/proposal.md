# 2026-07-15 Upstream Package Monitoring v1

## Why

The `upstream-package-monitoring` capability spec already defines the
steady-state monitor for MotherDuck, dltHub, LanceDB, and CocoIndex, but
only the CocoIndex v1 Apps were present in-tree. The Firecrawl monitor
entrypoints, the n8n webhook bridge, and the Dagster breaking-change
sensor were missing, leaving the package-drift loop incomplete.

## What changes

This change completes Phase 1 of the capability by wiring the missing
runtime surfaces:

- Verifies the three existing CocoIndex v1 Apps:
  `upstream_blog_monitor`, `upstream_api_surface`, and
  `cocoindex_v1_conformance`.
- Adds four Firecrawl-driven monitor entrypoints under
  `cianfhoghlaim/scripts/upstream/` for `motherduck`, `dlthub`,
  `lancedb`, and `cocoindex`.
- Adds a FastAPI n8n bridge at
  `cianfhoghlaim/web/hono-api/src/routes/upstream_webhook.py`.
- Adds a Dagster polling sensor at
  `cianfhoghlaim/orchestration/sensors/upstream_breaking_change_sensor.py`.
- Adds the Phase 1 completion requirement to the
  `upstream-package-monitoring` capability delta.

## Impact

The data platform now has an end-to-end path for upstream package
release changes:

1. Firecrawl fetches canonical changelog / blog / GitHub release pages.
2. BAML `ExtractPackageRelease` extracts typed release metadata.
3. Rows land in `md:oideachais_upstream.upstream_monitoring`.
4. Breaking changes are posted to the n8n bridge.
5. The Dagster sensor polls the MotherDuck table and emits downstream
   materialisation requests.

## Dependencies

Blocked by: none
Affected repos: cianfhoghlaim
