# oideachais-leabharlann — academic-history delta

## ADDED Requirements

### Requirement: UoG math/statistics coursework extraction

The system SHALL provide a `academic_history_math_coursework`
extraction that builds on `ExtractUoGArtifact` and applies
math-aware BAML functions from
`baml/education/university/mathematics_statistics_extraction.baml`.

#### Scenario: mata/ artefact extracted as math

- **GIVEN** a file under `leabharlann/ollscoil_na_gaillimhe/mata/`
- **WHEN** the academic-history extraction asset materialises
- **THEN** the artefact SHALL be partitioned on
  `domain = "mata"` and `document_kind ∈ {assignment, exam, lecture_notes, answer_script, worked_solution, formula_sheet, ...}`
- **AND** the BAML extraction SHALL call
  `b.ExtractCourseworkArtifact` (or the math-aware wrapper) and
  return typed `FormulaRecord` / `StatisticalProcedureRecord` /
  `NumericalMethodRecord` / `NonlinearSystemRecord` rows

## MODIFIED Requirements

### Requirement: 6 cross-archive edge rules (was: 4)

The system SHALL provide 6 cross-archive edge rules. The 2 new edges
are owned by this academic-history change:

| # | Rule | Description | Source → Target |
|:--|:--|:--|:--|
| 5 | `CourseworkArtifact-PART_OF-AcademicModule` | (new) A typed coursework artefact belongs to a typed module | match on `module_code` exact |
| 6 | `CourseworkArtifact-CONTAINS-FormulaRecord` | (new) A coursework artefact contains a typed formula | match on `file_hash` + `formula_id` |

#### Scenario: ST311 assignment mapped to module

- **GIVEN** a `CourseworkArtifact` row with `module_code = "ST311"`,
  `document_kind = ASSIGNMENT`
- **AND** an `AcademicModule` row with `module_code = "ST311"`,
  `module_title = "Statistical Inference"`
- **WHEN** the academic-history cognify pass runs
- **THEN** a `CourseworkArtifact-PART_OF-AcademicModule` edge SHALL
  be emitted
- **AND** the edge's `match_confidence = 1.0`