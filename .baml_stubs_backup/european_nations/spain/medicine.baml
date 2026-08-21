// Spain medicine extraction BAML schema.

class SpainMedicineDocument {
  mscbs_id string @description("The canonical per-medicine document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("The official language of Spain")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractSpainMedicineDocument(
  country_code: string,
  language: string,
  text: string
) -> SpainMedicineDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
