// CAN law extraction BAML schema.

class CANLawDocument {
  federal_laws_id string @description("The canonical per-law document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractCANLawDocument(
  country_code: string,
  language: string,
  text: string
) -> CANLawDocument {
  client Claude
  prompt #"
    Extract the canonical law record from the following Canada
    text. Preserve the canonical document id exactly.

    Country: { country_code }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
