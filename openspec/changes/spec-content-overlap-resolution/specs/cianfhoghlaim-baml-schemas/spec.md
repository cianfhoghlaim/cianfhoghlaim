## ADDED Requirements

### Requirement: BAML surface compiles cleanly across the 8 jurisdiction packs

The system SHALL compile the full British Isles BAML surface (Ireland
LC6 + England + Scotland/Wales/NI + Crown Dependencies + Commonwealth
+ EU + American Nations) without error. Specifically, the BAML
compiler SHALL resolve all `function` declarations including:

- 8 `ExtractCurriculumSyllabus(subject, language)` (one per
  jurisdiction)
- 8 `ExtractExamPaperLayout(paper_code, year)` (one per jurisdiction)
- 8 `ExtractMarkingSchemeGuideline(year, paper)` (one per
  jurisdiction)
- 8 `ExtractCrossLinguisticConcept(...)` (one per jurisdiction)
- 8 `ExtractSyllabusDiagram(...)` (one per jurisdiction)

#### Scenario: All 4 canonical BIEP functions are declared with valid signatures

- **WHEN** the user runs `mise run baml:generate`
- **THEN** the BAML compiler SHALL resolve all 40 of the above
      function declarations
- **AND** `baml_src/british_isles/<jurisdiction>/education/` SHALL
      NOT depend on the deprecated `_legacy/grading/` test files
      for compilation to succeed

### Requirement: All 50 pre-existing BAML `field: type` errors resolved

The BAML surface SHALL have zero remaining pre-existing
`field: type` parse errors after the v0.223+ whitespace-syntax
fix is applied across the British Isles jurisdiction packs.

#### Scenario: baml-cli reports zero errors
- **WHEN** the user runs `mise run baml:cli test`
- **THEN** zero `field: type` parse errors SHALL be reported
- **AND** the pre-fix error count of 50 SHALL be unreachable (the
      fix is permanent)