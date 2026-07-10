# Spec Delta: oideachais-cocoindex-v1-migration

## MODIFIED Requirements

### Requirement: V0 Archive

The system SHALL keep actual Python import examples in the `oideachais-cocoindex-v1-migration` spec aligned with the v4 `cianfhoghlaim` package root. When the spec shows a code import for an archived or migrated CocoIndex flow, it SHALL use `from cianfhoghlaim...` rather than `from oideachais...`.

The V0 archive SHALL remain read-only and SHALL preserve retired flow files under the archive path. Consumers SHALL import active v1 Apps from their v4 `cianfhoghlaim` package paths.

#### Scenario: Active research embedding import uses cianfhoghlaim

- **GIVEN** a migrated research embedding flow has an active v4 home
- **WHEN** the spec shows the import replacement for the archived flow
- **THEN** it uses `from cianfhoghlaim.cocoindex_flows.research_embedding import ...`
- **AND** it does not use `from oideachais.cocoindex_flows.research_embedding import ...`

#### Scenario: V0 archive remains non-authoritative

- **GIVEN** a file remains under the V0 archive path
- **WHEN** a contributor needs an active v1 App
- **THEN** the contributor SHALL use the v4 active app path under `cianfhoghlaim/cocoindex/`
- **AND** the archive SHALL NOT be treated as the runtime import surface
