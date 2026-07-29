// BRA medicine extraction BAML schema.

class BrazilMedicineDocument {
  anvisa_id string @description("The canonical per-medicine document id")
  jurisdiction string @description("ISO 3166-1 alpha-3 or sub-state slug")
  country_code string? @description("ISO 3166-1 alpha-3 (lowercase)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractBrazilMedicineDocument(
  jurisdiction: string,
  language: string,
  text: string
) -> BrazilMedicineDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
