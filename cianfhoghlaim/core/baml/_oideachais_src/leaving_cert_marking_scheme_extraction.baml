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

class MarkingPoint {
  questionNumber int
  partLabel string? @description("Optional sub-part label, e.g. '(a)', '(b)', '(i)'")
  markValue int @description("Marks awarded for this marking point")
  markType MarkingType @description("The type of mark (M1A1, M2A1, A1, B1, AO1-7, etc.)")
  answerText string @description("Expected answer or marking instruction text")
  alternativeAnswers string[]? @description("Acceptable alternative answers or marking instructions")
  isOptional bool @description("Is this marking point in an optional question?")
  requiresFormulaImage bool @description("True if this point depends on a LaTeX formula image (handled by Stage 2 diagram_detector)")
}

class MarkingScheme {
  subject string
  year int
  paper string
  level string @description("H, O, or F")
  totalMarks int
  markingPoints MarkingPoint[]
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

function ExtractMarkingScheme(pdf_text: string) -> MarkingScheme {
  client LitellmClient
  prompt #"
    You are an Irish Leaving Certificate marking scheme analyst. Extract
    all marking points from the following marking scheme PDF text.

    For each marking point:
    - `questionNumber`: the printed question number (1, 2, 3, ...)
    - `partLabel`: optional sub-part label like '(a)', '(b)', '(i)' (null if not present)
    - `markValue`: the marks awarded for this point (integer)
    - `markType`: the type of mark, one of:
      - `M1A1` — Method mark 1, Accuracy mark 1 (maths)
      - `M2A1` — Method mark 2, Accuracy mark 1 (maths)
      - `A1` — Accuracy mark 1 (maths)
      - `B1` — Band mark 1 (maths)
      - `AO1`-`AO7` — Assessment Objective 1-7 (most non-maths subjects)
    - `answerText`: the expected answer or marking instruction
    - `alternativeAnswers`: optional list of acceptable alternative answers
    - `isOptional`: true if this marking point is in an optional question
    - `requiresFormulaImage`: true if this marking point references a
      LaTeX formula image (these are handled by Stage 2 diagram_detector
      + the deepseek-ocr-2 model)

    Subject context: {{ ctx.subject }}
    Year context: {{ ctx.year }}
    Paper context: {{ ctx.paper }}

    Marking scheme text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}
