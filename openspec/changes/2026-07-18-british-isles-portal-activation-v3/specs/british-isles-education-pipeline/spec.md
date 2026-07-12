## ADDED Requirements

### Requirement: Central portal as the single entry point to the BIEP surface

The system SHALL publish the central portal at `portal.cianfhoghlaim.ie`
as the **single entry point** to the 6-subject BIEP surface. The 30
existing per-subject routes
(`apps/.../routes/en/subjects/<subject>/{index,syllabus,exam-papers,marking-schemes,study-plan}.tsx`)
SHALL be reachable from the central portal's Leaving Cycle tab.

This requirement is the canonical link between the BIEP data
pipeline and the new central portal entry described in
`openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md`
R19.

#### Scenario: A user clicks Mathematics from the central portal

- **GIVEN** the user is on `portal.cianfhoghlaim.ie/en/leaving-cycle`
- **WHEN** they click the Mathematics card
- **THEN** the page navigates to `/en/subjects/mathematics/`
- **AND** the Mathematics landing page renders the 4 sub-route cards
  (syllabus / exam-papers / marking-schemes / study-plan)
