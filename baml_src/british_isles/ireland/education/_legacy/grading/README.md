# _legacy/grading/ — Archived BAML grading files

The 6 BAML files in this directory were moved here (NOT deleted) per the
**2026-07-25-baml-archive-orphaned-and-superseded-v1** openspec change.

## Why archived

Each file declared per-subject grading prompt functions
(`Grade<Subject>Response` + `Explain<Subject>MarkingScheme`) but had
**zero callers** in active code across `dlt/`, `orchestration/`,
`agents/`, `notebooks/`, `scripts/`, `cocoindex/`, or `baml_src/`.

The canonical marking-scheme extraction lives at:
  `baml_src/british_isles/ireland/education/lc_extraction/marking_scheme.baml`
  → `ExtractMarkingSchemeGuideline(pdf_text, subject, scheme_code)`

## Migration

| Archived file | Superseded by |
|---|---|
| `chemistry_grading.baml` | `lc_extraction/marking_scheme.baml` |
| `computer_science_grading.baml` | `lc_extraction/marking_scheme.baml` |
| `english_grading.baml` | `lc_extraction/marking_scheme.baml` |
| `gaeilge_grading.baml` | `lc_extraction/marking_scheme.baml` |
| `geography_grading.baml` | `lc_extraction/marking_scheme.baml` |
| `mathematics_grading.baml` | `lc_extraction/marking_scheme.baml` |

## Revival

To revive any file, move it back to `grading/`, run `baml-cli generate`,
and update the corresponding Dagster asset to call the restored function.

Reference: `openspec/changes/2026-07-25-baml-archive-orphaned-and-superseded-v1/`