// South Africa law extraction BAML schema.

class ZAFLawDocument {
  sa_government_gazette_id string @description("The canonical per-law document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractZAFLawDocument(
  country_code: string,
  language: string,
  text: string
) -> ZAFLawDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
