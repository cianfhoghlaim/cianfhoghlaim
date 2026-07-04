// BAML schema: Exam Paper Layout Extraction
//
// Used by the LC5-subject pipeline to extract structured question data
// from NCCA Leaving Certificate exam papers (LC###ALP###EV.pdf format
// for English; LC###GLP###IV.pdf for Irish). Each paper contains a
// sequence of Question sections, each with sub-parts and allocate marks.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

enum QuestionType {
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
  q_id: string
  part: string              @description("e.g. 'a', 'b(i)', 'c(ii)'")
  text_en: string
  text_ga: string?
  question_type: QuestionType
  marks: int
  related_lo_id: string?    @description("Learning outcome from syllabus")
}

class QuestionSection {
  section_id: string
  section_name: string
  instructions: string?
  questions: Question[]
  total_marks: int
}

class ExamPaper {
  subject: string
  paper_code: string         @description("e.g. 'LC022ALP000EV'")
  language: string           @description("EN or GA")
  level: string              @description("OL, HL, or FDN")
  year: int                  @description("Exam year")

  source_pdf: string
  total_pages: int
  total_marks: int
  total_questions: int

  sections: QuestionSection[]

  // Heuristics
  duration_minutes: int?
  has_formula_sheet: bool
  has_data_booklet: bool
  formula_sheet_pages: int?
}
