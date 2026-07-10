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
  total_pages int
  total_marks int
  total_questions int

  sections QuestionSection[]

  // Heuristics
  duration_minutes int?
  has_formula_sheet bool
  has_data_booklet bool
  formula_sheet_pages int?
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
) -> ExamPaper {
  client ExtractEn
  prompt #"
    You are an Irish Leaving Certificate exam paper layout analyst.
    Given the text of a NCCA / SEC LC exam paper PDF, extract the
    structured paper.

    Subject context: {{ subject }}
    Paper code: {{ paper_code }} (e.g. 'LC022ALP000EV' — ALP = Higher, GLP = Ordinary, BLP = Foundation)
    Year: {{ year }}

    Section structure:
      - section_id: deterministic slug
      - section_name: e.g. 'Section A — Compulsory questions'
      - instructions: full instruction text (or null)
      - questions[]: each Question has:
          - q_id: deterministic ("q1a", "q2b(i)")
          - part: e.g. 'a', 'b(i)', 'c(ii)'
          - text_en: full question text in English
          - text_ga: Irish translation (null if EN-only)
          - question_type: SHORT_ANSWER / EXTENDED_RESPONSE /
            WORKED_SOLUTION / STRUCTURE_DRAWING / DIAGRAM_BASED /
            ESSAY / PRACTICAL / MULTIPLE_CHOICE / FILL_IN_BLANK
          - marks: integer
          - related_lo_id: link to NCCA syllabus LO (null if unclear)

    Document-level fields:
      - subject: canonical subject slug
      - paper_code: e.g. "LC022ALP000EV"
      - language: "EN" or "GA"
      - level: "HL" / "OL" / "FDN"
      - year: integer
      - source_pdf: filename
      - total_pages: integer
      - total_marks: sum of all question marks
      - total_questions: count
      - sections[]: the populated sections
      - duration_minutes: 90 / 120 / 180 / 240 (null if not stated)
      - has_formula_sheet / has_data_booklet / formula_sheet_pages: booleans

    Paper text:
    ---
    {{ pdf_text }}
    ---

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// Backward-compatibility alias (BIEP v1 — Phase 1.3 migration)
// ============================================================================
// The 8 per-subject DLT sources historically called
// `b.ExtractLeavingCertPastPaper` from `baml/education/pdfs/leaving_cert_past_paper.baml`.
// That legacy function is now `## REMOVED` (per the 1.2.2 task) and
// replaced by this canonical `ExtractExamPaperLayout`.
