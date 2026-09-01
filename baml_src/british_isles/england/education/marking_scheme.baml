// BAML schema: England Marking Scheme Extraction (BIEP v2)
//
// Used by the England pipeline to extract structured grading data from
// AQA / OCR / Edexcel marking-scheme + grade-boundary documents.
//
// The 9-1 grading scheme (GCSE) and the A*-E grading scheme (A-Level) are
// the canonical grading scales. UMS / raw-mark conversion tables are
// included for boards that publish them.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
//
// Reference: openspec/changes/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/

enum GCSEGrade {
  GRADE_9
  GRADE_8
  GRADE_7
  GRADE_6
  GRADE_5
  GRADE_4  @description("Standard pass")
  GRADE_3
  GRADE_2
  GRADE_1  @description("Lowest pass")
}

enum ALevelGrade {
  A_STAR
  A
  B
  C
  D
  E  @description("Lowest pass")
  U  @description("Ungraded / fail")
}

class GradeBoundary {
  grade string           @description("GCSEGrade or ALevelGrade enum value")
  raw_mark_min int
  raw_mark_max int
  ums_mark int?
}

class AQAMarkingScheme {
  board ExamBoard
  qualification_level QualificationLevel
  subject string

  grade_boundaries GradeBoundary[]
  component_weights float[]   @description("Per-component weighting percentages")

  source_pdf string
  source_pages int
  year int?
}

function ExtractAQAMarkingScheme(
  pdf_text: string,
  subject: string?,
  qualification_level: string?,
) -> AQAMarkingScheme {  client ExtractEn
  // Real extraction prompt (2026-08-08 docs-informed-quest-and-credential-
  // generation-v1 change) — same fix as ExtractAQAExamPaper above.
  prompt #"
    You are extracting the grade-boundary / marking guidance for an AQA
    GCSE/A-Level {{ subject }} qualification ({{ qualification_level }}
    level) from the document text below.

    Extract:
    - board: AQA.
    - qualification_level: the QualificationLevel matching
      {{ qualification_level }}.
    - subject: the subject slug; use {{ subject }} if given, otherwise
      infer it from the document title.
    - grade_boundaries: every grade boundary stated in the text, each
      with its grade (a GCSEGrade value like "GRADE_9".."GRADE_1" for
      GCSE, or an ALevelGrade value like "A_STAR".."U" for A-Level —
      choose the scheme matching {{ qualification_level }}),
      raw_mark_min, raw_mark_max, and ums_mark (null if the board
      doesn't publish UMS for this qualification).
    - component_weights: the per-component weighting percentages, in
      the order the components are listed in the text.
    - source_pdf: the PDF filename if it appears in the text; otherwise "".
    - source_pages: the PDF page count if stated; otherwise estimate
      from text length (never leave unset).
    - year: the year the grade boundaries apply to; null if not stated.

    Extract only what is actually present in the text; do not invent
    boundaries. Output exactly one complete JSON object. Never use
    ellipses (...) or comments; list every grade_boundary in full.

    {{ _.role("user") }}
    Document text (subject: {{ subject }}, qualification_level: {{ qualification_level }}):

    {{ pdf_text }}

    {{ ctx.output_format }}
  "#

}
