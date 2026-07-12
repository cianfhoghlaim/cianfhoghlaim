// Sweden medicine extraction BAML schema.

class SwedenHealthGuidance {
  agency string @description("The public-health agency issuing the guidance")
  advisory_id string @description("The canonical per-advisory document id")
  nation string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("Official language of the row (sv)")
  title string
  target_audience string? @description("general_public | clinicians | parents | schools | employers")
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractSwedenHealthGuidance(
  nation: string,
  language: string,
  text: string
) -> SWEHealthGuidance {
  client Claude
  prompt #"
    Extract the canonical health guidance record from the following
    Sweden text. Preserve the agency, advisory id, and
    target_audience exactly.

    Nation: { nation }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
