// GEO medicine / public-health extraction BAML schema (EU
// candidate/neighbour full-depth expansion).

class GEOHealthGuidance {
  agency string @description("The issuing public-health agency of Georgia")
  advisory_id string @description("The canonical per-advisory document id")
  language string @description("Official language of Georgia")
  target_audience string @description("general_public | clinicians | schools | travellers")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractGEOHealthGuidance(
  nation: string,
  language: string,
  text: string
) -> GEOHealthGuidance {
  client Claude
  prompt #"
    Extract the canonical public-health guidance record from the
    following Georgia text. Preserve the issuing agency + the
    advisory id.

    Nation: { nation }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
