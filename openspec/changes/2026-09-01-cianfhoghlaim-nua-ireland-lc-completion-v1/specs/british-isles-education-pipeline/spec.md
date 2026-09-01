## ADDED Requirements

### Requirement: All 14 NCCA LC subjects MUST have a BAML marking scheme extractor

The Cianfhoghlaim british-isles-education-pipeline capability MUST
expose a BAML `Extract<Subject>MarkingScheme(pdf_text, year, level)`
function for each of the 14 NCCA LC subjects:

- 8 NCCA LC priority: `chemistry`, `mathematics`, `geography`, `gaeilge`,
  `english`, `computer_science`, plus `physics` and `applied_mathematics`
- 6 NCCA-adjacent: `accounting`, `business`, `french`, `history`,
  `art`, `music`

Each extractor MUST consume a PDF text + year + level and return a
`<Subject>MarkingScheme` object with `grade_descriptors` +
`mark_allocations` + `<Subject>SubjectDiscriminator` (the
subject-specific schema).

#### Scenario: A history student requests the marking scheme

- **WHEN** a teacher invokes `b.ExtractHistoryMarkingScheme(pdf_text="...", year=2024, level="HL")`
- **THEN** the response is a `HistoryMarkingScheme` with:
  - `subject: "history"`
  - `language: "EN"`
  - `level: "HL"`
  - `year: 2024`
  - `grade_descriptors: [...]` (5 NCCA grade bands)
  - `mark_allocations: [...]`
  - `subject_specific: HistorySubjectDiscriminator` (history-specific enums)

### Requirement: The aistear + primary stages MUST have CocoIndex embeddings

The Cianfhoghlaim british-isles-education-pipeline capability MUST
expose CocoIndex Apps for the 2 early-years stages that are missing
embeddings:

1. `ireland_aistear_embedding` at
   `cocoindex_flows/british_isles/ireland/education/aistear_embedding.py`
   — consumes the ~70 Aistear PDFs from
   `stedding/site_scrape_samples/aistear/`
2. `ireland_primary_embedding` at
   `cocoindex_flows/british_isles/ireland/education/primary_embedding.py`
   — consumes the ~137 Primary PDFs from
   `stedding/site_scrape_samples/primary/`

Both Apps MUST have bilingual (EN + GA) fields per the canonical
Aistear + Primary BAML schemas.

#### Scenario: An educator queries the aistear corpus

- **WHEN** a Dagster asset runs the aistear CocoIndex App
- **THEN** the ~70 Aistear PDFs are split + embedded (BGE-M3 1024-d)
  + written to the `cianhfhoghlaim.ireland.education.aistear` LanceDB
  table
- **AND** each chunk has both `text_en` + `text_ga` fields (bilingual
  per operator direction)
- **AND** the canonical `subject_specific` discriminator includes
  the Aistear-specific `pedagogy_theme` (wellbeing /
  identity_belonging / communicating / exploring_thinking)