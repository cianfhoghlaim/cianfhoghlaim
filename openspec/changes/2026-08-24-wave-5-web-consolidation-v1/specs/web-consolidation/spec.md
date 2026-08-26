# web-consolidation Specification

## Purpose

`web-consolidation` is a capability of the Cianfhoghlaim platform
that codifies the Wave 5 web consolidation: the 12 legacy web apps
are consolidated to 4 cianfhoghlaim surfaces (one per sister repo), all
running on TanStack Start.

This spec captures Wave 5 of the 2026-08-24 master refactor plan.

## ADDED Requirements

### Requirement: 4 cianfhoghlaim web surfaces

The 4 cianfhoghlaim web surfaces SHALL be: `tuatha-ui`
(`tuatha.cianfhoghlaim.ie`), `ciandlithe-web` (`ciandlithe.cianfhoghlaim.ie`),
`cianchosaint-web` (`cianchosaint.cianfhoghlaim.ie`), and `croilar-portal`
(`croilar.cianfhoghlaim.ie`). All 4 SHALL use TanStack Start.

#### Scenario: All 4 surfaces serve on the canonical 4 URLs

- **WHEN** `curl -sI https://tuatha.cianfhoghlaim.ie/ -o /dev/null -w "%{http_code}"` runs
- **THEN** the output SHALL be `200`
- **AND** the same for `ciandlithe.cianfhoghlaim.ie`, `cianchosaint.cianfhoghlaim.ie`, `croilar.cianfhoghlaim.ie`

### Requirement: Per-sister web app + sister dlt + sister cocoindex cascade

Each per-sister web app SHALL consume its own sister dlt + sister
cocoindex flows via the per-PR reciprocal mirror + the per-quadrant
DuckLake `metadata_schema`.

#### Scenario: Per-sister cascade works

- **WHEN** the operator opens `https://ciandlithe-web.cianfhoghlaim.ie/`
- **THEN** the page loads sister dlt data from `oideachais.legal_ireland` schema
- **AND** the page loads sister cocoindex embeddings from the legal sister repo
- **AND** the page uses the `ciandlithe` metadata_schema

### Requirement: 12 → 4 web app consolidation

The 12 legacy web apps SHALL be archived + the 4 cianfhoghlaim
surfaces SHALL be the canonical entry points.

#### Scenario: No 12 legacy web apps remain in active deployment

- **WHEN** `find web -name "package.json" -not -path "*node_modules*" -not -path "*archive*" 2>/dev/null` runs
- **THEN** the result SHALL contain exactly 4 entries (the 4 canonical surfaces)
- **AND** the other 8 legacy apps SHALL be in `web/_archive/`
