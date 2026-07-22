// BAML schema: Exam Paper Layout Extraction
//
// Used by the LC5-subject pipeline to extract structured question data
// from NCCA Leaving Certificate exam papers (LC###ALP###EV.pdf format
// for English; LC###GLP###IV.pdf for Irish). Each paper contains a
// sequence of Question sections, each with sub-parts and allocate marks.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

enum LcQuestionType {
  SHORT_ANSWER      @description("1-3 sentence response")
  EXTENDED_RESPONSE @description("Longer paragraph response")
  WORKED_SOLUTION   @description("Step-by-step calculation/proof")
  STRUCTURE_DRAWING @description("Lewis structure, organic structure, etc.")
  DIAGRAM_BASED     @description("Read from a chart/figure/table")
  ESSAY             @description("Long-form essay (typically 25+ marks)")
  PRACTICAL         @description("Lab question with procedure")
  MULTIPLE_CHOICE   @description("Choose one option")
  FILL_IN_BLANK     @description("Complete the missing words/numbers")
}

class Question {
  q_id string
  part string              @description("e.g. 'a', 'b(i)', 'c(ii)'")
  text_en string
  text_ga string?
  question_type LcQuestionType
  marks int
  related_lo_id string?    @description("Learning outcome from syllabus")
}

class QuestionSection {
  section_id string
  section_name string
  instructions string?
  questions Question[]
  total_marks int
}

class ExamPaper {
  subject string
  paper_code string         @description("e.g. 'LC022ALP000EV'")
  language string           @description("EN or GA")
  level string              @description("OL, HL, or FDN")
  year int                  @description("Exam year")

  source_pdf string
  source_pages int           @description("Alias for total_pages kept for parity with SyllabusDocument.")
  total_pages int
  total_marks int
  total_questions int

  sections QuestionSection[]

  // Heuristics
  duration_minutes int?
  has_formula_sheet bool
  has_data_booklet bool
  formula_sheet_pages int?

  // Lineage provenance (R28). Composed from
  // `lc_extraction/_shared/lineage_trace.baml`.
  lineage LineageTrace?
}

// ============================================================================
// BAML function — the canonical extractor (BIEP v1)
// ============================================================================
// Replaces the legacy `b.ExtractLeavingCertPastPaper` from
// `baml/education/pdfs/leaving_cert_past_paper.baml`.
//
// Returns the canonical `ExamPaper` Pydantic class with
// `QuestionSection[]` and per-question `marks` + `related_lo_id` linkage.

function ExtractExamPaperLayout(
  pdf_text: string,
  subject: string?,
  paper_code: string?,
  year: int?,
) -> ExamPaper {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// ============================================================================
// Backward-compatibility alias (BIEP v1 — Phase 1.3 migration)
// ============================================================================
// The 8 per-subject DLT sources historically called
// `b.ExtractLeavingCertPastPaper` from `baml/education/pdfs/leaving_cert_past_paper.baml`.
// That legacy function is now `## REMOVED` (per the 1.2.2 task) and
// replaced by this canonical `ExtractExamPaperLayout`.
