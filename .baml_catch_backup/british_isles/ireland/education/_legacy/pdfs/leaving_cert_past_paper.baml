// BAML schema: Leaving Certificate Past Paper Extraction
//
// Extracts questions, marks, and topic tags from past exam paper PDFs.
// Used by the per-subject pipeline to generate the past exam analysis
// and topic frequency tables.
//
// Re-gen after changes:  `cd oideachais && uv run baml-cli generate`

class PastExamQuestion {
  questionNumber int
  year int
  paper string @description("Paper identifier, e.g. 'paper-1', 'paper-2'")
  level string @description("'H', 'O', or 'F'")
  topic string @description("Primary topic, e.g. 'Differentiation'")
  subtopic string? @description("Optional subtopic breakdown")
  marks int @description("Maximum marks for this question")
  questionText string @description("The full question text as printed")
  isOptional bool @description("Is this question optional (e.g. pick 4 of 6)?")
}

class PastPaper {
  subject string
  year int
  paper string
  level string
  totalMarks int
  questions PastExamQuestion[]
  @@stream.done
}

function ExtractPastPaper(pdf_text: string) -> PastPaper {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
