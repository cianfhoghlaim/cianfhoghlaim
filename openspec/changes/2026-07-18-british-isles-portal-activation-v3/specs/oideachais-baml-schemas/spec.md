## ADDED Requirements

### Requirement: Per-subject web schemas + stage schemas as UI schema inputs

The system SHALL cross-reference the 6 per-subject BAML web schemas
(`baml/education/web/<subject>_web.baml`) + the 5 stage BAML
extraction files
(`baml/education/stages/{aistear,primary,junior_cycle,senior_cycle,tertiary}.baml`)
as the **UI schema inputs** for the A2UI catalog at
`packages/ui/a2ui-catalog.tsx`.

This requirement is the source-of-truth for the UI schema pipeline
described in `openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md`
R18 + R21 + R22.

#### Scenario: A developer updates a per-subject web schema

- **GIVEN** a developer adds a new field to `mathematics_web.baml::MathematicsWebStudyPlanResponse`
- **WHEN** they re-generate the BAML client
- **THEN** the A2UI catalog TypeScript types update automatically
- **AND** the corresponding `<StudyPlanCard>` renderer signature updates
- **AND** `mise run baml:cli:test` fails until the catalog is updated
