// France medicine extraction BAML schema.

class FranceMedicineDocument {
  has_sante_id string @description("The canonical per-medicine document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("The official language of France")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractFranceMedicineDocument(
  country_code: string,
  language: string,
  text: string
) -> FranceMedicineDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
