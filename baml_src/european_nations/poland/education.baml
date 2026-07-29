// Poland education extraction BAML schema.

class PolandEducationDocument {
  men_id string @description("The canonical per-education document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("The official language of Poland")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractPolandEducationDocument(
  country_code: string,
  language: string,
  text: string
) -> PolandEducationDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
