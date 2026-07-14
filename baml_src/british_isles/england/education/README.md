# England BAML extraction schemas (BIEP v2)

This directory holds the 5 BAML extraction functions for the England
pipeline (3 awarding bodies × 9 priority subjects × 2 qualification levels):

- `curriculum_syllabus.baml` — `ExtractAQAQualSpec`, `ExtractOCRQualSpec`,
  `ExtractEdexcelQualSpec`
- `exam_paper_layout.baml` — `ExtractAQAExamPaper` (multi-board dispatch)
- `marking_scheme.baml` — `ExtractAQAMarkingScheme` (UMS / 9-1 grading)
- `subject_taxonomy.baml` — `ExamBoard`, `QualificationLevel`, `GCSEAQASubject`,
  `ALevelAQASubject` enums (88+ GCSE subjects, 45+ A-Level subjects)
- `ensembled_extraction.baml` — `ExtractEnglandEnsembleConsensus` (the input
  contract for Change 3's ensemble pipeline)

All 5 functions use the canonical `ExtractEnStrong` BAML client
(Qwen 3-VL 8B workhorse) — the same client the BIEP v1 LC pipeline uses
for layout-rich English-language extraction.

Reference: `openspec/changes/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/`.
