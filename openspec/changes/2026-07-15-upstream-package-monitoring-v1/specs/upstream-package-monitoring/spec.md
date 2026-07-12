## ADDED Requirements

### Requirement: Phase 1 completion

The system SHALL complete Phase 1 of the `upstream-package-monitoring`
capability with all five baseline requirements functional: three
CocoIndex v1 Apps, four Firecrawl monitors, one n8n webhook bridge, and
one breaking-change sensor wired for the MotherDuck / dltHub / LanceDB /
CocoIndex upstream surface.

#### Scenario: End-to-end upstream monitoring surfaces are present

- **GIVEN** the data-platform agent checks out the
  `pick-4-biep-v1` branch
- **WHEN** it inspects the upstream-package-monitoring implementation
- **THEN** the three CocoIndex v1 Apps SHALL exist at
  `cocoindex/upstream_blog_monitor.py`,
  `cocoindex/upstream_api_surface.py`, and
  `cocoindex/cocoindex_v1_conformance.py`
- **AND** the four Firecrawl monitor entrypoints SHALL exist at
  `scripts/upstream/motherduck_monitor.py`,
  `scripts/upstream/dlthub_monitor.py`,
  `scripts/upstream/lancedb_monitor.py`, and
  `scripts/upstream/cocoindex_monitor.py`
- **AND** the FastAPI n8n webhook bridge SHALL exist at
  `web/hono-api/src/routes/upstream_webhook.py`
- **AND** the Dagster breaking-change sensor SHALL exist at
  `orchestration/sensors/upstream_breaking_change_sensor.py`
- **AND** all listed Python files SHALL AST-parse cleanly.

#### Scenario: Firecrawl monitor data path is wired

- **GIVEN** one of the four Firecrawl monitor entrypoints runs with an
  available Firecrawl MCP / API scrape surface
- **WHEN** it fetches a canonical changelog, blog, docs, or GitHub
  releases URL
- **THEN** it SHALL call BAML `ExtractPackageRelease` to extract
  structured release metadata
- **AND** it SHALL write the extracted row to
  `md:oideachais_upstream.upstream_monitoring`
- **AND** it SHALL trigger the n8n webhook bridge at
  `https://n8n.cianfhoghlaim.ie/webhook/upstream-breaking-change`
  whenever the release includes at least one breaking change.

#### Scenario: Breaking-change sensor routes new MotherDuck rows

- **GIVEN** `md:oideachais_upstream.upstream_monitoring` contains a new
  row with `is_breaking = TRUE`
- **WHEN** `upstream_breaking_change_sensor` evaluates
- **THEN** it SHALL emit a downstream materialisation request tagged with
  the upstream package, version, release-notes URL, and content hash
- **AND** it SHALL advance its cursor so the same breaking-change row is
  not re-alerted on the next sensor tick.
