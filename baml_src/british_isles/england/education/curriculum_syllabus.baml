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

enum ExamBoard {
  AQA
  OCR
  EDEXCEL
  WJEC
  CAIE
}

enum QualificationLevel {
  GCSE
  A_LEVEL
  AS_LEVEL
  GCSE_SHORT
  BTEC
}

class AssessmentObjective {
  ao_id string
  title string
  description string
  weighting_pct int     @description("Percentage of total marks")
}

class AQAQualSpec {
  board ExamBoard = "AQA"
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
  language string = "en"
}

class OCRQualSpec {
  board ExamBoard = "OCR"
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
  language string = "en"
}

class EdexcelQualSpec {
  board ExamBoard = "EDEXCEL"
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
  language string = "en"
}

// ============================================================================
// BAML functions — the 3 England board-specific extractors (BIEP v2)
// ============================================================================

function ExtractAQAQualSpec(
  pdf_text: string,
  subject: string?,
  qualification_level: string?,
) -> AQAQualSpec {
  client ExtractEnStrong
  prompt #"
    You are an England AQA qualification specification analyst. Given the
    text of an AQA specification PDF (e.g. GCSE Mathematics 8035), extract
    the structured qualification record.

    Subject: { subject }
    Qualification Level: { qualification_level }

    {{ ctx.output_format }}
  "#
}

function ExtractOCRQualSpec(
  pdf_text: string,
  subject: string?,
  qualification_level: string?,
) -> OCRQualSpec {
  client ExtractEnStrong
  prompt #"
    You are an England OCR qualification specification analyst. Given the
    text of an OCR specification PDF, extract the structured qualification
    record.

    Subject: { subject }
    Qualification Level: { qualification_level }

    {{ ctx.output_format }}
  "#
}

function ExtractEdexcelQualSpec(
  pdf_text: string,
  subject: string?,
  qualification_level: string?,
) -> EdexcelQualSpec {
  client ExtractEnStrong
  prompt #"
    You are an England Edexcel (Pearson) qualification specification
    analyst. Given the text of an Edexcel specification PDF, extract the
    structured qualification record.

    Subject: { subject }
    Qualification Level: { qualification_level }

    {{ ctx.output_format }}
  "#
}
