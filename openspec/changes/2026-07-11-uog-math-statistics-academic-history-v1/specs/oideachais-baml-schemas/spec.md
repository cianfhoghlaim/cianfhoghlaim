# oideachais-baml-schemas — academic-history delta

## ADDED Requirements

### Requirement: Math/statistics extraction functions

The system SHALL provide 12 BAML functions in
`cianfhoghlaim/baml/education/university/mathematics_statistics_extraction.baml`:

1. `ExtractAcademicModuleSyllabus(pdf_text, module_code) -> AcademicModuleDescriptor`
2. `ExtractCourseworkArtifact(pdf_text, file_name, document_kind) -> CourseworkArtifactExtraction`
3. `ExtractTertiaryExamPaper(pdf_text, module_code, year) -> TertiaryExamPaper`
4. `ExtractAssignmentBrief(pdf_text, module_code) -> AssignmentBrief`
5. `ExtractStudentAnswerScript(pdf_text, assignment_id) -> StudentAnswerScript`
6. `ExtractWorkedSolution(pdf_text, question_id) -> WorkedSolution`
7. `ExtractFormulaRecords(pdf_text) -> FormulaRecord[]`
8. `ExtractTheorems(pdf_text) -> TheoremRecord[]`
9. `ExtractStatisticalProcedureRecords(pdf_text) -> StatisticalProcedureRecord[]`
10. `ExtractNumericalMethodRecords(pdf_text) -> NumericalMethodRecord[]`
11. `ExtractNonlinearSystemRecords(pdf_text) -> NonlinearSystemRecord[]`
12. `ExtractAcademicHistorySnapshot(history_json) -> AcademicHistorySnapshot`

All 12 functions SHALL route through the canonical `ExtractEn`
LiteLLM client (per the `oideachais-baml-schemas` spec).

The functions SHALL use these enums:
`TertiaryMathTopic` (40+), `DistributionFamily` (22),
`InferenceProcedure` (24+), `RegressionFamily` (16+),
`NumericalMethod` (40+), `ConvergenceRate` (7),
`NonlinearSystemKind`, `BifurcationType`, `MathContentLanguage`,
`AssignmentKind`, `DocumentKind`, `ValidationSeverity`.

#### Scenario: All 12 functions compile

- **WHEN** `baml-cli check` runs
- **THEN** exit code SHALL be 0
- **AND** the generated `baml_client` SHALL contain all 12 function
  entries plus the 13 new classes