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

function ExtractPastPaper(pdf_text: string) -> PastPaper {
  client LitellmClient
  prompt #"
    You are an Irish Leaving Certificate exam paper analyst. Extract all
    questions from the following exam paper PDF text.

    For each question:
    - `questionNumber`: the printed question number
    - `topic`: the primary Leaving Cert topic (e.g. 'Differentiation',
      'Cell Division', 'The Plant') — NOT generic terms like 'Question 1'
    - `subtopic`: optional more granular topic
    - `marks`: the maximum marks printed next to the question
    - `questionText`: the full text of the question
    - `isOptional`: true if this question is in a 'pick from' section

    Subject: {{ ctx.subject }}
    Year: {{ ctx.year }}
    Paper: {{ ctx.paper }}

    PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}
