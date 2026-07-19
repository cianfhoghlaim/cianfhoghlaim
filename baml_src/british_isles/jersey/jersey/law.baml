// JERSEY law extraction BAML schema (BIEP parity Crown layer).

class JERSEYLawDocument {
  url string @description("Canonical document URL")
  language string @description("The official language of the row")
  island string @description("Crown Dependency slug")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractJERSEYLawDocument(
  island: string,
  language: string,
  text: string
) -> JERSEYLawDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
