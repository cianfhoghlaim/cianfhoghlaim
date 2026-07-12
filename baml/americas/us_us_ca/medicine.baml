// US_US_CA medicine extraction BAML schema.

class US_US_CAMedicineDocument {
  cdph_id string @description("The canonical per-medicine document id")
  jurisdiction string @description("ISO 3166-1 alpha-3 or sub-state slug")
  country_code string? @description("ISO 3166-1 alpha-3 (lowercase)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractUS_US_CAMedicineDocument(
  jurisdiction: string,
  language: string,
  text: string
) -> US_US_CAMedicineDocument {
  client Claude
  prompt #"
    Extract the canonical medicine record from the following California
    text. Preserve the canonical document id exactly.

    Jurisdiction: { jurisdiction }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
