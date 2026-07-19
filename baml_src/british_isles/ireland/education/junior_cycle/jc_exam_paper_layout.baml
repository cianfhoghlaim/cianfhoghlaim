// BAML schema: Junior Cycle Exam Paper Layout Extraction
//
// Used by the BIEP v2 JC pipeline to extract structured exam-paper data from
// NCCA Junior Cycle exam paper PDFs. The JC exams combine CBA marks (from
// classroom-based assessment) with final-exam marks.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
//
// Reference: openspec/changes/2026-07-20-biep-v2-junior-cycle-extraction-v1/

enum JCExamLevel {
  COMMON_LEVEL   @description("All students sit the same paper")
  FOUNDATION     @description("Foundation Level (where applicable)")
  HIGHER         @description("Higher Level (where applicable)")
  OL            @description("Ordinary Level (where applicable)")
}

enum JCQuestionType {
  SHORT_ANSWER
  EXTENDED_RESPONSE
  MULTIPLE_CHOICE
  FILL_IN_BLANK
  PRACTICAL
  DIAGRAM_BASED
  ESSAY
  WORKED_SOLUTION
  MATCHING
  ORAL          @description("Oral / aural component")
  PORTFOLIO     @description("Portfolio submission")
}

class JCQuestion {
  q_id string
  part string?              @description("e.g. 'a', 'b(i)', 'c(ii)'")
  text_en string
  text_ga string?
  question_type JCQuestionType
  marks int
  related_lo_id string?    @description("Learning outcome from syllabus")
  related_cba_id string?   @description("Related CBA id, if any")
}

class JCExamSection {
  section_id string
  section_name_en string
  section_name_ga string?
  instructions_en string?
  instructions_ga string?
  questions JCQuestion[]
  total_marks int
  has_optional_questions bool
}

class JCExamPaper {
  // Document-level metadata
  subject string
  paper_code string         @description("e.g. 'JC001EN-2024-COMMON'")
  language string           @description("EN, GA, or EN_AND_GA")
  level JCExamLevel
  year int                  @description("Exam year")
  source_pdf string
  total_pages int
  total_marks int
  duration_minutes int?
  has_formula_sheet bool
  has_data_booklet bool

  // Sections + CBA marks
  sections JCExamSection[]
  cba_marks int             @description("Total marks carried over from CBAs")
  cba_percentage int        @description("Cba_percentage of final grade")

  // Heuristic metrics
  total_questions int
}


// ============================================================================
// BAML function — the canonical JC exam-paper extractor (BIEP v2)
// ============================================================================
// Returns the canonical `JCExamPaper` Pydantic class with per-section
// `JCQuestion[]` and per-paper `cba_marks` + `cba_percentage`.

function ExtractJCExamPaper(
  pdf_text: string,
  subject: string?,
  level: string?,
  year: int?,
) -> JCExamPaper {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
