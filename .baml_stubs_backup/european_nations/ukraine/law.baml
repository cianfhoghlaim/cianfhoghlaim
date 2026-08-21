// Ukraine law extraction BAML schema.

class UkraineLawDocument {
  zakon_rada_id string @description("The canonical per-law document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("The official language of Ukraine")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractUkraineLawDocument(
  country_code: string,
  language: string,
  text: string
) -> UkraineLawDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
