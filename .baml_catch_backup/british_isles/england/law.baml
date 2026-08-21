// EN law extraction BAML schema (BIEP parity).

class EnglandLawDocument {
  url string @description("Canonical syllabus / document URL")
  language string @description("The official language of the row")
  nation string @description("ISO 3166-1 alpha-3 or British Isles legacy slug")
  subject string? @description("Subject slug (e.g. mathematics, chemistry)")
  exam_board string? @description("Awarding body (AQA)")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractEnglandLawDocument(
  nation: string,
  language: string,
  text: string
) -> EnglandLawDocument {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
