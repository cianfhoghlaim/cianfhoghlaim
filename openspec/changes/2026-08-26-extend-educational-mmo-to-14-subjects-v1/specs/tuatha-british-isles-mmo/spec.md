## ADDED Requirements

### Requirement: Canonical mirror of the standalone tuatha-british-isles-mmo spec

The main-repo `openspec/specs/tuatha-british-isles-mmo/spec.md` MUST be a canonical mirror of the standalone `~/dev/tuatha/openspec/specs/tuatha-british-isles-mmo/spec.md` (the standalone spec is the source of truth; this mirror is the main-repo's authoritative copy).

#### Scenario: The main-repo mirror is byte-identical to the standalone

- **GIVEN** the standalone `tuatha/` repo at any commit
- **WHEN** the agent diffs `openspec/specs/tuatha-british-isles-mmo/spec.md` between the standalone and the main repo
- **THEN** the files MUST be byte-identical (no drift)
- **AND** the `kcg-sync-subapps` script SHALL keep the mirror in sync (per the `sync-subapps` spec)
