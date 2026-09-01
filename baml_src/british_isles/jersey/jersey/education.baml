// JERSEY education extraction BAML schema (BIEP parity Crown layer).

class JerseyEducationDocument {
  url string @description("Canonical document URL")
  language string @description("The official language of the row")
  island string @description("Crown Dependency slug")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractJerseyEducationDocument(
  island: string,
  language: string,
  text: string
) -> JerseyEducationDocument {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
