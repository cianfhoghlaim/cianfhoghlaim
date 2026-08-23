# Spec Delta: tuatha-platform (the deprecation delta)

## Purpose

`tuatha-platform` is the deprecated capability that was
superseded by `cianfhoghlaim-educational-mmo` per the
`2026-08-25-tuatha-british-isles-mmo-consolidation-v1`
change. This delta is the explicit deprecation notice that
finishes the supersession cycle.

## MODIFIED Requirements

### Requirement: Deprecated alias (the original 4 ADDED Requirements are moved to `cianfhoghlaim-educational-mmo` + `tuatha-british-isles-mmo`)

The system SHALL NOT add NEW capability to this spec. The 4
original ADDED Requirements (the Pent-Elemental Cosmology + the
Babylon.js 3D game front-end + the SpacetimeDB v2 game engine
backend + the Crypteolas financial token) are SUPERSEDED by:

- The `cianfhoghlaim-educational-mmo` spec (the canonical
  British Isles Formative Assessment MMO spec)
- The `tuatha-british-isles-mmo` spec (the new canonical
  Tuatha project capability)
- The 5 parent pending changes that
  `2026-08-25-tuatha-british-isles-mmo-consolidation-v1`
  `Blocked by`:
  - `2026-09-01-celtic-mythology-content-system-v1`
  - `2026-09-08-ogham-celtic-stones-pipeline-v1`
  - `2026-09-22-geospatial-british-isles-twin-v1`
  - `2026-09-29-familiar-dynamic-nft-system-v1`
  - `2026-10-06-spacetimedb-babylonjs-adr-clean-break-v1`

This spec remains as a back-compat alias for 1 release
(per the canonical `cianfhoghlaim-educational-mmo` spec
deprecation policy), then it is archived.

#### Scenario: A user opens the deprecated spec

- **WHEN** the user opens this spec
- **THEN** the spec's preamble carries the deprecation notice
  (in the format: "DEPRECATED: superseded by
  cianfhoghlaim-educational-mmo + tuatha-british-isles-mmo")
- **AND** the spec's 4 original ADDED Requirements are marked as
  `<!-- DEPRECATED: see cianfhoghlaim-educational-mmo for the
  canonical spec -->`
- **AND** the spec is not eligible for any new ADDED Requirements

#### Scenario: The 1-release back-compat window closes

- **WHEN** the operator runs `openspec archive
  2026-08-25-tuatha-british-isles-mmo-consolidation-v1 --yes`
  + the 5 parent changes archive
- **THEN** the operator runs `openspec archive tuatha-platform
  --yes` (a subsequent change)
- **AND** the spec moves to `openspec/specs/_archive/tuatha-platform/`
- **AND** the back-compat alias is removed
