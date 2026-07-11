// PRT medicine extraction BAML schema (EU nations full-depth).

class PRTHealthGuidance {
  agency string @description("The publishing agency (e.g. NIPH, EODY, NIJZ)")
  advisory_id string @description("The canonical advisory id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("Official language of the advisory")
  target_audience string @description("general_public | clinicians | schools | employers")
  title string
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractPRTHealthGuidance(
  nation: string,
  language: string,
  text: string
) -> PRTHealthGuidance {
  client Claude
  prompt #"
    Extract the canonical Portugal health guidance record from the text.
    Preserve the advisory_id and the target_audience tag exactly.

    Nation: { nation }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
