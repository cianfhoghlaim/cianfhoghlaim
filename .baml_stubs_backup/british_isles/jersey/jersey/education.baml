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
) -> JerseyEducationDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
