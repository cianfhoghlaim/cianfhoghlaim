// France education extraction BAML schema.

class FRAEducationDocument {
  ministere_education_nationale_id string @description("The canonical per-education document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("The official language of France")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractFRAEducationDocument(
  country_code: string,
  language: string,
  text: string
) -> FRAEducationDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
