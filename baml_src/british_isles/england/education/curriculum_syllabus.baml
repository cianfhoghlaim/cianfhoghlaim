// BAML schema: England Curriculum Syllabus Extraction (BIEP v2)
//
// Used by the England pipeline (3 awarding bodies × 9 subjects) to extract
// structured qualification-spec data from AQA / OCR / Edexcel specification
// PDFs. Each of the 3 awarding bodies has its own dedicated function for
// board-specific schemas (so future AQA-vs-OCR diffing is straightforward).
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
//
// Reference: openspec/changes/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/


class AssessmentObjective {
  ao_id string
  title string
  description string
  weighting_pct int     @description("Percentage of total marks")
}

class AQAQualSpec {
  board ExamBoard ?
  qualification_level QualificationLevel
  subject string       @description("Subject slug (e.g. 'mathematics', 'english_language')")
  specification_code string  @description("e.g. '8035' for AQA GCSE Maths")
  title string
  version string
  first_teaching_year int?
  last_certification_year int?

  // Content structure
  total_marks int
  assessment_objectives AssessmentObjective[]
  component_papers int

  source_pdf string
  source_pages int
  language string?
}

class OCRQualSpec {
  board ExamBoard ?
  qualification_level QualificationLevel
  subject string       @description("Subject slug (e.g. 'mathematics', 'english_language')")
  specification_code string  @description("e.g. 'J560' for OCR GCSE Maths")
  title string
  version string
  first_teaching_year int?
  last_certification_year int?

  total_marks int
  assessment_objectives AssessmentObjective[]
  component_papers int

  source_pdf string
  source_pages int
  language string?
}

class EdexcelQualSpec {
  board ExamBoard ?
  qualification_level QualificationLevel
  subject string       @description("Subject slug (e.g. 'mathematics', 'english_language')")
  specification_code string  @description("e.g. '1MA1' for Edexcel GCSE Maths")
  title string
  version string
  first_teaching_year int?
  last_certification_year int?

  total_marks int
  assessment_objectives AssessmentObjective[]
  component_papers int

  source_pdf string
  source_pages int
  language string?
}

// ============================================================================
// BAML functions — the 3 England board-specific extractors (BIEP v2)
// ============================================================================

function ExtractAQAQualSpec(
  pdf_text: string,
  subject: string?,
  qualification_level: string?,
) -> AQAQualSpec {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractOCRQualSpec(
  pdf_text: string,
  subject: string?,
  qualification_level: string?,
) -> OCRQualSpec {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractEdexcelQualSpec(
  pdf_text: string,
  subject: string?,
  qualification_level: string?,
) -> EdexcelQualSpec {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
