## ADDED Requirements

### Requirement: 14-subject standalone British Isles MMO coverage

The standalone `tuatha/` SHALL cover exactly **14** subjects
(the same 14 covered by the `cianfhoghlaim-educational-mmo`
spec as extended by this change). Each subject SHALL map to
its canonical `tuatha-british-isles-mmo` spec surface.

#### Scenario: The 14-subject `tuatha-british-isles-mmo` spec is shipped

- **GIVEN** the post-expansion `tuatha/openspec/specs/tuatha-british-isles-mmo/spec.md`
- **WHEN** the agent reads the spec
- **THEN** the spec SHALL declare the 14-subject coverage
  requirement + the single MMO client requirement + the
  per-subject SUBJECT_WIRING_REGISTRY requirement + the
  independent deployable TIER 3 subapp requirement

### Requirement: PixiJS v8 2.5D renderer supports 14 realms

The standalone `tuatha/web/packages/realm-canvas/` SHALL
expose a `RealmDescriptorMap` keyed by the 14 `SubjectSlug`
union members (mathematics + applied_mathematics + chemistry
+ geography + history + english + gaeilge + computer_science
+ accounting + biology + business + french + irish + physics).

#### Scenario: The 14-subject RealmDescriptorMap is registered

- **GIVEN** the post-expansion `tuatha/web/packages/realm-canvas/src/types.ts`
- **WHEN** the agent iterates over `ALL_SUBJECT_SLUGS`
- **THEN** the agent SHALL find 14 entries (one per subject)
- **AND** each entry SHALL have a matching
  `realm-canvas/src/subjects/<subject>.ts` sprite palette
