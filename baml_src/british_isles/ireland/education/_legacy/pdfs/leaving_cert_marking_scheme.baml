// BAML schema: Leaving Certificate Marking Scheme Extraction
//
// Extracts marking points, marks, and mark types from SEC marking-scheme
// PDFs. Used by the per-subject pipeline (Stage 3 of the 6-stage PDF
// processing pipeline at oideachais-pdf-processing/spec.md).
//
// Usage:
//   from oideachais.data_platform.baml_client import b
//   scheme = b.ExtractMarkingScheme(pdf_text, subject="Mathematics", year=2024, paper="paper-1")
//
// Re-gen after changes:  `cd oideachais && uv run baml-cli generate`

class MarkingPointSec {
  questionNumber int
  partLabel string? @description("Optional sub-part label, e.g. '(a)', '(b)', '(i)'")
  markValue int @description("Marks awarded for this marking point")
  markType MarkingType @description("The type of mark (M1A1, M2A1, A1, B1, AO1-7, etc.)")
  answerText string @description("Expected answer or marking instruction text")
  alternativeAnswers string[]? @description("Acceptable alternative answers or marking instructions")
  isOptional bool @description("Is this marking point in an optional question?")
  requiresFormulaImage bool @description("True if this point depends on a LaTeX formula image (handled by Stage 2 diagram_detector)")
}

class MarkingSchemeSec {
  subject string @stream.not_null
  year int
  paper string
  level string @description("H, O, or F")
  totalMarks int
  markingPoints MarkingPointSec[] @stream.with_state
  @@stream.done
}

enum MarkingType {
  M1A1
  M2A1
  A1
  B1
  AO1
  AO2
  AO3
  AO4
  AO5
  AO6
  AO7
}

function ExtractMarkingScheme(pdf_text: string, subject: string, year: int, paper: string) -> MarkingSchemeSec {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
