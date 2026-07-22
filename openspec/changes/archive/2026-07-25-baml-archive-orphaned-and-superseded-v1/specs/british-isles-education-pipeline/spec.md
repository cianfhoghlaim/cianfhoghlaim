## REMOVED Requirements

### Requirement: per-subject grading BAML files
**Reason:** Zero callers in active code (`dlt/`, `orchestration/`, `agents/`, `notebooks/`, `scripts/`, `cocoindex/`, `baml_src/`); superseded by `lc_extraction/marking_scheme.baml:Marks Allocation`.
**Migration:** `baml_src/british_isles/ireland/education/grading/<subject>_grading.baml` (6 files) → moved to `baml_src/british_isles/ireland/education/_legacy/grading/` (preserved for future revival).

### Requirement: per-subject web BAML files
**Reason:** Zero callers in active code; ALSO duplicate function names (`WebStudyPlan`, `WebExamPaperDiscussion`, `WebMarkingSchemeExplanation` declared in 6 files — would crash `baml-cli generate`).
**Migration:** `baml_src/british_isles/ireland/education/web/<subject>_web.baml` (6 files) → moved to `baml_src/british_isles/ireland/education/_legacy/web/` (preserved for future revival).

### Requirement: per-subject PDFs BAML files
**Reason:** Function names (`ExtractLeavingCertSyllabus`, `ExtractPastPaper`, `ExtractMarkingScheme`) shadow the canonical `lc_extraction/*.baml` versions — Dagster asset references pick up whichever loads last (pickup bug).
**Migration:** `baml_src/british_isles/ireland/education/pdfs/leaving_cert_*.baml` (3 files) → moved to `baml_src/british_isles/ireland/education/_legacy/pdfs/`. All Dagster assets now reference `lc_extraction/curriculum_syllabus.baml`, `lc_extraction/exam_paper_layout.baml`, `lc_extraction/marking_scheme.baml` unambiguously.