// South Africa medicine extraction BAML schema.

class SouthAfricaMedicineDocument {
  sahpra_id string @description("The canonical per-medicine document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractSouthAfricaMedicineDocument(
  country_code: string,
  language: string,
  text: string
) -> SouthAfricaMedicineDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
