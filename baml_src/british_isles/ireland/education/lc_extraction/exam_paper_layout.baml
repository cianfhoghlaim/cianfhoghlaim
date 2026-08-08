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
  prompt #"
    You are an expert at reading official Irish Leaving Certificate exam
    papers (State Examinations Commission format) and extracting their
    complete question structure with fidelity to the source — every
    question, part, and mark allocation below MUST come from the PDF
    text given; never invent a question or a mark total.

    Subject: {{ subject }}
    Paper code (if known): {{ paper_code }}
    Year (if known): {{ year }}

    From the exam paper text below, extract:
    - subject: the subject slug
    - paper_code: the paper's own code if visible in the text (e.g.
      'LC022ALP000EV'), else the paper_code given above
    - language: 'EN' or 'GA' based on the language of the paper text
    - level: 'OL', 'HL', or 'FDN' — read from the paper's own cover page
      / header text (e.g. 'Ordinary Level', 'Higher Level')
    - year: the exam year stated on the paper, else the year given above
    - source_pdf: leave as an empty string; the Python caller fills this
      in from the actual file path
    - source_pages / total_pages: your best count of distinct pages
      represented in the text (equal to each other)
    - sections: every distinct section (e.g. 'Section A', 'Section B')
      you can identify, each with:
      - section_id / section_name (from the paper's own headings)
      - instructions: any instruction text specific to that section
        ('Answer any three questions from this section', etc.)
      - questions: every question and sub-part in that section, each with:
        - q_id (e.g. '1', '2') and part (e.g. 'a', 'b(i)', 'c(ii)';
          use 'a' if the question has no lettered sub-parts)
        - text_en / text_ga (whichever language this paper is in;
          leave the other empty)
        - question_type: SHORT_ANSWER, EXTENDED_RESPONSE,
          WORKED_SOLUTION, STRUCTURE_DRAWING, DIAGRAM_BASED, ESSAY,
          PRACTICAL, MULTIPLE_CHOICE, or FILL_IN_BLANK — infer from the
          question's own instruction verb and format
        - marks: the marks allocated to that specific part, as stated
          in the paper (usually in brackets, e.g. '[10 marks]')
        - related_lo_id: omit unless the paper itself cross-references a
          syllabus learning-outcome code
      - total_marks: sum of that section's question marks
    - total_marks: sum across all sections
    - total_questions: count of top-level questions (not sub-parts)
    - duration_minutes: the exam duration if stated on the cover page
    - has_formula_sheet / has_data_booklet: true only if the paper text
      explicitly references an accompanying formula sheet or data
      booklet
    - formula_sheet_pages: only if stated

    If a field has no support in the text, leave it empty or its
    numeric default rather than fabricating content.

    Exam paper PDF text:
    {{ pdf_text }}

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
