## ADDED Requirements

### Requirement: Primary + Junior Cycle tabs on the central portal

The system SHALL publish the Primary + JC tabs on the central portal
(`portal.cianfhoghlaim.ie/en/primary` + `/junior-cycle`) populated
from the stage-specific BAML extraction files
(`baml/education/stages/primary.baml` + `junior_cycle.baml` +
`baml/education/primary/primary_extraction.baml` +
`baml/education/junior_cycle/junior_cycle_extraction.baml`) and the
CocoIndex apps (`primary_embedding.py` + `junior_cycle_embedding.py`).

This requirement is the canonical link between the Primary + JC data
pipeline and the new central portal entry described in
`openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md`
R17 + R19.

#### Scenario: A user opens the Primary tab

- **GIVEN** the user clicks "Primary" on the central portal
- **WHEN** the page loads
- **THEN** 4 cards render: English / Gaeilge / Mathematics / SESE
- **AND** each card shows the learning outcomes extracted by `ExtractPrimaryLearningOutcomes`

#### Scenario: A user opens the Junior Cycle tab

- **GIVEN** the user clicks "Junior Cycle" on the central portal
- **WHEN** the page loads
- **THEN** 24 JC subject cards render in a grid
- **AND** each card shows the assessment components + CBA tasks extracted by `ExtractJCSpec`
