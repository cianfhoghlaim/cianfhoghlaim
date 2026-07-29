# Spec Delta — british-isles-education-pipeline

This delta adds one new requirement to the existing `british-isles-education-pipeline` capability. Existing requirements are preserved unchanged.

## ADDED Requirements

### Requirement: All 7 lc_extraction/*.baml files use v0.212+ canonical `field Type` whitespace syntax

The British-Isles Education Pipeline SHALL enforce that every `.baml` file under `baml/education/lc_extraction/` uses the BAML v0.212+ canonical `field Type` (whitespace-separated) syntax — not the legacy Pydantic-style `field: type` colon-separated syntax. The 7 lc_extraction files (`circular_extraction.baml`, `cross_linguistic.baml`, `curriculum_syllabus.baml`, `exam_paper_layout.baml`, `lc_topic_extraction.baml`, `marking_scheme.baml`, `syllabus_diagram.baml`) define the canonical BIEP v1 contract types (`MarkingScheme`, `BilingualText`, `NCCAKeyCompetency`, `CrossNationLearningOutcome`, `PastPaper`, `SyllabusDocument`, `MarkAllocation`, `GradeDescriptor`, `DiagramPayload`, etc.) and the 7 canonical extraction functions (`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`, `ExtractMarkingSchemeGuideline`, `ExtractStrandFromCatalog`, `ExtractMarkingSchemeStrand`, `ExtractCelticCurriculumComparison`, `ExtractSyllabusDiagram`).

#### Scenario: all 7 lc_extraction/*.baml files use canonical syntax

- **GIVEN** the 2026-07-13-fix-baml-50-out-of-scope-errors-v1 change has landed
- **WHEN** `grep -rE '^\s+[a-z_][a-zA-Z0-9_]*:\s+(string|int|float|bool|list|map|class|enum|optional)\b' baml/education/lc_extraction/` is run
- **THEN** the count of Pydantic-style lines is 0 across all 7 files
- **AND** `mise run baml:generate` exits 0 against the BIEP v1 contract types

#### Scenario: BIEP v1 contract types remain unchanged

- **GIVEN** the duplicate-class renames (`MarkingScheme` → `MarkingSchemeShared` in `_shared/content_types.baml`; `BilingualText` → `BilingualTextRootPdf` in `pdfs/root_pdf_extraction.baml`; `NCCAKeyCompetency` → `NCCAKeyCompetencyRootPdf` in `pdfs/root_pdf_extraction.baml`; `CrossNationLearningOutcome` → `CrossNationLearningOutcomeIsles` in `cross_nation/isles_education.baml`)
- **WHEN** the BIEP v1 contract types are enumerated from the regenerated `baml_client/types.py`
- **THEN** the canonical class names `MarkingScheme`, `BilingualText`, `NCCAKeyCompetency`, `CrossNationLearningOutcome`, `PastPaper`, `MarkingSchemeSec`, `MarkingSchemeStrand`, `SyllabusDocument`, `MarkAllocation`, `GradeDescriptor`, `DiagramPayload` are all present
- **AND** no class name collides with the renamed duplicates (the duplicate-rename is forward-compatible with the BIEP v1 contract — the canonical names stay in `lc_extraction/*.baml` and the renamed duplicates live in adjacent files)

#### Scenario: 7 canonical BIEP v1 extraction functions still produce output

- **GIVEN** the BIEP v1 contract types are unchanged
- **WHEN** `mise run baml:test` is invoked
- **THEN** each of the 7 canonical extraction functions (`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`, `ExtractMarkingSchemeGuideline`, `ExtractStrandFromCatalog`, `ExtractMarkingSchemeStrand`, `ExtractCelticCurriculumComparison`, `ExtractSyllabusDiagram`) has at least one test block in `lc_extraction/*.baml` or `cross_nation/*.baml` that compiles successfully
- **AND** the `baml_client/` regeneration succeeds against the same input schemas as before this change