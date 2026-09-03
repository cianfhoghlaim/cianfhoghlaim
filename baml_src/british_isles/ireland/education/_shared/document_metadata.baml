// =============================================================================
// Document Metadata Functions (split from curriculum_extraction.baml)
// PDF metadata + curriculum syllabus extraction functions for the
// 6-stage PDF processing pipeline (per cianfhoghlaim-pdf-processing spec).
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
  pdf_urls: string[]) -> DocumentMetadata[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    DocumentMetadata[] {}
  }
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

function ExtractCurriculumExtraction(pdf_text: string) -> CurriculumExtraction {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    CurriculumExtraction {
      subject "",
      topics null,
      totalSuggestedHours 0,
    }
  }
}