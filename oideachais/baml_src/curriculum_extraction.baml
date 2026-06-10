// BAML schema: Leaving Certificate Curriculum Extraction
//
// Generic syllabus and exam-paper extraction for all Leaving Cert subjects.
// This replaces the older oideachais-specific extraction that was lost
// during the restructuring (referenced in CHANGELOG.md §8.5.4).

class CurriculumTopic {
  topicId string
  name string
  strand string @description("The strand/unit this topic belongs to")
  learningOutcomes string[] @description("The NCCA learning outcomes for this topic")
  suggestedHours int @description("Recommended teaching hours (0 if unknown)")
  linkedTopics string[] @description("Related topics in other strands")
}

class CurriculumExtraction {
  subject string
  level string @description("Higher, Ordinary, or Foundation")
  year int @description("Syllabus year")
  topics CurriculumTopic[]
  totalSuggestedHours int
}

function ExtractCurriculumSyllabus(pdf_text: string) -> CurriculumExtraction {
  client "litellm"
  prompt #"
    You are an Irish Leaving Certificate curriculum expert. Extract the
    full syllabus structure from the provided NCCA syllabus PDF text.

    For each topic:
    - `topicId`: a short kebab-case identifier (e.g. 'differentiation')
    - `name`: the formal topic name
    - `strand`: the NCCA strand/unit name
    - `learningOutcomes`: the full learning outcome statements
    - `suggestedHours`: the recommended teaching hours (0 if not stated)

    Subject: {{ ctx.subject }}
    Level: {{ ctx.level }}

    PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}
