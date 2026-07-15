// BAML schema: England Exam Paper Layout Extraction (BIEP v2)
//
// Multi-board dispatch for AQA / OCR / Edexcel exam papers. The
// `ExtractAQAExamPaper` function inspects the PDF text for board-specific
// markers (e.g. "AQA", "OCR", "Pearson Edexcel") and dispatches to the
// correct extraction path.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
//
// Reference: openspec/changes/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/

enum UKQuestionType {
  SHORT_ANSWER
  EXTENDED_RESPONSE
  MULTIPLE_CHOICE
  FILL_IN_BLANK
  PRACTICAL
  DIAGRAM_BASED
  ESSAY
  WORKED_SOLUTION
  MATCHING
}

class UKQuestion {
  q_id string
  part string?              @description("e.g. 'a', 'b(i)', 'c(ii)'")
  text_en string
  question_type UKQuestionType
  marks int
  related_lo_id string?
  related_specification_ao string?  @description("References AQA/OCR/Edexcel AO")
}

class UKExamSection {
  section_id string
  section_name string
  instructions string?
  questions UKQuestion[]
  total_marks int
}

class AQAExamPaper {
  board ExamBoard
  qualification_level QualificationLevel
  subject string
  paper_code string         @description("e.g. '8035/1F' for AQA GCSE Maths Foundation")
  language string = "en"
  level string               @description("e.g. 'foundation' / 'higher'")
  year int

  source_pdf string
  total_pages int
  total_marks int
  duration_minutes int?
  has_formula_sheet bool
  has_data_booklet bool

  sections UKExamSection[]
}

function ExtractAQAExamPaper(
  pdf_text: string,
  subject: string?,
  qualification_level: string?,
  year: int?,
) -> AQAExamPaper {
  client ExtractEnStrong
  prompt #"
    You are an England AQA / OCR / Edexcel exam-paper layout analyst. Given
    the text of an exam-paper PDF, detect the awarding body (AQA / OCR /
    Edexcel), then extract the structured exam paper.

    Subject: { subject }
    Qualification Level: { qualification_level }
    Year: { year }

    {{ ctx.output_format }}
  "#
}
