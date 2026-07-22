// Ukraine education extraction BAML schema.

class UKREducationDocument {
  ministry_education_science_id string @description("The canonical per-education document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("The official language of Ukraine")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractUKREducationDocument(
  country_code: string,
  language: string,
  text: string
) -> UKREducationDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
