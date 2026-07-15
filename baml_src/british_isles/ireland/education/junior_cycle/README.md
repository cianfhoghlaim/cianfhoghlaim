# Junior Cycle BAML extraction schemas (BIEP v2)

This directory holds the 4 BAML extraction functions for the Junior Cycle
promotion from a single DLT source to a full BIEP-grade pipeline:

- `jc_curriculum_syllabus.baml` — `ExtractJCCurriculum` → `JCCurriculumSpec`
  (per-subject per-year strand + learning outcome breakdown)
- `jc_cba_descriptor.baml` — `ExtractCBADescriptor` → `CBATask`
  (the 36 NCCA Classroom-Based Assessments)
- `jc_short_course.baml` — `ExtractJCShortCourse` → `JCShortCourse`
  (the 16 NCCA short courses: Coding, Chinese, Philosophy, etc.)
- `jc_exam_paper_layout.baml` — `ExtractJCExamPaper` → `JCExamPaper`
  (JC exam-paper layout with CBA marks carried over)

All 4 functions use the canonical `ExtractEn` BAML client
(Gemma 3 4B legacy) — the same client the BIEP v1 LC pipeline uses.
For Irish-language (GA) extraction, the future `ExtractGa` client (UCCIX-Mistral-24B)
is the routing target; today we route via the `ExtractEn` client which has
multilingual capabilities.

Reference: `openspec/changes/2026-07-20-biep-v2-junior-cycle-extraction-v1/`.
