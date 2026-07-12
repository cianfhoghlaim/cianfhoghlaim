// Finland law extraction BAML schema.

class FinlandStatute {
  statute_id string @description("The canonical per-statute document id")
  nation string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("Official language of the row (fi,sv)")
  jurisdiction string @description("Federal or sub-federal jurisdiction")
  title string
  official_status string? @description("in_force | amended | repealed | pending")
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractFinlandStatute(
  nation: string,
  language: string,
  text: string
) -> FINStatute {
  client Claude
  prompt #"
    Extract the canonical statute record from the following Finland
    text. Preserve the statute id, jurisdiction, and official_status exactly.

    Nation: { nation }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
