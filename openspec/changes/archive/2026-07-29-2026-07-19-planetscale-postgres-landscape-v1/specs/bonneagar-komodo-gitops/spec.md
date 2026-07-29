# Spec Delta: bonneagar-komodo-gitops

## ADDED Requirements

### Requirement: Komodo + FerretDB deferral (note)

The system SHALL keep the Komodo stack at `bonneagar/stacks/komodo/` on its local FerretDB v2 setup (the `komodo-postgres` container with the `documentdb` extension, plus the `ghcr.io/ferretdb/postgres-documentdb:17` image) **without modification** by the Phase B + C follow-ups.

This is per the operator's explicit choice in `openspec/changes/2026-07-19-planetscale-postgres-landscape-v1/`:

> *"Defer all Komodo work entirely"*

The Komodo re-architecture (if any) SHALL land in a separate future openspec change such as `2026-07-XX-komodo-ferretdb-rebuild-v1`.

#### Scenario: A consumer reads this deferral note

- **GIVEN** the operator opens `openspec/specs/bonneagar-komodo-gitops/spec.md`
- **WHEN** they look at the data substrate
- **THEN** they see the explicit deferral note pointing to the umbrella spec R8
- **AND** they do NOT expect any Phase B / Phase C modification to the Komodo compose.yaml

#### Scenario: An agent searches for Komodo substrate

- **GIVEN** the agent reads `openspec/specs/planetscale-postgres-data-strategy/spec.md` R8
- **WHEN** they look for Komodo in the 28-row matrix (R7)
- **THEN** Komodo SHALL NOT appear in R7 (deferred; no row)
- **AND** the agent SHALL consult `bonneagar-komodo-gitops/spec.md` for the local-substrate rationale
