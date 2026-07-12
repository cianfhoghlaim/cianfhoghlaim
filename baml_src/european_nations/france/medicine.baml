// France medicine extraction BAML schema.

class FRAMedicineDocument {
  has_sante_id string @description("The canonical per-medicine document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("The official language of France")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractFRAMedicineDocument(
  country_code: string,
  language: string,
  text: string
) -> FRAMedicineDocument {
  client Claude
  prompt #"
    Extract the canonical medicine record from the following France
    text. Preserve the canonical document id exactly.

    Country: { country_code }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
