// France law extraction BAML schema.

class FRALawDocument {
  legifrance_id string @description("The canonical per-law document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("The official language of France")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractFRALawDocument(
  country_code: string,
  language: string,
  text: string
) -> FRALawDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
