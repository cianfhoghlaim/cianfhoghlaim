# Spec Delta — oideachais-baml-schemas

This delta adds one new requirement to the existing `oideachais-baml-schemas` capability. Existing requirements are preserved unchanged.

## ADDED Requirements

### Requirement: All 50 pre-existing BAML `field: type` errors resolved

The `oideachais-baml-schemas` capability SHALL have all 50 pre-existing BAML `field: type` parse diagnostics (captured in the baseline at `openspec/changes/2026-07-13-baml-final-cleanup-v1/SCOPE_DECISION.md`) resolved across the full `cianfhoghlaim/baml/` tree. `mise run baml:generate` SHALL exit 0 against the current tree.

#### Scenario: baml:generate exits 0 against the full tree

- **GIVEN** the 2026-07-13-fix-baml-50-out-of-scope-errors-v1 change has landed
- **WHEN** `mise run baml:generate` is run from the repo root
- **THEN** it exits with code 0
- **AND** the `baml_client/` directory is regenerated successfully (14 files written to `cianfhoghlaim/baml_client/baml_client/`)
- **AND** the canonical types `MarkingScheme`, `MarkingSchemeSec`, `MarkingSchemeStrand`, `BilingualText`, `PastPaper`, `NCCAKeyCompetency`, `CrossNationLearningOutcome` are all present in the generated `baml_client/baml_client/types.py`

#### Scenario: full BAML tree compiles cleanly

- **GIVEN** the canonical 75-file `.baml` tree at `cianfhoghlaim/baml/`
- **WHEN** `uv run baml-cli generate --from cianfhoghlaim/baml_src` is invoked
- **THEN** the BAML parser reports 0 `error:` lines in its output
- **AND** the parser reports 0 `warning:` lines related to `field: type` syntax

#### Scenario: 7 lc_extraction/*.baml files are part of the fix scope

- **GIVEN** the user chose Option 2 from the SCOPE_DECISION.md (fix ALL 50 errors including the 7 `baml/education/lc_extraction/*.baml` files)
- **WHEN** the BAML tree is grep'd for `field: type` patterns (excluding inside prompt blocks)
- **THEN** the 7 `lc_extraction/*.baml` files report 0 Pydantic-style attribute lines
- **AND** the canonical 7 lc_extraction functions (`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`, `ExtractMarkingSchemeGuideline`, `ExtractStrandFromCatalog`, `ExtractMarkingSchemeStrand`, `ExtractCelticCurriculumComparison`, `ExtractSyllabusDiagram`) all remain present and produce the same Pydantic output classes as before