// New Zealand law extraction BAML schema.

class NZLLawDocument {
  nz_legislation_id string @description("The canonical per-law document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractNZLLawDocument(
  country_code: string,
  language: string,
  text: string
) -> NZLLawDocument {
  client Claude
  prompt #"
    Extract the canonical law record from the following New Zealand
    text. Preserve the canonical document id exactly.

    Country: { country_code }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
