// Spain education extraction BAML schema.

class ESPEducationDocument {
  mecd_id string @description("The canonical per-education document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("The official language of Spain")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractESPEducationDocument(
  country_code: string,
  language: string,
  text: string
) -> ESPEducationDocument {
  client Claude
  prompt #"
    Extract the canonical education record from the following Spain
    text. Preserve the canonical document id exactly.

    Country: { country_code }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
