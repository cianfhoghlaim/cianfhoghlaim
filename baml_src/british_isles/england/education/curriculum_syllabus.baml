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

// ============================================================================
// BAML function: Generic UK Qualification Specification (BIEP v3)
// ============================================================================
//
// Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change,
// the 3 board-specific functions above collapse into a single generic
// `ExtractUKQualSpec(board: ExamBoard, ...)` for the BIEP v3 generic
// jurisdiction pipeline. The 3 board-specific functions are retained for
// backwards compatibility but the v3 jurisdiction pipeline routes through
// the generic function.
//
// The generic function takes a `board` argument and returns a
// `UKQualificationSpec` (the union of the 3 board-specific types).

class UKQualificationSpec {
  board ExamBoard
  qualification_level QualificationLevel
  subject string              @description("Subject slug (e.g. 'mathematics', 'english_language')")
  specification_code string   @description("e.g. '8035' for AQA GCSE Maths, 'J560' for OCR GCSE Maths, '1MA1' for Edexcel GCSE Maths")
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

function ExtractUKQualSpec(
  pdf_text: string,
  board: ExamBoard,
  subject: string?,
  qualification_level: string?,
) -> UKQualificationSpec {
  client BIEPV3Extract
  prompt #"
    Extract the qualification specification from this {{ board }} further education
    document at {{ qualification_level }} level for the subject {{ subject }}.

    Look for:
    - Specification code (e.g. '8035' for AQA GCSE Maths, 'J560' for OCR GCSE Maths,
      '1MA1' for Edexcel GCSE Maths).
    - Total marks for the qualification.
    - Assessment objectives with their weightings.
    - Component papers count.
    - First teaching year and last certification year.
    - Source PDF page count.

    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}
