// ISLE_OF_MAN education extraction BAML schema (BIEP parity Crown layer).

class ISLE_OF_MANEducationDocument {
  url string @description("Canonical document URL")
  language string @description("The official language of the row")
  island string @description("Crown Dependency slug")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractISLE_OF_MANEducationDocument(
  island: string,
  language: string,
  text: string
) -> ISLE_OF_MANEducationDocument {
  client Claude
  prompt #"
    Extract the canonical education record from the following Isle of Man Government text.

    Island: { island }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
