## MODIFIED Requirements

### Requirement: 14 NCCA + NCCA-adjacent subject coverage (was: 8 NCCA Subjects)

The system SHALL provide end-to-end per-subject pipelines for
**14** subjects: the 8 NCCA Leaving Certificate subjects
(mathematics + applied_mathematics + chemistry + geography +
history + english + gaeilge + computer_science) + the 6
NCCA-adjacent subjects (accounting + biology + business +
french + irish (T2) + physics) added in the
`2026-08-26-extend-educational-mmo-to-14-subjects-v1` change.

The 8 NCCA subjects remain MANDATORY; the 6 NCCA-adjacent
subjects are an OPTIONAL extension consumers can opt into.

#### Scenario: A consumer opts into the 14-subject surface

- **GIVEN** the post-extension `cianfhoghlaim-educational-mmo` spec
- **WHEN** a consumer opts into the 14-subject surface via
  the `tuatha/` sub-project's `subapp_manifest.yaml`
- **THEN** the consumer SHALL receive:
  - 1 per-subject pipeline for each of the 14 subjects
  - 1 `qpack_<subject>.baml` BAML contract per subject
  - 1 DLT source per (subject × category) where category ∈
    {syllabus, past_paper, marking_scheme, formative_item,
    response_score}
  - 1 ADK LlmAgent per subject (in the `tuatha/subjects/`
    module)
  - 1 PixiJS realm route per subject (in the
    `tuatha/web/apps/tuatha-ui/src/routes/realm/`)
