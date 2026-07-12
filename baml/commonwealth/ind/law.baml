// India law extraction BAML schema.

class INDLawDocument {
  india_code_id string @description("The canonical per-law document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractINDLawDocument(
  country_code: string,
  language: string,
  text: string
) -> INDLawDocument {
  client Claude
  prompt #"
    Extract the canonical law record from the following India
    text. Preserve the canonical document id exactly.

    Country: { country_code }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
