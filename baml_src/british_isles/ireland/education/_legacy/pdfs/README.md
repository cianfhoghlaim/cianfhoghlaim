# _legacy/pdfs/ — Archived BAML PDFs files

The 3 BAML files in this directory were moved here (NOT deleted) per the
**2026-07-25-baml-archive-orphaned-and-superseded-v1** openspec change.

## Why archived (the lc_extraction/ shadow collision bug)

Each file declared a function with the **same name** as the canonical
`lc_extraction/*.baml` version:

| Archived function (here) | Canonical (lc_extraction/) |
|---|---|
| `ExtractLeavingCertSyllabus` | `curriculum_syllabus.baml:ExtractCurriculumSyllabus` |
| `ExtractPastPaper` | `exam_paper_layout.baml:ExtractExamPaperLayout` |
| `ExtractMarkingScheme` | `marking_scheme.baml:ExtractMarkingSchemeGuideline` |

Dagster asset references (`b.ExtractLeavingCertSyllabus` etc.) would
pick up **whichever BAML client loaded last** — a silent pickup bug.

## Migration

The canonical homes are:
  `baml_src/british_isles/ireland/education/lc_extraction/curriculum_syllabus.baml`
  `baml_src/british_isles/ireland/education/lc_extraction/exam_paper_layout.baml`
  `baml_src/british_isles/ireland/education/lc_extraction/marking_scheme.baml`

All Dagster assets now reference these canonicals unambiguously.

## Revival

Do NOT revive. If new PDF extraction functions are needed, add them to
the canonical `lc_extraction/*.baml` files.

Reference: `openspec/changes/2026-07-25-baml-archive-orphaned-and-superseded-v1/`