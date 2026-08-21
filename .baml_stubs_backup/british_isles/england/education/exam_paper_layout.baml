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
  language string?
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
) -> AQAExamPaper {  client ExtractEn
  // Real extraction prompt (2026-08-08 docs-informed-quest-and-credential-
  // generation-v1 change). Same placeholder-prompt bug class already fixed
  // for Ireland's lc_extraction functions and for England's own
  // ExtractUKQualSpec — this function was the one England extraction path
  // still left as "Auto-generated extraction prompt.", which blocked any
  // downstream exam-paper-grounded quest-pack generation for England.
  prompt #"
    You are extracting the structure of an AQA GCSE/A-Level exam paper
    for the subject {{ subject }} ({{ qualification_level }} level) from
    the document text below.

    Extract:
    - board: AQA.
    - qualification_level: the QualificationLevel matching
      {{ qualification_level }}.
    - subject: the subject slug; use {{ subject }} if given, otherwise
      infer it from the paper header.
    - paper_code: the paper code (e.g. "8035/1F"); read it from the
      header if present, otherwise "".
    - language: the paper's language (typically "en"); null if not stated.
    - level: "foundation" or "higher" as stated on the paper.
    - year: the exam year; use {{ year }} if given, otherwise read it
      from the header.
    - source_pdf: the PDF filename if it appears in the text; otherwise "".
    - total_pages: the PDF page count if stated in the text; otherwise
      estimate from the text length in hundreds of words per page (best
      effort — never leave this unset).
    - total_marks: the sum of all allocated marks across the paper.
    - duration_minutes: the stated exam duration in minutes; null if not
      stated.
    - has_formula_sheet / has_data_booklet: true if the paper references
      a formula sheet / data booklet.
    - sections: every exam section, each with its section_id,
      section_name, instructions (null if none), total_marks, and the
      full list of questions (q_id, part, text_en, question_type, marks,
      related_lo_id, related_specification_ao — null if not determinable).

    Count marks and questions carefully from the actual text; do not
    invent questions. Output exactly one complete JSON object. Never use
    ellipses (...) or comments; list every section and every question in
    full with all of its sub-parts, however long the list is.

    {{ _.role("user") }}
    Document text (subject: {{ subject }}, qualification_level: {{ qualification_level }}, year: {{ year }}):

    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}
