// VEN medicine extraction BAML schema.

class VENMedicineDocument {
  mpps_id string @description("The canonical per-medicine document id")
  jurisdiction string @description("ISO 3166-1 alpha-3 or sub-state slug")
  country_code string? @description("ISO 3166-1 alpha-3 (lowercase)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractVENMedicineDocument(
  jurisdiction: string,
  language: string,
  text: string
) -> VENMedicineDocument {
  client Claude
  prompt #"
    Extract the canonical medicine record from the following Venezuela
    text. Preserve the canonical document id exactly.

    Jurisdiction: { jurisdiction }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
