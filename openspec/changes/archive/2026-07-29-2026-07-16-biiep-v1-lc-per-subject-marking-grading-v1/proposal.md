# 2026-07-16-biiep-v1-lc-per-subject-marking-grading-v1

## Why

The BIEP v1 specification (capspec `british-isles-education-pipeline`)
ships the per-subject syllabus + exam paper + marking scheme + grading
loop for the 6 priority Irish Leaving Certificate subjects. The
generic `ExtractMarkingSchemeGuideline` + `ExtractExamPaperLayout`
extractors in
`baml_src/education/lc_extraction/{marking_scheme,exam_paper_layout}.baml`
already cover the cross-subject shape (GradeDescriptor[],
MarkAllocation[], QuestionSection[]), but the per-subject
**discriminators** — and the per-subject interactive grading —
were still missing. This change completes the BIEP v1 cycle.

## What Changes

Ships the per-subject marking scheme extraction + per-subject
interactive grading for the 6 BIEP v1 LC subjects (Mathematics,
Chemistry, Geography, Gaeilge, English, Computer Science):

- **6 per-subject marking scheme BAMLs** at
  `baml/education/marking/<subject>_marking.baml`
  Each adds a subject-specific discriminator (enums + class) on top
  of the canonical `MarkingScheme` type. Example: `MathMarkingBand`
  (Hl1..H7 / Ol1..Ol7), `MathQuestionType`, `MathCommonMistake` for
  Mathematics; analogous pairs for the other 5 subjects.
  Function: `Extract<Subject>MarkingScheme(pdf_text, year, level)`.

- **6 per-subject grading BAMLs** at
  `baml/education/grading/<subject>_grading.baml`
  Each exposes TWO functions:
  - `Grade<Subject>Response(student_answer, question, marking_scheme, is_higher_level)`
    → `<Subject>Grade` (per-step marks + per-subject detected mistakes
    + per-subject feedback channel)
  - `Explain<Subject>MarkingScheme(marking_scheme_id, marking_scheme)`
    → `<Subject>MarkingRationale` (per-subject rationale, weighted by the
    dominant mistake patterns).

- **6 L1 ingestion defs YAMLs** at
  `orchestration/defs/1_ingestion/marking/<subject>.yaml`
  Each wraps a `CelticIngestionComponent` with `source_id =
  filesystem.marking.<subject>`, weekly cron (marking schemes update
  rarely), per-subject partitions (year + paper + level + language).

- **6 L2 materials defs YAMLs** at
  `orchestration/defs/2_materials/grading/<subject>.yaml`
  Each wraps a `CelticMaterialsComponent` with the `b.Grade<Subject>Response`
  function as the per-subject BAML extraction step and the
  `b.Explain<Subject>MarkingScheme` function as the per-subject
  explain function. Per-subject asset-check variants:
  `irish_fada` for Gaeilge, `baml_fidelity` for the other 5.

Total: 12 new BAML files + 12 new defs YAMLs = 24 new files.

## Out of scope (per the locked plan)

- App Math + Hist (Applied Mathematics + History) are explicitly
  excluded (the existing `qpack_applied_mathematics.baml` +
  `qpack_history.baml` files stay but are not extended here).
- The existing
  `baml_src/education/lc_extraction/{marking_scheme,exam_paper_layout}.baml`
  are EXTENDED (not modified) — the generic extractors continue to work
  alongside the per-subject discriminators.

## Dependencies

`Blocked by: none` (the BIEP v1 capspec already exists; this
extends its scope with 1 ADDED requirement)

`Blocked by (soft): 2026-07-06-british-isles-education-pipeline-v1`

`Affected repos: cianfhoghlaim` (single-repo change)

## Acceptance

- `openspec validate 2026-07-16-biiep-v1-lc-per-subject-marking-grading-v1 --strict` passes
- 12 per-subject BAML files (6 marking + 6 grading) exist
- 12 per-subject defs YAMLs (6 L1 + 6 L2) exist
- 1 MODIFIED spec delta is well-formed (1 ADDED Requirement)
- Pushed to `origin/pick-4-biep-v1`
