# oideachais-university-deep-extraction — academic-history delta

## ADDED Requirements

### Requirement: Academic-module descriptor extraction

The system SHALL provide `b.ExtractAcademicModuleSyllabus` (per the
`oideachais-baml-schemas` academic-history delta) that takes an
official UoG module page (already scraped by
`uog_bulk_scrape` + `uog_extract_modules`) and produces a typed
`AcademicModuleDescriptor` record.

#### Scenario: ST311 module descriptor extracted

- **GIVEN** a module page for ST311 from
  `oideachais.education.ie.university_modules`
- **WHEN** `b.ExtractAcademicModuleSyllabus(markdown, "ST311")` runs
- **THEN** the returned `AcademicModuleDescriptor` SHALL include
  `module_code = "ST311"`, `module_title` (extracted),
  `topic_areas` (subset of `TertiaryMathTopic`),
  `key_theorems` (3-7 named theorems),
  `assessment_pieces` (per the assessment page),
  and `confidence ∈ [0.0, 1.0]`

### Requirement: Syllabus/assessment map joins personal + official

The system SHALL provide notebook
`02_module_syllabus_assessment_map.py` that joins the user's
extracted `CourseworkArtifact` rows to the official
`AcademicModuleDescriptor` rows via the
`CourseworkArtifact-PART_OF-AcademicModule` cross-archive edge
(per the `oideachais-leabharlann` academic-history delta).

#### Scenario: ST311 row joins module + LOs

- **WHEN** the user opens notebook `02_module_syllabus_assessment_map.py`
- **THEN** the table SHALL show every artefact with `module_code = "ST311"`
  alongside the official `learning_outcomes`, `assessment_pieces`,
  `prerequisites`, and `recommended_reading`