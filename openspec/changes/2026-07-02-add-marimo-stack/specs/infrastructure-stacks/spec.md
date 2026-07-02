# Infrastructure Stacks — Marimo Wave-3 Delta

> This file is the change-side delta for
> `2026-07-02-add-marimo-stack`. It applies on top of the
> canonical `infrastructure-stacks` spec at
> `../../../../specs/infrastructure-stacks/spec.md` and on
> top of the prior `2026-07-02-bunchloch-stack-bootstrap`
> + `2026-07-02-add-lancedb-and-logfire-stacks` deltas.

## ADDED Requirements

### Requirement: Marimo Wave 3 bring-up

The system SHALL provide a procedure to bring up the `marimo`
notebook server stack in Wave 3, after Wave 3's `invokeai` +
`convex` + `risingwave` are healthy (and after Wave 1's
`lakehouse` is healthy, since the notebook depends on
lakehouse-postgres for DuckDB queries).

#### Scenario: marimo Wave 3
- **WHEN** an agent runs `./scripts/stack.sh marimo up -d`
  after Wave 3's `invokeai` + `convex` + `risingwave` are
  healthy
- **THEN** the marimo container SHALL start using the
  pinned image `ghcr.io/marimo-team/marimo:0.11.19`
- **AND** the editor UI SHALL be reachable at
  `http://localhost:2718/`
- **AND** the loaded notebook SHALL be
  `dashboards/mmo/mission_control.py` (verified by the
  editor's title bar)

### Requirement: Image Pinning Policy applied to marimo

The system SHALL pin the marimo image to a specific semver
tag (`ghcr.io/marimo-team/marimo:0.11.19`). The
`bun run validate-stacks` Image Pinning Policy gate SHALL
report zero `:latest` WARNINGs for the marimo stack.

The marimo container SHALL mount the canonical v4 notebooks
directory at `/notebooks`
(`../../cianfhoghlaim/notebooks:/notebooks:ro`); the legacy
`../../oideachais/notebooks` path SHALL NOT be used (it no
longer exists after the 2026-06-28 v4 consolidation).

#### Scenario: marimo compose is pinned + v4-correct
- **WHEN** `bun run validate-stacks` runs against the
  marimo stack
- **THEN** the validator SHALL report zero `:latest`
  WARNINGs for the marimo stack
- **AND** the volume mount SHALL reference
  `../../cianfhoghlaim/notebooks` (NOT
  `../../oideachais/notebooks`)
- **AND** the command SHALL reference
  `dashboards/mmo/mission_control.py` (the actual location
  of the notebook in the v4 canonical layout; not the
  legacy flat `mission_control.py` reference)