## ADDED Requirements

### Requirement: All `*.cianfhoghlaim.ie` hostnames have live Traefik routers + live Pangolin siteResources

The system SHALL ensure that every documented `*.cianfhoghlaim.ie`
hostname has BOTH:
1. A live Traefik `router.Rule: Host(...)` entry in
   `bonneagar/pangolin/config/traefik/traefik_config.yml` that routes
   to the correct internal service.
2. A live Pangolin `siteResources` row bound to a live site (not an
   offline site).

The 17 documented hostnames SHALL include the 10 in scope for this
change (`litellm`/`langfuse`/`vikunja`/`n8n`/`glance`/`changedetection`/
`paperless`/`infisical`/`openchamber`/`komodo`) plus the 7
already-working (e.g. `pangolin`, `marimo`, `dagster`, etc.).

A `mise run lint:edge-tls-coverage` CI gate SHALL fail the build if
any hostname is missing a Traefik router OR has a Pangolin
siteResources row bound to an offline site.

#### Scenario: All 10 newly-fixed hostnames pass `check-edge-tls.sh`

- **GIVEN** the 10 hostnames in scope
- **WHEN** `bash scripts/check-edge-tls.sh --strict --all` runs
- **THEN** the command exits 0 with each hostname returning
  `verify return code: 0` (live cert) or a documented graceful
  offline-site exit
- **AND** no hostname returns `HTTP 000` (the offline-site bug) or
  `CN=TRAEFIK DEFAULT CERT` (the missing-router bug)

#### Scenario: `iac:health` reports the edge-tls check

- **GIVEN** the `iac:health` integration is wired
- **WHEN** `mise run iac:health` runs
- **THEN** the output includes a new "edge-tls" check status line
- **AND** if any hostname fails, the health check returns non-zero
- **AND** the operator sees the failing hostname(s) in the output

#### Scenario: Hourly probe catches future drift

- **GIVEN** the `cron-edge-tls-probe-both.toml` procedure is
  registered
- **WHEN** an operator introduces a hostname with a missing Traefik
  router (the regression scenario)
- **THEN** within 60 minutes (next probe cycle), the Komodo alert
  fires
- **AND** the operator receives a Slack notification (per the
  existing Komodo alert routing)

#### Scenario: Lint gate catches missing router at CI time

- **GIVEN** a developer adds a new `*.cianfhoghlaim.ie` hostname
  to a stack's `pangolin.yaml` but forgets to add the matching
  Traefik router
- **WHEN** `mise run lint:edge-tls-coverage` runs in CI
- **THEN** the lint fails with
  `missing_traefik_router: <hostname> declared in pangolin.yaml but
  no Host(...) router found in traefik_config.yml`
- **AND** the developer is forced to add the router before the
  change can ship
