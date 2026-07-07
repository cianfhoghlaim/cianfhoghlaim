# `croilar-cv-extraction` spec delta — MODIFIED for persona field

## MODIFIED Requirements

### Requirement: PDF Ingestion with Persona Discriminator
The system SHALL tag all ingested PDF records with a `persona` field.

#### Scenario: CV PDFs tagged with persona
- **WHEN** CV PDFs are ingested from `author_cian_deacy_lyons.../achievement/`
- **THEN** every DLT row SHALL include `persona = "cianfhoghlaim"`

#### Scenario: Teaching PDFs tagged with persona
- **WHEN** teaching PDFs are ingested from `author_cian_deacy_lyons.../teaching/`
- **THEN** every DLT row SHALL include `persona = "cianfhoghlaim"`

### Requirement: BAML Extraction with Persona Field
The system SHALL include the persona field in all extraction function signatures.

#### Scenario: CV extraction includes persona
- **WHEN** `ExtractCV` is called
- **THEN** the extracted `EducationEntry`, `Award`, `Publication`, and `Reference` records SHALL each include `persona = "cianfhoghlaim"`

#### Scenario: Teaching extraction includes persona
- **WHEN** `ExtractPlacement` or `ExtractStudentFeedback` is called
- **THEN** the extracted records SHALL each include `persona = "cianfhoghlaim"`

### Requirement: Search Index includes Persona Scope
The system SHALL scope LanceDB search indexes by persona.

#### Scenario: CV search scoped to cianfhoghlaim
- **WHEN** a semantic search query runs against `croilar_cv`
- **THEN** results SHALL be filtered by `persona = "cianfhoghlaim"`
