# Oideachais Marimo Dashboards — Marimo Stack Bring-up Delta

> This file is the change-side delta for
> `2026-07-02-add-marimo-stack`. It applies on top of the
> canonical `oideachais-marimo-dashboards` spec at
> `../../../../specs/oideachais-marimo-dashboards/spec.md`
> and on top of the prior `2026-07-02-bunchloch-stack-bootstrap`
> delta.

## ADDED Requirements

### Requirement: Marimo notebook server (single-notebook variant)

The system SHALL provide a self-hosted marimo server stack at
`bonneagar/stacks/marimo/` that serves the
`dashboards/mmo/mission_control.py` notebook over HTTP for
the Celtic Educational MMO mission-control surface.

The marimo server SHALL be brought up via
`./scripts/stack.sh marimo up -d` (the dev-mode direct CLI).
It SHALL join both the `cianfhoghlaim` internal network and
the `lakehouse_lakehouse` external network so the notebook
can query DuckDB tables via the lakehouse Postgres +
Lance Namespace.

The marimo container SHALL use the pinned image
`ghcr.io/marimo-team/marimo:0.11.19` (the latest available
GHCR tag; the upstream GitHub release is `0.23.12` but
marimo-team does not auto-publish every release to GHCR).

The container SHALL mount the canonical notebooks directory
at `/notebooks`:
`../../cianfhoghlaim/notebooks:/notebooks:ro` (the v4
canonical path; the legacy `../../oideachais/notebooks`
path no longer exists after the 2026-06-28 v4 consolidation).

The container SHALL launch with
`marimo edit /notebooks/dashboards/mmo/mission_control.py
--host=0.0.0.0 --port=2718 --headless` so the operator can
open the editor UI at `http://localhost:2718` and navigate
the mission-control notebook's 5-stage tabs (Aistear /
Primary / JC / SC / Tertiary).

#### Scenario: Server mode bring-up
- **WHEN** an agent runs `./scripts/stack.sh marimo up -d`
  after Wave 3's `invokeai` + `convex` + `risingwave` are
  healthy (and after Wave 1's `lakehouse` is healthy, since
  the notebook depends on lakehouse-postgres for its
  DuckDB queries)
- **THEN** the marimo container SHALL start using the pinned
  image `ghcr.io/marimo-team/marimo:0.11.19`
- **AND** the healthcheck endpoint SHALL respond at
  `http://localhost:2718/api/health` (HTTP 200)
- **AND** the editor UI SHALL be reachable at
  `http://localhost:2718/`
- **AND** the loaded notebook SHALL be
  `dashboards/mmo/mission_control.py` (verified by the
  editor's title bar showing the notebook name)

#### Scenario: Notebook can read from lakehouse
- **WHEN** the operator opens the notebook and runs any cell
  that queries DuckDB (e.g. the "Aistear stages" cell that
  reads `oideachais.aistear.*` tables)
- **THEN** the cell SHALL populate with real data from
  lakehouse-postgres (via the `lakehouse_lakehouse` external
  network bridge)

### Requirement: Multi-notebook dashboard deferred to follow-up

The marimo stack SHALL serve only the single-notebook
mission-control variant in this change. The 11-notebook
multi-tab dashboard pattern from the
`oideachais-marimo-dashboards` spec (5 educational stages +
6 leabharlann subdir analyses + cross-domain) SHALL be
deferred to a separate `2026-07-XX-marimo-multi-notebook-dashboard`
follow-up change.

The marimo CLI's `edit` command runs **one notebook per
process**; a multi-notebook dashboard would require either
(a) multiple marimo processes behind a reverse proxy, or
(b) a custom landing-page notebook that embeds the others.
Both patterns are out of scope for this change.

#### Scenario: Multi-notebook dashboard not yet supported
- **WHEN** an operator wants to access all 11 marimo
  notebooks via a single UI
- **THEN** the marimo stack SHALL serve only
  `dashboards/mmo/mission_control.py`
- **AND** the operator SHALL either (a) start additional
  marimo containers on different ports via Compose
  profiles, or (b) wait for the
  `2026-07-XX-marimo-multi-notebook-dashboard` follow-up
  change