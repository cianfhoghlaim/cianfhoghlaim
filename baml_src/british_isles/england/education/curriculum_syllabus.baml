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
  source_pages int?
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
  source_pages int?
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
  source_pages int?
  language string?
}

// ============================================================================
// BAML functions — the 3 England board-specific extractors (BIEP v2)
// ============================================================================

// The 3 functions below were `prompt #"Auto-generated extraction
// prompt."#` — a placeholder that was never filled in. That renders as a
// system-only chat with no user content, which MiniMax (BIEPV3Extract)
// rejects with 400 "chat content is empty" — the exact bug class already
// documented and fixed for Ireland's chemistry BAML functions and for
// ExtractUKQualSpec above (missing `{{ _.role("user") }}` marker). No
// live caller currently routes through these 3 (the v3 generic pipeline
// uses ExtractUKQualSpec instead — see above), so this was dormant, not
// yet hit in production. Given real prompts here rather than leaving
// live callers, if any use them via backwards compatibility.

function ExtractAQAQualSpec(
  pdf_text: string,
  subject: string?,
  qualification_level: string?,
) -> AQAQualSpec {  client BIEPV3Extract
  prompt #"
    Extract the qualification specification from this AQA further education
    document at {{ qualification_level }} level for the subject {{ subject }}.

    Look for:
    - Specification code (e.g. '8035' for AQA GCSE Maths).
    - Total marks for the qualification.
    - Assessment objectives with their weightings.
    - Component papers count.
    - First teaching year and last certification year.
    - Source PDF page count (leave null if extracting from a crawled web
      page rather than an actual PDF).

    {{ _.role("user") }}
    Document text (AQA {{ qualification_level }}, subject: {{ subject }}):

    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

function ExtractOCRQualSpec(
  pdf_text: string,
  subject: string?,
  qualification_level: string?,
) -> OCRQualSpec {  client BIEPV3Extract
  prompt #"
    Extract the qualification specification from this OCR further education
    document at {{ qualification_level }} level for the subject {{ subject }}.

    Look for:
    - Specification code (e.g. 'J560' for OCR GCSE Maths).
    - Total marks for the qualification.
    - Assessment objectives with their weightings.
    - Component papers count.
    - First teaching year and last certification year.
    - Source PDF page count (leave null if extracting from a crawled web
      page rather than an actual PDF).

    {{ _.role("user") }}
    Document text (OCR {{ qualification_level }}, subject: {{ subject }}):

    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

function ExtractEdexcelQualSpec(
  pdf_text: string,
  subject: string?,
  qualification_level: string?,
) -> EdexcelQualSpec {  client BIEPV3Extract
  prompt #"
    Extract the qualification specification from this Edexcel further
    education document at {{ qualification_level }} level for the subject
    {{ subject }}.

    Look for:
    - Specification code (e.g. '1MA1' for Edexcel GCSE Maths).
    - Total marks for the qualification.
    - Assessment objectives with their weightings.
    - Component papers count.
    - First teaching year and last certification year.
    - Source PDF page count (leave null if extracting from a crawled web
      page rather than an actual PDF).

    {{ _.role("user") }}
    Document text (Edexcel {{ qualification_level }}, subject: {{ subject }}):

    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
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
  source_pages int?
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

    {{ _.role("user") }}
    Document text ({{ board }} {{ qualification_level }}, subject: {{ subject }}):

    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}
