// BAML schema: Leaving Certificate Marking Scheme Extraction
//
// Extracts PCLM marking patterns, common mistakes, and allocation
// conventions from SEC marking scheme PDFs.
//
// Re-gen after changes:  `cd oideachais && uv run baml-cli generate`

class MarkingPoint {
  pointNumber int
  marksAllocated int
  description string
  validAlternatives string[] @description("Alternative acceptable answers (if any)")
}

class CommonMistake {
  topic string
  mistake string @description("What students commonly get wrong")
  marksLost string @description("How many marks are typically lost")
  howToAvoid string
}

class MarkingAllocation {
  topic string
  totalMarks int
  pclmPattern string @description("How marks are distributed: partial credit / logical marking")
  markingPoints MarkingPoint[] @description("Per-point breakdown if explicit in the scheme")
}

class MarkingScheme {
  subject string
  year int
  paper string
  level string
  totalMarks int
  allocations MarkingAllocation[]
  commonMistakes CommonMistake[]
}

function ExtractMarkingScheme(pdf_text: string) -> MarkingScheme {
  client LitellmClient
  prompt #"
    You are an Irish Leaving Certificate marking scheme analyst. Extract the
    marking point breakdown and common mistakes from the scheme PDF text.

    For each topic allocation:
    - `totalMarks`: total marks available for this topic across the scheme
    - `pclmPattern`: describe how marks are awarded (partial credit, logical
      marking, step-marking, etc.)

    For each common mistake:
    - `topic`: which topic area it relates to
    - `mistake`: the specific error students make
    - `marksLost`: typical impact on marks
    - `howToAvoid`: practical advice to avoid the mistake

    Subject: {{ ctx.subject }}
    Year: {{ ctx.year }}
    Paper: {{ ctx.paper }}

    PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}
