// India education extraction BAML schema.

class INDEducationDocument {
  ncert_id string @description("The canonical per-education document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractINDEducationDocument(
  country_code: string,
  language: string,
  text: string
) -> INDEducationDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
