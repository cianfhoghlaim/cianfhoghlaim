// India law extraction BAML schema.

class IndiaLawDocument {
  india_code_id string @description("The canonical per-law document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractIndiaLawDocument(
  country_code: string,
  language: string,
  text: string
) -> IndiaLawDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
