// =============================================================================
// Document Metadata Functions (split from curriculum_extraction.baml)
// PDF metadata + curriculum syllabus extraction functions for the
// 6-stage PDF processing pipeline (per oideachais-pdf-processing spec).
// =============================================================================

class DocumentMetadata {
  title string @description("The contextual title, e.g. \"Leaving Certificate English Specification\"")
  category DocumentCategory
  subject_slug string?
  cycle EducationLevel?
  year_effective int? @description("Extracted from phrases like \"effect earlier than 2027\"")
  year_examined int? @description("Extracted from phrases like \"examination to 2028\"")
  language string? @description("en or ga")
  url string @description("The exact URL to the PDF")
  @@stream.done
}

function ExtractAllPdfMetadata(page_markdown: string,
  pdf_urls: string[]) -> DocumentMetadata[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"You are an expert at extracting metadata from Irish education PDF documents.

Parse metadata for a batch of PDFs from their pre-extracted text content.

PDF URLS: {{ pdf_urls|join(", ") }}

PAGES MARKDOWN:
{{ page_markdown }}

For each PDF, extract:
1. Document type (curriculum_specification, exam_paper, marking_scheme, examiner_report, annual_report, policy_document)
2. Title (English and Irish if available)
3. Author/publisher (NCCA, SEC, Department of Education, etc.)
4. Year of publication
5. Subject (if applicable, use the canonical subject slug)
6. Educational cycle/level (early_childhood, primary, junior_cycle, senior_cycle, tertiary)
7. Language (en, ga, bilingual)
8. Year of examination (if exam material)
9. URL of the source PDF
10. Brief description of content

Group results by document type for downstream routing. This metadata enables efficient caching and topic-graph construction in the knowledge graph.

{{ ctx.output_format(prefix="Answer with this format:\n") }}

{{ _.role("user") }}
    BATCH: {{ pdf_urls|length }} URLs
"#
}


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
  @@stream.done
}

function ExtractCurriculumExtraction(pdf_text: string) -> CurriculumExtraction {
  client LitellmClient
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