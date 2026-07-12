// GUERNSEY law extraction BAML schema (BIEP parity Crown layer).

class GUERNSEYLawDocument {
  url string @description("Canonical document URL")
  language string @description("The official language of the row")
  island string @description("Crown Dependency slug")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractGUERNSEYLawDocument(
  island: string,
  language: string,
  text: string
) -> GUERNSEYLawDocument {
  client Claude
  prompt #"
    Extract the canonical law record from the following Government of Guernsey text.

    Island: { island }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
