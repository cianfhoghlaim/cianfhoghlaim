## ADDED Requirements

### Requirement: Per-subject marking scheme + exam paper ingestion + interactive grading (6 BIEP v1 LC subjects)

The system SHALL provide per-subject marking scheme ingestion + per-subject
interactive grading for the 6 BIEP v1 LC subjects — Mathematics,
Chemistry, Geography, Gaeilge, English, Computer Science — by extending
the canonical `MarkingScheme` + `ExamPaper` extractors with per-subject
discriminators (subject-specific enums + classes) and by adding
per-subject grading functions (`Grade<Subject>Response` +
`Explain<Subject>MarkingScheme`) that the 6 per-subject tutor agents
(Math, Chem, Geog, Gael, Eng, CS) can call.

The per-subject deliverable surface:

- 6 per-subject marking scheme BAML files at
  `baml/education/marking/<subject>_marking.baml`
- 6 per-subject grading BAML files at
  `baml/education/grading/<subject>_grading.baml`
- 6 L1 ingestion defs YAMLs at
  `orchestration/defs/1_ingestion/marking/<subject>.yaml`
- 6 L2 materials defs YAMLs at
  `orchestration/defs/2_materials/grading/<subject>.yaml`

Each per-subject marking BAML has the `<Subject>MarkingScheme` Pydantic
class (with `<Subject>SubjectDiscriminator`) and an
`Extract<Subject>MarkingScheme` function. Each per-subject grading
BAML has the `<Subject>Grade` + `<Subject>MarkingRationale` classes
and the `Grade<Subject>Response` + `Explain<Subject>MarkingScheme`
functions.

Each L1 ingestion defs YAML is a `CelticIngestionComponent` with
`source_id = filesystem.marking.<subject>`, weekly cron (marking
schemes update rarely), and per-subject partitions (year + paper +
level + language).

Each L2 materials defs YAML is a `CelticMaterialsComponent` with
`baml_function = b.Grade<Subject>Response` and
`baml_explain_function = b.Explain<Subject>MarkingScheme`. Gaeilge
uses the `irish_fada` asset check (the canonical Gaeilge-side
fidelity guard); the other 5 subjects use `baml_fidelity`.

#### Scenario: 12 per-subject BAML files exist for the 6 BIEP v1 LC subjects

- **GIVEN** the BIEP v1 capspec covers the 6 priority Irish LC subjects
- Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science
- **WHEN** the operator checks the per-subject BAML surface under
  `baml/education/marking/` + `baml/education/grading/`
- **THEN** 12 files SHALL exist:
  - `mathematics_marking.baml`, `mathematics_grading.baml`
  - `chemistry_marking.baml`, `chemistry_grading.baml`
  - `geography_marking.baml`, `geography_grading.baml`
  - `gaeilge_marking.baml`, `gaeilge_grading.baml`
  - `english_marking.baml`, `english_grading.baml`
  - `computer_science_marking.baml`, `computer_science_grading.baml`

#### Scenario: 12 per-subject defs YAMLs exist

- **WHEN** the operator checks the L1 + L2 defs surface
- **THEN** 12 YAMLs SHALL exist:
  - `orchestration/defs/1_ingestion/marking/{mathematics,chemistry,geography,gaeilge,english,computer_science}.yaml`
  - `orchestration/defs/2_materials/grading/{mathematics,chemistry,geography,gaeilge,english,computer_science}.yaml`
- **AND** each L1 YAML SHALL be a `CelticIngestionComponent` with
  `source_id = filesystem.marking.<subject>`
- **AND** each L2 YAML SHALL be a `CelticMaterialsComponent` with
  `baml_function = b.Grade<Subject>Response`

#### Scenario: per-subject grading uses per-subject discriminators (Mathematics)

- **GIVEN** a Mathematics question with `q_id = "q3a"`, `level = HL`
- **WHEN** the math tutor agent calls
  `b.GradeMathematicsResponse(student_answer, question, marking_scheme, is_higher_level=True)`
- **THEN** the system SHALL return a `MathematicsGrade` with
  `step_marks[].step_label` referring to Mathematics-specific
  step labels (e.g. "Set up chain rule", "Apply dy/dx")
- **AND** the `most_common_mistake_made` SHALL pick from the
  `MathCommonMistake` enum (e.g. `SIGN_ERROR`)
- **AND** the per-step `feedback` SHALL reference concrete
  calculus steps, not generic feedback

#### Scenario: Gaeilge grading is GA-primary

- **GIVEN** a Gaeilge question (taught in Irish)
- **WHEN** the gael tutor agent calls
  `b.GradeGaeilgeResponse(student_answer, question, marking_scheme, is_higher_level=True)`
- **THEN** the system SHALL return a `GaeilgeGrade` with
  `overall_feedback_ga` in Irish (canonical)
- **AND** `overall_feedback_en` SHALL be a translation helper (optional)
- **AND** the asset check on the L2 defs SHALL be `irish_fada`
  (asserts Irish text preserves the síneadh fada)

#### Scenario: Mathematics marking extraction yields subject discriminator

- **GIVEN** an NCCA Mathematics marking-scheme PDF for HL 2024
- **WHEN** the operator calls `b.ExtractMathematicsMarkingScheme(pdf_text, year=2024, level="hl")`
- **THEN** the system SHALL return a `MathematicsMarkingScheme` with
  `subject_specific.band_scheme = MathMarkingBand.H1..H7`
- **AND** `subject_specific.has_formula_sheet = true` (always true for LC Maths)
- **AND** `subject_specific.most_common_mistake` SHALL be one of the
  `MathCommonMistake` enum values
