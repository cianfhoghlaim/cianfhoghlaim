// GUERNSEY education extraction BAML schema (BIEP parity Crown layer).

class GUERNSEYEducationDocument {
  url string @description("Canonical document URL")
  language string @description("The official language of the row")
  island string @description("Crown Dependency slug")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractGUERNSEYEducationDocument(
  island: string,
  language: string,
  text: string
) -> GUERNSEYEducationDocument {
  client Claude
  prompt #"
    Extract the canonical education record from the following Government of Guernsey text.

    Island: { island }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
