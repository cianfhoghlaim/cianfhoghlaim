// Australia law extraction BAML schema.

class AUSLawDocument {
  federal_register_legislation_id string @description("The canonical per-law document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractAUSLawDocument(
  country_code: string,
  language: string,
  text: string
) -> AUSLawDocument {
  client Claude
  prompt #"
    Extract the canonical law record from the following Australia
    text. Preserve the canonical document id exactly.

    Country: { country_code }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
