# Spec delta — `oideachais-baml-schemas` — ADDED Requirement: canonical BAML 5-category compile-error fix

> This file is the spec delta for the change
> `2026-07-14-fix-foundation-v7-flattening-and-baml-drift-v1`. Apply by
> merging the ADDED Requirements block below into
> `openspec/specs/oideachais-baml-schemas/spec.md`.

## ADDED Requirements

### Requirement: BAML surface compiles cleanly across the 8 jurisdiction packs

The system SHALL compile the full British Isles BAML surface (Ireland LC6 +
England + Scotland/Wales/NI + Crown Dependencies + Commonwealth + EU +
American Nations) without error.

#### Scenario: All 4 canonical BIEP functions are declared with valid signatures

- **WHEN** the user runs `mise run baml:generate`
- **THEN** the BAML compiler SHALL resolve all `function` declarations,
      including:
  - 8 `ExtractCurriculumSyllabus(subject, language)` (one per jurisdiction)
  - 8 `ExtractExamPaperLayout(paper_code, year)` (one per jurisdiction)
  - 8 `ExtractMarkingSchemeGuideline(year, paper)` (one per jurisdiction)
  - 8 `ExtractCrossLinguisticConcept(...)` (one per jurisdiction)
  - 8 `ExtractSyllabusDiagram(...)` (one per jurisdiction)
- **AND THEN** `baml_src/british_isles/<jurisdiction>/education/` SHALL
      NOT depend on the deprecated `_legacy/grading/` test files for
      compilation to succeed

#### Scenario: Legacy grading files compile or are archived

- **WHEN** the BAML compiler walks `baml_src/british_isles/ireland/education/_legacy/grading/*.baml`
- **THEN** each file SHALL compile without error after the `test` → `Test`
      keyword fix
- **OR THEN** those files SHALL be archived to `_archive/` per the
      project's deprecation policy (one release cycle of deprecation
      shim is allowed)

#### Scenario: No missing-`client`-field errors in legacy web files

- **WHEN** the user runs `mise run baml:generate`
- **THEN** `_legacy/web/gaeilge_web.baml` SHALL compile without error after
      adding `client ExtractEn` to the 3 `Web*` functions
- **OR THEN** the file SHALL be archived to `_archive/`

#### Scenario: England schemas compile without default-value class fields

- **WHEN** the BAML compiler walks `baml_src/british_isles/england/education/`
- **THEN** `curriculum_syllabus.baml` (3 sites at lines 52, 71, 90) and
      `exam_paper_layout.baml` (line 47) SHALL NOT carry `language string = "en"`
- **AND THEN** the field type SHALL be `language string?` instead

#### Scenario: england_education ensembled_extraction.baml is valid

- **WHEN** the BAML compiler walks
      `baml_src/british_isles/england/education/ensembled_extraction.baml:38`
- **THEN** the `@description` string on `voted_canonical_id` SHALL be
      well-formed (closed before EOF)
- **AND THEN** the file SHALL compile
