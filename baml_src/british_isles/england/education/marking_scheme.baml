// BAML schema: England Marking Scheme Extraction (BIEP v2)
//
// Used by the England pipeline to extract structured grading data from
// AQA / OCR / Edexcel marking-scheme + grade-boundary documents.
//
// The 9-1 grading scheme (GCSE) and the A*-E grading scheme (A-Level) are
// the canonical grading scales. UMS / raw-mark conversion tables are
// included for boards that publish them.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
//
// Reference: openspec/changes/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/

enum GCSEGrade {
  GRADE_9
  GRADE_8
  GRADE_7
  GRADE_6
  GRADE_5
  GRADE_4  @description("Standard pass")
  GRADE_3
  GRADE_2
  GRADE_1  @description("Lowest pass")
}

enum ALevelGrade {
  A_STAR
  A
  B
  C
  D
  E  @description("Lowest pass")
  U  @description("Ungraded / fail")
}

class GradeBoundary {
  grade string           @description("GCSEGrade or ALevelGrade enum value")
  raw_mark_min int
  raw_mark_max int
  ums_mark int?
}

class AQAMarkingScheme {
  board ExamBoard
  qualification_level QualificationLevel
  subject string

  grade_boundaries GradeBoundary[]
  component_weights float[]   @description("Per-component weighting percentages")

  source_pdf string
  source_pages int
  year int?
}

function ExtractAQAMarkingScheme(
  pdf_text: string,
  subject: string?,
  qualification_level: string?,
) -> AQAMarkingScheme {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
