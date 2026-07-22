# _legacy/web/ — Archived BAML web files

The 6 BAML files in this directory were moved here (NOT deleted) per the
**2026-07-25-baml-archive-orphaned-and-superseded-v1** openspec change.

## Why archived (the duplicate-function-name shadow bug)

Each file declared **the same three function names** —
`WebStudyPlan`, `WebExamPaperDiscussion`, `WebMarkingSchemeExplanation` —
in 6 sibling files. Importing all 6 would have caused `baml-cli generate`
to crash with duplicate-function-name errors. Even if generated
individually, none had **any callers** in active code.

## Migration

There is no canonical replacement (no other web-side BAML functions
exist). If web routes need per-subject prompt templates, they should
use a single parameterised BAML function with a `subject: str`
argument (the same pattern as `cocoindex/subjects/lc_subject_embedding.py`).

## Revival

To revive, consolidate the 6 files into 1 parameterised function,
move it back to `web/`, run `baml-cli generate`, and wire the Dagster
assets that should consume it.

Reference: `openspec/changes/2026-07-25-baml-archive-orphaned-and-superseded-v1/`