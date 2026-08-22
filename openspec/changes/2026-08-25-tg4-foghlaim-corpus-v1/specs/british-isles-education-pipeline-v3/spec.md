## ADDED Requirements

### Requirement: MediaStreamingEnrichmentLink

The system SHALL extend the BIEP v3 subject taxonomy with a
`tg4_player_shows.biep_subject` joinable column populated by the BAML
`ClassifyTg4Episode` function from the new `tg4-foghlaim-corpus`
capability. The column SHALL map every TG4 episode + every Foghlaim
lesson to one of the 6 BIEP v1 LC subjects (`mathematics`, `chemistry`,
`geography`, `gaeilge`, `english`, `computer_science`) or one of the
18 BIEP v2 JC subjects (e.g. `history`, `gaeilge_oral`,
`gaeilge_literature`, `biology`, `physics`, `business`) or the
sentinel `non_curriculum` for purely entertainment shows.

#### Scenario: TG4 player episode joinable to BIEP Gaeilge

- **GIVEN** a `Nuacht TG4` episode is in
  `cianfhoghlaim.tg4.player_shows` with `biep_subject = "gaeilge"`
- **WHEN** an analyst queries
  `JOIN cianfhoghlaim.tg4.player_shows ON biep_subject = cianfhoghlaim.biep.leaving_cert.gaeilge.subject`
- **THEN** the join SHALL succeed with `biep_subject = "gaeilge"` matching
  `subject = "gaeilge"` in the BIEP registry

#### Scenario: Foghlaim Béaltriail lesson joinable to BIEP gaeilge_oral

- **GIVEN** a Foghlaim `Béaltriail` lesson is in
  `cianfhoghlaim.tg4.foghlaim_lessons` with `biep_subject =
  "gaeilge_oral"`
- **WHEN** the analyst runs the join against
  `cianfhoghlaim.biep.junior_cycle.gaeilge_oral`
- **THEN** the join SHALL succeed and surface the lesson's transcript
  + worksheets alongside the JC Gaeilge Oral syllabus

### Requirement: FoghlaimWorksheetAnswersLink

The system SHALL extend the BIEP v3 `lc_extraction` pipeline with a
joinable column on every BIEP LC subject that surfaces Foghlaim
worksheet answers extracted by the BAML `ExtractWorksheetAnswers`
function from the new `tg4-foghlaim-corpus` capability. The join key
SHALL be `(biep_subject, learning_outcome)` so that a JC / LC
extraction row that captures a Bloom-level outcome can be linked to the
Foghlaim worksheet questions that train that outcome.

#### Scenario: Bloom-level outcome joins to worksheet question

- **GIVEN** a BIEP `lc_extraction` row for `Leaving Cert Gaeilge` with
  `learning_outcome = "Líofacht cainte ar an ábhar reatha"` +
  `bloom_level = "apply"`
- **AND** a Foghlaim lesson `Nuacht TG4` with the same
  `biep_subject = "gaeilge"` + `learning_outcomes` containing
  `"Líofacht cainte ar an ábhar reatha"`
- **AND** the lesson has `has_worksheet = true`
- **WHEN** the analyst joins on `(biep_subject, learning_outcome)`
- **THEN** the `ExtractWorksheetAnswers` BAML output rows SHALL
  surface as the training questions for that Bloom-level outcome
- **AND** the analyst can render the worksheets in a marimo notebook
  cell

#### Scenario: Non-curriculum shows are not joined

- **GIVEN** a TG4 `Siamsaíocht` (entertainment) episode with
  `biep_subject = "non_curriculum"`
- **WHEN** the analyst joins against any BIEP subject
- **THEN** the join SHALL return zero rows (the episode is excluded
  from curriculum coverage analysis)