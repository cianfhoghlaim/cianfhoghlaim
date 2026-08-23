# docs-informed-content-generation Specification

## Purpose
The docs-informed content generation surface covers the docs → content pipeline (notebooks → blog posts → social cards → tutorials) across the Cianfhoghlaim monorepo. It defines 2 invariants: the canonical source-of-truth flow (notebooks/_shared/ → openspec/changes/ → docs/), and the GitHub Action that regenerates the content on every spec change.

## Requirements
### Requirement: Canonical extraction-to-generation wiring pattern

The system SHALL document and enforce a canonical pattern for turning
BAML extraction output into BAML-generated learner-facing content: every
generation function that produces quest/formative content SHALL declare
its input parameters as the current extraction schema types for its
jurisdiction (e.g. `SyllabusDocument`, `ExamPaper`, `MarkingScheme`,
`SyllabusDiagram` for the British Isles Education Pipeline v3 types), and
SHALL NOT declare a placeholder prompt body or reference a superseded
legacy schema. New subjects, jurisdictions, or content types added after
this change SHALL follow this pattern rather than re-introducing the
placeholder-prompt pattern this change removes.

#### Scenario: A new subject's generation function is added

- **GIVEN** a developer adds `qpack_biology.baml` for a new subject
- **WHEN** they write `GenerateBiologyFormativeItem`
- **THEN** the function's parameters include a real extraction type
  (`SyllabusDocument` or equivalent), not only scalar identifiers like
  `lo_code`
- **AND** the function body is a real prompt, not the literal string
  `"Auto-generated extraction prompt."`

#### Scenario: A lint check catches a regression to the placeholder pattern

- **GIVEN** a future change accidentally reintroduces a placeholder
  generation function
- **WHEN** `mise run lint:drift-docs` (or an equivalent check introduced
  by this change) runs
- **THEN** the check fails and names the offending BAML function

### Requirement: Generated-content traceability

The system SHALL ensure every piece of generated learner-facing content
(formative items, quest packs) carries evidence linking it back to the
specific source PDF page(s) it was generated from. This traceability
SHALL be queryable from the content's storage location (Convex
`questPacks` table for the MMO client) without needing to re-run
generation.

#### Scenario: Teacher inspects the source of a generated item

- **GIVEN** a quest item rendered in the MMO client
- **WHEN** a teacher requests its provenance
- **THEN** the system returns the source PDF filename and page number
  the item's content was generated from

