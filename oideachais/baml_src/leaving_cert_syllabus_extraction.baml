// BAML schema: Leaving Certificate Syllabus Extraction
//
// Extracts topics, learning outcomes, and weighting from NCCA syllabus PDFs.
// Used by the per-subject pipeline to generate the syllabus analysis section
// of the public portal pages.
//
// Usage:
//   from oideachais.data_platform.baml_client import b
//   syllabus = b.ExtractLeavingCertSyllabus(pdf_text)
//
// Re-gen after changes:  `cd oideachais && uv run baml-cli generate`

class SyllabusTopic {
  topicId string
  name string @description("Short display name, e.g. 'Differentiation'")
  description string
  learningOutcomes string[] @description("Full NCCA learning outcome statements for this topic")
  weightPct int @description("Estimated percentage of total exam marks (0-100). 0 if unknown.")
}

class LeavingCertSyllabus {
  subject string @description("Subject name, e.g. 'Mathematics'")
  year int @description("Year this syllabus applies to")
  level string @description("One of: 'Higher', 'Ordinary', 'Foundation', 'Higher+Ordinary'")
  topics SyllabusTopic[] @description("All topics in this syllabus")
}

function ExtractLeavingCertSyllabus(pdf_text: string) -> LeavingCertSyllabus {
  client "litellm"
  prompt #"
    You are an Irish Leaving Certificate syllabus expert. Extract all topics
    and learning outcomes from the following syllabus PDF text.

    For each topic:
    - `name` is a short display name (e.g. 'Differentiation', 'Cell Biology')
    - `description` is a 1-2 sentence summary of what the topic covers
    - `learningOutcomes` are the full NCCA learning outcome statements
    - `weightPct` is your best estimate of what % of the total exam this
      topic represents (0-100). If unknown, use 0.

    Subject context: {{ ctx.subject }}
    Year context: {{ ctx.year }}

    PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}
