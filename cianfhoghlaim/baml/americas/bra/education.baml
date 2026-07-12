// BRA education extraction BAML schema.

class BRAEducationDocument {
  mec_id string @description("The canonical per-education document id")
  jurisdiction string @description("ISO 3166-1 alpha-3 or sub-state slug")
  country_code string? @description("ISO 3166-1 alpha-3 (lowercase)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractBRAEducationDocument(
  jurisdiction: string,
  language: string,
  text: string
) -> BRAEducationDocument {
  client Claude
  prompt #"
    Extract the canonical education record from the following Brazil
    text. Preserve the canonical document id exactly.

    Jurisdiction: { jurisdiction }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
